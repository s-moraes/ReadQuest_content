## Q1
What is the primary difference between **Adapter** and **Decorator**?

### Option A [CORRECT]
Adapter converts an incompatible interface into one the client expects, whereas Decorator keeps the exact same interface while adding behavior.

### Option B
Adapter uses inheritance exclusively, whereas Decorator is a Creational pattern.

### Option C
Decorator hides an entire multi-class subsystem, whereas Adapter only caches method results.

### Option D
Adapter can only wrap Java interfaces, whereas Decorator only wraps primitive types.

### Explanation
Adapter bridges two incompatible interfaces by translating calls from Target to Adaptee. Decorator implements and wraps the same interface to stack additional responsibilities dynamically at runtime.

===

## Q2
You have 4 notification types (`Alert`, `Digest`, `Promo`, `Receipt`) and 3 delivery channels (`Email`, `Sms`, `Push`). Which pattern prevents an $M \times N$ explosion of 12 subclasses by separating these two dimensions?

### Option A
Composite

### Option B
Flyweight

### Option C [CORRECT]
Bridge

### Option D
Facade

### Explanation
Bridge splits an abstraction hierarchy (`Notification`) from its implementation hierarchy (`Channel`) and connects them via composition, reducing $M \times N$ subclasses down to $M + N$ classes.

===

## Q3
In an e-commerce catalog, a `BundleBox` can contain `SingleProduct` items as well as smaller nested `BundleBox` instances, and callers want to call `priceCents()` uniformly on any item. Which pattern fits best?

### Option A
Proxy

### Option B [CORRECT]
Composite

### Option C
Adapter

### Option D
Singleton

### Explanation
Composite arranges objects into tree structures so clients can treat individual leaves (`SingleProduct`) and recursive containers (`BundleBox`) through a single shared interface (`CatalogItem`).

===

## Q4
Which Java standard library API is a classic real-world example of the **Decorator** pattern?

### Option A
`Integer.valueOf(int)` caching small integers

### Option B
`java.sql.DriverManager`

### Option C [CORRECT]
`java.io` streams such as `new BufferedReader(new InputStreamReader(in))`

### Option D
`Runtime.getRuntime()`

### Explanation
`java.io` wrappers (`BufferedReader`, `GZIPOutputStream`, `DataInputStream`) implement the same base stream abstraction and wrap another stream to layer buffering, compression, or formatting dynamically.

===

## Q5
A controller currently orchestrates `InventoryService`, `PaymentService`, `FraudChecker`, and `ShippingService` in a strict sequence. Which pattern provides a single, simplified entry point for callers?

### Option A
Bridge

### Option B
Flyweight

### Option C
Prototype

### Option D [CORRECT]
Facade

### Explanation
Facade defines a simplified, unified interface (`OrderFulfillmentFacade.fulfill(order)`) over a complex multi-class subsystem, decoupling high-level callers from low-level orchestration details.

===

## Q6
In the **Flyweight** pattern, how is object state divided to save memory across hundreds of thousands of instances?

### Option A [CORRECT]
Shared, immutable intrinsic state is stored in cached Flyweights, while unique extrinsic state is passed in or kept per instance.

### Option B
All mutable fields are moved into static global variables.

### Option C
Objects are serialized to temporary files on disk between method calls.

### Option D
Every instance is wrapped in a dynamic Proxy that compresses fields.

### Explanation
Flyweight eliminates duplicate heavy data (such as 3D meshes or textures) by sharing immutable intrinsic state across instances while keeping lightweight, context-specific extrinsic state (such as `(x, y)` coordinates) separate.

===

## Q7
Which **Proxy** variant delays the creation of an expensive object until the client actually invokes a method on it?

### Option A
Protection Proxy

### Option B
Remote Proxy

### Option C [CORRECT]
Virtual Proxy

### Option D
Logging Proxy

### Explanation
A Virtual Proxy acts as a lightweight placeholder for a resource-heavy object, deferring its instantiation (lazy initialization) until the first real operation is requested.

===

## Q8
What distinguishes **Bridge** from **Adapter** in terms of design timing and intent?

### Option A
Bridge can only be used with databases, whereas Adapter is only for UI code.

### Option B [CORRECT]
Adapter is applied retroactively to make incompatible existing classes work together, whereas Bridge is designed up front so two independent hierarchies can evolve separately.

### Option C
Bridge converts one interface into another via static methods, whereas Adapter requires a tree structure.

### Option D
Adapter is a Behavioral pattern, whereas Bridge is a Creational pattern.

### Explanation
Both are Structural patterns. Adapter is a fix applied after classes already exist with mismatched interfaces. Bridge is a proactive architectural split between Abstraction and Implementation so both dimensions vary independently.

===

## Q9
When stacking multiple **Decorator** wrappers (such as compression and encryption on a stream), what important caveat must you keep in mind?

### Option A
Decorators cannot wrap other Decorators—only one layer is allowed.

### Option B
Java's compiler automatically reorders Decorators alphabetically.

### Option C [CORRECT]
The order of wrapping matters (e.g., compress before encrypting), and removing a specific middle wrapper at runtime is awkward.

### Option D
Every Decorator converts the wrapped object into a Singleton.

### Explanation
Because Decorators form a linked chain of wrappers, order directly affects behavior (encrypted data is high-entropy and barely compresses, so compression must wrap inside encryption). Also, clients hold the outermost wrapper, making middle-layer removal difficult.

===

## Q10
What is the main architectural risk to watch out for when introducing a **Facade**?

### Option A
The Facade forces every caller to implement all subsystem interfaces manually.

### Option B
The Facade automatically deletes the underlying subsystem classes at compile time.

### Option C [CORRECT]
The Facade can grow into a "God Object" coupled to too many classes if it absorbs business logic instead of remaining a thin coordinator.

### Option D
Facades prevent unit testing because they cannot accept constructor dependencies.

### Explanation
A Facade should stay a thin orchestration entry point over a subsystem. If developers keep adding conditional rules and domain logic directly into the Facade, it becomes a monolithic God Object.

===

## Q11
**Proxy** and **Decorator** both wrap an object that implements the same interface. How do their intents differ?

### Option A
Proxy uses inheritance, whereas Decorator can never use interfaces.

### Option B [CORRECT]
Decorator lets clients compose and stack extra behaviors dynamically, whereas Proxy transparently controls access or lifecycle for a target object.

### Option C
Decorator only works for remote network calls, whereas Proxy only works for file I/O.

### Option D
Proxy always mutates the wrapped object's source code at compile time.

### Explanation
While structurally similar, Decorator is about letting callers layer additional responsibilities in any combination. Proxy is about acting as a stand-in to control access, caching, permissions, or lazy initialization—often managing the real object's lifecycle itself.

===

## Q12
What is a common trade-off of using the **Composite** pattern for tree hierarchies?

### Option A
Clients must always write explicit `instanceof` checks for every node in the tree.

### Option B
Leaves can never hold primitive fields like `price` or `name`.

### Option C [CORRECT]
It is harder to restrict which child component types a composite can contain at compile time without runtime checks.

### Option D
Composite trees cannot be traversed recursively.

### Explanation
Because Composite treats leaves and containers through a single uniform interface, restricting a specific container to only accept certain leaf types (or preventing cycles) often requires runtime validation rather than purely static type checks.

