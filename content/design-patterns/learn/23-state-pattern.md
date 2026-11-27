# State Pattern

The **State** pattern lets an object **alter its behavior when its internal state changes**, appearing as if the object changed its class. It replaces sprawling `switch`/`if` state-machine conditionals with dedicated state objects.

---

## 1. The Problem It Solves

An `Order` moves through `DRAFT`, `PAID`, `SHIPPED`, and `CANCELLED`. If `pay()`, `ship()`, and `cancel()` each contain a giant `switch (status)` block, adding a new state like `REFUNDED` forces edits across every method—and makes invalid transitions easy to miss.

---

## 2. Structure

```text
  [Order] ---> [OrderState <<sealed interface>>]
  - state      + pay() / ship() / cancel()
                      ^
          +-----------+-----------+-----------+
          |           |           |           |
     [DraftState] [PaidState] [ShippedState] [CancelledState]
```

Each state object defines **only** the transitions valid from that state and throws or rejects illegal ones.

---

## 3. Deep-Dive Java Example (Immutable State Transitions)

Using a Java `sealed interface` makes all valid states explicit at compile time:

```java
public sealed interface OrderState
    permits DraftState, PaidState, ShippedState, CancelledState {
    OrderState pay();
    OrderState ship();
    OrderState cancel();
}

public final class DraftState implements OrderState {
    @Override
    public OrderState pay() { return new PaidState(); }

    @Override
    public OrderState ship() {
        throw new IllegalStateException("Cannot ship unpaid order");
    }

    @Override
    public OrderState cancel() { return new CancelledState(); }
}

public final class PaidState implements OrderState {
    @Override
    public OrderState pay() {
        throw new IllegalStateException("Order is already paid");
    }

    @Override
    public OrderState ship() { return new ShippedState(); }

    @Override
    public OrderState cancel() { return new CancelledState(); }
}
```

The `Order` context delegates every action to its current state:

```java
public final class Order {
    private OrderState state = new DraftState();

    public void pay() { state = state.pay(); }
    public void ship() { state = state.ship(); }
    public void cancel() { state = state.cancel(); }
    public OrderState currentState() { return state; }
}
```

### Idiomatic Java Alternative: `enum` State Machine
When states hold **no per-instance fields**, a Java `enum` with abstract methods (`DRAFT { OrderState pay() { return PAID; } }`) gives you the State pattern with zero extra heap allocations!

---

## 4. State vs. Strategy

| Dimension | State | Strategy |
| :--- | :--- | :--- |
| **Intent** | Model lifecycle transitions & rules | Swap interchangeable algorithms |
| **Awareness** | States know about & transition to next states | Strategies are independent and unaware of each other |
| **Who Switches** | Context or state objects trigger transitions | Client usually picks and injects the strategy |

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Eliminates massive `switch` statements | Overkill for simple 2-state boolean flags |
| Isolates state-specific rules & guards | Increases class count when there are many states |
| Makes illegal transitions explicit and testable | |
