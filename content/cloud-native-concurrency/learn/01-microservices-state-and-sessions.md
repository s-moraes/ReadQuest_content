# Managing State in Microservices

Microservices represent an architectural style where independently deployable services collaborate to deliver complex business capabilities. However, managing mutable state across this distributed landscape is one of the most challenging engineering hurdles. Without deliberate state boundaries, distributed systems quickly devolve into tightly coupled, fragile distributed monoliths.

---

## 1. The Distributed State Dilemma

In a monolithic architecture, state management is simplified by a shared memory space and a single relational database enforcing ACID transactions. In a distributed cloud-native architecture, compute instances are replicated, ephemeral, and distributed across failure domains:

```text
+-------------------------------------------------------------+
|                     MONOLITHIC STATE                        |
|  [ Thread 1 ] \                                             |
|  [ Thread 2 ] --+--> [ Shared JVM Heap ] --> [ Single DB ]  |
|  [ Thread N ] /                                             |
+-------------------------------------------------------------+
                              vs
+-------------------------------------------------------------+
|                 DISTRIBUTED CLOUD STATE                     |
|  [ Pod A (JVM) ] <--- Network Boundary ---> [ Pod B (JVM) ] |
|         |                                          |        |
|         v                                          v        |
|  [ State Store A ]                         [ State Store B ] |
+-------------------------------------------------------------+
```

When systems scale across distributed boundaries, engineers encounter the Fallacies of Distributed Computing:
- **The network is reliable:** Packets drop, timeouts occur, and latency spikes unpredictably.
- **Latency is zero:** Cross-network state lookups introduce milliseconds of delay compared to nanosecond in-memory reads.
- **Topology does not change:** Containers terminate, restart, and migrate dynamically.

Attempting to maintain synchronized in-memory state across multiple service replicas creates severe coordination bottlenecks and data consistency anomalies.

---

## 2. Stateless Service Architecture in Cloud & Kubernetes

The foundational rule of scalable cloud-native design is **Twelve-Factor App Principle VI: Execute the app as one or more stateless processes**.

A stateless service retains no client context, session data, or conversational state in its local memory between requests. Any available replica can process any incoming request with identical results.

```text
[ Client Request ]
       |
       v
[ Cloud Load Balancer / Ingress Controller ]
       |
       +------------------+------------------+
       | Round-Robin      | Round-Robin      | Round-Robin
       v                  v                  v
[ Order Pod 1 ]    [ Order Pod 2 ]    [ Order Pod 3 ]
 (Stateless JVM)    (Stateless JVM)    (Stateless JVM)
       |                  |                  |
       +------------------+------------------+
                          v
           [ Distributed Cache / DB Cluster ]
                     (State Layer)
```

### Operational Advantages in Kubernetes

1. **Effortless Horizontal Pod Autoscaling (HPA):** When CPU or request metrics spike, Kubernetes spawns new pods instantly. Since new pods require no historical session data, they handle traffic the moment their readiness probe passes.
2. **Resilience & Graceful Eviction:** When a node crashes or Kubernetes drains a node for maintenance (`kubectl drain`), pods receive a `SIGTERM` signal. Because no persistent session state lives on the heap, the pod finishes in-flight requests and exits cleanly without data loss.
3. **Zero-Downtime Deployments:** Rolling updates, blue-green deployments, and canary releases operate seamlessly. Traffic shifts dynamically across versions without session migration or complex session replication.

---

## 3. The Perils of Sticky Sessions

When teams attempt to preserve legacy stateful paradigms in the cloud, they often resort to **Sticky Sessions** (session affinity), where the load balancer pins a client to a specific server instance via IP hashing or cookie tracking.

```text
[ Client X ] ---> [ Load Balancer (Cookie: SESS=NodeA) ] ---> [ Node A ]
[ Client Y ] ---> [ Load Balancer (Cookie: SESS=NodeB) ] ---> [ Node B ]
```

While seemingly convenient, sticky sessions cause critical cloud anti-patterns:

- **Traffic Hotspots & Uneven Load:** If high-volume users or batch processes land on the same pod, that pod becomes CPU/memory saturated while neighboring pods sit idle.
- **Cascading Failures:** When Node A crashes, all users pinned to Node A immediately lose their active session data. The load balancer redistributes these orphaned users to remaining nodes, triggering CPU spikes and potential chain-reaction outages.
- **Broken Autoscaling:** The autoscaler cannot freely terminate underutilized pods because active user sessions are trapped in their local JVM memory.
- **Draining Latency:** Canary releases and rolling upgrades stall waiting for long-lived sessions to naturally expire before tearing down old pods.

---

## 4. Distributed Session Storage: Redis in Production

To preserve user continuity without violating stateless principles, applications offload session state to an external, distributed, high-speed in-memory store like **Redis**.

