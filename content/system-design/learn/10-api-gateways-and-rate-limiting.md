# API Gateways & Edge Routing

In microservice architectures, exposing dozens of internal backend services directly to public web and mobile clients introduces severe security risks, chatty network round-trips, and protocol coupling. An **API Gateway** acts as the single entry point, orchestrating traffic, enforcing security, and protecting services via rate limiting.

---

## 1. Direct Client-to-Microservice vs. API Gateway

```text
DIRECT CLIENT ACCESS (Anti-Pattern)
[ Mobile Client ] ---> [ Order Service (Port 8081) ]
                  ---> [ User Service (Port 8082) ]
                  ---> [ Payment Service (Port 8083) ]
- 3 separate TLS handshakes over cellular networks
- Internal endpoints exposed to public Internet
- Every service must independently implement auth & rate limiting

API GATEWAY PATTERN (Production Best Practice)
[ Mobile Client ] --- HTTPS (Single Entry Point) ---> [ API GATEWAY ]
                                                            |
                             +------------------------------+------------------------------+
                             v                              v                              v
                     [ Order Service ]              [ User Service ]              [ Payment Service ]
                     (Internal Network)             (Internal Network)             (Internal Network)
```

### Core Responsibilities of the API Gateway
1. **Reverse Proxy & Request Routing:** Maps public-facing URLs (`/api/v1/orders`) to internal service discovery instances.
2. **Protocol Translation:** Accepts public JSON/HTTP REST requests from browsers and translates them into internal high-performance **gRPC** calls to backend microservices.
3. **Cross-Cutting Concerns:** Centralizes JWT signature validation, TLS termination, CORS headers, and distributed tracing context injection (`traceparent`).
4. **Backend-For-Frontend (BFF):** Creates dedicated gateway variants tailored to specific clients (e.g., Mobile BFF vs. Desktop Web BFF), aggregating multiple backend queries into a single compact payload.

---

## 2. Rate Limiting Algorithms

To prevent Distributed Denial of Service (DDoS) attacks, brute-force credential stuffing, and noisy-neighbor service degradation, gateways enforce **Rate Limiting**.

```text
                  +--------------------------------+
                  |    RATE LIMITING ALGORITHMS    |
                  +--------------------------------+
                   /         |           |        \
                  v          v           v         v
             Token Bucket  Leaky Bucket Fixed Win  Sliding Win
```

### 1. Token Bucket
- The bucket has a maximum capacity $B$ and continuously refills at a rate of $R$ tokens per second.
- Every incoming request consumes 1 token. If the bucket is empty, the request is rejected with **HTTP 429 Too Many Requests**.
- **Strength:** Allows short bursts of traffic up to capacity $B$ while maintaining a steady-state average rate $R$.

### 2. Leaky Bucket
- Requests enter a bounded FIFO queue (bucket) and leak out at a **strictly constant rate**.
- If the incoming burst overflows the queue capacity, excess requests are dropped immediately.
- **Strength:** Smooths out traffic spikes into a predictable, constant-rate stream for sensitive backend databases.

### 3. Fixed Window Counter
- Divides time into fixed intervals (e.g., 1 minute). A counter tracks requests within that window.
- **The Critical Flaw (Boundary Spike):** If a user sends 100 requests at 00:59 and another 100 requests at 01:01, they successfully send 200 requests within a 2-second window, doubling the allowed rate!

### 4. Sliding Window Counter (Production Standard)
Combines the low memory usage of the fixed window counter with the boundary smoothness of sliding logs. It estimates current traffic by weighting the previous window's counter:

$$\text{Current Count} = \text{Current Window Count} + \text{Previous Window Count} \times (1 - \text{Overlap Percentage})$$

```text
[ Previous Window (70 reqs) ] | [ Current Window (30 reqs) ]
               <--- Elapsed 30% into Current Window --->
Estimated Count = 30 + 70 * (1 - 0.30) = 30 + 49 = 79 requests
```

---

## 3. Distributed Rate Limiting with Redis & Lua

When multiple API Gateway pods run in a Kubernetes cluster, local in-memory counters fail: a client could hit Pod A, Pod B, and Pod C, multiplying their allowed quota.

The counter must live in a centralized, shared in-memory store like **Redis**. To prevent race conditions, the check-and-increment logic executes as an **atomic Lua script**:

```lua
-- Redis Lua Script for Atomic Sliding Window Rate Limiting
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local current = tonumber(redis.call('get', key) or "0")

if current + 1 > limit then
    return 0 -- Rejected (Exceeded limit)
else
    redis.call('incrby', key, 1)
    if current == 0 then
        redis.call('expire', key, 60) -- 60s TTL on first request
    end
    return 1 -- Allowed
end
```

Because Redis executes Lua scripts as a single atomic transaction, no competing gateway pod can interleave operations.

---

## 4. API Gateway Comparison

| Gateway Engine | Runtime Core | Extension Model | Best Used For |
| :--- | :--- | :--- | :--- |
| **Kong** | NGINX / Lua | Lua plugins, Go, Wasm | High-throughput enterprise REST gateways |
| **Envoy Proxy** | C++ | C++, Wasm filters | Service mesh sidecars, high-performance edge |
| **Spring Cloud Gateway**| Java (Project Reactor)| Java Filters | JVM / Spring Boot native ecosystems |
| **AWS API Gateway** | Managed Serverless | AWS Lambda integrations | Serverless, AWS Lambda backends |
| **Apache APISIX** | NGINX / etcd | Lua, Java, Python, Wasm | Dynamic cloud-native configuration updates |
