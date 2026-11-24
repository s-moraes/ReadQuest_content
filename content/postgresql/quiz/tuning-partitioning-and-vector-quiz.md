## Q1
In `EXPLAIN (ANALYZE, BUFFERS)` output, what does `Sort Method: external merge Disk: 18432kB` indicate?

### Option A
The query used an `Index Only Scan` with zero heap fetches

### Option B [CORRECT]
The sort exceeded `work_mem` and spilled temporary files to disk

### Option C
The Visibility Map is 100% clean

### Option D
PgBouncer rejected the connection

### Explanation
When a `Sort` or `Hash` operation needs more memory than `work_mem`, PostgreSQL spills temporary data to disk (`external merge`), which severely degrades query latency.

===

## Q2
Why does setting `work_mem = 512MB` globally in `postgresql.conf` risk an Out-Of-Memory (OOM) crash under load?

### Option A
`work_mem` is allocated once per database, not per operation

### Option B [CORRECT]
Each concurrent query can allocate `work_mem` multiple times—once per sort or hash node

### Option C
`work_mem` disables `shared_buffers`

### Option D
`work_mem` is only used by `pg_dump`

### Explanation
`work_mem` is a per-operation limit, not a per-connection limit. A single complex query with 4 hash/sort nodes across 20 concurrent connections can allocate up to `80 * work_mem`.

===

## Q3
Why is `ALTER TABLE ... DETACH PARTITION ... CONCURRENTLY` followed by `DROP TABLE` far better than `DELETE FROM ... WHERE created_at < ...` for retiring old time-series data?

### Option A
`DELETE` cannot remove rows older than 30 days

### Option B
`DETACH PARTITION` automatically rewrites all remaining partitions with `VACUUM FULL`

### Option C [CORRECT]
It drops the old partition as a fast metadata/file removal with zero dead-tuple bloat or massive WAL generation

### Option D
`DROP TABLE` preserves all rows in `pg_stat_statements`

### Explanation
Mass `DELETE` statements generate huge WAL volume and millions of dead tuples that `VACUUM` must clean up later. Detaching and dropping a partition removes the entire child table cleanly with negligible bloat.

===

## Q4
What common mistake causes **Row-Level Security (RLS)** policies to be silently bypassed in production?

### Option A
Creating a B-tree index on `tenant_id`

### Option B [CORRECT]
Connecting the application as the table owner or a `SUPERUSER`/`BYPASSRLS` role without `FORCE ROW LEVEL SECURITY`

### Option C
Using `SET LOCAL app.tenant_id` inside a transaction

### Option D
Using `PgBouncer` in Session pooling mode

### Explanation
By default, table owners and superusers bypass RLS policies. Production apps should connect with a restricted non-owner role (or enable `FORCE ROW LEVEL SECURITY` on the table).

===

## Q5
When using `pgvector` on a table that starts empty and grows incrementally, which vector index type can be built immediately without needing training data first?

### Option A
`IVFFlat`

### Option B
`BRIN`

### Option C [CORRECT]
`HNSW`

### Option D
`Hash`

### Explanation
`IVFFlat` requires k-means clustering over existing vectors, so it should be created after loading data. `HNSW` builds a navigable graph incrementally and works cleanly even when created on an empty table.
