# Choosing the Right Pattern & Avoiding Over-Engineering

Knowing all three GoF categories is only half the skill. The real engineering craft lies in diagnosing **which axis of change** your code is actually facing—and deciding whether a pattern is warranted at all.

---

## 1. The Axis-of-Change Diagnostic

When a module becomes hard to change, ask what kind of friction you are feeling:

```text
What is causing friction in your code?
  |
  +--> "Creating the right object is messy or hardcoded"
  |       ==> Look at CREATIONAL patterns
  |           (Factory Method, Builder, Abstract Factory)
  |
  +--> "Integrating, wrapping, or simplifying types is awkward"
  |       ==> Look at STRUCTURAL patterns
  |           (Adapter, Decorator, Facade, Proxy)
  |
  +--> "Algorithms, state transitions, or notifications are tangled"
          ==> Look at BEHAVIORAL patterns
              (Strategy, State, Observer, Command)
```

---

## 2. Quick Pattern Selector by Symptom

| Code Smell / Symptom | Category | Candidate Pattern |
| :--- | :--- | :--- |
| Telescoping constructors with 7+ optional parameters | Creational | **Builder** |
| `if/else` chain deciding which concrete class to `new` | Creational | **Factory Method** |
| Third-party SDK method signatures don't match yours | Structural | **Adapter** |
| Exploding subclasses (`LoggedCachedRetryService`) | Structural | **Decorator** |
| Callers must orchestrate 6 subsystem classes in order | Structural | **Facade** |
| `switch` on mode/type selecting how to compute a result | Behavioral | **Strategy** |
| Giant `if/else` checking lifecycle status (`DRAFT`, `PAID`) | Behavioral | **State** |
| Service manually calls 5 unrelated modules after an event | Behavioral | **Observer** |

---

## 3. Combining Categories in Real Systems

In production architectures, patterns rarely live in isolation. A single feature often uses one pattern from each category:

1. **Creational** builds the pipeline (e.g., a `Factory` selects the right `PaymentGateway`).
2. **Structural** adapts and hardens it (e.g., an `Adapter` normalizes the external API, and a `Proxy` or `Decorator` adds retry/metrics).
3. **Behavioral** executes the business logic (e.g., a `Strategy` picks the fraud-scoring rule, and an `Observer` emits an `OrderPaidEvent`).

---

## 4. Guardrails Against Over-Engineering

Before introducing a pattern, apply three checks:

1. **Rule of Three:** Wait until you have at least two or three concrete variations before abstracting into a Factory or Strategy.
2. **Readability Test:** If a teammate must jump through 5 files to understand a 10-line operation, simplify.
3. **Language Features First:** Modern languages replace several classic GoF patterns natively—for example, lambdas/functions often replace single-method *Strategy* or *Command* classes, and `enum` or `sealed` types simplify *State*.
