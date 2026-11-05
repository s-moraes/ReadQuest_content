## Q1
In Hexagonal Architecture, which of the three hexagons contains pure business logic with zero dependencies on third-party frameworks or database drivers?

### Option A
The Framework Hexagon

### Option B
The Application Hexagon

### Option C [CORRECT]
The Domain Hexagon

### Option D
The Bootstrap Hexagon

### Explanation
The Domain Hexagon represents the core of the application. It contains pure Java POJOs (Entities, Value Objects, Specifications, and Domain Services) with zero dependencies on external frameworks or databases.

===

## Q2
What distinguishes an Input Port from an Output Port in the Application Hexagon?

### Option A
Input ports are always abstract interfaces, whereas output ports are concrete classes.

### Option B [CORRECT]
Input ports implement Use Case interfaces to handle incoming requests, while output ports are interfaces defining required external capabilities like persistence.

### Option C
Input ports connect directly to databases, whereas output ports connect to REST controllers.

### Option D
Input ports are managed by Quarkus CDI, while output ports can only be wired with Spring.

### Explanation
An Input Port is a concrete class in the Application Hexagon that implements a Use Case interface (handling driving operations). An Output Port is an interface in the Application Hexagon that abstracts external systems (such as databases or message queues) to be implemented by driven adapters in the Framework Hexagon.

===

## Q3
Why does Hexagonal Architecture categorize external interactions into "Driving" and "Driven" operations?

### Option A
To differentiate between read-only database queries and write operations.

### Option B
To separate frontend mobile clients from desktop web browser clients.

### Option C [CORRECT]
To distinguish between external actors that initiate application workflows (Driving) and external systems that the application invokes to fulfill a workflow (Driven).

### Option D
To determine whether an operation executes on CPU threads or GPU cores.

### Explanation
Driving (Primary) operations are initiated by external actors (e.g. HTTP clients, CLI users, test agents) through input adapters. Driven (Secondary) operations are triggered by the application itself towards external resources (e.g. databases, event brokers, external APIs) through output adapters.

===

## Q4
How does the Specification Pattern contribute to maintaining clean domain entities?

### Option A
It generates database schema DDL migrations automatically at application startup.

### Option B [CORRECT]
It encapsulates business rules into reusable predicate objects that can be combined with boolean logic without polluting entities.

### Option C
It exposes domain entities directly over HTTP as REST endpoints.

### Option D
It injects JPA EntityManager instances directly into entity constructors.

### Explanation
The Specification Pattern encapsulates individual business validation rules into composable classes implementing `isSatisfiedBy(T candidate)` and boolean operations (`and`, `or`, `not`), preventing domain entities from becoming bloated with complex procedural rule algorithms.
