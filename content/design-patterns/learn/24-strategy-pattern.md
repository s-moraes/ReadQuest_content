# Strategy Pattern

The **Strategy** pattern defines a **family of interchangeable algorithms**, encapsulates each one in its own class or function, and makes them swappable at runtime.

---

## 1. The Problem It Solves

A `ShippingCalculator` needs to support Standard Ground, Express Air, Same-Day Courier, and Partner Pickup. Embedding all formulas inside one `calculate(order, mode)` method with `if/else` branches violates Single Responsibility and grows harder to test with every new carrier.

---

## 2. Structure

```text
  [ShippingCalculator] ---> [ShippingStrategy <<interface>>]
  - strategy                  + costCents(order) : long
                                       ^
                          +------------+------------+
                          |                         |
                 [GroundStrategy]          [ExpressAirStrategy]
```

---

## 3. Java Example (Interfaces & Lambdas)

```java
@FunctionalInterface
public interface DiscountStrategy {
    long apply(long totalCents);
}

public final class PricingService {
    public long finalPrice(long totalCents, DiscountStrategy rule) {
        return rule.apply(totalCents);
    }
}
```

In Java 8+, single-method strategies can be classes **or** concise lambdas:

```java
PricingService pricing = new PricingService();
long vipTotal = pricing.finalPrice(10_000, total -> (long) (total * 0.8));
long flatTotal = pricing.finalPrice(10_000, total -> total - 1500);
```

### Real-World Java Examples
- **`java.util.Comparator<T>`:** Passed to `List.sort(comparator)` to swap sorting algorithms dynamically.
- **Spring Security `AuthenticationProvider`:** Pluggable strategies for JWT, LDAP, or OAuth2 authentication.

---

## 4. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Swaps algorithms cleanly at runtime | Callers must know which strategy to select |
| Isolates each algorithm for easy unit testing | Extra interfaces/classes if you only have 1–2 fixed rules |
