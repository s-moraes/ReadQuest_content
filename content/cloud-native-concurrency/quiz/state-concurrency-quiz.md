## Q1
Why is stateless microservice design preferred for cloud-native applications?

### Option A
It allows services to retain client sessions in JVM heap memory indefinitely.

### Option B [CORRECT]
It allows any instance to handle any request, enabling dynamic auto-scaling and seamless failover.

### Option C
It replaces the database layer entirely with local in-memory storage.

### Option D
It enforces strict Two-Phase Commit transactions across all microservice boundaries.

### Explanation
Stateless microservices do not store client context between requests. This allows load balancers to distribute traffic across instances arbitrarily and spin up or tear down pods without losing session state or requiring complex session migration.

===

## Q2
In a JPA/Hibernate application using optimistic locking with `@Version`, what occurs when two concurrent transactions attempt to commit conflicting updates to the same entity?

### Option A
The database automatically holds a pessimistic row lock until both transactions commit.

### Option B
The second transaction silently overwrites the changes made by the first transaction.

### Option C [CORRECT]
The second transaction detects a version mismatch and throws an `OptimisticLockException`.

### Option D
Both transactions are canceled and their database connections are permanently closed.

### Explanation
Optimistic locking includes the current version in the SQL `UPDATE ... WHERE id = ? AND version = ?`. If another transaction has already updated the row and bumped the version, the second query affects zero rows, triggering an `OptimisticLockException`.

===

## Q3
Why is Java's native `synchronized` keyword or `ReentrantLock` insufficient to prevent race conditions across cloud microservices?

### Option A
Java locking primitives only synchronize threads within a single JVM process, not across distributed container instances. [CORRECT]

### Option B
ReentrantLock cannot be used with multi-threaded executor pools in modern JDK versions.

### Option C
Java virtual threads disable synchronized blocks and throw runtime security exceptions.

### Option D
Local JVM locks automatically cause deadlocks whenever connecting to cloud databases.

### Explanation
`synchronized` and `ReentrantLock` operate entirely inside local JVM memory. In a cloud environment where multiple independent service pods run in separate containers, an in-JVM lock on Pod 1 has no visibility or influence over Pod 2.

===

## Q4
In an architecture using Command Query Responsibility Segregation (CQRS) and Event Sourcing, how is the current state of an aggregate root determined?

### Option A
By executing a SQL SELECT query against a single normalized relational table.

### Option B
By fetching the latest snapshot directly from the client's browser local storage.

### Option C [CORRECT]
By sequentially replaying the immutable domain events stored in the event store.

### Option D
By generating a synthetic state through a distributed two-phase commit coordinator.

### Explanation
In Event Sourcing, state is not stored as a single mutable record. Instead, every state change is recorded as an immutable event. The current state is calculated by replaying all historical events in chronological order from the event store.

===

## Q5
What is the primary benefit of storing microservice user sessions in a distributed store like Redis rather than using sticky sessions?

### Option A
It forces all user requests to route strictly to the same compute node.

### Option B [CORRECT]
It decouples session state from compute instances, preventing traffic hotspots and session drops during node restarts.

### Option C
It encrypts JVM bytecodes automatically to prevent unauthorized heap inspection.

### Option D
It eliminates the need for HTTP headers or JWT authentication tokens.

### Explanation
Offloading sessions to a distributed in-memory store like Redis allows any application instance to retrieve and update session state. This eliminates traffic imbalances caused by sticky sessions and ensures users do not lose their sessions when pods are redeployed.
