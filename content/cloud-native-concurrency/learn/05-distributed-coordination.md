# Distributed Coordination & Consensus Primitives

In distributed systems, microservices cannot rely on a single shared CPU or centralized operating system kernel to maintain order. Critical operational tasks—such as **leader election**, **distributed locking**, and **cluster configuration synchronization**—require formal consensus protocols to guarantee data consistency across network partitions and hardware failures.

---

## 1. The Distributed Coordination Problem

When multiple instances of a microservice run concurrently across a cloud cluster, several fundamental coordination challenges emerge:

```text
+---------------------------------------------------------------+
|                    COORDINATION CHALLENGES                    |
|                                                               |
|  1. Leader Election:                                          |
|     Who executes the nightly billing batch job so it doesn't  |
|     run 5 times concurrently across all replicas?             |
|                                                               |
|  2. Distributed Locking:                                      |
|     Who gets exclusive write access to a shared resource      |
|     without colliding with other nodes?                       |
|                                                               |
|  3. Dynamic Configuration:                                    |
|     How do all worker pods update feature flags or circuit    |
|     breaker thresholds simultaneously without restarts?       |
+---------------------------------------------------------------+
```

### Theoretical Foundations of Distributed Consensus

Distributed consensus is mathematically governed by fundamental theorems:

#### 1. The FLP Impossibility Result (Fischer, Lynch, Paterson, 1985)
In an asynchronous network, **no deterministic consensus protocol can guarantee both safety (nothing bad happens) and liveness (something good eventually happens) if even a single node can experience an unannounced crash.**

To overcome FLP, practical consensus systems use partially synchronous models with timeouts and randomized elections.

#### 2. Quorums & The Split-Brain Catastrophe
When a network partition occurs, a cluster can split into isolated sub-clusters. If both partitions believe they are the authoritative cluster and elect their own leaders, **Split-Brain** occurs, leading to silent data corruption.

```text
[ Node 1 ] --- [ Node 2 ]  | NETWORK |  [ Node 3 ] --- [ Node 4 ] --- [ Node 5 ]
     Partition A (2 nodes) | SEVERED |            Partition B (3 nodes)
    (2 < Quorum -> FROZEN) |         |        (3 >= Quorum -> ACTIVE LEADER)
```

Consensus engines require a **Strict Majority Quorum ($Q$)**:

$$Q = \left\lfloor \frac{N}{2} \right\rfloor + 1$$

Where $N$ is the total cluster size. Because $Q$ requires a strict majority:
- A 3-node cluster requires $Q = 2$ (tolerates 1 node failure).
- A 5-node cluster requires $Q = 3$ (tolerates 2 node failures).
- Clusters must **always contain an odd number of nodes** (3, 5, or 7). An even number (e.g., 4 nodes) requires $Q = 3$ but still tolerates only 1 failure, adding cost and latency without increasing fault tolerance.

---

## 2. Consensus Algorithms Demystified: Raft vs. Zab

Production coordination systems rely on **State Machine Replication (SMR)**: all nodes execute an identical sequence of state-transition commands starting from the same initial state.

```text
[ Client Write ] ---> [ Leader Node ] 
                            |
                   Append to Local Log
                            |
           +----------------+----------------+
           | AppendEntries                   | AppendEntries
           v                                 v
   [ Follower Node 1 ]               [ Follower Node 2 ]
    (Write to Disk)                   (Write to Disk)
           \                                 /
            +----------------+--------------+
                             v
               Quorum Acknowledged (2 of 3)
                             v
               [ Leader Commits Entry ]
```

### 1. Raft Consensus (Used by etcd and Consul)
Raft decomposes consensus into three independent sub-problems:
- **Leader Election:** When a follower's randomized heartbeat timer expires (e.g., 150–300ms), it transitions to *Candidate*, increments the *Term*, and broadcasts `RequestVote` RPCs.
- **Log Replication:** The elected leader accepts client commands, appends them to its write-ahead log, and broadcasts `AppendEntries` RPCs to followers.
- **Safety Invariant:** A candidate can only be elected leader if its log is at least as up-to-date as any other node in the majority quorum (guaranteeing committed entries are never lost).

### 2. Zab Protocol (Used by Apache ZooKeeper)
ZooKeeper Atomic Broadcast (Zab) operates in two distinct phases:
- **Crash-Recovery Mode:** If the leader crashes, nodes engage in Fast Leader Election to select a leader with the highest `zxid` (64-bit ZooKeeper transaction ID: 32-bit epoch + 32-bit sequential counter).
- **Atomic Broadcast Mode:** Similar to a non-blocking two-phase commit. The leader proposes an update; once a quorum of followers acknowledges receipt, the leader broadcasts a commit message.

---

## 3. Apache ZooKeeper in Production

**Apache ZooKeeper** coordinates distributed processes using an in-memory, hierarchical tree namespace of data registers called **znodes** (modeled after a Unix filesystem).

```text
                     / (Root)
                    /        \
             /services      /locks
             /        \        |
      /service-1   /service-2  +--- /lock-0000000001 (Ephemeral Sequential)
      (Ephemeral)  (Ephemeral)+--- /lock-0000000002
                               +--- /lock-0000000003
```

### Znode Types
- **Persistent:** Remains stored on the cluster until explicitly deleted by a client.
- **Ephemeral:** Automatically deleted by ZooKeeper when the client session disconnects or the heartbeat lease expires.
- **Sequential:** Appends a monotonically increasing 10-digit zero-padded integer (`0000000001`) to the znode path upon creation.

