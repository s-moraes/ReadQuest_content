# Distributed Consensus & Eventual Consistency

In distributed systems, nodes cannot rely on a single central clock or shared physical memory to coordinate state transitions. Achieving agreement across independent computing entities subject to network partitions and hardware crashes is the domain of **Distributed Consensus** and **Eventual Consistency**.

---

## 1. The Fundamental Consensus Problem

Distributed consensus requires a group of nodes to agree on a single value or state sequence, satisfying three formal mathematical invariants:

1. **Agreement (Safety):** No two correct nodes decide on different values.
2. **Validity (Non-triviality):** If a value is decided, it must have been proposed by at least one participant node.
3. **Termination (Liveness):** All non-failing nodes eventually reach a final decision.

---

## 2. Classical Thought Experiments

Theoretical computer science illustrates the limits of consensus using two foundational problems:

```text
TWO GENERALS' PROBLEM (Unreliable Channel)
General 1 --- Messenger (May be captured!) ---> General 2
How do they agree on the exact time of attack?
* Result: Proved impossible to achieve 100% certainty over an unreliable link.

BYZANTINE GENERALS' PROBLEM (Traitorous Nodes)
General 1 --- Orders Attack ---> General 2
General 3 (TRAITOR) --- Orders Retreat ---> General 4
* Result: Requires at least 3m + 1 nodes to tolerate m malicious/traitorous nodes.
```

- **Crash-Fault-Tolerant (CFT):** Assumes nodes are honest: they either operate correctly or stop functioning (crash). Used in enterprise datacenters (etcd, Raft, Paxos).
- **Byzantine Fault-Tolerant (BFT):** Assumes malicious or compromised nodes may send conflicting or forged messages. Used in decentralized blockchains (Bitcoin, Proof of Stake).

---

## 3. Crash-Fault-Tolerant Consensus: Paxos & Raft

Production systems rely on **State Machine Replication (SMR)**: all replicas execute an identical sequence of deterministic commands from an ordered write-ahead log.

```text
[ Client Request ] ---> [ Raft Leader ]
                              |
                    1. Append to Local Log
                              |
             +----------------+----------------+
             | 2. AppendEntries RPC            | 2. AppendEntries RPC
             v                                 v
     [ Follower Node 1 ]               [ Follower Node 2 ]
      (Write to Disk)                   (Write to Disk)
             \                                 /
              +---------------+---------------+
                              v
                 3. Quorum Acknowledged (2 of 3)
                              v
                 [ Leader Commits Entry ]
                              v
                 [ Client Returns Success ]
```

### 1. Paxos (Leslie Lamport, 1989)
The foundational consensus algorithm. It operates in two phases:
- **Phase 1 (Prepare / Promise):** A proposer selects a proposal number $n$ and broadcasts `Prepare(n)`. If acceptors receive $n$ greater than any previous proposal, they promise not to accept proposals numbered $< n$.
- **Phase 2 (Accept / Accepted):** Once a majority promises, the proposer sends `Accept(n, value)`. Acceptors register the value if they haven't made a conflicting promise.

### 2. Raft (Diego Ongaro & John Ousterhout, 2014)
Designed to be significantly more understandable than Paxos, dividing consensus into explicit sub-problems:
- **Leader Election:** Heartbeats suppress elections. If followers miss a heartbeat, a randomized timer triggers a new election term.
- **Log Replication:** The leader enforces that followers match its exact log entries sequentially.
- **Strict Majority Quorum ($Q$):** Any decision requires $Q = \lfloor N/2 \rfloor + 1$ nodes. A 3-node cluster tolerates 1 node failure; a 5-node cluster tolerates 2 node failures.

---

## 4. Eventual Consistency & CRDTs

When applications cannot tolerate the latency or availability penalties of strict Raft consensus, they adopt **Eventual Consistency**: replicas accept writes locally and reconcile differences asynchronously.

```text
Node A (Offline): Accepts cart mutation -> Item A added
Node B (Offline): Accepts cart mutation -> Item B added
                  ... Network Reconnects ...
Merged State: Cart contains [Item A, Item B] (No Data Loss!)
```

### Conflict-Free Replicated Data Types (CRDTs)
CRDTs are mathematically provable data structures designed for distributed systems. Concurrent writes can execute without coordination, and replicas are guaranteed to converge to the identical state once all updates are exchanged.

```java
// Simplified State-based PN-Counter (Positive-Negative Counter)
public class PNCounter {
    private final Map<String, Integer> positiveP = new ConcurrentHashMap<>();
    private final Map<String, Integer> negativeN = new ConcurrentHashMap<>();

    public void increment(String nodeId) {
        positiveP.merge(nodeId, 1, Integer::sum);
    }

    public void decrement(String nodeId) {
        negativeN.merge(nodeId, 1, Integer::sum);
    }

    public int value() {
        int pSum = positiveP.values().stream().mapToInt(Integer::intValue).sum();
        int nSum = negativeN.values().stream().mapToInt(Integer::intValue).sum();
        return pSum - nSum;
    }

    // Mathematical Join-Semilattice: Idempotent, Commutative, Associative merge
    public void merge(PNCounter remote) {
        remote.positiveP.forEach((node, val) -> 
            positiveP.merge(node, val, Math::max));
        remote.negativeN.forEach((node, val) -> 
            negativeN.merge(node, val, Math::max));
    }
}
```

Because `merge()` calculates the `Math.max()` per node ID, the operation is:
- **Commutative:** $A \star B = B \star A$ (order of arrival does not matter).
- **Associative:** $(A \star B) \star C = A \star (B \star C)$ (batching doesn't matter).
- **Idempotent:** $A \star A = A$ (duplicate network deliveries cause zero harm).

---

## 5. Architectural Decision Matrix

| Dimension | Strong Consensus (Raft / Paxos) | Eventual Consistency (CRDTs / LWW) |
| :--- | :--- | :--- |
| **Consistency** | Strict Linearizability | Eventual Convergence |
| **Write Latency** | High (Requires quorum round-trips)| Sub-millisecond (Local node commit) |
| **Availability** | Froze under partition if $Q$ lost | Always available for local writes |
| **Complexity** | High consensus state machine | High domain data structure modeling |
| **Ecosystem** | etcd, ZooKeeper, Spanner, CockroachDB | Cassandra, Riak, DynamoDB, collaborative apps |
| **Best Used For** | Financial ledgers, cluster coordination | Collaborative docs, likes, shopping carts |
