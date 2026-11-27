# Iterator Pattern

The **Iterator** pattern provides a standard way to access elements of a collection or data stream **sequentially** without exposing its underlying representation (array, linked list, tree, or paginated remote API).

---

## 1. The Problem It Solves

If callers traverse a custom structure using raw array indices or internal tree pointers, changing the internal storage breaks every caller. Worse, when data lives in a **paginated database or REST API** with 1,000,000 rows, loading everything into a `List` crashes the JVM with `OutOfMemoryError`.

---

## 2. Structure

```text
  [Iterable<T>] --creates--> [Iterator<T>]
  + iterator()               + hasNext() : boolean
                             + next() : T
```

Because traversal state (`cursor`, `currentPage`) lives inside the **Iterator** instance, multiple callers can iterate the same source concurrently at different positions.

---

## 3. Deep-Dive Java Example: Lazy Paginated Iterator

Here is a Java `Iterable` that fetches pages on demand from a data source, keeping memory usage constant ($O(\text{pageSize})$):

```java
public interface PageFetcher<T> {
    List<T> fetchPage(int pageNumber);
}

public final class PaginatedIterable<T> implements Iterable<T> {
    private final PageFetcher<T> fetcher;

    public PaginatedIterable(PageFetcher<T> fetcher) {
        this.fetcher = fetcher;
    }

    @Override
    public Iterator<T> iterator() {
        return new Iterator<>() {
            private int page = 0;
            private Iterator<T> current = Collections.emptyIterator();

            @Override
            public boolean hasNext() {
                while (!current.hasNext()) {
                    List<T> nextBatch = fetcher.fetchPage(page++);
                    if (nextBatch.isEmpty()) {
                        return false;
                    }
                    current = nextBatch.iterator();
                }
                return true;
            }

            @Override
            public T next() {
                if (!hasNext()) {
                    throw new NoSuchElementException();
                }
                return current.next();
            }
        };
    }
}
```

Callers can now stream millions of rows with a plain Java `for-each` loop:

```java
for (Order order : new PaginatedIterable<>(page -> repo.findPage(page))) {
    process(order);
}
```

---

## 4. Fail-Fast vs. Fail-Safe Iterators in Java

| Kind | Behavior on Concurrent Modification | JDK Examples |
| :--- | :--- | :--- |
| **Fail-Fast** | Tracks `modCount`; throws `ConcurrentModificationException` immediately if mutated during iteration | `ArrayList`, `HashMap`, `HashSet` |
| **Fail-Safe (Weakly Consistent)** | Iterates over a snapshot or concurrent segments; never throws `ConcurrentModificationException` | `CopyOnWriteArrayList`, `ConcurrentHashMap` |

### Turning an Iterator into a Java `Stream<T>`
Using `Spliterators.spliteratorUnknownSize(iterator, Spliterator.ORDERED)` with `StreamSupport.stream(spliterator, false)` lets any custom `Iterator` plug directly into Java Streams (`filter`, `map`, `limit`).

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Hides internal storage & pagination details | Overkill for simple fixed arrays |
| Enables lazy streaming with constant memory | Fail-fast iterators fail if collection is mutated mid-loop |
| Supports multiple independent traversals at once | `remove()` is optional and often throws `UnsupportedOperationException` |
