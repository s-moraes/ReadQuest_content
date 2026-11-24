## Q1
Which two conditions must be met for PostgreSQL to perform a **HOT (Heap-Only Tuple)** update?

### Option A
The table must be partitioned and have `work_mem` set to 512MB

### Option B [CORRECT]
No indexed columns are modified and there is enough free space on the same heap page for the new tuple

### Option C
The transaction runs under `SERIALIZABLE` isolation with `VACUUM FULL`

### Option D
All indexes on the table are `GIN` indexes

### Explanation
HOT updates avoid updating every index on a table when no indexed columns change and the new tuple fits on the same heap page (which you can encourage with `fillfactor < 100`).

===

## Q2
What catastrophic event does PostgreSQL's anti-wraparound `AUTOVACUUM` prevent by freezing old tuples?

### Option A
`pg_hba.conf` syntax corruption

### Option B [CORRECT]
32-bit Transaction ID (`XID`) wraparound, which would make old rows appear to belong to the future

### Option C
B-tree index page splits during `SELECT`

### Option D
PgBouncer running out of transaction slots

### Explanation
PostgreSQL's `XID` is a 32-bit circular counter. Freezing old tuples prevents XID wraparound, where committed rows older than ~2 billion transactions could suddenly become invisible.

===

## Q3
Why can running `ALTER TABLE orders ADD COLUMN ...` without `lock_timeout` cause an immediate application outage, even if the `ALTER` itself is fast?

### Option A
`ALTER TABLE` deletes all rows in `orders` before adding the column

### Option B
`ALTER TABLE` forces a full cluster restart

### Option C [CORRECT]
If it waits behind a long-running `SELECT` for an `AccessExclusiveLock`, all subsequent `SELECT` and `INSERT` queries queue behind it

### Option D
It disables `AUTOVACUUM` on the entire database permanently

### Explanation
`ALTER TABLE` requires `AccessExclusiveLock`, which conflicts with every lock mode including `AccessShareLock` (`SELECT`). Waiting behind one slow query causes all new reads and writes to pile up behind the `ALTER TABLE` in the lock queue.

===

## Q4
How can you add a `CHECK` constraint to a 500-million-row table in PostgreSQL without blocking concurrent reads and writes?

### Option A
Run `VACUUM FULL` right before `ALTER TABLE ... ADD CONSTRAINT`

### Option B [CORRECT]
Add the constraint with `NOT VALID` first, then run `ALTER TABLE ... VALIDATE CONSTRAINT`

### Option C
Disable MVCC during the migration window

### Option D
Run `CREATE INDEX` without `CONCURRENTLY`

### Explanation
`ADD CONSTRAINT ... NOT VALID` takes only a brief metadata lock and skips scanning existing rows. Running `VALIDATE CONSTRAINT` afterward uses `ShareUpdateExclusiveLock`, which allows concurrent `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.

===

## Q5
Which `VACUUM` option reclaims OS disk space back to the filesystem while blocking all reads and writes on the table?

### Option A
`VACUUM ANALYZE`

### Option B
`AUTOVACUUM`

### Option C [CORRECT]
`VACUUM FULL`

### Option D
`CREATE INDEX CONCURRENTLY`

### Explanation
Regular `VACUUM` marks dead space as reusable internally without shrinking the OS file. `VACUUM FULL` rewrites the entire table to shrink the file on disk, but acquires `AccessExclusiveLock` and blocks all queries while running.
