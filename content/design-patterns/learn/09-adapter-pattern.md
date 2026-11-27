# Adapter Pattern

The **Adapter** pattern converts the interface of an existing class into another interface that clients expect, allowing incompatible classes to work together without modifying their source code.

---

## 1. The Problem It Solves

Your application defines a clean `PaymentGateway` interface, but you need to integrate a third-party SDK (`LegacyPaySdk`) whose method names, parameter types, and return objects look completely different—and you cannot edit the SDK's code.

---

## 2. Structure (Object Adapter)

```text
  [Client] ---> [Target <<interface>>]
                  + charge(amountCents)
                          ^
                          |
                [LegacyPayAdapter] ---> [LegacyPaySdk]
                  charge(cents)           makePayment(dollars)
```

- **Target:** The interface your application code expects.
- **Adaptee:** The incompatible third-party or legacy class.
- **Adapter:** Implements `Target` and delegates calls to an instance of `Adaptee`, translating parameters and return values.

*(GoF also describes a **Class Adapter** using multiple inheritance, but modern languages favor **Object Adapter** via composition.)*

---

## 3. Code Example

```java
public interface PaymentGateway {
    Receipt charge(long amountCents, String currency);
}

public final class LegacyPayAdapter implements PaymentGateway {
    private final LegacyPaySdk sdk;

    public LegacyPayAdapter(LegacyPaySdk sdk) {
        this.sdk = sdk;
    }

    @Override
    public Receipt charge(long amountCents, String currency) {
        double dollars = amountCents / 100.0;
        String txId = sdk.makePayment(dollars, currency);
        return new Receipt(txId, amountCents);
    }
}
```

---

## 4. Adapter vs. Facade vs. Decorator

| Pattern | Intent |
| :--- | :--- |
| **Adapter** | Changes an interface to match what the client expects |
| **Decorator** | Keeps the same interface while adding behavior |
| **Facade** | Simplifies a complex subsystem into a new, smaller API |

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Isolates translation logic from business code | Adds an extra wrapper class per integration |
| Respects Open/Closed Principle | Can hide impedance mismatches (e.g., sync vs async) |
