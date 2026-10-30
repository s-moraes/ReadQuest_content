# Cloud-Native Concurrency Toolkits

Traditional cloud applications built on the "thread-per-request" model (such as classic Servlet containers like Tomcat and Jetty) struggle under extreme concurrency. Operating system threads consume significant memory (typically 1MB per thread stack) and incur heavy CPU penalties from kernel context switching when scaling to tens of thousands of concurrent connections.

Modern cloud-native toolkits replace blocking threads with asynchronous, event-driven, actor-based, and reactive architectures.

---

## 1. The Concurrency Paradigm Shift in Cloud Microservices

When designing high-throughput cloud microservices, understanding the physical cost of concurrency models is essential:

```text
THREAD-PER-REQUEST (Blocking OS Threads)
[ Request 1 ] ---> [ OS Thread 1 (1MB Stack) ] ---> [ Blocking JDBC / I/O ] (Idling CPU)
[ Request 2 ] ---> [ OS Thread 2 (1MB Stack) ] ---> [ Blocking HTTP Call ]  (Idling CPU)
[ Request N ] ---> [ OS Thread N (1MB Stack) ] ---> Out Of Memory / Context Switch Storm!

REACTIVE EVENT LOOP (Non-Blocking Multi-Reactor)
[ Request 1 ] \
[ Request 2 ] ---> [ Epoll / Netty Event Loop ] ---> Non-blocking Socket Multiplexing
[ Request N ] /     (Only 2x CPU Cores Threads)     (Zero Thread Idling, 100k+ Connections)
```

### The Limitations of Thread-Per-Request at Scale
1. **Memory Exhaustion:** Supporting 20,000 concurrent sockets requires 20GB of RAM purely allocated to OS thread call stacks, starving application heap memory.
2. **Context Switching Overhead:** When hundreds of OS threads wake up and block simultaneously, the CPU spends more time executing kernel context switches and invalidating CPU caches than executing business logic.
3. **Cascading Failure Under Latency Spikes:** If a downstream database or third-party service slows down from 20ms to 2,000ms, all upstream worker threads block waiting for I/O. Thread pools saturate rapidly, causing the entire service to reject incoming connections.

---

## 2. The Actor Model: Akka & Apache Pekko

Originating from Carl Hewitt's mathematical model (1973) and battle-tested by Erlang OTP in telecom infrastructure, the **Actor Model** replaces shared mutable state and lock-based synchronization with isolated, message-driven autonomous entities.

```text
[ Client Request ] 
       |
       | 1. Immutable Message ("tell")
       v
+--------------------------------------------------------+
|                      ACTOR                             |
|  +--------------------+                                |
|  |   Mailbox Queue    | ---> Processes 1 message       |
|  | [Msg 3][Msg 2][M1] |      at a time sequentially    |
|  +--------------------+                                |
|           |                                            |
|           v                                            |
|  +--------------------+                                |
|  |   Private State    | <--- Mutated without locks!    |
|  |  (Thread-Safe)     |                                |
|  +--------------------+                                |
+--------------------------------------------------------+
```

### Core Invariants of the Actor Model
- **Isolated State:** An actor's internal variables cannot be accessed or modified directly by external threads or other actors.
- **Sequential Message Processing:** An actor processes exactly one message from its mailbox at a time. Therefore, state mutations inside an actor are inherently thread-safe without needing `synchronized`, `volatile`, or `ReentrantLock`.
- **Asynchronous Message Passing:** Actors communicate strictly by sending immutable messages. The sender does not wait for the recipient to finish processing (`tell` is non-blocking).

### Akka Typed Implementation in Java

