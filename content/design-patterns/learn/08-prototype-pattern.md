# Prototype Pattern

The **Prototype** pattern lets you create new objects by **cloning an existing instance** (the prototype) rather than instantiating a class from scratch via `new`.

---

## 1. The Problem It Solves

Sometimes creating an object from scratch is expensive or awkward:
1. **Heavy Initialization:** Building the object requires parsing a large template, querying a database, or running costly computations.
2. **Unknown Concrete Types:** Your code holds an interface reference to a configured object and needs an exact copy without knowing its concrete subclass or private fields.

---

## 2. Structure

```text
  [Client] ---> [Prototype <<interface>>]
                  + clone() : Prototype
                          ^
                          |
                [DocumentTemplate]
                  - styles : List<Style>
                  + clone() : DocumentTemplate
```

Instead of calling `new DocumentTemplate(...)` and re-populating every field, the client calls `template.clone()` and mutates only what differs.

---

## 3. Shallow Copy vs. Deep Copy

The biggest pitfall in Prototype is **shared mutable state**:

- **Shallow Copy:** Copies primitive fields and object *references*. Both original and clone point to the **same** nested `List` or `Map`—mutating one corrupts the other.
- **Deep Copy:** Recursively clones nested mutable objects so the clone is 100% independent.

```java
public interface Prototype<T> {
    T copy();
}

public final class ReportConfig implements Prototype<ReportConfig> {
    private String title;
    private final List<String> columns;

    public ReportConfig(String title, List<String> columns) {
        this.title = title;
        this.columns = new ArrayList<>(columns);
    }

    @Override
    public ReportConfig copy() {
        // Deep copy of mutable list prevents shared-state bugs
        return new ReportConfig(title, new ArrayList<>(columns));
    }
}
```

> **Note on Java's `Cloneable`:** In Java, prefer a custom `copy()` method or **copy constructor** (`new ReportConfig(other)`) over `Object.clone()`, which has checked-exception quirks and skips constructors.

---

## 4. Prototype Registry

Applications often pair Prototype with a **Registry** (a `Map<String, Prototype>`) holding pre-configured templates (e.g., `"invoice-pdf"`, `"monthly-summary"`). Callers fetch by key and clone on demand.

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Avoids expensive repeated initialization | Deep-copying circular object graphs is tricky |
| Clones objects without coupling to concrete classes | Easy to introduce subtle shallow-copy bugs |
| Reduces subclassing for pre-configured variants | |
