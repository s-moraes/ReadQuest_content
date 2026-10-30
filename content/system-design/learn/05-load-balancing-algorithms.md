# Load Balancing Algorithms

Load balancers act as the central traffic dispatchers of modern cloud architectures. Positioned between clients and backend server fleets, they distribute incoming requests across multiple healthy instances to optimize resource utilization, prevent bottlenecks, and guarantee high availability.

---

## 1. Layer 4 vs. Layer 7 Load Balancing

Load balancers operate at different layers of the OSI model, presenting distinct trade-offs between throughput, resource overhead, and routing intelligence:

```text
+-------------------------------------------------------------+
|                 LAYER 4 (TRANSPORT LEVEL)                   |
|  Inspects: Source/Dest IP & Port (TCP/UDP)                  |
|  Action: Routes packets without reading HTTP payload        |
|  Performance: Ultra-fast, millions of QPS, low CPU overhead |
|  Examples: AWS Network Load Balancer (NLB), HAProxy (TCP)   |
+-------------------------------------------------------------+
                              vs
+-------------------------------------------------------------+
|                LAYER 7 (APPLICATION LEVEL)                  |
|  Inspects: HTTP Methods, Headers, Cookies, URL Paths        |
|  Action: Terminates TLS, inspects JSON, smart routing       |
|  Performance: Higher CPU overhead, rich feature set         |
|  Examples: AWS Application Load Balancer (ALB), NGINX, Envoy|
+-------------------------------------------------------------+
```

### Layer 4 Load Balancing (Transport Level)
L4 balancers make routing decisions based purely on IP addresses and TCP/UDP ports. They do not terminate or inspect the application-layer payload:
- **Direct Server Return (DSR):** High-end L4 balancers route incoming packets to backend servers, which then reply directly to the client, bypassing the balancer on the return path to maximize egress throughput.
- **Limitation:** Cannot perform cookie-based session tracking, URL path routing, or header-based authentication.

### Layer 7 Load Balancing (Application Level)
L7 balancers terminate incoming TLS connections, decrypt the request, and parse the HTTP/2 or gRPC headers:
- **Path-Based Routing:** Route `/api/v1/orders` to the Order Service and `/api/v1/users` to the User Service.
- **Header & Cookie Inspection:** Perform SSL termination, inspect JWT tokens, and inject tracing correlation headers (`X-Request-ID`).

---

## 2. Core Load Balancing Algorithms

Choosing the right distribution algorithm directly impacts resource utilization and tail latency.

```text
                  +--------------------------------+
                  |   LOAD BALANCING ALGORITHMS    |
                  +--------------------------------+
                   /         |           |        \
                  v          v           v         v
             Round Robin  Least Conn  Hash-Based  Latency
```

### 1. Round Robin
Rotates requests sequentially across all registered servers in a fixed cyclical order.

```java
public class RoundRobinBalancer {
    private final List<String> servers;
    private final AtomicInteger index = new AtomicInteger(0);

    public RoundRobinBalancer(List<String> servers) {
        this.servers = new ArrayList<>(servers);
    }

    public String getNextServer() {
        if (servers.isEmpty()) throw new IllegalStateException("No healthy servers");
        int current = index.getAndIncrement();
        return servers.get(Math.abs(current % servers.size()));
    }
}
```
- **Best Used For:** Homogeneous server pools where all nodes have identical CPU/RAM and incoming requests require similar processing time.

### 2. Weighted Round Robin
Assigns a static weight integer to each server based on its physical hardware capacity. A server with weight `3` receives three times as many requests as a server with weight `1`.

### 3. Least Connections
Directs incoming traffic to the server currently maintaining the smallest number of active, concurrent network connections.
- **Best Used For:** Workloads with highly variable processing times (e.g., short HTTP ping requests mixed with heavy PDF generation tasks) or persistent long-lived connections (WebSockets).

### 4. IP / Source Hash
Hashes the client's source IP address (`hash(ClientIP) % N`) to map the client to a specific server deterministically.
- **Drawback:** In an era of mobile users switching between cellular and Wi-Fi networks, client IP addresses change constantly, breaking session stickiness.

### 5. Consistent Hashing
Maps both server nodes and incoming request keys onto a virtual $360^\circ$ hash ring. When nodes join or leave the pool, only a tiny fraction ($1/N$) of keys are remapped, preserving cache locality and preventing cache stampedes.

### 6. Least Response Time / Latency
Dynamic algorithms continuously probe backend server response times and route requests to the node demonstrating the lowest combined response latency and active connection count.

---

## 3. Algorithm Selection Matrix

| Algorithm | Distribution Logic | Strengths | Weaknesses |
| :--- | :--- | :--- | :--- |
| **Round Robin** | Cyclic sequential | Simple, zero state overhead | Hotspots if request costs vary |
| **Weighted Round Robin** | Capacity-proportional | Accommodates mixed instance sizes | Requires manual weight tuning |
| **Least Connections** | Active connection count| Excellent for long-lived tasks | Slower to react on fast spikes |
| **Consistent Hashing** | Virtual hash ring | Preserves cache affinity | Moderate implementation complexity |
| **Least Response Time**| Probed latency metrics | Optimizes tail latency (p99) | High probing monitoring overhead |

---

## 4. Health Checking & Failover Mechanics

A load balancer is only as effective as its health-checking subsystem. Routing traffic to an unresponsive server triggers cascading 502/504 Bad Gateway errors.

```text
[ Load Balancer ] --- Active Probe (GET /healthz) ---> [ Node A: 200 OK ] (Healthy)
                  --- Active Probe (GET /healthz) ---> [ Node B: TIMEOUT ] (UNHEALTHY!)
                                                             |
                            Traffic instantly redirected to Node A
```

### Active vs. Passive Probing

1. **Active Health Checks (Out-of-Band):**
   - The balancer periodically sends synthetic heartbeat requests (e.g., HTTP `GET /healthz` every 5 seconds) to each node.
   - Requires endpoints to return HTTP `200 OK` within a strict timeout (e.g., $1,000\text{ms}$).
   - Verifies deep dependency health (e.g., database connectivity, disk space).

2. **Passive Health Checks (In-Line):**
   - The balancer monitors live user traffic flowing through the backend.
   - If a server returns three consecutive HTTP `5xx` errors or drops TCP connections, the balancer automatically removes the server from the pool.

### Preventing Server Flapping
When a struggling server reboots, it may pass an initial health check, receive a surge of traffic, crash immediately, and repeat the cycle. Balancers mitigate this using **Threshold Counters**:
- **Healthy Threshold:** Server must pass 3 consecutive health checks before receiving production traffic.
- **Unhealthy Threshold:** Server is evicted after 2 consecutive failed health checks.
