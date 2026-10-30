## Q1
What is a cache penetration problem?

### Option A [CORRECT]
Queries for non-existent keys bypass the cache and directly hit the database repeatedly.

### Option B
A key expires and thousands of requests hit the database simultaneously.

### Option C
The cache runs completely out of memory and crashes.

### Option D
Data in the cache becomes permanently stale.

### Explanation
Cache penetration occurs when requests query data that exists neither in cache nor DB; Bloom filters or caching null objects mitigate this.
===
## Q2
Which cache invalidation policy removes the item that has not been accessed for the longest time?

### Option A [CORRECT]
Least Recently Used (LRU)

### Option B
Least Frequently Used (LFU)

### Option C
First In First Out (FIFO)

### Option D
Random Replacement

### Explanation
LRU tracks access order and evicts keys with the oldest last access timestamp.
===
## Q3
In a Cache-Aside (Lazy Loading) pattern, what does the application do on a cache miss?

### Option A [CORRECT]
Reads from the database, writes the result to the cache, and returns the data.

### Option B
Throws an exception back to the client.

### Option C
Asynchronously triggers a full cache rebuild.

### Option D
Writes an empty record to the database.

### Explanation
With Cache-Aside, the application queries the cache first, loads from DB on a miss, and populates the cache for subsequent reads.
===
## Q4
What is the primary risk of Write-Through caching?

### Option A [CORRECT]
Higher write latency because data is written to both cache and backing storage synchronously.

### Option B
Data loss on node crash.

### Option C
Stale reads from the cache.

### Option D
High memory fragmentation.

### Explanation
Write-Through ensures cache consistency but incurs latency by waiting for both storage tiers to confirm the write.
