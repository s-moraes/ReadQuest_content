## Q1
Which core architectural mechanism allows PostgreSQL to provide concurrent data access without reader queries blocking writer queries?

### Option A
Table-level read/write spinlocks

### Option B [CORRECT]
Multiversion Concurrency Control (MVCC)

### Option C
Global transaction undo segment logs

### Option D
Pessimistic row-level exclusive locks

### Explanation
PostgreSQL uses Multiversion Concurrency Control (MVCC), where updating or deleting a row writes a new tuple version with corresponding `xmin` and `xmax` transaction identifiers rather than blocking concurrent readers with read locks.

===

## Q2
What are the hidden system columns stored in every PostgreSQL table row to track tuple visibility?

### Option A
`row_id` and `tx_stamp`

### Option B
`version_id` and `commit_seq`

### Option C [CORRECT]
`xmin` and `xmax`

### Option D
`undo_lsn` and `redo_lsn`

### Explanation
`xmin` records the transaction ID of the inserting transaction, while `xmax` records the transaction ID of the updating or deleting transaction (or 0 if the tuple remains active).

===

## Q3
What is the primary role of Write-Ahead Logging (WAL) in PostgreSQL?

### Option A
To speed up sequential queries by keeping an uncompressed plain-text cache

### Option B [CORRECT]
To ensure durability and crash recovery by recording changes sequentially before modifying heap pages

### Option C
To automatically generate monthly table partitions based on creation timestamps

### Option D
To compile SQL queries into native machine assembly code

### Explanation
Write-Ahead Logging guarantees ACID Durability. Delta changes are written sequentially to WAL segments and flushed to disk before modified shared buffer pages are written to the database heap, enabling reliable crash recovery and point-in-time recovery (PITR).

===

## Q4
Why is the background Autovacuum daemon critical for healthy PostgreSQL operations?

### Option A
It re-encrypts stored passwords using stronger cryptographic algorithms

### Option B
It restarts the postmaster server when free memory drops below threshold

### Option C [CORRECT]
It reclaims dead tuple space, updates query optimizer statistics, and prevents transaction ID wraparound

### Option D
It synchronizes application code git commits with database schemas

### Explanation
Because updates and deletes produce dead tuple versions, `autovacuum` scans pages to mark dead space as reusable in the Free Space Map, updates cost-based optimizer table statistics (`ANALYZE`), and freezes old transaction IDs to prevent 32-bit transaction wraparound.

===

## Q5
In PostgreSQL's process architecture, how does the database handle incoming client connections?

### Option A
A single shared thread handles all concurrent network connections asynchronously

### Option B
Client queries are dispatched directly to disk controllers without central supervision

### Option C [CORRECT]
The Postmaster daemon forks a dedicated backend operating system process for each client connection

### Option D
Queries are stored in a distributed Redis queue before being polled by worker threads

### Explanation
PostgreSQL relies on a multi-process architecture: the Postmaster daemon listens for connection requests and forks a dedicated backend OS process for each client, allocating dedicated memory (`work_mem`) while accessing the shared buffer pool.
