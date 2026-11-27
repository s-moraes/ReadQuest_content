# Observer Pattern

The **Observer** pattern defines a **one-to-many** subscription mechanism so that when one object (the **Subject**) changes state or publishes an event, all registered dependents (**Observers**) are notified automatically.

---

## 1. The Problem It Solves

When a customer pays an order, your system may need to email a receipt, reserve warehouse stock, update analytics, and award loyalty points. Hardcoding calls to all four services inside `PaymentService` violates Single Responsibility and forces you to edit billing code whenever a new downstream reaction is added.

---

## 2. Structure

```text
  [Subject (OrderEventBus)]
    - listeners : List<OrderListener>
    + subscribe(listener) : Subscription
    + publish(event)
           |
           +---> [EmailReceiptListener]
           +---> [AnalyticsListener]
           +---> [LoyaltyPointsListener]
```

---

## 3. Deep-Dive Java Example: Safe Event Bus + Unsubscribe

In production Java, an Observer bus should handle three real-world concerns:
1. **Thread-safe iteration** (`CopyOnWriteArrayList`) so subscribing/unsubscribing during `publish()` never throws `ConcurrentModificationException`.
2. **Easy unsubscription** (returning an `AutoCloseable` handle) to prevent **lapsed listener memory leaks**.
3. **Failure isolation** so one broken listener does not block the remaining listeners.

```java
public record OrderPaidEvent(String orderId, long amountCents) {}

@FunctionalInterface
public interface OrderListener {
    void onOrderPaid(OrderPaidEvent event);
}

public final class OrderEventBus {
    private final List<OrderListener> listeners =
        new CopyOnWriteArrayList<>();

    public AutoCloseable subscribe(OrderListener listener) {
        listeners.add(listener);
        return () -> listeners.remove(listener);
    }

    public void publish(OrderPaidEvent event) {
        for (OrderListener listener : listeners) {
            try {
                listener.onOrderPaid(event);
            } catch (RuntimeException ex) {
                // Log and isolate so other observers still run
                System.err.println("Listener failed: " + ex);
            }
        }
    }
}
```

Usage with automatic cleanup:

```java
OrderEventBus bus = new OrderEventBus();
try (AutoCloseable sub = bus.subscribe(
    e -> System.out.println("Receipt for " + e.orderId())
)) {
    bus.publish(new OrderPaidEvent("ORD-101", 4900));
} // automatically unsubscribed when scope exits
```

---

## 4. Synchronous vs. Asynchronous Observers in Java

- **Synchronous (In-Thread):** Simple and deterministic, but a slow observer blocks the publisher's thread.
- **Asynchronous (`Executor` / `Flow`):** Offloads notifications to background threads, improving latency, though you must handle retries and ordering.

### Real-World Java Examples
- **Spring `ApplicationEventPublisher` & `@EventListener`:** Plus `@TransactionalEventListener(phase = AFTER_COMMIT)` so emails only fire if the DB transaction commits.
- **`java.util.concurrent.Flow`:** Java 9+ Reactive Streams (`Publisher`, `Subscriber`, `Subscription`) with backpressure.

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Respects Open/Closed Principle for new reactions | Execution order among observers is usually unspecified |
| Dynamic runtime subscribe/unsubscribe | Forgotten subscriptions cause **lapsed listener** memory leaks |
| Cleanly decouples core domain from side effects | Deep event chains can be hard to trace in debugging |
