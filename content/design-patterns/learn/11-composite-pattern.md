# Composite Pattern

The **Composite** pattern composes objects into **tree structures** to represent part-whole hierarchies, allowing clients to treat **individual objects (leaves)** and **compositions of objects (containers)** uniformly.

---

## 1. The Problem It Solves

Consider a file system (files and folders) or an order pricing engine (single products and nested gift boxes). Without Composite, callers must constantly write `if (item instanceof Box) ... else ...`, duplicating recursive traversal logic across billing, reporting, and UI rendering code.

---

## 2. Structure

```text
           [CatalogItem <<interface>>]
           + priceCents() : long
           + printTree(indent)
                     ^
          +----------+----------+
          |                     |
   [SingleProduct]         [BundleBox]
   (Leaf)                  (Composite)
                           - children : List<CatalogItem>
                           + priceCents() -> sum(children)
```

- **Component (`CatalogItem`):** Common interface for both leaves and containers.
- **Leaf (`SingleProduct`):** Terminal node with no children.
- **Composite (`BundleBox`):** Container storing child `CatalogItem` references and delegating operations recursively.

---

## 3. Deep-Dive Java Example

Using Java `record` for immutable leaves and defensive copying in the composite keeps the tree clean and safe:

```java
public interface CatalogItem {
    String name();
    long priceCents();
}

public record SingleProduct(String name, long cents)
    implements CatalogItem {
    @Override
    public long priceCents() { return cents; }
}

public final class BundleBox implements CatalogItem {
    private final String name;
    private final long discountCents;
    private final List<CatalogItem> items = new ArrayList<>();

    public BundleBox(String name, long discountCents) {
        this.name = name;
        this.discountCents = discountCents;
    }

    public void add(CatalogItem item) {
        if (item == this) {
            throw new IllegalArgumentException("Cycle detected");
        }
        items.add(Objects.requireNonNull(item));
    }

    public List<CatalogItem> children() {
        return List.copyOf(items);
    }

    @Override
    public String name() { return name; }

    @Override
    public long priceCents() {
        long sum = items.stream()
            .mapToLong(CatalogItem::priceCents)
            .sum();
        return Math.max(0, sum - discountCents);
    }
}
```

Building and pricing a multi-level tree requires zero `instanceof` checks in client code:

```java
BundleBox starterKit = new BundleBox("Starter Kit", 500);
starterKit.add(new SingleProduct("USB-C Cable", 1500));
starterKit.add(new SingleProduct("Wall Charger", 3000));

BundleBox officePack = new BundleBox("Office Pack", 1000);
officePack.add(starterKit);
officePack.add(new SingleProduct("Laptop Stand", 6000));

long total = officePack.priceCents(); // 9000 cents
```

---

## 4. Key Java Design Decisions & Pitfalls

1. **Where should `add()` / `remove()` live?**
   - **On `BundleBox` only (Type-Safe):** Prevents callers from calling `singleProduct.add(...)`, which respects the Interface Segregation Principle.
   - **On `CatalogItem` (Transparent):** Lets callers build trees without knowing container types, but forces leaves to throw `UnsupportedOperationException`.
2. **Restricting Child Types:** Because `BundleBox` accepts any `CatalogItem`, restricting a specific box to only hold `SingleProduct` (or preventing cycles) requires **runtime validation** rather than purely compile-time checks.
3. **Java `sealed` Interfaces:** In Java 17+, `public sealed interface CatalogItem permits SingleProduct, BundleBox` gives exhaustive `switch` support when you occasionally need type-specific rendering.

---

## 5. Real-World Java Examples

- **Java Swing / AWT:** `java.awt.Container` extends `java.awt.Component`, allowing panels to nest buttons and other panels uniformly.
- **Spring Boot Actuator:** `CompositeHealthContributor` aggregates individual `HealthIndicator` leaves and nested health groups.
- **Jackson `JsonNode`:** Models JSON primitives, arrays, and nested objects under one tree abstraction.

---

## 6. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Uniform treatment of trees and single items | Harder to restrict child types at compile time |
| Eliminates `instanceof` branching in callers | Risk of cycles if parent/child checks are omitted |
| Easy to add new leaf or container types | Transparent `add()` on leaves violates ISP |
