# Reactive Streams & Architecture Decision Matrix

Building resilient, high-throughput cloud applications requires shifting from synchronous, blocking paradigms to asynchronous, non-blocking execution models. However, adopting asynchronous patterns introduces architectural trade-offs that dictate how components interact, handle failures, and scale under extreme traffic.

---

## 1. Modern Asynchronous & Reactive Paradigms

When decoupled services communicate asynchronously, the rate of data production often mismatches the rate of consumption:

```text
[ FAST PRODUCER ] (10,000 items/sec) ===> [ SLOW CONSUMER ] (500 items/sec)
                                                 |
                                          Buffers Overflow!
                                                 v
                                        OutOfMemoryError / Crash
```

### The Push vs. Pull Dilemma
- **Pure Push Model:** The producer pushes data as soon as it is generated. If the consumer is overwhelmed, in-memory buffers overflow, leading to JVM heap exhaustion and dropped packets.
- **Pure Pull Model:** The consumer repeatedly polls the producer for data. While safe from buffer overflows, polling wastes CPU cycles and network bandwidth when no data is available and introduces polling latency.

### The Solution: Dynamic Push-Pull with Backpressure

The **Reactive Streams Specification** (formalized in Java 9 as `java.util.concurrent.Flow`) solves this by establishing a contract for non-blocking stream processing with **asynchronous backpressure**:

```text
+----------------+                                   +-----------------+
|   Publisher    | <------- 1. subscribe(sub) -------|   Subscriber    |
|   (Producer)   |                                   |   (Consumer)    |
|                | ------- 2. onSubscribe(sub) ----> |                 |
|                |                                   |                 |
|                | <------- 3. request(10) ----------|  Signals Demand |
|                |                                   |                 |
|                | ------- 4. onNext(item 1..10) --->| Processes data  |
|                | (Pauses until further demand!)    |                 |
|                |                                   |                 |
|                | <------- 5. request(5) -----------|  Signals Demand |
|                | ------- 6. onNext(item 11..15) -->|                 |
+----------------+                                   +-----------------+
```

### The Four Reactive Interfaces
1. `Publisher<T>`: Emits elements to subscribers according to downstream demand.
2. `Subscriber<T>`: Receives items and signals readiness for more via its subscription.
3. `Subscription`: The dynamic bridge between publisher and subscriber (`request(long n)` and `cancel()`).
4. `Processor<T, R>`: A processing stage acting as both a subscriber and a publisher.

### Spring WebFlux & Project Reactor in Action

```java
@RestController
@RequestMapping("/api/telemetry")
public class TelemetryStreamingController {

    private final TelemetryIngestService service;

    public TelemetryStreamingController(TelemetryIngestService service) {
        this.service = service;
    }

    @GetMapping(value = "/live", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<DeviceMetricDto> streamMetrics(
            @RequestParam String deviceId,
            @RequestParam(defaultValue = "medium") String priority) {

        return service.streamDeviceMetrics(deviceId)
            .filter(metric -> metric.severity() > 2)
            // Backpressure: request 50 items at a time from upstream
            .limitRate(50)
            // Buffer up to 500 items, dropping oldest on extreme downstream lag
            .onBackpressureBuffer(500, 
                dropped -> log.warn("Dropped metric: {}", dropped.id()),
                BufferOverflowStrategy.DROP_OLDEST)
            // Execute non-blocking transformation
            .map(this::enrichMetric)
            .timeout(Duration.ofSeconds(10))
            .onErrorResume(TimeoutException.class, e -> Flux.empty());
    }
}
```

---

## 2. Reactive Streams vs. Virtual Threads (Java 21+ Project Loom)

Java 21 introduced **Virtual Threads**, fundamentally reshaping the JVM concurrency landscape and challenging the necessity of complex reactive pipelines:

```text
REACTIVE STREAMS (Mono / Flux)
- Non-blocking Event Loops
- Functional, declarative pipelines
- Complex stack traces and debugging
- High mental model overhead
- Ideal for continuous event flows

VIRTUAL THREADS (Project Loom)
- Blocking calls yield carrier thread automatically
- Clean, imperative synchronous syntax
- Full stack traces and thread dumps
- Drop-in replacement for existing code
- Ideal for standard request-response CRUD
```

### Direct Architectural Comparison

| Dimension | Reactive Streams (Reactor / Vert.x) | Virtual Threads (Java 21+ Loom) |
| :--- | :--- | :--- |
| **Programming Paradigm** | Declarative / Functional Pipelines | Imperative / Synchronous (`try-catch`)|
| **Stack Trace Debugging** | Fragmented across async boundaries | Traditional, complete call stack |
| **Existing Ecosystem** | Requires non-blocking drivers (R2DBC) | Works transparently with JDBC, JPA |
| **Backpressure Control** | Native, granular credit-based control| Handled via bounded thread pools/queues|
| **Streaming & Composition**| Exceptional (`merge`, `zip`, `window`)| Requires manual queue orchestration |

