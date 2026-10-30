# In-Memory Caching & Invalidation

Reading records from physical database disks takes milliseconds, while reading from random-access memory (RAM) takes nanoseconds. **Caching** places frequently accessed data in high-speed in-memory storage tiers to slash query latency and shield backend databases from traffic saturation.

---

## 1. In-Process vs. Distributed Caching

```text
IN-PROCESS CACHE (Caffeine / Guava)
[ Pod 1 (JVM) ] ---> [ Local Heap Cache ] (Nanosecond Speed)
- Zero network round-trips
- Data diverges across pods (Cache Incoherence!)
- Lost when container restarts

DISTRIBUTED CACHE (Redis / Memcached)
[ Pod 1 ] \
[ Pod 2 ] ---> [ Shared Redis Cluster ] (Sub-millisecond RTT)
[ Pod 3 ] /
- Consistent view of state across all application replicas
- Survives application crashes and rolling deployments
- Scales memory independently from compute
```

---

## 2. Core Caching Patterns

Applications coordinate data synchronization between the cache and underlying database using distinct architectural patterns:

```text
1. CACHE-ASIDE (Lazy Loading)
[ App ] --- 1. Check Key ---> [ Cache ] (Miss!)
[ App ] --- 2. Query DB -----> [ Database ]
[ App ] --- 3. Populate -----> [ Cache ]

2. WRITE-THROUGH
[ App ] --- Write Data ---> [ Cache ] --- Synchronous Write ---> [ Database ]

3. WRITE-BEHIND (Write-Back)
[ App ] --- Write Data ---> [ Cache ] (Returns Success!)
                            ... Asynchronous Batch Flush ... ---> [ Database ]
```

### 1. Cache-Aside (Lazy Loading)
The application code orchestrates all caching logic:
- Reads query the cache first. On a **Cache Miss**, the app reads from the database, writes the result into the cache with a Time-To-Live (TTL), and returns the payload.
- Writes update the database and either invalidate (`DEL key`) or update the cache.
- **Advantage:** Resilient. If the cache crashes, queries fall back directly to the database.

### 2. Write-Through
The application treats the cache as the primary data store. The cache engine synchronously updates the underlying database before acknowledging success to the caller.
- **Advantage:** Guarantees data in cache is never stale.
- **Drawback:** Higher write latency due to two sequential writes.

### 3. Write-Behind (Write-Back)
The application writes data to the cache, which acknowledges immediately. The cache asynchronously batches mutations and flushes them to the database in the background.
- **Advantage:** Blazing fast write throughput (absorbs massive write spikes).
- **Drawback:** Risk of permanent data loss if the cache node crashes before flushing dirty buffers to durable disk.

---

## 3. Cache Eviction Policies

When cache memory fills to capacity, the engine must evict items to accommodate incoming records:

| Policy | Eviction Criteria | Best Used For |
| :--- | :--- | :--- |
| **Least Recently Used (LRU)**| Discards items that have not been read for the longest time | General web applications, e-commerce |
| **Least Frequently Used (LFU)**| Discards items with the lowest historical access frequency counter | Static reference data, zip codes |
| **First In, First Out (FIFO)**| Discards items in the order they were inserted | Time-series data, temporary queues |
| **Random Eviction** | Randomly purges keys | Workloads with uniform access distributions |

---

## 4. The Three Catastrophic Cache Failure Scenarios

In high-concurrency systems, unhandled cache edge cases can instantly bring down backend relational databases:

```text
                  +--------------------------------+
                  |    CRITICAL CACHE FAILURES     |
                  +--------------------------------+
                   /               |              \
                  v                v               v
           Penetration         Stampede        Avalanche
          (Non-existent)     (Hot Key Dies)   (Mass Expire)
```

### 1. Cache Penetration
- **The Problem:** Malicious clients or bugs repeatedly query keys that **exist neither in the cache nor in the database** (e.g., `GET /users/-9999`). Every request bypasses the cache and hammers the database.
- **Solution A (Bloom Filters):** A memory-efficient probabilistic data structure that tests whether an element is definitely not in the set. If the Bloom filter says no, the request is rejected immediately without touching the cache or database.
- **Solution B (Cache Null Objects):** Store empty values (`key: null`) in the cache with a short TTL (e.g., 60 seconds).

### 2. Cache Stampede (Thundering Herd / Breakdown)
- **The Problem:** A super-popular "hot key" (e.g., homepage banner or breaking news article) expires. At that exact millisecond, 10,000 concurrent requests miss the cache and query the database simultaneously to recompute the value, crashing the DB.
- **Solution A (Distributed Mutex):** The first thread to miss acquires a lock (`SET lock:item NX PX 5000`) to recompute the cache. All other threads wait and re-read the cache once populated.
- **Solution B (Probabilistic Early Expiration):** Recompute the cache in the background *before* it officially expires based on incoming traffic probabilities.

### 3. Cache Avalanche
- **The Problem:** Thousands of cache keys are initialized with the exact same TTL (e.g., 1 hour). 60 minutes later, every key expires simultaneously, exposing the database to the entire site's traffic.
- **Solution:** Add **Randomized Jitter** to every TTL:

```java
int baseTtlSeconds = 3600;
int jitter = ThreadLocalRandom.current().nextInt(-300, 300); // +/- 5 mins
int actualTtl = baseTtlSeconds + jitter;
redis.set(key, value, Duration.ofSeconds(actualTtl));
```
