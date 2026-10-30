## Q1
In Apache ZooKeeper, which type of znode is automatically deleted when the client session that created it terminates?

### Option A
Persistent znode

### Option B [CORRECT]
Ephemeral znode

### Option C
Static snapshot znode

### Option D
Immutable schema znode

### Explanation
Ephemeral znodes exist only as long as the client session that created them remains active. If the client crashes or its heartbeat expires, ZooKeeper automatically deletes the node, making ephemeral znodes ideal for leader election and service presence detection.

===

## Q2
Which formal distributed consensus algorithm is used by etcd to ensure linearizable writes and cluster consistency?

### Option A
Paxos

### Option B
Two-Phase Commit (2PC)

### Option C [CORRECT]
Raft

### Option D
Gossip Protocol

### Explanation
etcd uses the Raft consensus algorithm. Raft decomposes consensus into leader election, log replication, and safety guarantees, providing strong consistency and understandable failure recovery across Kubernetes and distributed key-value stores.

===

## Q3
In the Reactive Streams specification, what critical problem does backpressure solve?

### Option A
It encrypts network packets to prevent man-in-the-middle attacks.

### Option B [CORRECT]
It prevents fast producers from overwhelming slow consumers by allowing consumers to demand only the items they can process.

### Option C
It enforces sequential single-threaded execution across all cluster worker nodes.

### Option D
It forces synchronous blocking calls between microservices to prevent lost updates.

### Explanation
Backpressure allows a Subscriber to signal its consumption capacity to the Publisher via `Subscription.request(n)`. This flow control prevents in-memory buffer overflows and out-of-memory crashes when producers generate data faster than consumers can process it.

===

## Q4
What distinctive capability does HashiCorp Consul provide out of the box in addition to distributed key-value storage?

### Option A
An append-only relational SQL execution engine.

### Option B
A distributed MapReduce compiler for big data analytics.

### Option C [CORRECT]
An integrated service mesh, service discovery, dynamic health checking, and multi-datacenter routing.

### Option D
A byte-code transpiler for migrating Java applications to WebAssembly.

### Explanation
Consul provides an integrated service mesh and discovery catalog with first-class support for health monitoring, multi-datacenter federation, and DNS/HTTP routing, making it broader in scope than basic distributed lock stores.

===

## Q5
How does asynchronous messaging via message brokers (such as Apache Kafka or RabbitMQ) improve microservice resilience during traffic spikes?

### Option A
By holding database connections open until all downstream workers acknowledge receipt.

### Option B [CORRECT]
By temporarily queuing incoming messages, allowing consumer worker pools to process work at a sustainable rate.

### Option C
By converting all asynchronous requests into synchronous blocking socket calls.

### Option D
By automatically restarting failed database pods whenever queues become full.

### Explanation
Message brokers act as durable shock absorbers. During traffic spikes, requests are buffered safely in queues or log partitions rather than directly hitting downstream microservices, preventing cascade failures and allowing workers to process tasks at their maximum stable throughput.
