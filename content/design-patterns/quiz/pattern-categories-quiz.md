## Q1
Which GoF design pattern category focuses on decoupling object instantiation from the client code that uses those objects?

### Option A [CORRECT]
Creational

### Option B
Structural

### Option C
Behavioral

### Option D
Architectural

### Explanation
Creational patterns (such as Factory Method, Abstract Factory, Builder, Prototype, and Singleton) abstract the instantiation process so systems are independent of how their objects are created, composed, and represented.

===

## Q2
You need to integrate a legacy third-party shipping SDK whose method names and parameter types do not match your application's `ShippingClient` interface. Which category and pattern best fit this problem?

### Option A
Creational — Builder

### Option B
Behavioral — Observer

### Option C [CORRECT]
Structural — Adapter

### Option D
Behavioral — Command

### Explanation
Structural patterns deal with how classes and objects are composed. The Adapter pattern converts the interface of an existing class into another interface that clients expect, allowing incompatible types to work together.

===

## Q3
An order processing class has a large `switch` statement that selects different tax calculation formulas based on the customer's country. Which category and pattern cleanly replaces this conditional logic?

### Option A
Creational — Singleton

### Option B
Structural — Facade

### Option C
Structural — Flyweight

### Option D [CORRECT]
Behavioral — Strategy

### Explanation
Behavioral patterns govern algorithms and responsibility assignment between objects. The Strategy pattern encapsulates each tax calculation algorithm behind a common interface so they can be swapped at runtime without modifying the order processor.

===

## Q4
What is the key difference between **Class-scope** patterns and **Object-scope** patterns in the Gang of Four taxonomy?

### Option A
Class-scope patterns only apply to Java, while Object-scope patterns only apply to C++.

### Option B [CORRECT]
Class-scope patterns use inheritance (static compile-time binding), whereas Object-scope patterns use composition (dynamic runtime binding).

### Option C
Class-scope patterns cannot be used in Behavioral patterns.

### Option D
Object-scope patterns require global static variables, while Class-scope patterns do not.

### Explanation
The GoF classifies patterns by Purpose (Creational, Structural, Behavioral) and by Scope (Class vs Object). Class-scope patterns rely on inheritance and are fixed at compile time, while Object-scope patterns use object composition and can be changed dynamically at runtime.

===

## Q5
Which symptom most strongly indicates that you should consider the **Decorator** pattern (Structural) rather than subclassing?

### Option A
You need to ensure only a single instance of a configuration loader exists in memory.

### Option B
You need to notify multiple unrelated subsystems whenever a user profile is updated.

### Option C [CORRECT]
You are facing a combinatorial explosion of subclasses to support combinations of features like logging, caching, and encryption.

### Option D
You want to clone an expensive pre-initialized object instead of building it from scratch.

### Explanation
Subclassing for every combination of optional features (e.g., `CachedLoggedEncryptedStream`) causes class explosion. Decorator (Structural) lets you wrap an object with stackable layers dynamically at runtime.
