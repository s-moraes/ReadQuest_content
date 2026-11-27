## Q1
In a Java backend interview, you are asked to implement a thread-safe lazy **Singleton** without using `synchronized` on `getInstance()`. Which approach is safest and why?

### Option A
Checking `if (instance == null)` without any synchronization or `volatile` keyword.

### Option B [CORRECT]
Using the Initialization-on-Demand Holder idiom (static inner class) or a single-element `enum`, because JVM class loading guarantees thread-safe initialization.

### Option C
Making the constructor `public` so callers can cache the instance themselves.

### Option D
Cloning a `Prototype` inside `finalize()`.

### Explanation
Without synchronization or `volatile`, double-checked locking can expose a partially constructed object due to instruction reordering. The static Holder idiom (Bill Pugh) and `enum` Singletons rely on JVM class-initialization locks, providing thread safety with zero per-call locking overhead.

===

## Q2
An interviewer asks: "When would you choose **Abstract Factory** over **Factory Method**?" What is the clearest answer?

### Option A
When you only need to instantiate a single concrete class with no variants.

### Option B
When you want to clone an existing object instead of calling `new`.

### Option C [CORRECT]
When you must guarantee that an entire family of related objects (such as `DarkButton` and `DarkCheckbox`) are created together and remain compatible.

### Option D
When you want to convert a legacy third-party interface into a new one.

### Explanation
Factory Method defers instantiation of a single product type, whereas Abstract Factory groups multiple creation methods into one factory interface so callers always receive matching products from the same family.

===

## Q3
Why do interviewers prefer the **Builder** pattern over JavaBeans-style setters (`obj.setX(...)`) for complex domain objects?

### Option A
Setters cannot be called more than once in Java.

### Option B [CORRECT]
Builder keeps the target object immutable and validates all invariants atomically inside `build()`, preventing half-initialized invalid states.

### Option C
Builder eliminates the need for any classes or constructors.

### Option D
Setters automatically trigger `ConcurrentModificationException` on single threads.

### Explanation
JavaBeans setters leave an object mutable and potentially inconsistent between setter calls. A Builder collects all required and optional values first, checks cross-field invariants in `build()`, and returns a fully valid, immutable object.

===

## Q4
A classic interview question: "**Strategy** and **State** have almost identical UML diagrams. How do you explain the difference?"

### Option A
Strategy is Structural and State is Creational.

### Option B
Strategy can only be used with `enum`, while State requires `Proxy`.

### Option C [CORRECT]
Strategy swaps independent algorithms chosen by the caller, whereas State models lifecycle rules where states often know about and transition to the next state.

### Option D
State cannot throw exceptions on invalid operations, whereas Strategy always throws.

### Explanation
Although both delegate work to an interface reference, Strategy implementations are mutually unaware and interchangeable, while State objects represent lifecycle phases that enforce valid transitions (e.g., `DraftState` -> `PaidState`).

===

## Q5
In a system design interview, you need to wrap a third-party SDK whose method signatures do not match your domain port. Which pattern applies, and why not **Facade**?

### Option A
Decorator, because it changes the interface completely.

### Option B [CORRECT]
Adapter, because Adapter translates an existing interface to match an expected target interface, whereas Facade defines a brand-new simplified API over a subsystem.

### Option C
Proxy, because Proxy always translates incompatible parameter types.

### Option D
Flyweight, because it shares immutable SDK instances.

### Explanation
Adapter is specifically about interface compatibility (1-to-1 translation to your existing port interface). Facade is about simplifying a complex multi-class subsystem behind a new convenience API.

===

## Q6
In a Spring Boot interview: "Why does calling `this.processPayment()` from another method in the same `@Service` class ignore `@Transactional` or `@Cacheable`?"

### Option A
Because Spring disables proxies on classes that implement interfaces.

### Option B
Because `@Transactional` only works on `private static` methods.

### Option C [CORRECT]
Because Spring AOP wraps the bean in a **Proxy**; internal `this.method()` calls bypass the proxy and invoke the raw target object directly.

### Option D
Because `@Cacheable` uses the Interpreter pattern instead of Proxy.

### Explanation
This is the classic Java **self-invocation pitfall** of the Proxy pattern. External callers invoke the Spring Proxy (which starts a transaction or checks the cache), whereas `this.processPayment()` jumps directly inside the target instance, skipping proxy interception.

===

## Q7
If you stack a `GzipCompressionDecorator` and an `EncryptionDecorator` around a `DataSource`, which order should you choose and why?

### Option A
Encrypt first, then compress, because encrypted bytes contain more repeated patterns.

### Option B [CORRECT]
Compress first (inner), then encrypt (outer), because encrypted data has high entropy and barely compresses.

### Option C
Order never matters when stacking Decorators.

### Option D
Use Singleton instead so only one Decorator runs at a time.

### Explanation
Decorator order directly affects behavior. Plaintext has structural redundancy that GZIP compresses well; ciphertext looks like random noise and cannot be compressed effectively.

===

## Q8
What memory-leak bug can happen when using the **Observer** pattern in a long-running Java service, and how do you prevent it?

### Option A
StackOverflowError from `CopyOnWriteArrayList` sorting listeners.

### Option B [CORRECT]
The "lapsed listener" leak: the Subject keeps strong references to short-lived Observers unless they explicitly unsubscribe (e.g., via an `AutoCloseable` handle).

### Option C
Observers automatically delete the Subject after one event.

### Option D
JVM garbage collection destroys the Subject while Observers are still running.

### Explanation
Because the Subject holds a list of registered Observers, any short-lived listener (like a UI screen or per-request handler) that forgets to unsubscribe stays reachable in memory and cannot be garbage-collected.

===

