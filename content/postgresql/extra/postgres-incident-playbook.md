# Production Incident Playbook: CPU, Locks & WAL Bloat

Keep these diagnostic queries handy when a PostgreSQL cluster spikes in latency, saturates CPU, or runs out of disk space.

---

## 1. Lock Contention ("Queries Hanging")

```sql
SELECT a.pid,
       now() - a.query_start AS duration,
       a.wait_event_type,
       a.wait_event,
       pg_blocking_pids(a.pid) AS blocked_by,
       left(a.query, 70) AS query
FROM pg_stat_activity a
WHERE a.state <> 'idle'
ORDER BY duration DESC;
```

- Look for a long `idle in transaction` session holding a lock.
- Cancel gracefully first: `SELECT pg_cancel_backend(<pid>);`
- Terminate only if needed: `SELECT pg_terminate_backend(<pid>);`

---

## 2. CPU 100% ("Sudden Latency Spike")

```sql
-- Active queries running longer than 2 seconds
SELECT pid, now() - query_start AS elapsed, left(query, 70)
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '2 seconds'
ORDER BY elapsed DESC;
```

Check if a recent deploy dropped an index, caused stale statistics (fix with `ANALYZE <table>;`), or introduced an unindexed `JOIN`.

---

## 3. Disk Filling Up from WAL (`pg_wal/`)

A common silent killer is an **inactive replication slot** (from a dead replica or stopped Debezium/CDC connector) forcing PostgreSQL to retain every WAL segment indefinitely:

```sql
SELECT slot_name,
       active,
       pg_size_pretty(
         pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)
       ) AS retained_wal
FROM pg_replication_slots;
```

If an abandoned slot is `active = false` and retaining gigabytes of WAL, drop it (`SELECT pg_drop_replication_slot('<name>');`) and configure `max_slot_wal_keep_size` as a safety cap.
