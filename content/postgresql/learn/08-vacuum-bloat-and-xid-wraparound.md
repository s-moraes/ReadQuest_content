# Autovacuum, Dead Tuples, HOT Updates & XID Wraparound

Because PostgreSQL uses **MVCC (Multi-Version Concurrency Control)**, an `UPDATE` or `DELETE` never overwrites a row in place. Instead, it marks the old tuple version as dead and writes a new tuple version—leaving cleanup to **VACUUM**.

---

## Dead Tuples, Bloat & the Visibility Map

Every `UPDATE` creates a dead tuple that still occupies disk pages and index entries until reclaimed:

```text
Page 1: [ Tuple v1 (DEAD) ] [ Tuple v2 (LIVE) ] [ Free Space ]
```

If dead tuples accumulate faster than cleanup runs, you get **table and index bloat**: sequential scans read mostly empty or dead pages, and B-tree indexes grow shallow and slow.

### What `VACUUM` Actually Does

1. **Marks dead tuple space reusable** inside existing heap pages (without shrinking the OS file size, unlike `VACUUM FULL`).
2. **Removes dead index pointers** pointing to reclaimed tuples.
3. **Updates the Visibility Map (VM):** Marks pages where *all* tuples are visible to every active transaction—which unlocks fast **Index-Only Scans**.
4. **Freezes old Transaction IDs (`XID`)** to prevent wraparound.

| Command | Locking Impact | Reclaims OS Disk Space? |
| :--- | :--- | :--- |
| `VACUUM` / `AUTOVACUUM` | Non-blocking (runs concurrently) | No (reuses space internally) |
| `VACUUM FULL` | `AccessExclusiveLock` (blocks all) | Yes (rewrites entire table) |
| `pg_repack` (extension) | Minimal lock at final swap | Yes (online table rewrite) |

---

## HOT (Heap-Only Tuple) Optimization

Updating a row normally requires updating **every index** on that table—even if you only changed an unindexed `last_login` column.

PostgreSQL avoids this with **HOT (Heap-Only Tuple)** updates when two conditions hold:
1. None of the **indexed columns** changed.
2. There is enough **free space on the same heap page** for the new tuple version.

```sql
-- Leave 15% free space on update-heavy tables to enable HOT
ALTER TABLE user_sessions SET (fillfactor = 85);
```

With HOT, indexes still point to the original tuple, which chains locally to the new version on the same page—cutting write amplification dramatically.

---

## Tuning Autovacuum & Preventing XID Wraparound

PostgreSQL uses a 32-bit Transaction ID (`XID`) counter (~4.2 billion transactions). Because `XID` arithmetic is circular, any unfrozen row older than ~2 billion transactions would suddenly appear to be "in the future" and vanish from queries.

To prevent this **XID wraparound** catastrophe, PostgreSQL triggers an aggressive anti-wraparound autovacuum—and will **refuse all writes** if `XID` age approaches the hard limit.

### Essential Autovacuum Checks

```sql
-- Find tables with high dead tuples or stale vacuum
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;

-- Check XID age per database (danger near 2,000,000,000)
SELECT datname, age(datfrozenxid) AS xid_age
FROM pg_database
ORDER BY xid_age DESC;
```

On very large tables (100M+ rows), the default `autovacuum_vacuum_scale_factor = 0.2` waits until 20M rows are dead before running. Override it per table:

```sql
ALTER TABLE orders SET (
  autovacuum_vacuum_scale_factor = 0.01,
  autovacuum_analyze_scale_factor = 0.005
);
```
