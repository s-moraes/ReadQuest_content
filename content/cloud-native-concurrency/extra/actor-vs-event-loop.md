# Actor Model vs Event Loop Under the Hood

When high-throughput systems process 100,000 requests per second, traditional thread-per-request architectures crumble under thread contention and OS scheduler overhead. Both **Akka (Actor Model)** and **Eclipse Vert.x (Multi-Reactor Event Loop)** solve this, but they adopt fundamentally different mechanical approaches under the hood.

---

## 1. Akka Actor Mechanics: Lock-Free Mailboxes

In Akka, actors are not bound to dedicated OS threads. Instead, actors are lightweight memory objects (~300 bytes of heap memory). Millions of actors can live concurrently inside a single JVM.

```text
[ Sender Thread ] ---> [ Concurrent Linked Mailbox ]
                             | (Lock-free enqueue)
                             v
                     [ Dispatcher / ForkJoinPool ]
                             | (Assigns worker thread)
                             v
                     [ Actor.receive() ]
```

### The Dispatcher & ForkJoinPool
When a message is sent via `actorRef.tell(msg)`:
1. The sender thread enqueues the message into the recipient actor's **Mailbox** using a lock-free, single-consumer/multi-producer queue (MPSC).
2. If the actor is not currently executing, the Akka **Dispatcher** schedules the actor on an available worker thread from a shared `ForkJoinPool`.
3. The assigned thread invokes `actor.receive()` to process a batch of messages sequentially.
4. Once finished or when its throughput quota is reached, the thread yields back to the pool, ready to execute another actor.

Because only one thread ever executes an actor at any given moment, the actor's state remains strictly isolated and thread-safe without locks.

---

## 2. Vert.x Mechanics: The Multi-Reactor Event Loop

Eclipse Vert.x relies on Netty and the operating system's native I/O multiplexing primitives (`epoll` on Linux, `kqueue` on macOS).

```text
               +--------------------------------------+
[ epoll / I/O ]|  Worker Loop Thread 1 (pinned to Core 1) |
[ Readiness   ]|  Worker Loop Thread 2 (pinned to Core 2) |
[ Notification]|  Worker Loop Thread N (pinned to Core N) |
               +--------------------------------------+
```

### The Event Loop Architecture
1. **Thread Allocation:** Vert.x starts a fixed number of event loop threads, defaulting to $2 \times \text{available CPU cores}$.
2. **Channel Registration:** When a new TCP connection connects, it is registered with one specific event loop thread for its entire lifecycle.
3. **Non-Blocking Execution:** All I/O events, read operations, and timer callbacks for that connection are executed directly on that thread's single-threaded run loop.
4. **Cache Locality:** Because connection state always executes on the same thread pinned to the same CPU core, Vert.x achieves optimal CPU L1/L2 cache locality and eliminates inter-core memory bus invalidations.

---

## Mechanical Comparison

| Dimension | Akka Actor Model | Vert.x Multi-Reactor Event Loop |
| :--- | :--- | :--- |
| **Fundamental Unit** | Autonomous Actor entity | Event Loop callback / Verticle |
| **Thread Association** | Actors dynamically borrow pool threads | Sockets statically bound to an Event Loop |
| **State Encapsulation** | Private mutable actor state | Stateful context or shared event bus |
| **Handling Blocking I/O**| Dedicated blocking dispatcher pool | Worker Verticles (`executeBlocking()`) |
| **Primary Sweet Spot** | Complex distributed stateful clusters | High-density I/O, proxies & gateways |
