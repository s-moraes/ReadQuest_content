# Cloud Database Concurrency & Locking

In cloud-native environments, dozens or hundreds of microservice replicas connect to shared relational or distributed databases simultaneously. Managing concurrent access to shared resources without corrupting data, introducing deadlocks, or crippling transaction throughput requires a rigorous, multi-layered concurrency strategy.

---

## 1. The Concurrency Dilemma in Cloud Databases

When multiple transactions run concurrently across distributed application nodes, they risk violating the fundamental ACID contract of the underlying database:

```text
[ Pod 1 (Tx 1) ] ---> Read Balance: $100
[ Pod 2 (Tx 2) ] ---> Read Balance: $100
[ Pod 1 (Tx 1) ] ---> Deduct $40 -> Write Balance: $60 (Commit)
[ Pod 2 (Tx 2) ] ---> Deduct $30 -> Write Balance: $70 (Commit Overwrites!)
                      *** LOST UPDATE: Actual balance should be $30 ***
```

### Classic Concurrency Anomalies

- **Lost Updates (G0/P4):** Two transactions read the same row and calculate new values based on that read. The last write silently overwrites the previous commit without incorporating its changes.
- **Dirty Reads (P1):** Transaction 1 mutates a row but has not committed. Transaction 2 reads the uncommitted value. Transaction 1 then rolls back, leaving Transaction 2 with invalid phantom data.
- **Non-Repeatable Reads (Fuzzy Reads, P2):** Transaction 1 reads a row. Transaction 2 modifies or deletes that row and commits. Rereading the row within Transaction 1 yields different values.
- **Phantom Reads (P3):** Transaction 1 executes a range query (e.g., `WHERE status = 'PENDING'`). Transaction 2 inserts new matching rows and commits. Re-executing the range query returns rows that were not previously present.
- **Write Skew:** Two concurrent transactions read overlapping data sets, satisfy an invariant independently, and perform disjoint writes that violate the global constraint (e.g., two on-call doctors concurrently requesting leave when at least one must remain active).

---

## 2. ANSI SQL Isolation Levels & MVCC Mechanics

Relational databases define four ANSI SQL isolation levels to govern the trade-off between consistency and concurrency:

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | Write Skew |
| :--- | :--- | :--- | :--- | :--- |
| **Read Uncommitted** | Possible | Possible | Possible | Possible |
| **Read Committed** | Prevented | Possible | Possible | Possible |
| **Repeatable Read** | Prevented | Prevented | Prevented (in MVCC)| Possible |
| **Serializable** | Prevented | Prevented | Prevented | Prevented |

Most cloud databases (PostgreSQL, Amazon Aurora, Oracle) default to **Read Committed** to maximize throughput.

### Multi-Version Concurrency Control (MVCC)

Modern relational engines avoid read locks using **MVCC**. The core philosophy of MVCC is:

> **Readers never block writers, and writers never block readers.**

```text
Row v1: [ Balance = 100 | xmin = 1001 | xmax = 1004 ] (Visible to Tx <= 1003)
Row v2: [ Balance = 60  | xmin = 1004 | xmax = null ] (Visible to Tx >= 1004)
```

Each row carries transaction metadata (such as `xmin` and `xmax` in PostgreSQL or undo logs in MySQL InnoDB). When an update occurs, the database creates a new version tuple rather than overwriting the row on disk.

- Long-running read queries read a consistent snapshot of the data as of their transaction start time without locking table rows.
- **The Cost of MVCC:** Accumulating dead tuples causes database bloat. Databases require background maintenance workers (e.g., `VACUUM` in PostgreSQL) to reclaim dead tuple disk space and prevent Transaction ID (XID) wraparound failures.

---

## 3. In-JVM Synchronization vs Cloud Reality

Java developers often reach for language-level synchronization primitives:

```java
// ANTI-PATTERN in a clustered cloud environment
@Service
public class OrderService {
    private final Lock localLock = new ReentrantLock();

    public void deductStock(Long productId, int quantity) {
        localLock.lock();
        try {
            Product p = productRepo.findById(productId).orElseThrow();
            p.setStock(p.getStock() - quantity);
            productRepo.save(p);
        } finally {
            localLock.unlock();
        }
    }
}
```

### The Limitation of In-JVM Locks

```text
[ Kubernetes Cluster ]
  +----------------------+      +----------------------+
  | Pod 1 (JVM A)        |      | Pod 2 (JVM B)        |
  | ReentrantLock (LOCAL)|      | ReentrantLock (LOCAL)|
  +----------------------+      +----------------------+
             \                              /
              v                            v
          [ Mutate Stock ]             [ Mutate Stock ]
                   \                  /
                    v                v
                 [ Shared Aurora PostgreSQL ]
                 (CONCURRENT CORRUPTION OCCURS)
```

