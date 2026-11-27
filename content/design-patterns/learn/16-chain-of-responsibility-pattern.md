# Chain of Responsibility Pattern

The **Chain of Responsibility** pattern passes a request along a **chain of handlers**. Upon receiving a request, each handler decides either to process it, enrich it, short-circuit it, or forward it to the next handler in the chain.

---

## 1. The Problem It Solves

In an HTTP API, webhook processor, or order validation pipeline, every incoming request may need authentication, IP rate limiting, payload sanitization, fraud scoring, and schema validation. Cramming all checks into one monolithic method with nested `if/else` blocks makes it hard to reorder, toggle, or unit-test individual steps.

---

## 2. Structure & Two Chain Variants

```text
  [Client] ---> [AuthFilter] ---> [RateLimitFilter] ---> [AuditFilter]
                 | fail: 401       | fail: 429            | pass: OK
```

There are two common variants in production Java systems:
1. **Short-Circuit (Intercepting) Chain:** The first handler that rejects (or fully handles) the request stops the chain immediately (e.g., `AuthFilter` returning `401`).
2. **Pass-Through (Pipeline) Chain:** Every handler inspects or enriches a shared context and passes it along, similar to middleware or event enrichment pipelines.

---

## 3. Deep-Dive Java Example: Functional + Classic Chain

You can build a clean, immutable chain in Java where each step receives the request and a `next` continuation—just like Jakarta Servlet `FilterChain`:

```java
public record ApiRequest(String user, String ip, String payload) {}
public record ApiResponse(int status, String body) {}

@FunctionalInterface
public interface FilterChain {
    ApiResponse proceed(ApiRequest request);
}

public interface RequestFilter {
    ApiResponse filter(ApiRequest request, FilterChain next);
}
```

Implementing concrete filters for authentication and rate limiting:

```java
public final class AuthFilter implements RequestFilter {
    @Override
    public ApiResponse filter(ApiRequest req, FilterChain next) {
        if (req.user() == null || req.user().isBlank()) {
            return new ApiResponse(401, "Missing user");
        }
        return next.proceed(req); // forward to next handler
    }
}

public final class LoggingFilter implements RequestFilter {
    @Override
    public ApiResponse filter(ApiRequest req, FilterChain next) {
        long start = System.nanoTime();
        ApiResponse res = next.proceed(req);
        long ms = (System.nanoTime() - start) / 1_000_000;
        System.out.println(req.user() + " -> " + res.status()
            + " (" + ms + "ms)");
        return res;
    }
}
```

Assembling the chain with a terminal handler at the end:

```java
public final class FilterPipeline {
    public static FilterChain build(
        List<RequestFilter> filters,
        FilterChain terminal
    ) {
        FilterChain chain = terminal;
        for (int i = filters.size() - 1; i >= 0; i--) {
            RequestFilter current = filters.get(i);
            FilterChain next = chain;
            chain = req -> current.filter(req, next);
        }
        return chain;
    }
}
```

Notice how `LoggingFilter` runs code **both before and after** `next.proceed(req)`, making it ideal for timing, transactions, and exception mapping.

---

## 4. Real-World Java Examples

- **Jakarta Servlet `Filter` & `FilterChain`:** Classic web filter pipeline.
- **Spring Security `SecurityFilterChain`:** Chains CORS, CSRF, JWT/session auth, and authorization filters.
- **Netty `ChannelPipeline`:** Chains inbound and outbound network codecs and handlers.
- **`java.util.logging.Logger`:** Delegates log records up parent logger hierarchies.

---

## 5. Chain of Responsibility vs. Decorator

| Dimension | Chain of Responsibility | Decorator |
| :--- | :--- | :--- |
| **Control Flow** | Any handler can **short-circuit** and stop execution | Decorators typically all execute around the target |
| **Target** | Usually ends at a terminal handler or fallback | Always wraps a core `Component` |
| **Awareness** | Handlers are independent pipeline stages | Wrappers enhance one specific object's contract |

---

## 6. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Decouples sender from concrete handlers | Request may go unhandled if no terminal fallback exists |
| Reorder, add, or remove filters without editing callers | Long chains can make stack traces deeper to debug |
| Single Responsibility per filter | Misordered filters (e.g., auth after body parse) cause bugs |
