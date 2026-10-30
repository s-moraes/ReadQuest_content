## Q1
What is the primary architectural distinction between Apache Hadoop MapReduce and Apache Spark?

### Option A
Hadoop MapReduce is written in Scala, whereas Apache Spark is written strictly in C++.

### Option B [CORRECT]
MapReduce writes intermediate results to physical disk between stages, while Spark performs computations primarily in-memory using RDDs.

### Option C
Spark only supports batch workloads, while Hadoop MapReduce is dedicated exclusively to real-time streaming.

### Option D
MapReduce does not support Java APIs, requiring all map and reduce jobs to be written in Python.

### Explanation
Hadoop MapReduce persists intermediate state to HDFS disks between the map, shuffle, and reduce phases, introducing high disk I/O latency. Spark caches intermediate partitions in cluster memory across Resilient Distributed Datasets (RDDs), accelerating multi-pass computations.

===

## Q2
In the Akka toolkit, how does an actor prevent race conditions and protect its internal mutable state?

### Option A
By acquiring database-level table locks for each incoming request.

### Option B
By requiring every field inside the actor to be annotated with `volatile`.

### Option C [CORRECT]
By isolating state and processing messages sequentially from an asynchronous mailbox, one message at a time.

### Option D
By duplicating the actor instance across all CPU cores simultaneously.

### Explanation
Akka actors communicate exclusively via asynchronous message passing. Each actor has a mailbox and processes incoming messages sequentially. Because only one message is handled at any given moment, the actor's state cannot experience concurrent modification, eliminating the need for locks.

===

## Q3
What is the "Golden Rule" of reactive programming when executing code on an Eclipse Vert.x event loop thread?

### Option A
Always execute database queries synchronously inside the request handler.

### Option B [CORRECT]
Never block the event loop thread with sleep statements, long computations, or blocking I/O.

### Option C
Create a new operating system thread for every incoming socket connection.

### Option D
Convert all HTTP endpoints to synchronous Java RMI remote procedures.

### Explanation
Vert.x uses a small pool of event loop threads to serve thousands of concurrent connections. If code blocks an event loop thread (e.g., via `Thread.sleep()` or synchronous JDBC), that entire thread halts, freezing all other connections assigned to that loop.

===

## Q4
How does Apache Spark restore lost data if a worker node crashes during a distributed parallel computation?

### Option A
By halting the entire cluster and restoring from the previous midnight database tape backup.

### Option B
By querying the operating system swap partition on the master node.

### Option C [CORRECT]
By using the RDD lineage graph to recompute only the lost partitions from the original dataset.

### Option D
By rolling back the entire cluster state to the master node's boot sector.

### Explanation
Spark RDDs maintain a lineage graph (DAG) of the transformations applied to the data. If a partition is lost due to a worker crash, Spark re-executes the transformation lineage for that specific partition on another healthy node.

===

## Q5
What architectural foundation does the Lagom framework build upon to simplify cloud-native microservices development?

### Option A
It builds directly on classic Java EE Servlets and Enterprise Java Beans.

### Option B
It relies on Hadoop MapReduce for inter-service RPC communication.

### Option C [CORRECT]
It builds on Akka and Play, offering built-in CQRS, Event Sourcing, and asynchronous service descriptors.

### Option D
It replaces JVM bytecode with native assembly instructions via GraalVM substrate.

### Explanation
Lagom was created by Lightbend to bring the power of Akka and Play to enterprise microservices through opinionated abstractions. It natively guides developers toward CQRS, Event Sourcing, and non-blocking asynchronous APIs.
