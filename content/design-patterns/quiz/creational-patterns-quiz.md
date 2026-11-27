## Q1
Why is the **Initialization-on-Demand Holder** (or `enum`) approach preferred over a naive `if (instance == null)` check when implementing a Java Singleton?

### Option A
It allows multiple instances to be created per thread automatically.

### Option B [CORRECT]
It guarantees thread-safe lazy initialization without paying synchronization lock overhead on every `getInstance()` call.

### Option C
It forces the Singleton to be serialized to disk on every access.

### Option D
It removes the need for a private constructor in any class.

### Explanation
A naive `if (instance == null)` check has a race condition where two threads can instantiate the Singleton simultaneously. The Holder idiom relies on JVM class-loading guarantees so the instance is created lazily and thread-safely without `synchronized` on `getInstance()`.

===

## Q2
How does **Abstract Factory** differ from **Factory Method**?

### Option A
Abstract Factory only creates immutable primitives, while Factory Method creates objects.

### Option B
Factory Method requires a global static registry, while Abstract Factory does not.

### Option C [CORRECT]
Factory Method typically creates a single product via subclassing, whereas Abstract Factory produces families of related, compatible products via composition.

### Option D
Abstract Factory is a Structural pattern, whereas Factory Method is a Creational pattern.

### Explanation
Both are Creational patterns. Factory Method focuses on deferring the instantiation of a single product to subclasses or a factory method, while Abstract Factory groups creation methods for an entire suite of related objects (e.g., `DarkButton` + `DarkCheckbox`) so they always match.

===

## Q3
Which problem is the **Builder** pattern specifically designed to solve?

### Option A
Cloning an expensive pre-populated object graph without knowing its concrete class.

### Option B
Guaranteeing that only one instance of a database connection pool exists.

### Option C
Converting an incompatible legacy class interface into a modern interface.

### Option D [CORRECT]
Constructing complex objects with many optional parameters step-by-step while keeping the final object immutable and valid.

### Explanation
Builder eliminates telescoping constructors (`new Foo(a, b, c, d, e, f)`) and avoids half-initialized mutable objects by collecting configuration fluently and validating invariants inside `build()`.

===

## Q4
When implementing the **Prototype** pattern, what bug occurs if you only perform a **shallow copy** on an object containing a mutable `List` or `Map`?

### Option A
The JVM throws a `StackOverflowError` immediately upon cloning.

### Option B [CORRECT]
The original object and the clone share the same nested collection reference, so mutating one silently corrupts the other.

### Option C
Primitive `int` and `boolean` fields fail to copy to the new instance.

### Option D
The clone automatically becomes a Singleton across the application.

### Explanation
A shallow copy copies object references rather than duplicating nested mutable structures. Modifying the clone's `List` or `Map` mutates the original object's collection too; a deep copy prevents this shared-state bug.

===

## Q5
In a logistics service, `Logistics.dispatch()` calls `createTransport()` to obtain a `Transport` interface without knowing whether it receives a `Truck` or `CargoShip`. Which pattern is this?

### Option A [CORRECT]
Factory Method

### Option B
Prototype

### Option C
Builder

### Option D
Singleton

### Explanation
Factory Method defines an interface or abstract method (`createTransport()`) for creating an object, letting concrete creator subclasses (`RoadLogistics`, `SeaLogistics`) decide which concrete `Transport` implementation to instantiate.

===

## Q6
Why do many modern Java engineers prefer Dependency Injection (DI) singleton scoping over hand-coding the classic `getInstance()` Singleton pattern?

### Option A
DI containers automatically convert Singletons into Prototype clones on every request.

### Option B
Hand-coded Singletons cannot be used in multi-threaded applications.

### Option C [CORRECT]
Hand-coded Singletons introduce hidden global dependencies that are difficult to mock or isolate in unit tests.

### Option D
DI containers forbid classes from having any private fields.

### Explanation
A static `getInstance()` call hardcodes a global dependency inside callers, making it hard to substitute a mock or fake during unit testing. With DI singleton scoping, the class remains a plain, testable object whose lifecycle is managed externally.

===

## Q7
What distinguishes a **Static Factory Method** (such as `LocalDate.parse(...)` or `List.of(...)`) from the **GoF Factory Method** pattern?

### Option A [CORRECT]
A Static Factory Method is a static helper without polymorphism, whereas the GoF Factory Method uses inheritance or a factory interface to decouple callers from concrete types.

### Option B
A Static Factory Method can only return `null`, whereas GoF Factory Method always throws exceptions.

### Option C
GoF Factory Method can only be used in C++, not in Java or Kotlin.

### Option D
Static Factory Methods require an Abstract Factory to compile.

### Explanation
Static factory methods improve readability, allow caching, or return subtypes, but they are static calls bound at compile time. The GoF Factory Method pattern relies on polymorphism (overriding or implementing a factory method) so core logic stays decoupled from concrete product classes.

===

## Q8
What is the primary drawback of the **Abstract Factory** pattern when requirements evolve?

### Option A
It cannot guarantee that products from the same family are compatible.

### Option B
It forces every product to be a Singleton.

### Option C [CORRECT]
Adding a new product type to the family requires modifying the Abstract Factory interface and every concrete factory implementation.

### Option D
It prevents clients from using dependency injection.

### Explanation
Abstract Factory makes it easy to swap entire product families (e.g., `LightThemeFactory` to `DarkThemeFactory`), but adding a brand-new product (e.g., `createTooltip()`) breaks the factory interface contract and requires updating all existing concrete factories.

===

## Q9
When designing a **Builder** for an object with both mandatory and optional fields, what is the cleanest way to enforce that mandatory fields are never omitted?

### Option A
Make all fields `public` and non-final so callers can set them later.

### Option B [CORRECT]
Pass mandatory fields into the `Builder` constructor (or static `builder(...)` method) and validate remaining invariants inside `build()`.

### Option C
Use a `Prototype` registry instead of a `Builder`.

### Option D
Silently replace missing mandatory fields with random values inside `toString()`.

### Explanation
Requiring mandatory parameters in `HttpRequest.builder(url)` gives compile-time safety that callers cannot forget them, while optional parameters remain fluent methods with sensible defaults and `build()` enforces cross-field invariants atomically.

===

## Q10
How does a **Prototype Registry** complement the **Prototype** pattern in real-world applications?

### Option A
It converts all Prototypes into immutable Singletons that cannot be modified.

### Option B
It automatically generates SQL migrations for cloned objects.

### Option C
It replaces `copy()` with reflection-based `new` calls on private constructors.

### Option D [CORRECT]
It stores pre-configured template instances in a lookup map so callers can fetch a template by key and clone it on demand.

### Explanation
A Prototype Registry acts as a catalog (e.g., `Map<String, Prototype>`) of ready-to-use, pre-initialized templates such as `"invoice-pdf"` or `"monthly-summary"`. Callers look up a template by name and clone it without knowing how it was originally constructed.

