# Creational vs Structural vs Behavioral

The Gang of Four cataloged **23 classic design patterns** and grouped them into three fundamental categories based on **what kind of problem they solve**:

1. **Creational** — How objects are created.
2. **Structural** — How classes and objects are composed.
3. **Behavioral** — How objects communicate and share responsibilities.

```text
+-------------------------------------------------------------------+
|                   THE THREE GOF PATTERN CATEGORIES                |
+-----------------------+---------------------+---------------------+
|      CREATIONAL       |     STRUCTURAL      |     BEHAVIORAL      |
|  "How is it built?"   | "How is it wired?"  | "How does it act?"  |
+-----------------------+---------------------+---------------------+
| Decouples instantiation| Composes classes &  | Manages algorithms, |
| from usage            | objects into larger | state, & messaging  |
|                       | structures          | between objects     |
+-----------------------+---------------------+---------------------+
```

---

## 1. Creational Patterns

**Core Question:** *How do we instantiate objects without coupling client code to concrete classes or complex construction steps?*

Calling `new ConcreteClass()` directly throughout your codebase hardcodes dependencies. If construction requires multi-step validation, environment-specific variants, or resource pooling, Creational patterns encapsulate that logic.

### Common Creational Patterns
- **Singleton:** Ensures a class has only one instance and provides a global access point (use sparingly; prefer dependency injection).
- **Factory Method:** Defines an interface for creating an object, letting subclasses or factories decide which concrete class to instantiate.
- **Abstract Factory:** Produces families of related objects (e.g., `DarkButton` + `DarkCheckbox`) without specifying concrete classes.
- **Builder:** Constructs complex objects step-by-step, separating construction from final representation.
- **Prototype:** Creates new objects by cloning an existing instance when initialization from scratch is expensive.

```java
// Creational (Builder): clean, readable step-by-step creation
HttpRequest req = HttpRequest.builder()
    .method("POST")
    .url("https://api.example.com/orders")
    .timeoutMs(3000)
    .build();
```

---

## 2. Structural Patterns

**Core Question:** *How do we assemble classes and objects into larger, flexible structures while keeping interfaces clean and decoupled?*

Structural patterns use inheritance or composition to bridge incompatible interfaces, wrap objects with new capabilities, or simplify complex subsystems.

### Common Structural Patterns
- **Adapter:** Converts one interface into another that the client expects (like a power plug adapter).
- **Decorator:** Dynamically attaches additional responsibilities to an object by wrapping it, avoiding subclass explosion.
- **Facade:** Provides a simplified, unified interface to a complex subsystem of classes.
- **Proxy:** Acts as a placeholder or surrogate to control access, add lazy loading, caching, or security checks.
- **Composite:** Composes objects into tree structures so clients treat individual items and groups uniformly.
- **Bridge:** Splits an abstraction from its implementation so both can vary independently.
- **Flyweight:** Shares common immutable state across thousands of fine-grained objects to save memory.

```java
// Structural (Decorator): stacking capabilities via wrapping
DataSource source = new CompressionDecorator(
    new EncryptionDecorator(
        new FileDataSource("orders.dat")
    )
);
```

---

## 3. Behavioral Patterns

**Core Question:** *How do objects collaborate, distribute work, and react to events or state changes without tight coupling?*

Behavioral patterns focus on runtime communication, control flow, and encapsulating algorithms or requests as first-class objects.

### Common Behavioral Patterns
- **Strategy:** Defines a family of interchangeable algorithms and lets you swap them at runtime.
- **Observer:** Establishes a one-to-many subscription so dependent objects are notified automatically on state changes.
- **Command:** Encapsulates a request as an object, enabling queuing, logging, and undo/redo.
- **State:** Allows an object to alter its behavior when its internal state changes, replacing sprawling `switch` blocks.
- **Template Method:** Defines the skeleton of an algorithm in a base class, letting subclasses override specific steps.
- **Chain of Responsibility:** Passes a request along a chain of handlers until one handles it or all process it.
- **Iterator:** Provides sequential access to elements of a collection without exposing its underlying structure.
- **Mediator:** Centralizes complex many-to-many communication between objects into one coordinator.

```java
// Behavioral (Strategy): swapping behavior at runtime
ShippingCalculator calc = new ShippingCalculator(
    new ExpressAirStrategy()
);
BigDecimal cost = calc.calculate(order);
```

---

## 4. Side-by-Side Comparison

| Dimension | Creational | Structural | Behavioral |
| :--- | :--- | :--- | :--- |
| **Primary Focus** | Object instantiation | Object & class composition | Object interaction & flow |
| **Main Pain Solved** | Rigid `new` calls, complex setup | Incompatible APIs, rigid trees | Tangled conditionals, tight coupling |
| **Typical Mechanism** | Factories, builders, cloning | Wrappers, proxies, trees | Interfaces, callbacks, delegation |
| **Axis of Change** | *Which* concrete type is built | *How* types are connected | *What* action or rule runs |
| **Signature Examples** | Factory, Builder, Singleton | Adapter, Decorator, Facade | Strategy, Observer, State |

---

## 5. Class Scope vs. Object Scope

The GoF also classifies patterns along a second axis—**Scope**:

- **Class-scope patterns** rely on **inheritance** to bind relationships statically at compile time (e.g., *Factory Method*, *Template Method*, *Class Adapter*).
- **Object-scope patterns** rely on **composition** to bind relationships dynamically at runtime (e.g., *Abstract Factory*, *Decorator*, *Strategy*, *Observer*).

Most modern systems strongly favor **object-scope patterns** because runtime composition is easier to test, mock, and extend without fragile inheritance hierarchies.