`ReentrantLock` and `synchronized` operate strictly within the bounds of a single operating system process and its local JVM heap. When multiple pods run behind a Kubernetes service, Pod 1 and Pod 2 execute their local locks independently, offering zero protection against concurrent database updates.

To achieve safe concurrency, synchronization must occur at the **database level** or via a **distributed lock manager**.

---

## 4. Optimistic Locking in Production

Optimistic locking assumes that concurrent collisions are infrequent. Instead of acquiring physical locks during reading, it verifies at commit time that no other transaction has mutated the record.

```java
@Entity
@Table(name = "inventory_items")
public class InventoryItem {

    @Id
    private Long id;

    private String sku;
    private int availableQuantity;

    @Version
    private Long version; // Managed automatically by Hibernate/JPA
}
```

### The Underlying SQL Mechanism

When Hibernate flushes updates, it appends the version check directly into the `WHERE` clause:

```sql
UPDATE inventory_items 
SET available_quantity = 42, version = version + 1 
WHERE id = 501 AND version = 3;
```

If another transaction has already updated version `3` to `4`, the database reports `0 rows updated`. Hibernate detects this mismatch and immediately throws an `OptimisticLockException` (or `StaleObjectStateException`).

```text
Tx 1: Read (v3) -----------------> Update (v3 -> v4) [SUCCESS]
Tx 2: Read (v3) ---- Wait... ----> Update (WHERE v3) [FAILS: 0 rows affected]
                                   ==> OptimisticLockException thrown
```

### Handling Retries with Exponential Backoff & Jitter

When an optimistic lock fails, the application must catch the exception, reload the fresh state, and retry the operation:

```java
@Service
public class InventoryService {

    @Retryable(
        retryFor = { OptimisticLockException.class },
        maxAttempts = 4,
        backoff = @Backoff(delay = 100, maxDelay = 1000, multiplier = 2.0, random = true)
    )
    @Transactional
    public void reserveInventory(Long itemId, int qty) {
        InventoryItem item = itemRepo.findById(itemId).orElseThrow();
        if (item.getAvailableQuantity() < qty) {
            throw new InsufficientStockException("Out of stock");
        }
        item.setAvailableQuantity(item.getAvailableQuantity() - qty);
        itemRepo.save(item);
    }
}
```

Adding randomized jitter prevents **retry storms**, where multiple pods repeatedly retry at identical time intervals and collide continuously.

---

## 5. Pessimistic Locking in Cloud Databases

When contention is high (e.g., flash sales, ticketing platforms, or high-volume bank accounts), optimistic locking causes excessive retry loops and wasted CPU cycles. Pessimistic locking acquires exclusive database locks immediately when reading the row.

```java
public interface InventoryRepository extends JpaRepository<InventoryItem, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT i FROM InventoryItem i WHERE i.id = :id")
    Optional<InventoryItem> findByIdForUpdate(@Param("id") Long id);
}
```

This generates native SQL locking clauses:

```sql
SELECT id, sku, available_quantity, version 
FROM inventory_items 
WHERE id = 501 
FOR UPDATE;
```

Any competing transaction attempting to read (with `FOR UPDATE`) or modify row `501` blocks until the holding transaction commits or rolls back.

### The Hidden Trap: Connection Pool Starvation
Holding pessimistic locks during long-running operations (such as making external HTTP calls or generating PDFs) keeps both the database row locked and the database connection checked out from the pool (e.g., HikariCP). When all pool connections are blocked waiting for locks, the entire microservice stops accepting new requests.

### The Modern Secret Weapon: `SKIP LOCKED`

For high-throughput worker queues implemented in relational databases, `SKIP LOCKED` eliminates contention completely:

```sql
SELECT id, task_payload 
FROM task_queue 
WHERE status = 'PENDING' 
ORDER BY priority DESC, created_at ASC 
LIMIT 1 
FOR UPDATE SKIP LOCKED;
```

```text
Worker Pod 1: SELECT FOR UPDATE SKIP LOCKED -> Locks and processes Task 1
Worker Pod 2: SELECT FOR UPDATE SKIP LOCKED -> Skips Task 1, locks Task 2
Worker Pod 3: SELECT FOR UPDATE SKIP LOCKED -> Skips Tasks 1 & 2, locks Task 3
```

Workers never wait on locks; each pod instantly claims the next available unallocated record.

---

## 6. Distributed Locks & The Redlock Controversy

