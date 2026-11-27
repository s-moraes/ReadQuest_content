# Builder Pattern

The **Builder** pattern separates the **construction of a complex object** from its final representation, allowing you to construct objects step by step with clean, readable code.

---

## 1. The Problem It Solves

Objects with many optional fields often suffer from the **telescoping constructor** anti-pattern:

```java
// Hard to read, easy to swap boolean or int arguments!
new HttpClient(5000, 3000, true, false, null, "TLSv1.3", 3);
```

Using setters (`client.setTimeout(...)`) solves readability, but leaves the object **mutable** and potentially **partially initialized** (invalid state) between setter calls.

---

## 2. Structure

```text
  [Client] ---> [Order.Builder]
                  .customerId("C-42")
                  .addItem(sku, qty)
                  .coupon("SAVE10")
                  .build()  ----------> [Immutable Order]
```

- **Product:** The complex, often immutable object being constructed.
- **Builder:** Holds temporary configuration state, exposes fluent setter methods returning `this`, and validates invariants inside `build()`.
- **Director (optional):** Encapsulates reusable construction recipes (e.g., `buildExpressOrder()`).

---

## 3. Code Example

```java
public final class HttpRequest {
    private final String url;
    private final String method;
    private final int timeoutMs;

    private HttpRequest(Builder b) {
        this.url = b.url;
        this.method = b.method;
        this.timeoutMs = b.timeoutMs;
    }

    public static Builder builder(String url) {
        return new Builder(url);
    }

    public static final class Builder {
        private final String url;
        private String method = "GET";
        private int timeoutMs = 5000;

        private Builder(String url) { this.url = url; }

        public Builder method(String m) {
            this.method = m;
            return this;
        }

        public Builder timeoutMs(int ms) {
            this.timeoutMs = ms;
            return this;
        }

        public HttpRequest build() {
            if (timeoutMs <= 0) {
                throw new IllegalArgumentException("Invalid timeout");
            }
            return new HttpRequest(this);
        }
    }
}
```

---

## 4. When to Use & Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Eliminates telescoping constructors | Requires writing extra Builder boilerplate |
| Supports immutable target objects | Duplicates fields between product and builder |
| Validates invariants atomically in `build()` | Overkill for objects with 2–3 required fields |

**Tip:** Require mandatory fields in the `Builder` constructor (`builder(url)`), and keep optional settings as fluent methods with sensible defaults.
