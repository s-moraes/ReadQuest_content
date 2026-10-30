## Q1
What is the primary difference between horizontal and vertical scaling?

### Option A [CORRECT]
Horizontal adds more machines; vertical adds more resources (CPU/RAM) to a single machine.

### Option B
Horizontal increases database storage; vertical increases network bandwidth.

### Option C
Horizontal requires downtime; vertical does not require downtime.

### Option D
There is no architectural difference between them.

### Explanation
Horizontal scaling (scale-out) distributes workload across multiple nodes, while vertical scaling (scale-up) upgrades capacity of a single instance.
===
## Q2
What is the role of a reverse proxy in web architecture?

### Option A [CORRECT]
Routes client requests to backend servers, providing caching, SSL termination, and load balancing.

### Option B
Generates cryptographically secure private keys for client browsers.

### Option C
Acts as a client-side database cache.

### Option D
Prevents all network partitions in a cluster.

### Explanation
A reverse proxy intercepts client requests before they hit internal services, facilitating load balancing, security, and edge caching.
===
## Q3
Which hashing technique minimizes re-keying when nodes are added or removed from a cache cluster?

### Option A [CORRECT]
Consistent Hashing

### Option B
Modulus Hashing (hash(key) % N)

### Option C
Linear Probing

### Option D
SHA-256 Checksum

### Explanation
Consistent hashing maps both servers and keys to a ring, ensuring only k/N keys need to be remapped on average when a node joins or leaves.
===
## Q4
In the CAP theorem, what does Partition Tolerance guarantee?

### Option A [CORRECT]
The system continues to operate despite an arbitrary number of messages being dropped or delayed by the network.

### Option B
All reads return the most recent write instantly across all nodes.

### Option C
Every non-failing node returns a successful response without guarantee of latest data.

### Option D
Transactions follow strict ACID serialization.

### Explanation
Partition tolerance means the system sustains network communication failures between nodes without collapsing.
===
## Q5
Why are stateless services preferred for horizontal auto-scaling?

### Option A [CORRECT]
Any instance can handle any incoming request without needing shared memory or sticky sessions.

### Option B
Stateless services do not use any databases.

### Option C
They eliminate network latency entirely.

### Option D
They cannot crash or experience out-of-memory errors.

### Explanation
Stateless nodes hold no client session data, so traffic can be dynamically routed to any available instance.
