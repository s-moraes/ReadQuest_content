# Facade Pattern

The **Facade** pattern provides a **simplified, unified interface** to a complex subsystem of classes, libraries, or frameworks.

---

## 1. The Problem It Solves

Converting a video or fulfilling an order in Java often requires coordinating multiple low-level services (`InventoryService`, `PaymentService`, `FraudDetector`, `ShippingService`, `AuditLog`) in a strict transactional sequence. If every REST controller or batch job orchestrates those 5 classes directly, business code becomes tightly coupled to subsystem internals.

---

## 2. Structure

```text
  [Controller] ---> [OrderFulfillmentFacade]
                      + fulfill(order)
                            |
          +-----------------+-----------------+
          v                 v                 v
  [InventoryService] [PaymentService] [ShippingService]
```

A Facade does **not** forbid advanced callers from using the subsystem directly—it simply offers a clean 80/20 entry point for common workflows.

---

## 3. Deep-Dive Java Example: Thin Coordinator

Here is a clean Java Facade using constructor injection and immutable records:

```java
public record FulfillmentResult(
    String orderId,
    String trackingCode
) {}

public final class OrderFulfillmentFacade {
    private final InventoryService inventory;
    private final FraudService fraud;
    private final PaymentService payments;
    private final ShippingService shipping;

    public OrderFulfillmentFacade(
        InventoryService inventory,
        FraudService fraud,
        PaymentService payments,
        ShippingService shipping
    ) {
        this.inventory = inventory;
        this.fraud = fraud;
        this.payments = payments;
        this.shipping = shipping;
    }

    public FulfillmentResult fulfill(Order order) {
        fraud.verify(order);
        inventory.reserve(order.items());
        try {
            payments.capture(order.id(), order.totalCents());
            String code = shipping.dispatch(order.address());
            return new FulfillmentResult(order.id(), code);
        } catch (RuntimeException ex) {
            inventory.release(order.items());
            throw ex;
        }
    }
}
```

Notice what the Facade does—and does **not** do:
- **Does:** Coordinates sequence, error rollback (`inventory.release`), and returns a clean DTO.
- **Does NOT:** Implement tax math, fraud heuristics, or SQL queries itself.

---

## 4. Avoiding the "God Object" Anti-Pattern

A common mistake in Java services is letting a Facade accumulate `if/else` business rules over time until it becomes a 2,000-line **God Object** with 15 constructor dependencies.

**Guardrails:**
1. Keep domain rules inside domain entities or specialized services, not the Facade.
2. Split oversized Facades by bounded context (e.g., `CheckoutFacade` vs `RefundFacade`).
3. Prefer constructor injection so growing dependency counts are immediately visible in tests.

---

## 5. Real-World Java Examples & Comparisons

- **Spring `JdbcTemplate`:** Acts as a Facade over verbose JDBC boilerplate (`Connection`, `PreparedStatement`, `ResultSet`, `SQLException` cleanup).
- **SLF4J `LoggerFactory`:** Simplifies binding and logger lookup across logging subsystems.

| Pattern | Intent |
| :--- | :--- |
| **Facade** | Defines a **new, simpler** interface over multiple subsystem classes |
| **Adapter** | Translates an **existing** interface into another expected interface |
| **Mediator** | Centralizes **peer-to-peer** communication among colleague objects |
