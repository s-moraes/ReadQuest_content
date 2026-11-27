## Q1
Which pattern passes an HTTP request through a sequence of independent filters (such as auth, rate limiting, and logging) where each filter can either short-circuit or forward to the next?

### Option A [CORRECT]
Chain of Responsibility

### Option B
Memento

### Option C
Visitor

### Option D
Flyweight

### Explanation
Chain of Responsibility links handlers sequentially (`FilterChain` in Jakarta Servlet / Spring Security). Each handler decides whether to reject/handle the request or delegate to `next`.

===

## Q2
Why does the **Command** pattern encapsulate a request as an object with `execute()` and `undo()` methods?

### Option A
To force all methods in a class to be `static`.

### Option B [CORRECT]
To decouple the invoker from the receiver and enable queuing, logging, retries, and undo/redo stacks.

### Option C
To clone objects without calling constructors.

### Option D
To replace `Iterable` in Java collections.

### Explanation
Turning an action into a first-class `Command` object lets invokers store, queue, schedule, or reverse operations without knowing the receiver's concrete methods.

===

## Q3
Which Java standard library feature is a classic example of the **Interpreter** pattern?

### Option A
`Collections.unmodifiableList(...)`

### Option B [CORRECT]
`java.util.regex.Pattern`

### Option C
`java.sql.DriverManager`

### Option D
`Runtime.getRuntime()`

### Explanation
Interpreter evaluates sentences in a small grammar or DSL using an AST. `java.util.regex.Pattern` parses regex grammar strings into an internal matcher tree to evaluate input text.

===

## Q4
In Java, why does the **Iterator** pattern store traversal state inside a separate `Iterator<T>` object rather than inside the collection itself?

### Option A
Because Java interfaces cannot declare fields.

### Option B [CORRECT]
So multiple callers can traverse the same collection concurrently at independent positions without exposing its internal structure.

### Option C
To convert a `List` into a Singleton.

### Option D
To avoid implementing `hasNext()` and `next()`.

### Explanation
Keeping the cursor inside `Iterator<T>` decouples traversal from the collection's underlying storage (array, tree, or paginated DB cursor) and allows simultaneous independent loops.

===

## Q5
Six UI components in a checkout screen currently hold direct references to each other, forming a tangled many-to-many web. Which pattern centralizes their coordination?

### Option A
Decorator

### Option B
Prototype

### Option C [CORRECT]
Mediator

### Option D
Template Method

### Explanation
Mediator eliminates $N \times (N-1)$ peer-to-peer dependencies by routing all component events through a single coordinator object.

===

## Q6
How does **Memento** support saving and restoring an object's state without violating encapsulation?

### Option A [CORRECT]
The Originator creates an opaque Snapshot/Memento that the Caretaker stores without inspecting or modifying its internal fields.

### Option B
The Caretaker reads all `private` fields via reflection and writes them to a `Map`.

### Option C
All fields on the Originator are declared `public static`.

### Option D
The Originator clones itself using a `Factory Method`.

### Explanation
Memento separates state capture (`Originator.save()`) from history management (`Caretaker`), keeping internal state private to the Originator.

===

## Q7
What is the "lapsed listener" memory leak risk in the **Observer** pattern?

### Option A
Observers execute in parallel on separate CPU cores automatically.

### Option B [CORRECT]
If an Observer is not unsubscribed when it is no longer needed, the Subject continues holding a strong reference to it, preventing garbage collection.

### Option C
`CopyOnWriteArrayList` deletes all listeners after the first event.

### Option D
Observers cannot receive immutable Java `record` events.

### Explanation
Because the Subject retains references to registered Observers, short-lived listeners that forget to unsubscribe remain reachable in memory and leak.

===

## Q8
How do **State** and **Strategy** differ in intent despite having similar class diagrams?

### Option A
State is Creational, while Strategy is Structural.

### Option B
Strategy can only be used with `enum` types.

### Option C [CORRECT]
State models lifecycle transitions where states often transition to one another, whereas Strategy swaps independent, mutually unaware algorithms.

### Option D
State uses `final` template methods, while Strategy uses `Proxy`.

### Explanation
In State, `DraftState` knows how to transition to `PaidState` based on lifecycle rules. In Strategy, `GroundStrategy` and `ExpressAirStrategy` are independent algorithms selected by the caller.

===

## Q9
In Java 8+, how can single-method **Strategy** implementations (such as `Comparator<T>` or `DiscountStrategy`) often be written without creating extra concrete classes?

### Option A
Using `volatile` fields

### Option B [CORRECT]
Using lambdas or method references implementing a `@FunctionalInterface`

### Option C
Using `Object.clone()`

### Option D
Using `final` abstract classes

### Explanation
A `@FunctionalInterface` with one abstract method can be instantiated inline with a Java lambda (e.g., `total -> (long) (total * 0.8)`), removing boilerplate Strategy classes.

===

## Q10
Why is the template method inside a **Template Method** base class (such as `ReportExporter.export(...)`) typically marked `final` in Java?

