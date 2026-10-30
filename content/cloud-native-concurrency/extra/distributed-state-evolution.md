# The Evolution of Distributed State

Managing state across multiple servers has undergone a profound architectural shift over the past three decades. As systems evolved from centralized corporate mainframes to globally distributed cloud clusters, the engineering industry had to dismantle long-held assumptions about transactions, consistency, and failure modes.

---

## 1. The Era of Two-Phase Commit (2PC) & EJB

In the late 1990s and early 2000s, Enterprise Java Beans (EJB) and Java EE dominated enterprise software architectures. Applications coordinated transactions across multiple databases and message queues using **XA Transactions** and the **Two-Phase Commit (2PC)** protocol.

```text
               [ Transaction Coordinator ]
                      /            \
       1. Prepare?   /              \   1. Prepare?
                    v                v
         [ Database A ]            [ Database B ]
                    \                /
        2. Commit!   \              /   2. Commit!
                      v            v
```

### The Pitfalls of 2PC in the Cloud
2PC assumes a stable, low-latency local network and a highly available central coordinator:
- **Blocking Protocol:** If the coordinator or network fails during the commit phase, all participating database nodes hold row locks indefinitely, exhausting connection pools.
- **Latency Multiplication:** The total commit latency equals the slowest node's round trip, crippling throughput across cloud regions.
- **Incompatible with Microservices:** Tying independent databases together with distributed locks directly violates microservice boundaries and autonomy.

---

## 2. The Shift to BASE and Eventual Consistency

As internet scale exploded with companies like Google and Amazon, Eric Brewer introduced the CAP theorem, leading architects to trade strict immediate consistency for system availability and partition tolerance.

The enterprise mindset shifted from **ACID** (Atomicity, Consistency, Isolation, Durability) to **BASE**:
- **Basically Available:** The system guarantees availability for most requests despite partial network failures.
- **Soft State:** State may fluctuate over time, even without new input, as background synchronization catches up.
- **Eventual Consistency:** The system will become consistent over time if no new updates are made to the object.

---

## 3. The Modern Era: Sagas and Event Sourcing

Modern cloud-native Java microservices solve distributed state coordination through **compensating transactions** rather than distributed database locks.

```text
[ Step 1: Create Order ] ---> [ Step 2: Authorize Payment ] ---> [ Step 3: Reserve Stock ]
         |                                  |
         | (If Payment Fails)               |
         v                                  v
[ Cancel Order ] <--- [ Compensating Tx ] <-+
```

### The Saga Pattern
A Saga is a sequence of local transactions. Each transaction updates data within a single service and publishes an event. Subsequent steps execute based on incoming events:
- **Choreography:** Services listen to domain events and execute their steps without a central coordinator.
- **Orchestration:** A dedicated orchestrator service sends commands to participants and triggers compensating transactions if any step fails.

---

## Historical Evolution Timeline

| Era | Dominant Technology | Transaction Model | Failure Handling |
| :--- | :--- | :--- | :--- |
| **1990s - 2005** | EJB, XA, Oracle Tuxedo | Two-Phase Commit (2PC) | Distributed rollback with locks |
| **2006 - 2015** | Spring Framework, Redis, AMQP | Local transactions + Queues | Retry queues, dead-letter topics |
| **2016 - Present**| Axon, Kafka, Reactive Streams | Sagas & Event Sourcing | Compensating transactions & state replays |
