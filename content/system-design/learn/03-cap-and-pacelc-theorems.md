# CAP & PACELC Theorems

Designing distributed data architectures requires navigating fundamental physical trade-offs between consistency, availability, latency, and fault tolerance. The **CAP Theorem** and its modern extension, the **PACELC Theorem**, provide the formal mathematical boundaries for what distributed systems can and cannot achieve.

---

## 1. Eric Brewer's CAP Theorem

Introduced by Eric Brewer in 2000 and mathematically proved by Seth Gilbert and Nancy Lynch in 2002, the CAP theorem establishes that any distributed data store can simultaneously provide at most two of the following three guarantees:

```text
                      [ CAP THEOREM ]
                             /\
                            /  \
                           /    \
            [ Consistency ]------[ Availability ]
                          \      /
                           \    /
                     [ Partition Tolerance ]
```

### Definitions Under the Gilbert & Lynch Proof

#### 1. Consistency (Linearizability / Atomic Consistency)
Every read operation receives the most recent write or an error. All nodes in the cluster agree on the exact same value at the exact same logical instant.

#### 2. Availability
Every non-failing node must return a non-error response for every request it receives. The response does not guarantee returning the absolute latest write, but the node cannot crash, block indefinitely, or reject requests with errors.

#### 3. Partition Tolerance
The system continues to operate despite an arbitrary number of dropped, delayed, or duplicated messages between nodes over the network.

---

## 2. The Great CAP Misconception: "Pick 2 of 3"

A pervasive myth in software engineering states that developers can freely pick any two letters from $\{C, A, P\}$, implying that a system can choose **CA (Consistency + Availability)**.

> **In a distributed system, you cannot choose CA.**

```text
[ Node A (Datacenter East) ]  | NETWORK PARTITION |  [ Node B (Datacenter West) ]
Write Balance = $50           |  (FIBER SEVERED)  |  Read Balance = ???
```

Network partitions are not an architectural preference; they are an unyielding physical reality of operating computers across physical cables, switches, and regions. When a network partition inevitably strikes, the system has exactly two mutually exclusive choices:

```text
WHEN A PARTITION OCCURS (P):
- OPTION CP: Cancel or reject operations on Node B until partition heals
             ===> Preserves CONSISTENCY, sacrifices AVAILABILITY.
- OPTION AP: Allow Node B to accept local reads/writes independently
             ===> Preserves AVAILABILITY, sacrifices CONSISTENCY (data diverges!).
```

---

## 3. The PACELC Theorem (Daniel Abadi, 2012)

While CAP is foundational, it suffers from a major practical limitation: **it only describes system behavior during an active network partition.**

In high-reliability enterprise datacenters, network partitions are rare edge cases (occurring less than $0.1\%$ of the time). How does a system behave during the $99.9\%$ of normal operating time?

Daniel Abadi formulated the **PACELC Theorem**:

$$\text{If } \mathbf{P} \text{ (Partition): } [\mathbf{A} \text{ vs } \mathbf{C}] \quad \mathbf{E} \text{ (Else): } [\mathbf{L} \text{ vs } \mathbf{C}]$$

```text
                                [ PACELC ]
                                    |
            +-----------------------+-----------------------+
            |                                               |
     IS THERE A PARTITION? (P)                      NORMAL STATE (E)
     Trade Availability vs Consistency              Trade Latency vs Consistency
       /                     \                        /                 \
     (A)                     (C)                    (L)                 (C)
  Keep Serving           Block until            Return fast         Wait for quorum
  Stale Data            Quorum Heals            (Stale reads)      sync (Higher RTT)
```

During normal operations ($\mathbf{E}$), maintaining strong Consistency ($\mathbf{C}$) requires waiting for cross-node replication and consensus acknowledgments before acknowledging a write, directly increasing system Latency ($\mathbf{L}$). If an application demands ultra-low latency, it must relax consistency.

---

## 4. Classifying Real-World Distributed Databases

Using PACELC, distributed data stores are classified into distinct architectural quadrants:

| System | PACELC Type | Partition Behavior (P/A or P/C) | Normal Behavior (E/L or E/C) |
| :--- | :--- | :--- | :--- |
| **Apache Cassandra** | **PA / EL** | Remains available; accepts local writes | Returns immediately from local node; resolves conflicts via hinted handoff |
| **Amazon DynamoDB** | **PA / EL** | Highly available across partitions | Tunable: defaults to eventual consistency for lowest latency |
| **Google Cloud Spanner**| **PC / EC** | Aborts writes if majority quorum lost | Uses TrueTime atomic clocks to deliver linearizable writes globally |
| **Apache ZooKeeper / etcd**| **PC / EC**| Freezes writes if majority lost | Guarantees strict linearizability on every state change |
| **MongoDB** | **PC / EC** (tunable)| Enforces single-primary write locks | Tunable: supports secondary reads (`readPreference=nearest`) to shift to **EL** |

---

## 5. The Consistency Spectrum

Consistency in distributed systems is not a binary choice between "ACID" and "Inconsistent". It exists along a nuanced continuum:

```text
[ Strict Linearizability ] ---> [ Causal Consistency ] ---> [ Read-Your-Own-Writes ] ---> [ Eventual Consistency ]
<-- Strongest / Highest Latency                                                      Weakest / Lowest Latency -->
```

1. **Linearizability (Strong Consistency):** A global real-time clock ordering. Once a write completes, every subsequent read anywhere in the cluster must observe that write or a later one.
2. **Sequential Consistency:** All operations appear to execute in some sequential order that is consistent with the order seen by each individual node, though not necessarily tied to physical real-time.
3. **Causal Consistency:** Operations that are causally related must be seen by every node in the same order. Concurrent operations with no causal link may be observed in different orders.
4. **Read-Your-Own-Writes (Monotonic Reads):** A user who updates a profile or writes a comment is guaranteed to see their own update immediately upon refreshing, even if other users experience a brief replication delay.
5. **Eventual Consistency:** If no new updates are made, all replicas will eventually converge to identical values. Guarantees zero order or timing invariants during convergence.

---

## 6. Architectural Decision Summary

| Business Requirement | Recommended Strategy | Paradigm |
| :--- | :--- | :--- |
| **Financial Ledger / Double-Entry Bookkeeping** | CP / EC | Strict Linearizability (Spanner, PostgreSQL with Raft) |
| **Social Media Feed / Likes & Views Counter** | AP / EL | Eventual Consistency (Cassandra, DynamoDB) |
| **Shopping Cart / User Session Store** | AP / EL | Read-Your-Own-Writes (Redis Cluster, DynamoDB) |
| **Distributed Lock Manager / Cluster Leader** | CP / EC | Strict Quorum Consensus (etcd, ZooKeeper) |
