# Indexing Strategies & Query Planner Internals

A database system is only as fast as its query planner and indexing strategies. PostgreSQL features a sophisticated **Cost-Based Optimizer (CBO)** that estimates the computational cost (CPU and I/O disk pages) of multiple candidate execution plans before choosing the fastest path.

---

## Query Lifecycle & The Cost-Based Optimizer

When a client sends an SQL query, it passes through four distinct phases:

```text
SQL String ---> [ Parser ] ---> Query Tree
                      |
                      v
               [ Rewriter ] ---> Rewritten Tree (Views & Rules applied)
                      |
                      v
               [ Optimizer / Planner ] ---> Physical Execution Plan
                      |
                      v
               [ Executor ] ---> Result Rows to Client
```

```mermaid
flowchart LR
    A["SQL Query"] --> B["Parser"]
    B --> C["Rewriter"]
    C --> D["Optimizer / Planner"]
    D --> E["Executor"]
    E --> F["Result Set"]
```

The optimizer calculates cost based on configurable cost units:
- `seq_page_cost` (Default: 1.0): Cost of sequentially fetching an 8KB page from disk.
- `random_page_cost` (Default: 4.0): Cost of a random non-sequential disk page read (often set to 1.1–1.5 on fast NVMe SSDs).
- `cpu_tuple_cost` (Default: 0.01): CPU cost to process a single row.

---

## Mastering `EXPLAIN` and `EXPLAIN ANALYZE`

To inspect the execution plan selected by the planner, prepend `EXPLAIN` to any SQL statement. To actually run the query and measure real wall-clock execution times and buffer hits, use `EXPLAIN (ANALYZE, BUFFERS)`:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, SUM(total_amount)
FROM orders
WHERE order_date >= '2025-01-01'
GROUP BY customer_id;
```

### Key Execution Node Types to Recognize:
- **Seq Scan (Sequential Scan):** Scans all table pages sequentially. Fast for small tables; disastrous for multi-million row tables with selective filters.
- **Index Scan:** Traverses the index tree to locate matching tuple pointers (`ctid`), then fetches the actual data page from the heap.
- **Index-Only Scan:** Answers the entire query directly from the index tree without fetching heap pages, provided the table's **Visibility Map** confirms no concurrent unvacuumed modifications.
- **Bitmap Index Scan:** When multiple rows match, creates an in-memory bitmap of target page IDs, sorts them sequentially to optimize disk I/O, and accesses heap pages in order.

---

## Diverse Index Types for Diverse Workloads

PostgreSQL provides five specialized index types:

| Index Type | Internal Structure | Best Use Case | Query Operators |
| :--- | :--- | :--- | :--- |
| **B-Tree** | Balanced Tree | General-purpose scalar data, equality, and range queries | `<`, `<=`, `=`, `>=`, `BETWEEN` |
| **GIN** | Generalized Inverted Index | Composite elements: Arrays, JSONB documents, Full-Text | `@>`, `?`, `&&`, `@@` |
| **GiST** | Generalized Search Tree | Geometric points, shapes, network ranges, full-text | `&&`, `&<`, `<->`, `ST_DWithin` |
| **BRIN** | Block Range Index | Massive time-series or append-only tables sorted on disk | `<`, `<=`, `=`, `>=`, `BETWEEN` |
| **Hash** | Bucket Hash Table | High-concurrency exact equality checks | `=` |

### The Power of BRIN (Block Range Index)
For append-only tables containing hundreds of millions of timestamped rows (e.g., IoT telemetry or financial tick logs), a B-Tree index might require 20 GB of RAM. 

A **BRIN index** records only the minimum and maximum value for each block of disk pages (e.g., every 128 pages). It uses only tens of kilobytes of memory, providing fast range filtering with virtually zero storage overhead:

```sql
CREATE INDEX idx_telemetry_timestamp_brin 
ON sensor_telemetry USING BRIN (recorded_at);
```

---

## Advanced Indexing Techniques

### 1. Partial Indexes
Indexes only a subset of rows meeting a specific condition. This dramatically cuts index storage and keeps write operations fast:

```sql
-- Index ONLY unresolved open support tickets (ignoring 99% of closed rows)
CREATE INDEX idx_open_tickets 
ON support_tickets (priority, created_at) 
WHERE status != 'CLOSED';
```

### 2. Expression (Functional) Indexes
Indexes the computed output of an expression or function rather than the raw column:

```sql
-- Speed up case-insensitive user lookups
CREATE INDEX idx_users_lower_email 
ON users (LOWER(email));

-- The query planner automatically uses this index when the same expression is queried:
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';
```

### 3. Covering Indexes (`INCLUDE`)
Adds non-key payload columns to the leaf pages of a B-Tree index to enable **Index-Only Scans** without adding them to the search tree:

```sql
CREATE INDEX idx_orders_customer_covering 
ON orders (customer_id) INCLUDE (order_date, total_amount);
```
