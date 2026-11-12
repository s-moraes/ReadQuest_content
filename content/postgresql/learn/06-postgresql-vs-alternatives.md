# PostgreSQL vs Alternatives: Choosing the Right Database

Selecting the foundational database for an enterprise software stack is one of the most impactful architectural decisions an engineering team makes. 

While PostgreSQL is often the default choice for modern greenfield applications, understanding how it compares against **MySQL**, **MongoDB**, and **MariaDB** is crucial for making informed trade-offs.

---

## PostgreSQL vs MySQL

Both PostgreSQL and MySQL are mature, battle-tested open-source relational database management systems, but they reflect fundamentally different engineering philosophies:

```text
+--------------------------------------------------------------------------+
|                  MySQL (InnoDB)                  PostgreSQL (ORDBMS)     |
|                                                                          |
| Concurrency:     Undo Logs + In-place updates    Tuple Versioning (MVCC) |
| Read/Write Bias: Optimized for simple reads      Optimized for writes &  |
|                                                  complex transactions    |
| Extensibility:   Fixed schema & storage engine   User-defined types,     |
|                                                  custom operators & CBO  |
| Compliance:      Pragmatic SQL dialect           Strict ANSI SQL:2023    |
+--------------------------------------------------------------------------+
```

### Concurrency Mechanics: Undo Logs vs MVCC Tuples
- **MySQL (InnoDB):** Performs row updates **in place**. To provide snapshot isolation for readers, InnoDB writes pre-image row states to an append-only **Undo Log**. When readers request an older view, MySQL re-applies undo logs backwards to reconstruct the requested state.
- **PostgreSQL:** Appends a new **tuple** on disk for every update, marking the old tuple's `xmax`. Readers scan tuples without reconstructing state from undo logs. However, old dead tuples must eventually be cleaned up by `autovacuum`.

### When to Choose Which?
- **Choose MySQL if:**
  - Your application is heavily read-dominant with straightforward single-table filters or simple primary key lookups.
  - Your operations team already maintains extensive tooling and expertise around MySQL replication topologies.
- **Choose PostgreSQL if:**
  - You require complex multi-table joins, window functions, recursive CTEs, and sophisticated analytical queries.
  - You require strict ACID guarantees with advanced isolation (like true Serializable Snapshot Isolation).
  - You want a hybrid database handling both relational tables and indexed JSON documents.

---

## PostgreSQL vs MongoDB

Comparing PostgreSQL with MongoDB contrasts an ACID-compliant object-relational system with a distributed document store:

| Dimension | MongoDB | PostgreSQL (with JSONB) |
| :--- | :--- | :--- |
| **Data Model** | JSON-like BSON documents | Relational tables + native binary `JSONB` |
| **Schema Governance** | Dynamic / Schema-free | Enforced relational schema or hybrid semi-structured |
| **Joins & Relations** | `$lookup` aggregation (slower) | Native, highly optimized relational `JOIN` algorithms |
| **Horizontal Scaling** | Native automatic sharding | Declarative partitioning, Citus extension |
| **Transaction Boundaries** | Document-level ACID (multi-doc ACID available) | Full ACID across entire relational schemas |

### The Hybrid Advantage
In early prototyping, teams often reach for MongoDB because schema-less collections allow rapid schema iteration. However, as applications mature, relations naturally emerge (e.g., users have orders, orders have payments). 

PostgreSQL enables teams to store unpredictable payload structures inside `JSONB` columns while keeping core identifiers, billing records, and audit entities anchored in strictly enforced relational schemas.

---

## PostgreSQL vs MariaDB

MariaDB was created as a community-driven fork of MySQL following Oracle's acquisition of Sun Microsystems:

- **MariaDB** introduces enhanced storage engines (Aria, ColumnStore for OLAP, Spider for sharding) and offers drop-in compatibility with MySQL clients.
- If your workload requires MySQL syntax and behavior but demands open-source governance and columnar analytical storage engines, MariaDB is an appealing choice.
- However, if the limiting factor is the absence of advanced SQL standards, PostGIS geospatial capabilities, or rich procedural languages, migrating to PostgreSQL is generally the superior path.

---

## Comprehensive Database Decision Matrix

| Capability | PostgreSQL | MySQL (InnoDB) | MongoDB | MariaDB |
| :--- | :--- | :--- | :--- | :--- |
| **License** | PostgreSQL (MIT/BSD-like) | GPLv2 / Commercial | SSPL (Non-OSI) | GPLv2 |
| **ACID Engine** | MVCC Tuple versions | Undo Logs + Redo Logs | WiredTiger Cache | Undo/Redo |
| **SQL Standards** | Exceptionally High | Moderate | MQL / Aggregations | Moderate |
| **Complex Joins** | Hash, Merge, Nested Loop | Nested Loop (Hash in 8.0) | `$lookup` only | Hash, Nested Loop |
| **Geospatial** | Industry-leading (PostGIS) | Basic spatial types | 2dsphere indexing | Basic spatial types |
| **JSON Indexing** | Inverted Index (GIN) | Multi-value indexes | Native BSON indexes | Virtual columns |
| **Community Lock-in** | Zero corporate lock-in | Owned by Oracle | Commercial vendor | MariaDB Foundation |

---

## The Default Choice Rule

In modern software engineering, the consensus architecture principle is:

> **Start with PostgreSQL by default.** Only migrate away or introduce a secondary database when an explicit technical constraint (such as single-digit microsecond caching requirements or petabyte-scale distributed document storage) genuinely demands a specialized engine.
