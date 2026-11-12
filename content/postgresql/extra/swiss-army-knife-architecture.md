# The Swiss Army Knife Architecture: Postgres as Redis, Mongo, and Queue

Early-stage startups and engineering teams frequently fall into the **distributed systems trap**: deploying a dedicated database for every technical requirement.

A typical premature stack often looks like this:
- **PostgreSQL** for relational user data
- **MongoDB** for flexible JSON documents
- **Redis** for session caching and rate limiting
- **RabbitMQ** or **Kafka** for background worker queues
- **Elasticsearch** for search and auto-complete

Maintaining five distinct distributed clusters introduces immense operational complexity, five backup strategies, distributed transaction failures, and thousands of dollars in cloud infrastructure overhead.

---

## How to Consolidate on PostgreSQL

PostgreSQL can replace all five tools during early-to-mid stages of product evolution with zero distributed synchronization issues:

```text
+--------------------------------------------------------------------------+
|                         Unified PostgreSQL Instance                      |
|                                                                          |
|  [Relational Core]   --> User accounts, invoices, billing tables         |
|  [Document Store]    --> JSONB columns with GIN indexes (replaces Mongo) |
|  [Fast Key-Value]    --> UNLOGGED tables with Hash index (replaces Redis)|
|  [Job Queue]         --> FOR UPDATE SKIP LOCKED (replaces SQS/RabbitMQ)  |
|  [Search Engine]     --> tsvector + GIN index (replaces Elasticsearch)   |
|  [Pub / Sub]         --> LISTEN / NOTIFY (replaces Redis PubSub)         |
+--------------------------------------------------------------------------+
```

---

## 1. Replacing a Background Job Queue (`SKIP LOCKED`)

One of the historical pitfalls of implementing a job queue in a relational database was lock contention: multiple worker threads would block each other while querying for the next available pending job.

PostgreSQL solved this with `SELECT ... FOR UPDATE SKIP LOCKED`:

```sql
CREATE TABLE background_jobs (
    job_id       BIGSERIAL PRIMARY KEY,
    queue_name   TEXT NOT NULL,
    payload      JSONB NOT NULL,
    status       TEXT NOT NULL DEFAULT 'QUEUED',
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    attempts     INT NOT NULL DEFAULT 0
);

-- Worker query: atomically lock and claim the next available job
-- without blocking other concurrent workers!
WITH next_job AS (
    SELECT job_id
    FROM background_jobs
    WHERE status = 'QUEUED' AND scheduled_at <= now()
    ORDER BY job_id
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
UPDATE background_jobs
SET status = 'PROCESSING', attempts = attempts + 1
WHERE job_id = (SELECT job_id FROM next_job)
RETURNING job_id, payload;
```

This guarantees that 50 concurrent worker processes will each grab a distinct job with zero lock contention or deadlocks.

---

## 2. Replacing Redis Caching with `UNLOGGED` Tables

When caching transient sessions or ephemeral tokens where losing data upon a rare server crash is acceptable, writing to the Write-Ahead Log (WAL) adds unnecessary disk I/O overhead.

PostgreSQL supports `UNLOGGED` tables:

```sql
CREATE UNLOGGED TABLE ephemeral_cache (
    cache_key   TEXT PRIMARY KEY,
    cache_val   JSONB NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL
);

-- Queries to an unlogged table bypass WAL generation completely,
-- delivering write throughput nearly comparable to in-memory caches.
```

---

## 3. Real-Time Push with `LISTEN` and `NOTIFY`

Need to alert workers or connected WebSocket servers when a record changes? Rather than setting up a Redis Pub/Sub cluster, use PostgreSQL's native asynchronous signaling:

```sql
-- Inside a trigger or stored procedure:
PERFORM pg_notify('new_orders_channel', json_build_object('order_id', NEW.id)::text);

-- In your Node.js / Go / Python backend worker:
LISTEN new_orders_channel;
```

---

## When SHOULD You Break Out of Postgres?

Consolidating on PostgreSQL is wise until you reach clear scaling boundaries:
1. **Cache Latencies:** You require sub-millisecond $P_{99}$ response times that only in-memory stores like Redis or Dragonfly can satisfy.
2. **Heavy Distributed Ingestion:** You ingest 100,000+ telemetry events per second that require distributed log architectures like Apache Kafka or ClickHouse.
3. **Fuzzy Linguistic Search at Scale:** You need complex BM25 scoring, fuzzy term highlighting, and synonym dictionaries across tens of millions of documents that justify Elasticsearch or Meilisearch.
