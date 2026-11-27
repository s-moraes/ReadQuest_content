# Flyweight Pattern

The **Flyweight** pattern minimizes memory usage by **sharing common, immutable state** across thousands or millions of fine-grained objects instead of duplicating that data in every instance.

---

## 1. The Problem It Solves

In a game engine rendering a forest of 500,000 trees, each `Tree` object might hold a 20 KB texture, mesh, and color palette alongside `(x, y)` coordinates. Storing 20 KB × 500,000 trees consumes **10 GB** of RAM and crashes the process.

---

## 2. Intrinsic vs. Extrinsic State

Flyweight splits object state into two parts:

1. **Intrinsic State (Shared, Immutable):** Heavy data that is identical across many instances (e.g., `TreeType`: mesh, bark texture, leaf color). Stored inside the Flyweight.
2. **Extrinsic State (Unique, Contextual):** Lightweight data that varies per instance (e.g., `x`, `y`, `scale`). Passed in by the caller or stored in a lightweight wrapper.

```text
  [Tree (500k instances)]         [TreeType (Flyweight, ~5 instances)]
    - x, y, scale                   - name, mesh, texture (immutable)
    - type  --------------------->  + draw(x, y, scale)
```

---

## 3. Code Example

```java
public record TreeType(String name, String texture) {
    public void draw(int x, int y) {
        // Render using shared texture at unique (x, y)
    }
}

public final class TreeTypeFactory {
    private static final Map<String, TreeType> CACHE =
        new HashMap<>();

    public static TreeType get(String name, String texture) {
        return CACHE.computeIfAbsent(
            name, k -> new TreeType(k, texture)
        );
    }
}
```

Java's `Integer.valueOf(int)` (caching `-128..127`) and `String.intern()` are built-in Flyweight examples.

---

## 4. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Dramatically reduces RAM for massive object counts | Trades CPU lookup time for memory savings |
| Centralizes shared immutable assets | Increases code complexity (splitting state) |
| | Only worthwhile when profiling proves memory pressure |
