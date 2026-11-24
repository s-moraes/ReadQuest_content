# Declarative Partitioning, Pruning & Fast Retention

Once a single table crosses hundreds of millions of rows, B-tree indexes outgrow RAM and `AUTOVACUUM` struggles to keep up. **Declarative partitioning** splits one logical table into smaller physical child tables.

---

## Partitioning Strategies

PostgreSQL supports three native partitioning schemes:

| Strategy | Best For | Example Partition Key |
| :--- | :--- | :--- |
| **`RANGE`** | Time-series events, logs, invoices | `created_at` (monthly/daily) |
| **`LIST`** | Discrete regions, tenants, or statuses | `region` (`'us'`, `'eu'`, `'br'`) |
| **`HASH`** | Evenly spreading huge IDs with no natural range | `tenant_id` (`MODULUS 16`) |

```sql
CREATE TABLE audit_events (
  id         BIGINT GENERATED ALWAYS AS IDENTITY,
  created_at TIMESTAMPTZ NOT NULL,
  payload    JSONB NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE audit_events_2026_11
  PARTITION OF audit_events
  FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');
```

---

## Partition Pruning & Zero-Bloat Retention

### 1. Partition Pruning

When your `WHERE` clause includes the partition key (`created_at >= '2026-11-15'`), the planner **skips all other partitions** at both plan time and execution time.

### 2. Instant Data Retention (No `DELETE` Bloat)

Deleting 50 million old rows with `DELETE FROM audit_events WHERE created_at < ...` generates massive WAL volume and dead-tuple bloat.

With partitioning, retiring an old month is an **instant metadata operation**:

```sql
-- Detach without blocking queries (PostgreSQL 14+)
ALTER TABLE audit_events
  DETACH PARTITION audit_events_2025_01 CONCURRENTLY;

-- Archive or drop the standalone table cleanly
DROP TABLE audit_events_2025_01;
```

---

## When NOT to Partition

Partitioning adds planning overhead and imposes rules (every `UNIQUE` or `PRIMARY KEY` must include the partition key). **Avoid partitioning** if:
- Your table is under ~50 GB or fits comfortably with a standard index.
- Your most frequent queries do *not* filter by the partition key (forcing Postgres to scan all 60 partitions).
- You create thousands of tiny partitions (keep total partitions per table under ~1,000 for fast planning).
