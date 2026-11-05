## Q1
How does the Java Platform Module System (JPMS) enforce hexagonal architecture boundaries more effectively than standard package conventions?

### Option A
JPMS automatically generates SQL database schemas for domain entities at compile time.

### Option B
JPMS converts all synchronous Java method calls into asynchronous reactive streams.

### Option C [CORRECT]
JPMS enforces compile-time and runtime modular encapsulation, completely blocking unexported packages and prohibiting cyclic module dependencies.

### Option D
JPMS requires all domain entities to be serialized into JSON format across modules.

### Explanation
JPMS provides strong encapsulation via `module-info.java`. Classes in unexported packages cannot be accessed even via reflection, and cyclic dependencies between modules cause immediate compilation failure, preventing architectural erosion.

===

## Q2
In a multi-module hexagonal Java project using JPMS, what should the `module-info.java` of the `domain` module declare?

### Option A
It must require `jakarta.persistence` and `jakarta.ws.rs`.

### Option B [CORRECT]
It exports its domain API packages and requires only `java.base`.

### Option C
It requires the `framework` module to enable automatic repository generation.

### Option D
It opens all packages for deep reflection by third-party testing libraries.

### Explanation
To preserve architectural purity, the `domain` module must depend on nothing outside the standard Java base library (`java.base`). It exports entity, value object, and specification packages so the application hexagon can consume them.

===

## Q3
How can an input adapter dynamically discover an output port implementation without hardcoding a dependency on a concrete database adapter?

### Option A
By using Java's native ServiceLoader mechanism combined with SPI `uses` and `provides` declarations. [CORRECT]

### Option B
By reading the database connection string from environment variables inside the domain entity.

### Option C
By creating an instance of the concrete adapter using the `new` keyword inside the input port.

### Option D
By merging the domain and framework packages into a single JAR file.

### Explanation
Java's Service Provider Interface (SPI) and `ServiceLoader.load(...)` enable runtime decoupling. The application module declares that it `uses` the output port interface, while the framework module declares that it `provides` the implementation, allowing dynamic discovery with zero direct coupling between adapters.
