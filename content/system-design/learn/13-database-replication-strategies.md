# Database Replication & Consistency

Replication means keeping synchronized copies of the same data across multiple physical machines connected by a network. It provides fault tolerance against hardware crashes, scales read throughput across replicas, and reduces geographic latency for global users.

---

## 1. Replication Topologies

Distributed databases employ three primary replication architectures, each presenting distinct trade-offs between write coordination, consistency, and conflict resolution:

```text
1. SINGLE-LEADER (Active-Passive)
[ Clients ] --- All Writes ---> [ Leader DB ] --- Async Stream ---> [ Follower 1 ]
            <-- Read Queries ---------------------------------------+ [ Follower 2 ]

2. MULTI-LEADER (Active-Active)
[ US Clients ] ---> [ Leader US ] <==== Cross-DC Sync ====> [ Leader EU ] <--- [ EU Clients ]
                    (Writes)                                (Writes)

3. LEADERLESS (Dynamo-Style)
[ Client ] --- Write to Quorum (W=2) ---> [ Node A ] [ Node B ] [ Node C ]
           <-- Read from Quorum (R=2) ---
```

---

## 2. Single-Leader Replication (Master-Follower)

The most widely adopted topology in relational databases (PostgreSQL, MySQL):
- **Write Path:** All mutating operations (`INSERT`, `UPDATE`, `DELETE`) are directed exclusively to the single designated **Leader**.
- **Replication Log:** The leader writes state changes to a durable write-ahead log (WAL / binlog) and streams it across the network to **Followers**.
- **Read Path:** Clients can read from either the leader or any read replica.

### Synchronous vs. Asynchronous Replication

```text
SYNCHRONOUS REPLICATION
Client Write ---> [ Leader ] --- Sync Send ---> [ Follower 1 ] (Waits for ACK!)
                  [ Leader ] <--- ACK --------- [ Follower 1 ]
Client Success <--+
* Invariant: Follower is guaranteed 100% up to date.
* Hazard: If Follower 1 is slow or down, WRITES FREEZE!

ASYNCHRONOUS REPLICATION
Client Write ---> [ Leader ] (Commits & returns Success immediately!)
                  [ Leader ] ... Streams log in background ... ---> [ Follower 1 ]
* Invariant: Leader returns instantly; high write throughput.
* Hazard: If Leader crashes before log reaches Follower, COMMITTED WRITES ARE LOST!
```

**Semi-Synchronous Replication (Best Practice):** Configures one follower to replicate synchronously (guaranteeing at least one node has the latest data for zero data loss), while remaining replicas replicate asynchronously.

---

## 3. Multi-Leader Replication (Active-Active)

In multi-region setups (e.g., AWS US-East and AWS EU-West), routing writes across the Atlantic introduces high latency ($80\text{ms+}$). Multi-leader architectures place an active write leader in each geographic region.

### The Conflict Resolution Nightmare
If two users modify the exact same database record concurrently in different regions, their writes conflict when synchronized:

```text
US Region: User changes Title to "Red" (Timestamp: 12:00:01.100)
EU Region: User changes Title to "Blue" (Timestamp: 12:00:01.105)
```

1. **Last-Write-Wins (LWW):** Resolves conflicts by discarding the write with the older timestamp. Highly vulnerable to clock drift (NTP skew can cause valid writes to be silently deleted).
2. **Conflict-Free Replicated Data Types (CRDTs):** Mathematical data structures (such as PN-Counters or Observed-Remove Sets) that can be merged concurrently across nodes without coordination.
3. **Custom Application Conflict Handlers:** Queuing conflicting rows into an exceptions table for manual user or business logic resolution.

---

## 4. Leaderless Replication & Quorums (Dynamo-Style)

Pioneered by Amazon Dynamo and utilized by Apache Cassandra, leaderless architectures abandon the concept of a master node entirely: clients write directly to multiple replica nodes in parallel.

### The Quorum Condition Formula

To guarantee that read operations always observe the latest committed write, the number of replicas written to ($W$) and read from ($R$) must satisfy the **Strict Quorum Condition**:

$$W + R > N$$

Where $N$ is the total replication factor (typically $N = 3$ or $N = 5$).

```text
Cluster Replicas (N = 3): [ Node 1 ]  [ Node 2 ]  [ Node 3 ]
Write Quorum (W = 2):     [ WRITE  ]  [ WRITE  ]  [        ]
Read Quorum (R = 2):      [        ]  [ READ   ]  [ READ   ]
                                            ^
                         Overlap guarantees Node 2 returns the newest write!
```

Because the write set and read set overlap by at least one node, the client is mathematically guaranteed to read the latest version tag.

### Quorum Self-Healing Mechanisms
- **Read Repair:** When a client reads from a quorum and discovers that Node 3 holds a stale version, the client asynchronously writes the fresh value back to Node 3.
- **Anti-Entropy with Merkle Trees:** Background maintenance processes compare cryptographic hash trees (Merkle Trees) of partition ranges across nodes to sync missing data ranges without transferring entire datasets.

---

## 5. Replication Lag Anomalies

In asynchronous leader-follower replication, followers lag behind the leader by milliseconds to seconds:

```text
1. User submits profile update: Name = "Alice" -> Committed to Leader
2. User immediately refreshes browser
3. Load Balancer routes read to Follower 2 (Replication Lag: 800ms)
4. Follower 2 returns OLD profile: Name = "Bob"!
```

### Critical Consistency Guarantees
- **Read-Your-Own-Writes (Monotonic Writes):** Guarantees a user always observes updates they submitted themselves. Achieved by routing reads for a user's recently updated profile to the Leader for 60 seconds after a write.
- **Monotonic Reads:** Prevents users from "moving backward in time" (e.g., repeatedly refreshing and seeing new data, then old data, then new data). Enforced by pinning a user's reads to the same replica via consistent hash.
- **Consistent Prefix Reads:** Guarantees causal sequences are preserved (e.g., answers are never displayed before the questions that prompted them).