## Q9
Why does the Gang of Four emphasize **"favor object composition over class inheritance"** across patterns like **Bridge**, **Decorator**, and **Strategy**?

### Option A
Because Java does not support `extends` on concrete classes.

### Option B
Because inheritance is slower at runtime than network I/O.

### Option C [CORRECT]
Inheritance binds behavior statically at compile time and causes class explosion when dimensions combine, whereas composition lets you swap and combine behaviors at runtime.

### Option D
Because composition removes the need for interfaces.

### Explanation
Combining $M$ notification types with $N$ delivery channels via inheritance creates $M \times N$ rigid subclasses. Composition (Bridge/Strategy/Decorator) keeps hierarchies separate ($M + N$) and allows runtime swapping and easy unit mocking.

===

## Q10
An interviewer asks: "When should you **avoid** applying a GoF design pattern?" What is the strongest senior-level answer?

### Option A
Never—every class in a production codebase should implement at least two patterns.

### Option B [CORRECT]
When there is only one implementation and no concrete axis of change yet, or when a modern language feature (like a lambda or `record`) solves it more simply.

### Option C
Only when writing unit tests, because patterns cannot be tested.

### Option D
Whenever the project uses Java 17 or newer, because all patterns are deprecated.

### Explanation
Premature abstraction ("patternitis") adds indirection and boilerplate without real flexibility. Follow the Rule of Three and YAGNI: start simple, leverage modern language features (lambdas for single-method Strategy, `enum` for simple State), and refactor toward a pattern when real variation emerges.

===

## Q11
An interviewer asks: "Compare **Template Method** and **Strategy**. Which one would you prefer in modern Java and why?"

### Option A
Template Method uses composition and Strategy uses inheritance, so Template Method is always more flexible.

### Option B [CORRECT]
Template Method uses inheritance to customize steps of a fixed skeleton, whereas Strategy uses composition (and often lambdas) to swap whole algorithms at runtime, making Strategy easier to test and combine.

### Option C
Template Method can only be used in Creational factories.

### Option D
Strategy requires `abstract` base classes with `final` methods.

### Explanation
Template Method locks the outer algorithm in a `final` base method and relies on subclassing (`protected abstract` hooks). Strategy uses composition via an interface (or `@FunctionalInterface` lambda), avoiding rigid inheritance hierarchies.

===

## Q12
In a Java interview, why do senior engineers warn against relying on `Object.clone()` and `Cloneable` when implementing the **Prototype** pattern?

### Option A
`Object.clone()` is a compile-time error in Java 17+.

### Option B
`Cloneable` automatically deep-copies all nested `List` and `Map` fields.

### Option C [CORRECT]
`Object.clone()` performs a shallow copy by default, skips constructors, and has awkward checked-exception (`CloneNotSupportedException`) ergonomics; a copy constructor or explicit `copy()` method is safer.

### Option D
`Object.clone()` converts the cloned object into a `Singleton`.

### Explanation
Java's `Cloneable` is a marker interface with well-known design flaws: it does a field-by-field shallow copy (sharing mutable nested collections) and bypasses constructors. Writing an explicit `copy()` method or copy constructor lets you enforce deep copies cleanly.

===

## Q13
How does the **Flyweight** pattern explain `Integer.valueOf(42) == Integer.valueOf(42)` being `true` in Java, while `Integer.valueOf(500) == Integer.valueOf(500)` is `false`?

### Option A
Java uses the `Builder` pattern for numbers above 127.

### Option B [CORRECT]
`Integer.valueOf` acts as a Flyweight factory caching immutable `Integer` instances in the `-128..127` range, returning the same shared object reference for small values.

### Option C
Numbers above 127 are stored in a `Proxy` that always returns `false` on `==`.

### Option D
`Integer` is a `Singleton` whose value changes at runtime.

### Explanation
Flyweight shares immutable intrinsic state to save memory. The JDK caches commonly used `Integer` objects (`-128` to `127`), so `valueOf(42)` returns the exact same cached instance, whereas `500` allocates distinct objects.

===

## Q14
Both **Mediator** and **Observer** reduce direct coupling between objects. In an interview, how do you distinguish when to use each?

### Option A
Observer is for synchronous UI dialogs, while Mediator is only for distributed message brokers.

### Option B
Mediator broadcasts events to unknown subscribers, while Observer enforces peer-to-peer references.

### Option C [CORRECT]
Use **Observer** for one-to-many broadcasts where independent listeners react to events; use **Mediator** to centralize bidirectional coordination rules among a known group of peers.

### Option D
Observer requires inheritance, while Mediator cannot use interfaces.

### Explanation
In Observer, the publisher does not know or care who subscribes or how they coordinate. In Mediator, a central coordinator explicitly orchestrates interactions among named colleagues (e.g., enabling `SubmitButton` only when both `TermsCheckbox` and `AgeCheckbox` are checked).

===

## Q15
In a Java 21+ interview: "What is the main trade-off of the **Visitor** pattern, and how do `sealed` interfaces + pattern matching `switch` affect it?"

### Option A
Visitor makes adding new element subclasses easy, while `sealed` interfaces forbid `switch` statements.

### Option B [CORRECT]
Classic Visitor makes adding new operations easy but adding new element types hard; `sealed` interfaces with exhaustive pattern-matching `switch` achieve similar type safety without double-dispatch boilerplate.

### Option C
`sealed` interfaces turn Visitor into an `Abstract Factory`.

### Option D
Visitor requires every element class to be `final` with no fields.

### Explanation
Visitor optimizes for adding new operations over a stable element hierarchy, at the cost of updating every `Visitor` when a new element is added. Java 21's `sealed` hierarchies + pattern matching `switch` give compile-time exhaustiveness checks directly, reducing double-dispatch boilerplate.