```text
+---------------+      Write Session (JSON/Proto)      +---------------+
|  Microservice | -----------------------------------> | Redis Cluster |
|   Instance A  | <----------------------------------- |  (Primary /   |
+---------------+      Read Session By SessionId       |   Replica)    |
                                                       +---------------+
                                                               ^
+---------------+                                              |
|  Microservice | ---------------------------------------------+
|   Instance B  |             Read Same Session
+---------------+
```

### Implementation with Spring Session & Redis

Spring Session decouples session storage from the underlying servlet container (Tomcat, Jetty), transparently intercepting `HttpServletRequest` to store attributes in Redis:

```java
@Configuration
@EnableRedisHttpSession(
    maxInactiveIntervalInSeconds = 1800,
    redisNamespace = "readquest:session"
)
public class DistributedSessionConfig {

    @Bean
    public LettuceConnectionFactory redisConnectionFactory() {
        RedisStandaloneConfiguration config = 
            new RedisStandaloneConfiguration("redis-cluster", 6379);
        config.setPassword("secure-vault-pass");

        LettuceClientConfiguration clientConfig = 
            LettuceClientConfiguration.builder()
                .commandTimeout(Duration.ofMillis(250))
                .build();

        return new LettuceConnectionFactory(config, clientConfig);
    }

    @Bean
    public RedisSerializer<Object> springSessionDefaultRedisSerializer() {
        // Use JSON serialization instead of JDK binary serialization
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JavaTimeModule());
        return new GenericJackson2JsonRedisSerializer(mapper);
    }
}
```

### Production Considerations for Distributed Sessions

- **TTL (Time-To-Live) Sliding Windows:** Redis automatically purges expired keys. Ensure the session store refreshes the TTL on each authenticated read to prevent active users from being logged out mid-operation.
- **Serialization Overhead:** Default Java native serialization (`JdkSerializationRedisSerializer`) is brittle across class version changes, vulnerable to deserialization exploits, and inflates payload sizes. Always prefer JSON (Jackson) or Protocol Buffers.
- **Connection Pooling & Timeouts:** Configure strict connection pool limits and aggressive network timeouts ($\le 250\text{ms}$) on Redis calls. If Redis slows down, your web tier threads must not block indefinitely.
- **Memory Eviction Policy:** Configure Redis with `maxmemory-policy volatile-lru` or `volatile-ttl` to prevent the cache from dropping persistent application keys when memory thresholds are reached.

---

## 5. Stateless Authentication: JWT vs Distributed Sessions

Cloud-native systems frequently evaluate two primary paradigms for authentication state:

```text
[ Client ] -- 1. Bearer Token (JWT) --> [ API Gateway ] -- No DB Lookup --> [ Microservice ]
                                               |
                                        Cryptographic
                                         Verification
                                               v
                                        [ Valid / Expired ]
```

### Architectural Comparison

| Dimension | Distributed Session (Redis) | Stateless Token (JWT) |
| :--- | :--- | :--- |
| **State Location** | Centralized in Redis | Client stores signed token |
| **Verification** | Network call to Redis per request | Local cryptographic check (Public Key)|
| **Payload Size** | Minimal (opaque UUID session ID) | Medium/Large (claims, scopes, roles) |
| **Instant Revocation**| Immediate (`DEL session:<id>`) | Difficult without central blacklist |
| **Network Overhead** | 1 cache lookup per request | 0 network lookups per request |

### The Hybrid Token Pattern (Production Best Practice)
To combine the speed of stateless tokens with the security of instant revocation, high-scale architectures adopt a **hybrid approach**:
1. Issue a **short-lived Access Token** (JWT, lifespan: 5–15 minutes) signed with an asymmetric key (RS256/ES256).
2. Issue a **long-lived Refresh Token** (opaque UUID, lifespan: 7–30 days) stored in a secure, HttpOnly cookie and tracked in Redis.
3. Microservices validate access tokens locally with zero database or cache latency.
4. When permissions change, passwords reset, or suspicious activity occurs, the refresh token in Redis is deleted immediately, blocking token renewal.

---

## 6. CQRS and Event Sourcing: State as an Immutable Ledger

In write-heavy microservice domains or complex business workflows, storing only the latest snapshot of an entity causes major problems:
- Concurrent updates overwrite intermediate states (lost updates).
- Historical context, intent, and audit trails are lost forever.
- Relational schema normalization conflicts with high-speed denormalized queries.

The combination of **Command Query Responsibility Segregation (CQRS)** and **Event Sourcing (ES)** solves this fundamentally:

```text
                      [ Command Service ]
                               |
                        Validate Invariants
                               |
                               v
                     +-------------------+
                     | Append Event Log  | ---> [ Event Store (Kafka/RDBMS) ]
                     +-------------------+            |
                                                      v
                                            [ Project / Replay ]
                                                      |
                                                      v
  [ Client Query ] <--- [ Read Service ] <--- [ Materialized Read DB ]
                                                (MongoDB / Elastic / SQL)
```

