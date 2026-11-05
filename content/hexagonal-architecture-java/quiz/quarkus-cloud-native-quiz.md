## Q1
What is the primary role of the `bootstrap` module in a cloud-native hexagonal application using Quarkus?

### Option A
To compile domain entities directly into database stored procedures.

### Option B [CORRECT]
To act as the application aggregation root, configuring Quarkus CDI dependencies and wiring ports and adapters together.

### Option C
To run automated security penetrations against the Kubernetes cluster.

### Option D
To replace all HTTP REST endpoints with GraphQL queries.

### Explanation
The `bootstrap` module groups together the domain, application, and framework modules. It contains application configuration (`application.properties`), the Quarkus main entry point, and CDI producers that wire input ports to output adapters without polluting the core modules.

===

## Q2
When building reactive adapters with Quarkus (RESTEasy Reactive and Hibernate Reactive), where should reactive streaming types like `Uni<T>` or `Multi<T>` be positioned?

### Option A
Deeply integrated within domain entity methods and specification validators.

### Option B
Only inside the database schema migration scripts.

### Option C [CORRECT]
Confined to the framework adapters and application port boundaries, keeping domain entity logic synchronous and pure.

### Option D
Exclusively in the Kubernetes deployment YAML file.

### Explanation
To prevent reactive library lock-in and keep business logic maintainable, reactive primitives (`Uni<T>`, `Multi<T>`) should handle async I/O in adapters and ports. Domain entities remain synchronous, pure Java POJOs that operate on resolved domain models.

===

## Q3
What operational benefit does Ahead-Of-Time (AOT) compilation with GraalVM provide for a Quarkus hexagonal microservice?

### Option A
It eliminates the need for unit tests and integration tests.

### Option B [CORRECT]
Sub-50 millisecond startup times and significantly lower resident memory footprint (RSS) compared to traditional JVM execution.

### Option C
Automatic horizontal database sharding across multiple cloud providers.

### Option D
The ability to modify bytecode dynamically at runtime via hot-swapping.

### Explanation
GraalVM native compilation creates an OS-specific executable binary that bypasses JVM JIT warmup, yielding near-instantaneous startup (tens of milliseconds) and minimal memory consumption (sub-50MB), which is ideal for serverless and rapidly autoscaling containers.

===

## Q4
Which of the following is considered a severe anti-pattern in Hexagonal Architecture?

### Option A
Writing unit tests for domain entities without spinning up a database container.

### Option B
Attaching both a REST adapter and a CLI adapter to the same use case input port.

### Option C
Using value objects to encapsulate and validate IP addresses and entity identifiers.

### Option D [CORRECT]
Having a driving REST adapter bypass the application use case to query the database repository adapter directly.

### Explanation
The "Adapter Bypass" anti-pattern violates hexagonal isolation by allowing driving adapters to invoke driven adapters directly. This circumvents domain business rules, validation invariants, and orchestrating use cases, leading back to tangled spaghetti code.
