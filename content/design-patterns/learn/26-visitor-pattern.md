# Visitor Pattern

The **Visitor** pattern lets you separate **algorithms from the object structures** on which they operate, allowing you to add new operations across a stable hierarchy of element classes without modifying those element classes.

---

## 1. The Problem It Solves

You have an AST or billing document with `Book`, `Electronics`, and `GiftCard` classes. Tomorrow you need a `TaxCalculator`, next week a `JsonExporter`, and next month a `ShippingEstimator`. Putting every new operation inside `Book`, `Electronics`, and `GiftCard` bloats those domain classes with unrelated infrastructure code.

---

## 2. Structure (Double Dispatch)

```text
  [Element <<interface>>]               [CartVisitor <<interface>>]
  + accept(CartVisitor v)               + visit(Book b)
          ^                             + visit(Electronics e)
          |
  [Book] -> accept(v) { v.visit(this); }
```

**Double Dispatch:** Calling `element.accept(visitor)` resolves the concrete `Element` type first, and `visitor.visit(this)` resolves the concrete `Visitor` operation second—without `instanceof` chains.

---

## 3. Java Example

```java
public interface CartItem {
    void accept(CartVisitor visitor);
}

public record Book(String title, long priceCents) implements CartItem {
    @Override
    public void accept(CartVisitor v) { v.visit(this); }
}

public record Electronics(String sku, long priceCents)
    implements CartItem {
    @Override
    public void accept(CartVisitor v) { v.visit(this); }
}

public interface CartVisitor {
    void visit(Book book);
    void visit(Electronics electronics);
}

public final class TaxVisitor implements CartVisitor {
    private long totalTaxCents = 0;

    @Override
    public void visit(Book book) { /* books tax-exempt */ }

    @Override
    public void visit(Electronics item) {
        totalTaxCents += (long) (item.priceCents() * 0.15);
    }

    public long totalTaxCents() { return totalTaxCents; }
}
```

### Real-World Java Examples
- **`java.nio.file.Files.walkFileTree` (`FileVisitor`):** Separates directory traversal from file-handling operations (`visitFile`, `preVisitDirectory`).
- **Java Compilers & Linters (ASM, Javac AST):** Traverse syntax nodes with `TreeVisitor`.

*(Note: In Java 21+, `sealed` interfaces + pattern matching `switch` often replace classic Visitor with less boilerplate.)*

---

## 4. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Easy to add **new operations** without editing element classes | Adding a **new element class** requires updating every Visitor |
| Groups related operation logic in one Visitor class | Double dispatch boilerplate can feel verbose |
