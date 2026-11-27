# Proxy Pattern

The **Proxy** pattern provides a **surrogate or placeholder** for another object to control access to it—performing work before or after forwarding the request to the real object.

---

## 1. The Problem It Solves

Sometimes callers should not talk directly to a target object because:
- The target is **expensive to initialize** and may never be used (lazy loading).
- Access requires **authorization checks**, **rate limiting**, or **caching**.
- The real object lives in a **remote service** or requires **cross-cutting transactions**.

---

## 2. Structure

```text
  [Client] ---> [ReportService <<interface>>]
                          ^
               +----------+----------+
               |                     |
      [RealReportService]    [CachingReportProxy]
                               - real : ReportService
                               + generate(id) -> cache or delegate
```

Because both `Proxy` and `RealService` implement the same interface, the client cannot tell (and does not care) that it is talking to a proxy.

---

## 3. Common Types of Proxies

| Proxy Type | Purpose |
| :--- | :--- |
| **Virtual Proxy** | Delays creating an expensive object until first use (lazy init) |
| **Protection Proxy** | Checks caller roles/permissions before forwarding |
| **Caching Proxy** | Stores results of expensive calls for repeated inputs |
| **Remote Proxy** | Local stub representing a remote HTTP/gRPC/RMI service |
| **Transactional / Metrics Proxy** | Opens transactions or records latency transparently |

---

## 4. Deep-Dive Java Examples

### A. Virtual + Caching Proxy (Explicit Class)
```java
public interface VideoLibrary {
    VideoInfo getVideo(String id);
}

public final class CachingVideoProxy implements VideoLibrary {
    private final Supplier<VideoLibrary> factory;
    private final Map<String, VideoInfo> cache =
        new ConcurrentHashMap<>();
    private VideoLibrary real;

    public CachingVideoProxy(Supplier<VideoLibrary> factory) {
        this.factory = factory;
    }

    @Override
    public VideoInfo getVideo(String id) {
        return cache.computeIfAbsent(id, key -> {
            if (real == null) {
                real = factory.get(); // lazy virtual init
            }
            return real.getVideo(key);
        });
    }
}
```

### B. Java Dynamic Proxy (`java.lang.reflect.Proxy`)
Java's standard library can generate proxy instances at runtime for **any interface** using `InvocationHandler`—avoiding boilerplate when wrapping many methods:

```java
public final class TimingHandler implements InvocationHandler {
    private final Object target;

    public TimingHandler(Object target) {
        this.target = target;
    }

    @Override
    public Object invoke(
        Object proxy, Method method, Object[] args
    ) throws Throwable {
        long start = System.nanoTime();
        try {
            return method.invoke(target, args);
        } finally {
            long ms = (System.nanoTime() - start) / 1_000_000;
            System.out.println(method.getName() + ": " + ms + "ms");
        }
    }
}
```

Creating the proxy in Java:

```java
VideoLibrary timed = (VideoLibrary) Proxy.newProxyInstance(
    VideoLibrary.class.getClassLoader(),
    new Class<?>[] { VideoLibrary.class },
    new TimingHandler(new RealVideoLibrary())
);
```

---

## 5. Frameworks & The Java Self-Invocation Pitfall

- **Spring AOP & Hibernate:** Use JDK Dynamic Proxies (for interfaces) or **CGLIB/ByteBuddy** subclass proxies (for classes) to implement `@Transactional`, `@Cacheable`, and `@Lazy` JPA associations.
- **Self-Invocation Pitfall:** In Java, if `methodA()` inside `RealService` calls `this.methodB()`, the call bypasses the proxy (`this` is the raw target, not the proxy), so `@Transactional` or `@Cacheable` on `methodB()` will **not** trigger.

---

## 6. Proxy vs. Decorator

| Dimension | Proxy | Decorator |
| :--- | :--- | :--- |
| **Primary Intent** | Control access or manage lifecycle | Dynamically stack extra behavior |
| **Who Wires It** | Often created/managed by framework or factory | Explicitly stacked by client code |
| **Target Creation** | Virtual proxy may instantiate target lazily | Decorator always receives an existing instance |