```java
public class BankAccountActor 
    extends AbstractBehavior<BankAccountActor.Command> {

    // Immutable Command interfaces and records
    public interface Command {}

    public record Deposit(BigDecimal amount) implements Command {}
    public record Withdraw(BigDecimal amount, ActorRef<StatusReply> replyTo) 
        implements Command {}
    public record GetBalance(ActorRef<BigDecimal> replyTo) implements Command {}
    public record StatusReply(boolean success, String reason) {}

    private BigDecimal balance = BigDecimal.ZERO;

    private BankAccountActor(ActorContext<Command> context) {
        super(context);
    }

    public static Behavior<Command> create() {
        return Behaviors.setup(BankAccountActor::new);
    }

    @Override
    public Receive<Command> createReceive() {
        return newReceiveBuilder()
            .onMessage(Deposit.class, this::onDeposit)
            .onMessage(Withdraw.class, this::onWithdraw)
            .onMessage(GetBalance.class, this::onGetBalance)
            .build();
    }

    private Behavior<Command> onDeposit(Deposit cmd) {
        this.balance = this.balance.add(cmd.amount());
        return this;
    }

    private Behavior<Command> onWithdraw(Withdraw cmd) {
        if (this.balance.compareTo(cmd.amount()) >= 0) {
            this.balance = this.balance.subtract(cmd.amount());
            cmd.replyTo().tell(new StatusReply(true, "Approved"));
        } else {
            cmd.replyTo().tell(new StatusReply(false, "Insufficient funds"));
        }
        return this;
    }

    private Behavior<Command> onGetBalance(GetBalance cmd) {
        cmd.replyTo().tell(this.balance);
        return this;
    }
}
```

### Supervision & Self-Healing ("Let It Crash")
In the Actor model, individual actors are never responsible for catching their own fatal errors. Instead, parent actors supervise child actors using declarative failure directives:

```text
           [ Supervisor (Parent) ]
                      |
             Supervision Strategy:
             (Restart / Resume / Stop / Escalate)
                      |
         +------------+------------+
         |                         |
         v                         v
[ Worker Actor A ]        [ Worker Actor B (Crashes!) ]
                            ==> Supervisor restarts Actor B
                                with fresh initial state!
```

- **Restart:** Recreates the failed actor with fresh initial state while preserving its mailbox.
- **Resume:** Ignores the exception and continues processing the next message in the mailbox.
- **Stop:** Terminates the child actor permanently.
- **Escalate:** Propagates the failure up to the parent's own supervisor.

### Cluster Sharding & Location Transparency
With Akka Cluster Sharding, actors represent stateful entities (such as active shopping carts or connected gaming sessions) distributed dynamically across a Kubernetes cluster. Messages are routed to an `ActorRef` transparently: whether the actor resides in the local JVM or on a pod across the datacenter, Akka handles the networking and routing automatically.

---

## 3. Eclipse Vert.x: The Multi-Reactor Engine

**Eclipse Vert.x** is an unopinionated, lightweight, event-driven toolkit built on top of Netty. Vert.x delivers ultra-high I/O throughput by leveraging the **Multi-Reactor Pattern**.

```text
                           +-------------------------------------+
                           |         Vert.x Multi-Reactor        |
[ Incoming Sockets ] ----->|  Event Loop Thread 1 (Core 0)       |
(100,000+ Connections)     |  Event Loop Thread 2 (Core 1)       |
                           |  Event Loop Thread 3 (Core 2)       |
                           |  Event Loop Thread 4 (Core 3)       |
                           +-------------------------------------+
                                              |
                   +--------------------------+--------------------------+
                   v                                                     v
          [ Non-blocking I/O ]                                  [ Blocking I/O Work ]
       (HTTP, WebSockets, Redis)                             (Legacy JDBC, Image Processing)
                   |                                                     |
            Executes directly                                   Offloaded via:
            on Event Loop Thread                                vertx.executeBlocking()
```

### The Golden Rule of Vert.x
> **Never block the event loop!**

Because each event loop thread manages thousands of active client sockets, executing a blocking call (such as `Thread.sleep()`, synchronous database queries, or heavy CPU cryptography) halts that event loop, freezing all concurrent requests assigned to that thread.