### 1. Command Side (Write Path)
Commands express user intent (`PlaceOrderCommand`, `CancelSubscriptionCommand`). The Command Handler loads the aggregate root, checks business validation rules, and appends one or more immutable domain events:

$$\text{Current State} = \sum_{i=1}^{n} \text{Event}_i$$

### 2. Query Side (Read Path)
Projections asynchronously listen to committed domain events and update optimized read models (Elasticsearch, PostgreSQL views, or Redis). Queries never touch the aggregate event store directly.

### Aggregate Root Example with Axon Framework

```java
@Aggregate
public class BankAccountAggregate {

    @AggregateIdentifier
    private String accountId;
    private BigDecimal balance;

    protected BankAccountAggregate() {} // Required by Axon

    @CommandHandler
    public BankAccountAggregate(CreateAccountCommand cmd) {
        if (cmd.getInitialDeposit().compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Initial deposit cannot be negative");
        }
        AggregateLifecycle.apply(
            new AccountCreatedEvent(cmd.getAccountId(), cmd.getInitialDeposit())
        );
    }

    @CommandHandler
    public void handle(WithdrawFundsCommand cmd) {
        if (cmd.getAmount().compareTo(this.balance) > 0) {
            throw new InsufficientFundsException("Balance exceeded");
        }
        AggregateLifecycle.apply(
            new FundsWithdrawnEvent(this.accountId, cmd.getAmount())
        );
    }

    @EventSourcingHandler
    public void on(AccountCreatedEvent event) {
        this.accountId = event.getAccountId();
        this.balance = event.getInitialDeposit();
    }

    @EventSourcingHandler
    public void on(FundsWithdrawnEvent event) {
        this.balance = this.balance.subtract(event.getAmount());
    }
}
```

### Snapshotting at Scale
When an aggregate processes thousands of events, replaying the entire event stream on every write degrades performance. Event-sourced engines use **Snapshots**:

```text
[ Event 1 ] -> [ Event 2 ] ... [ Event 100 ] -> [ SNAPSHOT v100 ]
                                                       |
[ Load State ] <---------------------------------------+
      |
      +---> [ Event 101 ] -> [ Event 102 ] -> [ Current State v102 ]
```

The system loads the latest snapshot and replays only the delta events committed afterward.

---

## 7. The Saga Pattern: Distributed Transactions Without 2PC

Traditional databases rely on **Two-Phase Commit (2PC)** to coordinate distributed transactions. However, 2PC is a blocking protocol: if the transaction coordinator fails, resource locks remain held across all nodes, bringing microservices to a halt.

Cloud-native systems replace 2PC with the **Saga Pattern**: a sequence of local transactions where each step updates data within a single service and publishes an event or message to trigger the next step.

```text
+-------------------+      1. Reserve Stock      +--------------------+
|   Order Service   | -------------------------> |  Inventory Service |
+-------------------+                            +--------------------+
          |                                                 |
          | 2. Order Placed                                 | Stock Reserved
          v                                                 v
+-------------------+      3. Process Charge     +--------------------+
|  Payment Service  | <------------------------- |   Event Stream     |
+-------------------+                            +--------------------+
          |
     Charge Failed!
          |
          v
+-------------------+   4. Compensating Action   +--------------------+
|  Payment Service  | -------------------------> |  Inventory Service |
|  (Emit Failure)   |    (Release Stock Lock)    |   (Compensate)     |
+-------------------+                            +--------------------+
```

### Saga Flavors: Choreography vs Orchestration

1. **Choreography (Decentralized):**
   - Services react to domain events published by other services.
   - Ideal for simple workflows (2–4 services) with low complexity.
   - Hazard: Difficult to trace, risk of circular event dependencies.

2. **Orchestration (Centralized):**
   - A dedicated Orchestrator (state machine) directs participants by sending commands and listening for responses.
   - Frameworks: Temporal, Camunda, AWS Step Functions, Axon Saga.
   - Clear centralized visibility and deterministic error handling.

---

## 8. Summary & Architectural Trade-Off Matrix

| Strategy | Scalability | Complexity | Fault Tolerance | Best Used For |
| :--- | :--- | :--- | :--- | :--- |
| **Stateless Services** | Extreme (Linear) | Minimal | Instantaneous failover | Core business APIs, compute, batch workers |
| **Distributed Redis Sessions** | High | Low-Moderate | Redis Cluster failover | Shopping carts, user sessions, wizard forms |
| **Stateless JWT Tokens** | Extreme | Moderate | High (Local verification) | Mobile/Web auth, public API gateways |
| **CQRS + Event Sourcing** | Very High (Reads) | High | Complete audit replay | Financial ledgers, tracking, order lifecycles |
| **Saga Transactions** | High | High | Explicit compensations | Multi-service purchases, order fulfillment |
