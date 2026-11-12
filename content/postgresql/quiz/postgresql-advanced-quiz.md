## Q1
Which index type is specifically designed for indexing composite elements like JSONB documents, arrays, and full-text search vectors?

### Option A
B-Tree

### Option B [CORRECT]
GIN (Generalized Inverted Index)

### Option C
Hash Index

### Option D
BRIN (Block Range Index)

### Explanation
GIN (Generalized Inverted Index) decomposes composite elements into individual components and creates inverted index entries, making it ideal for JSONB containment queries (`@>`), array searches, and full-text search lexemes.

===

## Q2
When querying append-only tables containing hundreds of millions of naturally ordered time-series rows, which index type provides range filtering with minimal memory and disk overhead?

### Option A
Hash Index

### Option B
Partial Index

### Option C [CORRECT]
BRIN (Block Range Index)

### Option D
Covering B-Tree Index

### Explanation
BRIN (Block Range Index) stores only the minimum and maximum values for physical ranges of disk pages (such as every 128 pages). For tables naturally ordered on disk by timestamp or sequence, BRIN provides fast range filtering using orders of magnitude less disk and RAM than a standard B-Tree.

===

## Q3
Why is a connection pooler like PgBouncer or pgcat strongly recommended in front of a high-concurrency PostgreSQL database?

### Option A
PostgreSQL lacks support for standard TCP/IP networking

### Option B
It converts SQL syntax into MongoDB BSON queries

### Option C [CORRECT]
PostgreSQL uses a process-per-connection model where thousands of idle connections consume excessive memory and CPU context-switching

### Option D
It bypasses Write-Ahead Logging to speed up write operations

### Explanation
Because PostgreSQL allocates a distinct operating system process (consuming 2–10MB of RAM each) per connection, thousands of client connections lead to severe memory exhaustion and CPU context-switching contention. Connection poolers maintain a small pool of database connections and multiplex thousands of client transactions over them.

===

## Q4
Which SQL clause allows concurrent background workers to atomically claim pending jobs from a queue table without blocking or deadlocking each other?

### Option A
`FOR SHARE`

### Option B
`LOCK TABLE IN EXCLUSIVE MODE`

### Option C [CORRECT]
`FOR UPDATE SKIP LOCKED`

### Option D
`WHERE status IS PENDING REPEATABLE`

### Explanation
`SELECT ... FOR UPDATE SKIP LOCKED` instructs PostgreSQL to lock eligible rows for the current transaction and silently skip any rows that are already locked by other concurrent transactions, enabling lock-free, concurrent worker queues.

===

## Q5
In PostGIS, which operator performs high-speed K-Nearest Neighbor (KNN) spatial searches directly utilizing the GiST spatial index tree?

### Option A
`ST_Intersects`

### Option B [CORRECT]
`<->`

### Option C
`@>`

### Option D
`ST_Within`

### Explanation
The `<->` distance operator computes bounding-box distance directly inside the GiST R-Tree index, enabling lightning-fast top-$K$ nearest neighbor searches without performing full table scans.
