# Relational vs NoSQL Storage

Data persistence forms the bedrock of system design. Selecting the wrong database model introduces schema rigidity, crippling query latency, or catastrophic data inconsistency. Systems choose between traditional **Relational (RDBMS)**, specialized **NoSQL**, and modern **NewSQL** engines based on access patterns and consistency requirements.

---

## 1. The Core Paradigm: ACID vs. BASE

```text
ACID (Relational / Traditional)
- Atomicity: All operations succeed or all rollback.
- Consistency: Invariants and constraints enforced.
- Isolation: Concurrent transactions do not interfere.
- Durability: Committed data survives hardware power loss.

BASE (NoSQL / Distributed)
- Basically Available: System guarantees availability under partitions.
- Soft State: Data may change over time without explicit input (replication).
- Eventual Consistency: Replicas eventually converge to the same value.
```

---

## 2. Relational Databases (RDBMS)

Relational databases organize data into rigid tabular rows and columns with enforced mathematical schemas:

```sql
-- Relational Schema with Foreign Key Constraint
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(id),
    total_amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Strengths of RDBMS
- **Complex Relational Joins:** Efficiently stitch normalized entities together (`JOIN orders o ON o.customer_id = c.id`).
- **Strict ACID Guarantees:** Ensures financial transactions and regulatory data never violate schema constraints or experience partial writes.
- **Mature Ecosystem:** Decades of query optimization, indexing trees (B-Trees), and standardized SQL.

### Scaling Bottlenecks
- **Write Scalability:** Scaling writes requires multi-master clustering or manual application-level sharding, which breaks foreign keys and cross-shard transactions.
- **Schema Rigidity:** Altering massive tables (`ALTER TABLE orders ADD COLUMN ...`) with billions of rows locks tables and requires complex zero-downtime migration patterns.

---

## 3. The Four NoSQL Families

NoSQL engines abandon rigid relational normalization in favor of horizontal elasticity and specialized data models:

```text
                  +--------------------------------+
                  |         NoSQL FAMILIES         |
                  +--------------------------------+
                   /         |           |        \
                  v          v           v         v
              Key-Value   Document  Wide-Column  Graph
```

### 1. Key-Value Stores (Redis, Amazon DynamoDB, Memcached)
- **Model:** Opaque blob associated with a unique string key.
- **Performance:** $O(1)$ sub-millisecond lookups directly from memory or indexed NVMe storage.
- **Best Used For:** Caching, session management, user carts, real-time counters.

### 2. Document Stores (MongoDB, Couchbase)
- **Model:** Hierarchical, semi-structured documents (JSON / BSON).
- **Advantage:** Eliminates object-relational impedance mismatch. Related data is embedded within a single document, eliminating expensive multi-table joins.
- **Best Used For:** E-commerce product catalogs, user profiles, content management systems (CMS).

### 3. Wide-Column Stores (Apache Cassandra, ScyllaDB)
- **Model:** Tables with dynamic rows indexed by a **Partition Key** (determines which cluster node stores the data) and a **Clustering Key** (determines sort order on disk).
- **Storage Engine:** Uses **LSM-Trees (Log-Structured Merge-Trees)** to deliver extreme, lock-free write throughput.
- **Best Used For:** IoT sensor time-series, messaging history, financial telemetry, audit logs.

### 4. Graph Databases (Neo4j, Amazon Neptune)
- **Model:** Nodes (entities), Edges (relationships), and Properties.
- **Advantage (Index-Free Adjacency):** Each node holds direct physical pointers to adjacent nodes. Traversing relationships requires $O(1)$ pointer dereferencing rather than expensive $O(N \log N)$ recursive SQL joins.
- **Best Used For:** Social connection graphs, fraud detection rings, recommendation engines.

---

## 4. NewSQL: Distributed ACID Databases

To eliminate the painful compromise between SQL ACID guarantees and NoSQL horizontal write scalability, **NewSQL** engines emerged (such as **Google Cloud Spanner**, **CockroachDB**, and **YugabyteDB**).

```text
[ Application ] ---> Standard PostgreSQL / SQL Dialect
                           |
                  Distributed Raft Consensus per Shard
                           |
            +--------------+--------------+
            v                             v
[ Node 1 (Raft Leader) ]      [ Node 2 (Raft Follower) ]
  ACID Distributed Write        Linearizable Consistency
```

- **Distributed Transactions:** Use consensus algorithms (Raft or Paxos) across distributed shards to guarantee serializable ACID transactions globally.
- **Clock Synchronization:** Google Cloud Spanner utilizes atomic clocks and GPS receivers (**TrueTime API**) to bound clock uncertainty and enforce globally ordered transactions without central coordinator locks.

---

## 5. Database Selection Decision Matrix

| Dimension | Relational (PostgreSQL) | Document (MongoDB) | Wide-Column (Cassandra) | Graph (Neo4j) | NewSQL (CockroachDB) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Data Structure** | Tables & Foreign Keys | Hierarchical JSON | Partitioned Rows / Columns| Nodes & Edges | Relational Tables |
| **Transactions** | Full ACID (Single DB)| Single-Document ACID| Eventual / Lightweight | Full ACID | Distributed ACID |
| **Write Scale** | Moderate (Vertical) | High (Sharded) | Extreme (Multi-Master) | Moderate | High (Horizontal) |
| **Query Style** | Declarative SQL | Rich JSON queries | CQL (Restricted queries)| Cypher / Gremlin | Standard SQL |
| **Best Used For** | Finance, ERP, Core CRUD| Catalogs, CMS, Profiles| Time-Series, IoT, Logs | Social, Fraud Detection| Global Multi-Region ACID |
