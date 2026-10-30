# Distributed Systems Overview

A distributed system is a collection of autonomous computing entities (nodes) that communicate over a network and coordinate actions by passing messages, presenting themselves to end users as a unified, coherent system.

---

## 1. The Anatomy of a Distributed System

In a single-machine paradigm, execution is bound to a shared physical motherboard: threads share the same random-access memory (RAM), synchronize via CPU bus locks, and experience synchronized hardware clock ticks.

```text
+-------------------------------------------------------------+
|                     SINGLE MACHINE NODE                     |
|  [ Thread A ] <--- Nanosecond In-Memory Memory Bus ---> [ Thread B ]  |
|  Shared RAM, Single Kernel, Coordinated Hardware Clock      |
+-------------------------------------------------------------+
                              vs
+-------------------------------------------------------------+
|                     DISTRIBUTED SYSTEM                      |
|  [ Node A (US-East) ] <--- Network Boundary ---> [ Node B (EU-West) ] |
|  Isolated RAM           (Packet Jitter, Dropped   Isolated RAM       |
|  Independent Clock      Packets, High Latency)    Independent Clock  |
+-------------------------------------------------------------+
```

When systems scale beyond a single physical chassis, the core rules of computation change fundamentally. A distributed system introduces spatial separation, network unreliability, and asynchronous concurrency.

---

## 2. Core Properties of Distributed Systems

Distributed architectures are characterized by three fundamental operational realities:

### 1. Concurrent Execution
Multiple nodes execute instructions simultaneously. Without a shared memory bus, components cannot inspect another node's private internal state directly; state must be serialized, transmitted as bytes over a physical wire, and deserialized.

### 2. Independent & Partial Failures
In a monolith, if the operating system kernel panics, the entire system crashes deterministically. In a distributed system:
- Node A may crash while Node B continues processing.
- The network link connecting Node A and Node B may fail while both nodes remain fully operational (a network partition).
- A node may experience a Stop-The-World garbage collection pause, appearing dead to other nodes, and later resume processing.

Systems must be designed for **graceful degradation**, containing failures so they do not trigger cascading collapse across the cluster.

### 3. Absence of a Global Physical Clock
There is no absolute global reference for time. Every machine possesses its own physical quartz crystal oscillator clock, which drifts due to temperature fluctuations and hardware variance.

```text
Node 1 (Local Clock): 14:00:00.002
Node 2 (Local Clock): 13:59:59.988 (14ms behind!)
Event X happens on Node 2 -> sent to Node 1 -> Node 1 timestamps it earlier!
```

---

## 3. Logical Time & Event Ordering

Because physical clocks drift, relying on wall-clock timestamps (`System.currentTimeMillis()`) to determine causal order (did event $A$ cause event $B$?) leads to silent data corruption in distributed databases.

### Lamport Timestamps
Leslie Lamport formulated the **Happens-Before Relationship** ($\to$):
- If events $a$ and $b$ occur within the same process and $a$ occurs before $b$, then $a \to b$.
- If $a$ is the sending of a message and $b$ is the receipt of that message, then $a \to b$.
- If $a \to b$ and $b \to c$, then $a \to c$ (transitivity).

A **Lamport Logical Clock** is a monotonically increasing integer maintained by each node:

```java
public class LamportClock {
    private int counter = 0;

    public synchronized int tickOnLocalEvent() {
        return ++counter;
    }

    public synchronized int updateOnReceive(int incomingTimestamp) {
        counter = Math.max(counter, incomingTimestamp) + 1;
        return counter;
    }
}
```

```text
Node A: [ Event 1 (L=1) ] ---> Send Msg (L=2) --------------------+
                                                                  |
Node B: [ Event 1 (L=1) ] ---> Receive (max(1, 2)+1 = 3) <--------+
```

### Vector Clocks
While Lamport timestamps produce a total ordering, they cannot determine whether two events are causally related or concurrent. **Vector Clocks** maintain an integer array of clock values for every node in the cluster, allowing databases (such as Amazon DynamoDB and Apache Cassandra) to detect concurrent conflicting writes.

---

## 4. Why Distribute? The 4 Core Motivations

Organizations transition from monolithic architectures to distributed topologies to achieve four critical engineering goals:

```text
                  +--------------------------------+
                  |  DRIVERS FOR DISTRIBUTING      |
                  +--------------------------------+
                   /         |           |        \
                  v          v           v         v
            Scalability  Resilience  Geo-Latency Compliance
```

1. **Horizontal Scalability (Scale-Out):** Single machines hit hard physical limits in CPU socket density, memory bus bandwidth, and thermal dissipation. Distributing workloads across hundreds of commodity nodes enables elastic scaling.
2. **High Availability & Fault Tolerance:** Eliminating Single Points of Failure (SPOFs). Redundant compute nodes and replicated databases ensure services stay online during hardware breakdowns.
3. **Geo-Proximity & Latency:** Speed-of-light propagation through fiber optics requires $\approx 70\text{ms}$ to travel from London to Singapore. Placing edge compute and storage nodes geographically close to users slashes round-trip times (RTT).
4. **Data Sovereignty & Compliance:** Legal requirements (such as GDPR or HIPAA) mandate that customer data reside within specific legal boundaries and geographic jurisdictions.

---

## 5. System Models: Synchronous vs. Asynchronous

When designing distributed algorithms, architects must define their assumptions regarding time and network behavior:

| Model Dimension | Synchronous Model | Asynchronous Model | Partially Synchronous (Reality) |
| :--- | :--- | :--- | :--- |
| **Message Latency** | Strictly bounded ($\le D$) | Unbounded (arbitrarily late) | Bounded most of the time |
| **Clock Drift** | Strictly bounded rate | Arbitrary / Unpredictable | Controlled via NTP with jitter |
| **Failure Detection**| Heartbeat timeout guarantees dead node | Impossible to distinguish slow node from dead node | Probabilistic (Phi-accrual failure detectors) |

Modern cloud environments are **partially synchronous**: under normal conditions, network packets arrive within milliseconds. However, during network congestion or routing failovers, delays become unpredictable.

---

## 6. The Distributed Systems Tax

Distributing systems introduces immense power, but charges an unavoidable architectural tax:

- **Network Overhead:** Serialization/deserialization (JSON, Protobuf), socket connection establishment, and TLS handshakes consume CPU cycles.
- **Observability Complexity:** A single user transaction may span 30 distinct microservices. Tracing requests requires distributed correlation IDs (OpenTelemetry, Jaeger, W3C TraceContext).
- **Testing & Debugging:** Race conditions, split-brain scenarios, and packet reordering are difficult to reproduce in local developer environments.