### Non-Blocking Verticle with Worker Offloading

```java
public class ApiGatewayVerticle extends AbstractVerticle {

    @Override
    public void start(Promise<Void> startPromise) {
        Router router = Router.router(vertx);

        // Non-blocking endpoint: runs entirely on the Event Loop
        router.get("/api/health").handler(ctx -> {
            ctx.response()
                .putHeader("content-type", "application/json")
                .end("{\"status\":\"UP\"}");
        });

        // Blocking workload: safely offloaded to dedicated worker pool
        router.post("/api/report").handler(ctx -> {
            vertx.executeBlocking(promise -> {
                // Synchronous CPU-heavy or legacy blocking operation
                String report = generateHeavyReportSync();
                promise.complete(report);
            }, false, res -> {
                if (res.succeeded()) {
                    ctx.response().end(res.result().toString());
                } else {
                    ctx.fail(res.cause());
                }
            });
        });

        vertx.createHttpServer()
            .requestHandler(router)
            .listen(8080)
            .<Void>mapEmpty()
            .onComplete(startPromise);
    }
}
```

### Clustered Event Bus
Vert.x includes an event bus that connects verticles across separate JVMs:
- **Point-to-Point:** Sends a message to a single receiver.
- **Publish / Subscribe:** Broadcasts events to all registered handlers.
- **Request / Response:** Asynchronously waits for a reply with a timeout.

---

## 4. Quarkus & SmallRye Mutiny: Cloud-Native Reactive

Modern cloud runtimes require instant container startup and tiny memory footprints for serverless (AWS Lambda, Google Cloud Run) and fast autoscaling. **Quarkus** combines reactive event-loops with build-time optimization and **SmallRye Mutiny**.

```java
@Path("/orders")
@Produces(MediaType.APPLICATION_JSON)
public class ReactiveOrderResource {

    @Inject
    PgPool client; // Non-blocking reactive PostgreSQL client

    @GET
    @Path("/{id}")
    public Uni<OrderDto> getOrder(@PathParam("id") Long id) {
        return client.preparedQuery("SELECT id, total FROM orders WHERE id = $1")
            .execute(Tuple.of(id))
            .onItem().transform(RowSet::iterator)
            .onItem().transform(iterator -> {
                if (!iterator.hasNext()) {
                    throw new NotFoundException("Order not found");
                }
                Row row = iterator.next();
                return new OrderDto(row.getLong("id"), row.getBigDecimal("total"));
            });
    }
}
```

- `Uni<T>`: Represents an asynchronous stream emitting either a single item or a failure (ideal for REST requests).
- `Multi<T>`: Represents a stream emitting 0 to $N$ items (ideal for Server-Sent Events, Kafka streams, and real-time feeds).

---

## 5. Modern Concurrency Paradigms Comparison

| Paradigm | Exemplar Toolkits | Thread Model | Memory per Connection | Programming Model |
| :--- | :--- | :--- | :--- | :--- |
| **Thread-per-Request** | Spring MVC, Tomcat | 1 OS Thread per request | $\approx 1\text{MB}$ (Stack) | Synchronous / Imperative |
| **Virtual Threads** | Java 21+ Project Loom | Lightweight virtual thread on carrier | $\approx 1\text{KB}$ (Heap) | Synchronous / Imperative |
| **Actor Model** | Akka / Apache Pekko | Small thread pool processing mailboxes| $\approx 300\text{ bytes}$ | Asynchronous Message-Driven |
| **Multi-Reactor** | Eclipse Vert.x, Netty | Event loop ($2 \times \text{Cores}$) | $\approx 500\text{ bytes}$ | Event-Driven Callbacks / Fluent |
| **Reactive Streams** | Project Reactor, Mutiny| Bounded elastic / Event loop | $\approx 1\text{KB}$ | Declarative Functional Pipelines |
