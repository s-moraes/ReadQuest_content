# Database Sharding & Partitioning

When a database's storage requirements exceed physical disk limits, or write transactions saturate the I/O capacity of a single primary instance, read replicas are no longer sufficient. Scaling writes horizontally requires **Sharding**—partitioning a monolithic dataset across multiple independent database servers.

---

## 1. Vertical vs. Horizontal Partitioning

```text
ORIGINAL TABLE: USERS (100 Million Rows, 20 Columns)

VERTICAL PARTITIONING (Column Splitting)
Database A: [ user_id | email | password_hash ] (Authentication Table)
Database B: [ user_id | bio | avatar_url | profile_json ] (Profile Table)
* Splits wide tables into distinct logical tables.

HORIZONTAL PARTITIONING / SHARDING (Row Splitting)
Shard 1: Users with ID 1 to 25,000,000       (Physical Database 1)
Shard 2: Users with ID 25,000,001 to 50,000,000 (Physical Database 2)
Shard 3: Users with ID 50,000,001 to 75,000,000 (Physical Database 3)
Shard 4: Users with ID 75,000,001 to 100,000,000 (Physical Database 4)
* Splits rows across separate physical database instances with identical schemas.
```

---

## 2. Core Sharding Strategies

The routing layer maps incoming queries to specific database shards using algorithmic or lookup strategies:

```text
                  +--------------------------------+
                  |      SHARDING STRATEGIES       |
                  +--------------------------------+
                   /         |           |        \
                  v          v           v         v
             Range-Based  Hash-Based  Consistent  Directory
```

### 1. Range-Based Sharding
Assigns contiguous ranges of keys to specific shards (e.g., users A–D on Shard 1, E–H on Shard 2, or transactions grouped by month).
- **Advantage:** Range queries are fast and localized (`SELECT * FROM orders WHERE created_at BETWEEN '2026-01-01' AND '2026-01-31'`).
- **Hazard (Severe Hotspots):** If data is partitioned by timestamp, **$100\%$ of all incoming writes hit the single current month's shard**, leaving older shards completely idle!

### 2. Hash-Based Sharding
Computes a cryptographic hash (MD5, MurmurHash3) of the Shard Key modulo the number of shards ($N$):

$$\text{Shard Index} = \text{hash}(\text{Shard Key}) \pmod N$$

- **Advantage:** Distributes records uniformly across all physical shards, eliminating hotspots.
- **Critical Flaw:** If the database expands from $N = 4$ to $N = 5$ shards, changing the modulus causes **almost all existing keys to map to different shards**, requiring a massive, downtime-inducing cluster migration!

### 3. Consistent Hashing (Production Standard)
Maps both database shards (with virtual replica nodes) and shard keys onto a virtual $360^\circ$ circular ring:

```text
                     [ Node 1 (0°) ]
                         /     \
    [ Key A (330°) ]    /       \    [ Node 2 (120°) ]
           |           |  RING   |        |
           v            \       /         v
    Maps to Node 1       \     /     [ Key B (90°) ]
                     [ Node 3 (240°) ] (Maps to Node 2)
```

When a new shard node is added to the cluster, **only $1/N$ of keys are migrated**, allowing dynamic scaling without global re-sharding.

### 4. Directory-Based (Lookup Table) Sharding
A centralized routing service or database maintains a static lookup map (`CustomerID "cust_88" -> Shard 3`).
- **Advantage:** Extremely flexible; allows migrating individual large customer accounts ("whales") to dedicated hardware shards without changing IDs.
- **Drawback:** The lookup directory becomes a Single Point of Failure (SPOF) and adds an extra network lookup hop to every query.

---

## 3. Selecting the Shard Key

The Shard Key is the single most important architectural decision in database design:

```text
GOOD SHARD KEY CRITERIA:
1. High Cardinality: Millions of unique values (e.g., user_id, order_uuid).
2. Uniform Distribution: Prevents single accounts from monopolizing space.
3. Query Alignment: Matches the primary WHERE clause of high-volume queries.
```

> **Anti-Pattern:** Sharding by `country_code`. If $80\%$ of your users live in the United States, Shard `US` will run out of disk and memory while Shard `IS` (Iceland) sits empty.

---

## 4. The Engineering Pains of Sharding

While sharding solves write scaling, it introduces massive operational and coding complexity:

### 1. Scatter-Gather Queries
If a query does not include the shard key (e.g., `SELECT * FROM users WHERE email = 'alice@example.com'` when the table is sharded by `user_id`), the application must send the query to **all $N$ shards in parallel** and merge the results:

```text
Client Query (No Shard Key) ---> [ Router ]
                                   |
         +-------------------------+-------------------------+
         v (Query Shard 1)         v (Query Shard 2)         v (Query Shard 3)
     [ Shard 1 ]               [ Shard 2 ]               [ Shard 3 ]
         \                         |                         /
          +------------------------+------------------------+
                                   v
             Router Merges Results -> Returns to Client
             (Query latency equals the SLOWEST shard!)
```

### 2. Cross-Shard Joins
Executing SQL joins across tables distributed on separate physical machines is computationally expensive and unsupported by relational engines natively. Applications must either denormalize related data into the same document or execute two separate queries and stitch data in memory.

### 3. Distributed Transactions (Two-Phase Commit)
Transferring funds from Account A (Shard 1) to Account B (Shard 2) requires coordinating a distributed transaction. Two-Phase Commit (2PC) locks records across shards, creating latency spikes and deadlock risks.