### Option A
So subclasses can reorder the algorithm steps freely.

### Option B
So the JVM converts the class into a `record`.

### Option C [CORRECT]
To prevent subclasses from overriding and breaking the invariant order of the algorithm's skeleton while still customizing hook steps.

### Option D
Because `abstract` classes cannot have non-final methods.

### Explanation
Template Method locks down the overall workflow sequence in the base class (`final`) while allowing subclasses to override specific `protected abstract` hook steps.

===

## Q11
What is the main trade-off of the **Visitor** pattern when your domain model evolves?

### Option A [CORRECT]
Adding new operations (Visitors) is easy, but adding a new Element subclass requires updating the Visitor interface and every Visitor implementation.

### Option B
Adding new Element subclasses is effortless, but adding a new Visitor requires editing every Element.

### Option C
Visitor cannot be used in Java without reflection.

### Option D
Visitor forces all elements to be mutable.

### Explanation
Visitor uses double dispatch (`element.accept(visitor)` -> `visitor.visit(this)`). It optimizes for adding new operations over a stable element hierarchy, at the cost of making new element types harder to add.

===

## Q12
How does control flow in **Chain of Responsibility** typically differ from **Decorator**?

### Option A [CORRECT]
In Chain of Responsibility, any handler can short-circuit and stop the chain immediately, whereas Decorators usually all execute around a single target.

### Option B
Chain of Responsibility uses inheritance exclusively, whereas Decorator never uses interfaces.

### Option C
Decorator can short-circuit requests, whereas Chain of Responsibility must always invoke every handler.

### Option D
Chain of Responsibility is a Creational pattern, whereas Decorator is Behavioral.

### Explanation
In a Chain of Responsibility (like an `AuthFilter` returning `401`), any handler may reject or handle the request and skip downstream filters. Decorators typically wrap one component and delegate through every layer.

===

## Q13
In a **Command** `CommandHistory` implementation with `undoStack` and `redoStack`, what should happen when a brand-new command is executed via `run(cmd)`?

### Option A
Both `undoStack` and `redoStack` should be cleared.

### Option B [CORRECT]
The command is pushed onto `undoStack` and `redoStack` is cleared, because the new action starts a new edit timeline.

### Option C
The command is pushed onto `redoStack` only.

### Option D
All previous commands are converted into `Memento` snapshots automatically.

### Explanation
Executing a new command after undoing earlier steps creates a new timeline branch; clearing `redoStack` prevents redoing stale future commands that no longer match the current state.

===

## Q14
What distinguishes a **fail-fast** Java `Iterator` (such as `ArrayList`) from a **fail-safe** (weakly consistent) `Iterator` (such as `CopyOnWriteArrayList`)?

### Option A
Fail-fast iterators are thread-safe without synchronization, while fail-safe iterators are single-threaded only.

### Option B
Fail-safe iterators throw `NoSuchElementException` on empty lists, while fail-fast iterators return `null`.

### Option C [CORRECT]
Fail-fast iterators detect structural modifications via `modCount` and throw `ConcurrentModificationException`, whereas fail-safe iterators iterate over a snapshot or concurrent segments without throwing.

### Option D
Fail-fast iterators cannot be used inside enhanced `for-each` loops.

### Explanation
`ArrayList` and `HashMap` iterators check a `modCount` counter and fail immediately with `ConcurrentModificationException` if mutated outside the iterator. `CopyOnWriteArrayList` iterates over an immutable array snapshot.

===

## Q15
In the **Memento** pattern, how does separating a **narrow** public interface (`DocumentMemento`) from a **wide** `private record Snapshot` preserve encapsulation in Java?

### Option A
It allows the `Caretaker` to edit `content` and `cursor` fields directly.

### Option B [CORRECT]
The `Caretaker` can store and pass `DocumentMemento` tokens without seeing or mutating the `Originator`'s private fields.

### Option C
It forces the JVM to serialize every snapshot to JSON on disk.

### Option D
It turns the `Originator` into a `Singleton`.

### Explanation
Because `Snapshot` is a `private` nested record inside `Document`, external classes like `BoundedHistory` only see the narrow `DocumentMemento` type and cannot inspect or corrupt internal state.

===

## Q16
Why is it good practice for an **Observer** event bus in Java to wrap each listener invocation in `try/catch` and return an `AutoCloseable` subscription handle?

### Option A
To convert synchronous observers into Creational factories automatically.

### Option B
To force `CopyOnWriteArrayList` to throw `ConcurrentModificationException`.

### Option C [CORRECT]
To isolate failures so one broken listener does not block other observers, and to make unsubscribing deterministic to avoid lapsed listener leaks.

### Option D
Because Java `@FunctionalInterface` listeners cannot throw checked or unchecked exceptions.

### Explanation
Without isolation, an exception in the first listener aborts `publish()` before remaining observers are notified. Returning an `AutoCloseable` handle encourages deterministic cleanup so short-lived observers do not leak memory.