### Architectural Recommendation
- **Use Virtual Threads** when building standard microservice APIs, REST endpoints, and database CRUD operations where imperative readability and existing libraries (JPA, JDBC) dominate.
- **Use Reactive Streams** when building real-time event streaming systems, API gateways, WebSocket servers, or pipelines requiring end-to-end backpressure propagation across network boundaries.

---

## 3. Asynchronous Messaging & Distributed Streaming

While in-memory reactive streams govern intra-process concurrency, enterprise distributed systems decouple microservices using **Message Brokers** and **Distributed Event Logs**:

```text
[ Checkout Service ] 
         |
         v (Transactional Outbox)
[ Local PostgreSQL DB ] ---> [ Debezium CDC ] ---> [ Apache Kafka Topic: orders ]
                                                            |
                            +-------------------------------+-------------------------------+
                            |                                                               |
                            v                                                               v
                 [ Inventory Consumer ]                                          [ Notification Consumer ]
                 (Consumer Group A)                                              (Consumer Group B)
```

### Key Messaging Architecture Patterns

#### 1. The Transactional Outbox Pattern
Avoid the dangerous "dual-write" anti-pattern (writing to a database and publishing to Kafka in separate uncoordinated actions). If Kafka is down, the database commit succeeds, but messages are lost forever!

**Solution:** The business service writes the entity state AND an outbox message into the local relational database in a **single local ACID transaction**. A Change Data Capture (CDC) connector (e.g., Debezium) streams the outbox records reliably to Kafka.

#### 2. Idempotent Consumer & De-duplication
Message brokers guarantee **at-least-once delivery** during retries or network reconnections. Consumers must handle duplicate messages safely:

```java
@Component
public class PaymentOrderConsumer {

    private final RedisTemplate<String, String> redis;

    @KafkaListener(topics = "order-payments", groupId = "payment-group")
    public void processPayment(OrderPaymentEvent event, Acknowledgment ack) {
        String idempotencyKey = "idemp:payment:" + event.getPaymentId();

        // Atomically set key if absent with 24-hour TTL
        Boolean isNew = redis.opsForValue()
            .setIfAbsent(idempotencyKey, "PROCESSED", Duration.ofHours(24));

        if (Boolean.TRUE.equals(isNew)) {
            executePaymentTransaction(event);
        } else {
            log.info("Duplicate payment event ignored: {}", event.getPaymentId());
        }
        ack.acknowledge();
    }
}
```

#### 3. Non-Blocking Retry Topics & Dead Letter Queues (DLQ)
Blocking consumer threads during temporary downstream failures creates consumer lag. Modern architectures route failed messages to progressive retry topics:

```text
[ orders ] ---> Processing Fails!
   |
   +---> [ orders.retry.10s ] ---> [ orders.retry.60s ] ---> [ orders.DLQ ]
         (Delay: 10 seconds)       (Delay: 60 seconds)       (Manual Inspection)
```

---

## 4. The Cloud Concurrency Decision Matrix

Choosing the correct concurrency and coordination pattern requires balancing four architectural dimensions:

```text
                     [ ARCHITECTURAL DIMENSIONS ]
                                  |
     +-------------------+--------+--------+-------------------+
     |                   |                 |                   |
[ Contention ]     [ Latency SLA ]   [ Coordination ]   [ Complexity ]
```

### Master Architecture Selection Table

| Scenario / Requirement | Recommended Solution | Secondary Alternative | Key Architectural Trade-off |
| :--- | :--- | :--- | :--- |
| **High-Volume Microservice Auth** | Stateless JWT + Refresh Token | Redis Distributed Sessions | Local verification speed vs instant token revocation capability |
| **Shopping Cart / Ephemeral State** | Redis Cluster with TTL | Hazelcast IMDG | Simple key-value expiry vs complex in-memory compute clustering |
| **Hot Database Rows (Low Contention)**| Optimistic Locking (`@Version`) | Retry Loops with Jitter | Zero database lock overhead; fails fast with retry cost |
| **Hot Database Rows (High Contention)**| Pessimistic Locking (`FOR UPDATE`)| Redis Distributed Mutex | Database handles queueing; risks connection pool starvation |
| **Distributed Worker Task Queues** | PostgreSQL `SKIP LOCKED` | RabbitMQ / Kafka | Zero external infrastructure vs dedicated message broker scale |
| **Financial Ledger / Audit Trail** | CQRS + Event Sourcing (Axon) | Kafka Event Log | Ultimate auditability and replay vs steep domain learning curve |
| **Ultra-High Throughput Gateway** | Eclipse Vert.x / Spring WebFlux | Java 21 Virtual Threads | Maximum resource efficiency vs simple imperative debugging |
| **Cluster Leader Election** | Apache ZooKeeper (Curator) | etcd / Consul | Zab/Raft consensus guarantees single leader without split-brain |
| **Microservice Decoupling** | Apache Kafka (Partitioned Log) | RabbitMQ | Long-term replayability and partitioning vs flexible message routing |
| **Cluster-Wide Configuration** | etcd (gRPC Watches) | HashiCorp Consul | Native Kubernetes integration vs rich service discovery catalog |
