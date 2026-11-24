# Reading EXPLAIN (ANALYZE, BUFFERS) & Join Strategies

Guessing why a query is slow wastes hours. PostgreSQL's `EXPLAIN (ANALYZE, BUFFERS)` executes the query and reports the exact execution plan, row-estimate errors, and I/O buffer hits.

---

## Anatomy of `EXPLAIN (ANALYZE, BUFFERS)`

Always include `ANALYZE` (actual timings) and `BUFFERS` (memory vs. disk reads):

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.id, o.total_cents
FROM orders o
WHERE o.customer_id = 42 AND o.status = 'PAID';
```

```text
Index Scan using idx_orders_cust on orders o
  (cost=0.43..12.85 rows=3 width=12)
  (actual time=0.031..0.048 rows=4 loops=1)
  Index Cond: (customer_id = 42)
  Filter: (status = 'PAID')
  Rows Removed by Filter: 18
  Buffers: shared hit=7
Planning Time: 0.14 ms
Execution Time: 0.08 ms
```

### Four Signals to Check First

1. **`actual rows` vs. `estimated rows`:** If the planner estimated `rows=10` but actual was `rows=50000`, table statistics are stale—run `ANALYZE <table>`.
2. **`Rows Removed by Filter`:** High numbers mean the index matched too many rows and Postgres had to discard them after reading heap pages (consider a composite index `(customer_id, status)`).
3. **`Buffers: shared hit` vs `shared read`:** `hit` means found in `shared_buffers` RAM; `read` means fetched from OS cache or disk.
4. **`loops=N`:** Total time for a nested node is `actual time * loops`.

---

## Scan & Join Strategies Compared

### Scan Types

| Scan Type | When It Happens | Performance Profile |
| :--- | :--- | :--- |
| **Seq Scan** | No usable index, or >15% of table matches | Fast for small tables; bad for selective lookups |
| **Index Scan** | Selective lookup; fetches heap rows | Great for small result sets |
| **Index Only Scan** | All requested columns live in the index + VM clean | Fastest possible (zero heap fetches) |
| **Bitmap Heap Scan** | Medium selectivity; batches heap reads by page | Avoids random I/O on medium-sized ranges |

### Join Algorithms

- **Nested Loop:** Best when the outer side has **few rows** (1–100) and the inner side has an index.
- **Hash Join:** Builds an in-memory hash table of the smaller table. Fast for **large unsorted sets** when `work_mem` fits the hash table.
- **Merge Join:** Zips two **pre-sorted** inputs together (great when both sides already have matching B-tree indexes).

---

## Spotting `work_mem` Disk Spills

If a `Sort` or `Hash` node exceeds `work_mem`, PostgreSQL spills temporary files to disk—destroying latency:

```text
Sort  (actual time=412.1..489.3 rows=250000 loops=1)
  Sort Method: external merge  Disk: 18432kB
```

Seeing `external merge Disk:` or `Batches: 8` in a Hash Join is a direct signal to either add a supporting index (to eliminate the sort) or raise `work_mem` for that session (`SET LOCAL work_mem = '64MB'`).