When critical sections span multiple heterogeneous databases, external payment gateways, or third-party APIs, database row locks cannot provide protection. Applications use **Distributed Locks** managed by Redis or ZooKeeper.

```text
[ Pod 1 ] ---> SET lock:order:101 <unique_uuid> NX PX 30000 ---> [ Redis ]
               (NX = Set if Not Exists, PX = Expiration 30000ms)
```

Releasing the lock must be atomic using a Lua script to ensure a pod only deletes its own lock:

```lua
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

### The Martin Kleppmann vs Redlock Debate

Distributed systems researcher Martin Kleppmann highlighted a critical vulnerability in lease-based distributed locks without fencing tokens:

```text
[ Client 1 ] Acquired Lock (Lease 30s)
     |
  [ JVM Stop-The-World GC Pause (45s) ] ---> Lock expires in Redis!
     |                                        [ Client 2 ] Acquires Lock
  [ Client 1 Wakes Up ]                       Writes to Storage (v1)
  Writes to Storage (CORRUPTING Client 2's write!)
```

### The Solution: Fencing Tokens

To guarantee safety in asynchronous networks subject to GC pauses and network delays, the lock service must return a monotonically increasing **Fencing Token** with every lock grant:

```text
Client 1 acquires lock -> receives Fencing Token 33
Client 2 acquires lock -> receives Fencing Token 34

Storage Engine Rule: Reject any write with token <= highest seen token!

Client 2 writes (Token 34) ---> Storage accepts (highest seen = 34)
Client 1 wakes up, writes (Token 33) ---> Storage REJECTS (33 < 34)!
```

### Production Distributed Locking with Redisson

The Redisson client library provides robust, battle-tested distributed locks with an automatic **Watchdog** that renews the lock lease as long as the holding thread is alive:

```java
@Service
public class PaymentProcessingService {

    private final RedissonClient redisson;

    public PaymentProcessingService(RedissonClient redisson) {
        this.redisson = redisson;
    }

    public void processPayment(String paymentId) {
        RLock lock = redisson.getLock("lock:payment:" + paymentId);

        try {
            // Wait up to 5s, auto-renew lease via watchdog while processing
            if (lock.tryLock(5, TimeUnit.SECONDS)) {
                try {
                    executeExternalPayment(paymentId);
                } finally {
                    lock.unlock();
                }
            } else {
                throw new LockAcquisitionException("Payment already processing");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

---

## 7. Distributed In-Memory Data Grids (IMDG) & Entry Processors

Distributed In-Memory Data Grids (Hazelcast, Apache Ignite) partition data in-memory across cluster nodes using consistent hashing.

### The Network Bottleneck Anti-Pattern
```text
[ App Pod ] -- 1. Network Lock Request --> [ Cache Node ]
[ App Pod ] -- 2. Network Read Data ------> [ Cache Node ]
[ App Pod ] -- (Mutate data locally) --
[ App Pod ] -- 3. Network Write Back ----> [ Cache Node ]
[ App Pod ] -- 4. Network Unlock --------> [ Cache Node ]
Total: 4 network round-trips + high lock contention!
```

### The High-Performance Pattern: Entry Processors
Instead of transferring data across the network to the code, **Entry Processors move the computation to the data**:

```java
// Execute atomic mutation directly inside the partition thread on the cluster
IMap<String, AccountDto> accounts = hazelcast.getMap("accounts");

accounts.executeOnKey("acc-9001", entry -> {
    AccountDto account = entry.getValue();
    account.debit(BigDecimal.valueOf(50.00));
    entry.setValue(account);
    return account.getBalance();
});
```

Because the mutation executes directly within the single thread owning that partition in the cluster, it requires **zero distributed locks** and **zero network round-trips for data transfer**.

---

## 8. Concurrency Strategy Selection Matrix

| Mechanism | Contention Profile | Scope | Failure Mode | Overhead |
| :--- | :--- | :--- | :--- | :--- |
| **Optimistic (`@Version`)** | Low to Moderate | Single Database | `OptimisticLockException` | Minimal (Version column check) |
| **Pessimistic (`FOR UPDATE`)** | High / Hotspots | Single Database | Deadlocks, connection starvation| High (Queueing and blocked threads) |
| **Pessimistic (`SKIP LOCKED`)**| Worker Task Queues | Single Database | None (skips locked rows) | Very Low (Lock-free polling) |
| **Distributed Lock (Redisson)**| Moderate | Multi-System / APIs | Lease expiration, GC pauses | Moderate (Redis network calls) |
| **IMDG Entry Processor** | Extreme Throughput | Clustered In-Memory | Partition rebalance during crash | Ultra-low (In-memory execution) |
