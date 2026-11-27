# Template Method Pattern

The **Template Method** pattern defines the **skeleton of an algorithm** in an abstract base class, deferring specific customizable steps to subclasses without changing the overall algorithm's structure.

---

## 1. The Problem It Solves

Suppose you have three data importers: `CsvImporter`, `JsonImporter`, and `XmlImporter`. All three open a file, parse records, validate rows, save to the database, and close resources. Only the *parsing* step differs—duplicating the outer workflow across three classes invites subtle bugs.

---

## 2. Structure

```text
  [DataImporter (abstract)]
  + importData(path)  <-- final template method
      1. open(path)
      2. parseRecords()  <-- abstract hook
      3. validate()
      4. save()
            ^
     +------+------+
     |             |
  [CsvImporter] [JsonImporter]
```

---

## 3. Java Example

```java
public abstract class ReportExporter {
    // 'final' prevents subclasses from altering the workflow order
    public final String export(List<String> rows) {
        String header = formatHeader();
        String body = formatRows(rows);
        return header + "\n" + body;
    }

    protected abstract String formatHeader();
    protected abstract String formatRows(List<String> rows);
}

public final class CsvExporter extends ReportExporter {
    @Override
    protected String formatHeader() { return "item,status"; }

    @Override
    protected String formatRows(List<String> rows) {
        return String.join("\n", rows);
    }
}
```

### Real-World Java Examples
- **`java.util.AbstractList`:** Implements `indexOf`, `equals`, and `iterator` on top of subclass-supplied `get(int)` and `size()`.
- **Spring `JdbcTemplate` / `RestTemplate`:** Handles resource acquisition and exception translation while delegating query mapping.

---

## 4. Template Method vs. Strategy

- **Template Method** uses **inheritance** (class-scope) to vary *parts* of an algorithm.
- **Strategy** uses **composition** (object-scope) to swap an *entire* algorithm at runtime.

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Eliminates duplicated workflow boilerplate | Relies on inheritance (tighter coupling than Strategy) |
| Enforces invariant step ordering via `final` | Violates Liskov Substitution if subclasses break base assumptions |
