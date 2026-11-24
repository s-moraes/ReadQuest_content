# Lock Hierarchy, Deadlocks & Zero-Downtime DDL

Most PostgreSQL production outages are not caused by slow `SELECT` queries—they are caused by **lock queues** triggered by careless schema migrations.

---

## PostgreSQL Lock Hierarchy

Every SQL statement acquires a table-level lock before touching rows. Understanding which locks conflict prevents accidental downtime:

| Lock Mode | Acquired By | Conflicts With |
| :--- | :--- | :--- |
| `AccessShareLock` | `SELECT` | `AccessExclusiveLock` only |
| `RowExclusiveLock` | `INSERT`, `UPDATE`, `DELETE` | `Share`, `ShareRowExclusive`, `Exclusive`, `AccessExclusive` |
| `ShareLock` | `CREATE INDEX` (without `CONCURRENTLY`) | `RowExclusiveLock` (blocks writes!) |
| `AccessExclusiveLock` | `ALTER TABLE`, `DROP`, `TRUNCATE`, `VACUUM FULL` | **Everything** (blocks reads and writes) |

### The Lock Queue Pile-Up Trap

Suppose a slow analytics `SELECT` holds an `AccessShareLock` for 45 seconds. If you run `ALTER TABLE orders ADD COLUMN ...`:
1. `ALTER TABLE` requests `AccessExclusiveLock` and **waits** for the analytics query to finish.
2. Every *new* `SELECT` and `INSERT` on `orders` now **queues behind** the waiting `ALTER TABLE`.
3. Within 5 seconds, your application connection pool is completely exhausted.

---

## Zero-Downtime DDL Recipes

Never run unguarded DDL in production. Follow these battle-tested PostgreSQL patterns:

### 1. Always Set `lock_timeout`

Force a migration to fail fast rather than blocking application traffic:

```sql
SET lock_timeout = '2s';
SET statement_timeout = '10s';
ALTER TABLE orders ADD COLUMN promo_code TEXT;
```

If the lock cannot be acquired within 2 seconds, the migration aborts cleanly and can be retried.

### 2. Build Indexes `CONCURRENTLY`

```sql
-- Does NOT block INSERT/UPDATE/DELETE
CREATE INDEX CONCURRENTLY idx_orders_customer_id
ON orders (customer_id);
```

Note: `CREATE INDEX CONCURRENTLY` cannot run inside a `BEGIN ... COMMIT` transaction block and takes longer, because it performs two table scans.

### 3. Add Constraints Without Full Table Scans

```sql
-- Step 1: Metadata-only lock (instant, skips existing rows)
ALTER TABLE orders
  ADD CONSTRAINT chk_amount_pos CHECK (amount > 0) NOT VALID;

-- Step 2: Validates existing rows with ShareUpdateExclusiveLock
-- (allows concurrent SELECT, INSERT, UPDATE, DELETE)
ALTER TABLE orders VALIDATE CONSTRAINT chk_amount_pos;
```

### 4. Inspecting Blocked Queries & Deadlocks

```sql
SELECT pid, state, wait_event_type, wait_event,
       pg_blocking_pids(pid) AS blocked_by, left(query, 80)
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
```

To avoid **deadlocks** in application code, always lock multiple rows in a **consistent deterministic order** (e.g., `ORDER BY id` before `SELECT ... FOR UPDATE`).
