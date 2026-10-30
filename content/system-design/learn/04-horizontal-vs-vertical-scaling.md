# Horizontal vs Vertical Scaling

Scalability describes a system's capability to handle increasing workloads gracefully by adding hardware resources without degrading user response times or throughput SLAs.

![Scalability Architecture](../assets/scalability-diagram.webp)

---

## 1. Vertical Scaling (Scale-Up)

**Vertical Scaling** increases the capacity of an existing individual server by adding more CPU cores, faster RAM, wider network interfaces, or larger NVMe SSD storage volumes.

```text
+-----------------------+              +-----------------------+
|  COMMODITY INSTANCE   |              |   ENTERPRISE INSTANCE  |
|  4 vCPUs              |  Scale-Up    |  128 vCPUs            |
|  16 GB RAM            | ===========> |  1,024 GB RAM         |
|  1 Gbps Network       |              |  100 Gbps Network     |
+-----------------------+              +-----------------------+
```

### Advantages of Vertical Scaling
- **Zero Architecture Changes:** Monolithic software, legacy single-threaded processes, and standard SQL databases require no code modifications to leverage upgraded cores and memory.
- **In-Memory Concurrency:** Threads communicate over nanosecond CPU memory buses. There is zero distributed network latency, serialization overhead, or distributed locking.
- **Strong ACID Consistency:** A single database instance guarantees ACID transactions out of the box with zero split-brain risks.

### Limitations & Bottlenecks
- **Hard Hardware Ceilings:** Physical architectures have finite limits on motherboard socket counts, memory bus channels, and PCI Express lanes.
- **Exponential Cost Curve:** A 64-core enterprise server often costs $10\times$ more than sixteen 4-core commodity instances.
- **Single Point of Failure (SPOF):** If the motherboard, CPU, or hypervisor fails, the entire application suffers complete downtime until the hardware is restored.
- **Downtime for Upgrades:** Scaling up almost always requires stopping the instance to resize its compute profile.

---

## 2. Horizontal Scaling (Scale-Out)

**Horizontal Scaling** adds more commodity compute instances (virtual machines, containers, or pods) in parallel behind a **Load Balancer**.

```text
                                [ Load Balancer ]
                                        |
     +------------------+---------------+---------------+------------------+
     | Round-Robin      | Round-Robin   | Round-Robin   | Round-Robin      |
     v                  v               v               v                  v
[ App Server 1 ] [ App Server 2 ] [ App Server 3 ] [ App Server 4 ] [ App Server N ]
 (Commodity)      (Commodity)      (Commodity)      (Commodity)      (Commodity)
```

### Advantages of Horizontal Scaling
- **Near-Infinite Elasticity:** Compute capacity can scale from 5 to 5,000 instances dynamically using cloud autoscalers (such as Kubernetes Horizontal Pod Autoscaler).
- **Fault Tolerance & Redundancy:** If Server 3 crashes or burns a power supply, health checks detect the failure within seconds and redirect traffic to surviving nodes with zero user impact.
- **Cost Efficiency:** Workloads leverage cheap, commoditized hardware and spot/preemptible instances.
- **Zero-Downtime Deployments:** Rolling updates and canary releases deploy new software versions one server at a time while the remaining fleet processes live user traffic.

---

## 3. The Core Requirement: Stateless Application Tier

To achieve true horizontal scalability, application servers must adhere to a strict rule: **they must be completely stateless**.

```text
ANTI-PATTERN: Storing session state on the local JVM Heap
[ User X ] ---> [ App Server 1 (Session: Cart=[Shirt, Shoes]) ]
[ User X ] ---> (Next request routed to Server 2)
[ User X ] ---> [ App Server 2 (Cart is EMPTY! Session Lost!) ]
```

### The Peril of Sticky Sessions
When teams cannot decouple state from memory, they resort to **Sticky Sessions** (session affinity), where the load balancer forces a user to always hit the same node. As explored in distributed system design, sticky sessions create severe hotspots, break autoscaling elasticity, and cause data loss during pod crashes.

### Production Solution: Externalized State

```text
[ Client Request ]
       |
       v
[ Load Balancer ]
       |
       +-----------------------+-----------------------+
       |                       |                       |
       v                       v                       v
[ App Server 1 ]        [ App Server 2 ]        [ App Server 3 ]
  (Stateless)             (Stateless)             (Stateless)
       |                       |                       |
       +-----------------------+-----------------------+
                               v
               [ Distributed Redis Cluster ]
                 (External In-Memory State)
```

1. **Distributed In-Memory Stores:** User sessions, shopping carts, and transient states are stored in an external cluster (such as Redis or Memcached).
2. **Stateless Tokens (JWT):** Authentication claims and user roles are cryptographically signed and stored on the client device, allowing any server in the pool to verify permissions without database lookups.

---

## 4. Scaling the Stateful Data Tier

While compute servers can scale out statelessly with ease, databases store stateful, durable records on disk. Scaling the database tier horizontally introduces distributed coordination challenges:

```text
                   +-----------------------+
                   |  PRIMARY DATABASE     |
                   |  (Handles All Writes) |
                   +-----------------------+
                               |
             Asynchronous Binary Log Replication
                               |
            +------------------+------------------+
            v                                     v
+-----------------------+             +-----------------------+
|  READ REPLICA 1       |             |  READ REPLICA 2       |
|  (Handles Reads)      |             |  (Handles Reads)      |
+-----------------------+             +-----------------------+
```

1. **Read Replicas (Read-Heavy Systems):** Direct all `INSERT`, `UPDATE`, and `DELETE` commands to a single primary database, while fanning out `SELECT` queries across multiple read replicas.
2. **Sharding / Partitioning (Write-Heavy Systems):** Split a monolithic database table across multiple physical database instances using a hash-based or range-based **Shard Key**.
3. **NoSQL Distributed Stores:** Engines like Apache Cassandra and Google Cloud Bigtable partition data across cluster rings automatically using consistent hashing.

---

## 5. Architectural Comparison Matrix

| Dimension | Vertical Scaling (Scale-Up) | Horizontal Scaling (Scale-Out) |
| :--- | :--- | :--- |
| **Scaling Limit** | Hard physical hardware ceiling | Virtually unlimited elastic nodes |
| **System Complexity** | Very Low (Single node) | Moderate to High (Requires load balancers) |
| **High Availability** | None (Single Point of Failure) | Built-in redundancy and failover |
| **Cost Trajectory** | Exponential at higher tiers | Linear across commodity hardware |
| **Deployment Model** | Requires downtime to resize | Zero-downtime rolling deployments |
| **Best Used For** | Small startups, internal tools, ACID DBs | Web-scale consumer apps, microservices |
