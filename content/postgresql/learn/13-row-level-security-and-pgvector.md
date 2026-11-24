# Multi-Tenant Row-Level Security & `pgvector` Hybrid Search

Modern SaaS and AI applications need **tenant isolation** and **semantic vector search** without introducing separate security proxies or standalone vector databases.

---

## Row-Level Security (RLS) for Multi-Tenancy

**Row-Level Security (RLS)** enforces tenant isolation inside the database engine itself—even if an application query forgets a `WHERE tenant_id = ...` clause.

```sql
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON invoices
  USING (tenant_id = current_setting('app.tenant_id')::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);
```

Your application sets the session/transaction context once per request:

```sql
SET LOCAL app.tenant_id = '7f9c2e10-...';
```

### Two Critical RLS Gotchas

1. **Table Owners & `BYPASSRLS`:** By default, the table owner and superusers bypass RLS! Always connect your app as a **non-owner, non-superuser role**, or run `ALTER TABLE ... FORCE ROW LEVEL SECURITY`.
2. **Index Performance:** Always index `tenant_id` (or put `tenant_id` first in composite indexes) so the RLS predicate uses an Index Scan instead of a Seq Scan.

---

## Hybrid Search with `pgvector` + Full-Text Search

With the **`pgvector`** extension, PostgreSQL stores embeddings (`VECTOR(1536)`) alongside relational columns and `tsvector` full-text search—giving you **transactional hybrid search** in one query.

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE docs (
  id        BIGSERIAL PRIMARY KEY,
  tenant_id UUID NOT NULL,
  body      TEXT NOT NULL,
  fts       TSVECTOR GENERATED ALWAYS AS
              (to_tsvector('english', body)) STORED,
  embedding VECTOR(1536) NOT NULL
);

CREATE INDEX idx_docs_fts ON docs USING GIN (fts);
CREATE INDEX idx_docs_vec ON docs
  USING hnsw (embedding vector_cosine_ops);
```

### `HNSW` vs. `IVFFlat` Indexes

| Index Type | Build Speed | Recall & Query Speed | Needs Training Data? |
| :--- | :--- | :--- | :--- |
| **`HNSW`** | Slower, higher RAM | Best recall & low latency | No (works on empty table) |
| **`IVFFlat`** | Fast, lower RAM | Good if tuned (`lists`) | Yes (build after data load) |

Combine `RLS` + `tsvector` + `embedding <=> $1` in one SQL query so vector results never leak across tenants and stay 100% consistent with relational deletes.