### The "Thundering Herd" Problem & The Fair Lock Recipe
If 500 pods set a watch on a single lock znode (`/locks/global_lock`), releasing the lock fires 500 simultaneous push notifications. 500 pods wake up and attempt to acquire the lock at once, causing extreme CPU spikes and network saturation.

**The Solution (Curator Recipe):**
1. Each client creates an **Ephemeral Sequential** znode: `/locks/lock-000000000X`.
2. The client fetches all children of `/locks` and sorts them.
3. If the client's znode has the lowest sequence number, it holds the lock!
4. If not, the client sets a watch **only on the immediately preceding znode** ($i - 1$).
5. When znode $i - 1$ is deleted, only znode $i$ wakes up, eliminating herd stampedes completely.

```java
// Production Leader Election using Apache Curator in Java
public class ClusterCoordinator {

    private final CuratorFramework client;
    private final LeaderSelector leaderSelector;

    public ClusterCoordinator(String connectString) {
        this.client = CuratorFrameworkFactory.builder()
            .connectString(connectString)
            .sessionTimeoutMs(15000)
            .connectionTimeoutMs(5000)
            .retryPolicy(new ExponentialBackoffRetry(1000, 3))
            .build();
        this.client.start();

        this.leaderSelector = new LeaderSelector(client, "/readquest/leader",
            new LeaderSelectorListenerAdapter() {
                @Override
                public void takeLeadership(CuratorFramework client) throws Exception {
                    System.out.println("Node elected leader: Starting scheduled jobs...");
                    // This method must block while leadership is retained
                    while (!Thread.currentThread().isInterrupted()) {
                        executeClusterCronTask();
                        Thread.sleep(60000);
                    }
                }
            });

        // Automatically requeue for election if leadership is surrendered
        this.leaderSelector.autoRequeue();
        this.leaderSelector.start();
    }
}
```

---

## 4. etcd: The Cloud-Native Kubernetes Backbone

**etcd** is an open-source, strongly consistent distributed key-value store built in Go, designed specifically as the primary state store and source of truth for **Kubernetes**.

```text
[ Kubernetes API Server ] <--- gRPC / HTTP/2 ---> [ etcd Cluster (Raft) ]
  (Watches / Revisions)                             (Bbolt B+tree on SSD)
```

### Architectural Pillars of etcd

1. **MVCC & 64-Bit Global Revisions:** Every write operation (put or delete) increments a single cluster-wide 64-bit revision number. etcd retains historical revisions, allowing clients to query exact snapshots of state at past revisions.
2. **Streaming Watchers (gRPC):** Kubernetes controllers use long-lived HTTP/2 gRPC streaming watches starting from a specific revision (`watch(prefix="/registry/pods", start_revision=1042)`). If a controller disconnects, it resumes streaming without missing any events.
3. **Leases with Keep-Alive:** Keys are attached to time-bounded leases. If a microservice crashes and stops sending keep-alive heartbeats, etcd automatically deletes all keys tied to that lease.
4. **Compare-And-Swap (CAS) Transactions:** Atomic multi-key transactions:
   ```text
   Txn: If(Revision("keyA") == 40)
        Then(Put("keyA", "v2"), Put("keyB", "active"))
        Else(Abort)
   ```

> **Operational Warning:** etcd requires consistent $fdatasync$ disk latency under $10\text{ms}$. Running etcd on slow magnetic disks or throttled cloud volumes will trigger Raft leader election timeouts and destabilize the entire Kubernetes control plane.

---

## 5. HashiCorp Consul: Service Mesh & Hybrid Coordination

While ZooKeeper and etcd focus heavily on low-level CP storage, **HashiCorp Consul** provides an integrated coordination, service discovery, and service mesh platform.

```text
[ Datacenter 1 (AWS us-east) ]               [ Datacenter 2 (AWS eu-west) ]
  [ Server 1 ] [ Server 2 ]                    [ Server 1 ] [ Server 2 ]
       \           /                                \           /
       (Local Raft)                                 (Local Raft)
            \                                            /
             +--- WAN Gossip Pool (SWIM Protocol) ------+
```

### The Dual-Protocol Architecture
Consul uniquely pairs two protocols:
- **Raft (CP):** Powers the strongly consistent key-value store, catalog registrations, and session locks.
- **SWIM Gossip Protocol (AP):** Powers decentralized node discovery, health monitoring, and cross-datacenter WAN federation. Membership checks scale to thousands of nodes with $O(1)$ network overhead without burdening the central Raft consensus servers.

---

## 6. Distributed Coordination Engines Comparison

| Dimension | Apache ZooKeeper | etcd | HashiCorp Consul |
| :--- | :--- | :--- | :--- |
| **Consensus Protocol** | Zab (Atomic Broadcast) | Raft | Raft (State) + SWIM (Gossip) |
| **CAP Classification** | CP (Strict Consistency)| CP (Linearizable Reads)| CP (KV) / AP (Discovery) |
| **Data Hierarchy** | Filesystem Tree (Znodes)| Flat Key-Value with MVCC | Key-Value + Service Catalog |
| **Client Protocols** | Custom Binary (Jute TCP)| gRPC / HTTP/2 (Protobuf)| HTTP REST / gRPC / Native DNS|
| **Primary Ecosystem** | Hadoop, Kafka, Solr | Kubernetes, Cloud Native | Multi-Cloud, Service Meshes |
| **Hardware Demands** | JVM Memory & GC Tuning | Ultra-fast SSDs ($<10\text{ms}$)| Lightweight Go binary |
