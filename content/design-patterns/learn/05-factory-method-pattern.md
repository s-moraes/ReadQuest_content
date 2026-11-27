# Factory Method Pattern

The **Factory Method** pattern defines an interface for creating an object, while letting **subclasses or concrete factories decide** which class to instantiate. It defers instantiation from the caller to a specialized creator method.

---

## 1. The Problem It Solves

Imagine a logistics app that starts with `Truck` deliveries. Over time, you add `Ship`, `Plane`, and `Drone`. If your core routing logic calls `new Truck()` directly, adding each new transport mode forces you to modify and retest core business code—violating the **Open/Closed Principle**.

---

## 2. Structure

```text
  [Creator]                         [Product <<interface>>]
  + createTransport() : Product     + deliver()
        ^                                   ^
        |                                   |
  +-----+-------------+             +-------+-------+
  |                   |             |               |
[RoadLogistics]  [SeaLogistics]  [Truck]          [Ship]
createTransport() createTransport()
  -> new Truck()    -> new Ship()
```

- **Product:** Common interface for all objects the factory produces.
- **Concrete Products:** Specific implementations (`Truck`, `Ship`).
- **Creator:** Declares the factory method returning `Product` and may contain shared workflow logic that uses `Product`.
- **Concrete Creators:** Override the factory method to return a specific `ConcreteProduct`.

---

## 3. Code Example

```java
public interface Transport {
    void deliver(String packageId);
}

public abstract class Logistics {
    public void dispatch(String packageId) {
        Transport transport = createTransport();
        transport.deliver(packageId);
    }

    protected abstract Transport createTransport();
}

public class SeaLogistics extends Logistics {
    @Override
    protected Transport createTransport() {
        return new CargoShip();
    }
}
```

Notice that `Logistics.dispatch(...)` works with **any** future `Transport` without ever knowing concrete classes like `CargoShip`.

---

## 4. Static Factory Method vs. GoF Factory Method

Do not confuse the two:
- **Static Factory Method** (e.g., `List.of(...)`, `LocalDate.parse(...)`): A static helper on a class that improves naming or caches instances, without polymorphism.
- **GoF Factory Method**: A polymorphic method (often overridden by subclasses or injected as a factory interface) that decouples caller code from concrete product types.

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Eliminates tight coupling to concrete classes | Adds extra subclasses or factory types |
| Respects Open/Closed & Single Responsibility | Can feel verbose for simple 2-branch cases |
| Easy to plug in new product types | |
