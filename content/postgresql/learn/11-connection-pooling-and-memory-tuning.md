# Connection Pooling, `pg_stat_statements` & Memory Tuning

PostgreSQL uses a **process-per-connection** architecture. Spawning 1,000 idle backend processes consumes gigabytes of RAM and causes severe CPU context-switching overhead.

---

## Why `max_connections` = 1000 Hurts Performance

Each PostgreSQL backend process allocates its own memory and competes for internal lightweight locks (`LWLock`). Beyond roughly `2x–4x` CPU cores of *active* queries, throughput actually **drops**.

The solution is placing **PgBouncer** (or an app-side pool + proxy) in front of PostgreSQL:

```text
App Pods (500 connections) --> [ PgBouncer ] --> Postgres (40 backends)
```

### PgBouncer Pooling Modes

| Mode | Connection Assigned For | Supports Prepared Statements? | Supports `LISTEN/NOTIFY`? |
| :--- | :--- | :--- | :--- |
| **Session** | Entire client session | Yes | Yes |
| **Transaction** | Single `BEGIN ... COMMIT` | Requires PgBouncer `>= 1.21` config | No |
| **Statement** | Single SQL statement | No | No |

**Transaction pooling** gives the highest multiplexing ratio for microservices, while **Session pooling** is safest for legacy apps relying on session-level `SET` variables or advisory locks.

---

## Finding Bottlenecks with `pg_stat_statements`

`pg_stat_statements` tracks execution counts, total time, mean time, and buffer I/O for every normalized query across the cluster:

```sql
-- Top 5 queries by total cumulative database time
SELECT calls,
       round(total_exec_time::numeric, 1) AS total_ms,
       round(mean_exec_time::numeric, 2) AS mean_ms,
       rows,
       left(query, 70) AS sql
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 5;
```

Always optimize by **total cumulative time** (`calls * mean_exec_time`), not just the single slowest query—a 15 ms query called 50,000 times per minute dominates CPU.

---

## Core Memory Parameters

Three `postgresql.conf` settings govern 80% of memory tuning:

| Parameter | Recommended Starting Point | Purpose |
| :--- | :--- | :--- |
| `shared_buffers` | **25% of total RAM** | Postgres's own page cache (leaves room for OS page cache) |
| `effective_cache_size` | **50%–75% of total RAM** | Hint to the planner on total RAM available for caching (does not allocate RAM) |
| `work_mem` | **4 MB – 32 MB** (careful!) | Per-sort / per-hash-node memory—multiplied by concurrent active nodes |

> **Warning:** Setting `work_mem = 512MB` globally can trigger an Out-Of-Memory (OOM) kill if 20 concurrent queries each run 3 hash/sort nodes (`20 * 3 * 512MB = 30GB`). Keep global `work_mem` modest and raise it only per session for batch jobs.
