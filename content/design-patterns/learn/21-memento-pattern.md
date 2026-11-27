# Memento Pattern

The **Memento** pattern lets you **save and restore** the previous state of an object without exposing its private implementation details to external classes.

---

## 1. The Problem It Solves

To build an Undo feature, "Restore Draft" button, or transaction rollback, you might be tempted to expose every internal field of a domain object via public getters and setters. Doing so **breaks encapsulation**—any caller can read or mutate internal invariants directly.

---

## 2. Structure (Wide vs. Narrow Interface)

```text
  [Caretaker] ----stores----> [Memento] (Narrow: opaque token)
       |                          ^
       | save() / restore()       | creates & reads (Wide: full state)
       v                          |
  [Originator] -------------------+
```

- **Originator:** Creates snapshots of its own internal state and restores from them.
- **Memento:** Holds the saved state. External callers see only a **narrow** opaque interface (e.g., `timestamp()`), while the Originator accesses the **wide** internal fields.
- **Caretaker:** Manages the history stack without inspecting or mutating Memento contents.

---

## 3. Deep-Dive Java Example (Opaque Snapshot + Bounded History)

Using a `private` nested class inside `Document` guarantees **strict encapsulation**—the `History` caretaker can store `DocumentMemento` tokens without ever reading `content` or `cursor`:

```java
public interface DocumentMemento {
    Instant savedAt();
}

public final class Document {
    private String content = "";
    private int cursor = 0;

    public void write(String text) {
        this.content += text;
        this.cursor = this.content.length();
    }

    public DocumentMemento save() {
        return new Snapshot(content, cursor, Instant.now());
    }

    public void restore(DocumentMemento memento) {
        if (!(memento instanceof Snapshot snap)) {
            throw new IllegalArgumentException("Invalid memento");
        }
        this.content = snap.content;
        this.cursor = snap.cursor;
    }

    public String content() { return content; }

    private record Snapshot(
        String content,
        int cursor,
        Instant savedAt
    ) implements DocumentMemento {}
}
```

Now a **Caretaker** (`BoundedHistory`) caps memory usage by evicting the oldest snapshot when the limit is reached:

```java
public final class BoundedHistory {
    private final int maxSnapshots;
    private final Deque<DocumentMemento> stack = new ArrayDeque<>();

    public BoundedHistory(int maxSnapshots) {
        this.maxSnapshots = maxSnapshots;
    }

    public void push(DocumentMemento snap) {
        if (stack.size() >= maxSnapshots) {
            stack.removeLast(); // evict oldest snapshot
        }
        stack.push(snap);
    }

    public Optional<DocumentMemento> pop() {
        return Optional.ofNullable(stack.poll());
    }
}
```

---

## 4. Memento vs. Command vs. Event Sourcing

| Approach | What It Stores | Best For |
| :--- | :--- | :--- |
| **Memento** | Full immutable state snapshot | Complex state where inverse actions are hard to compute |
| **Command** | Action + inverse `undo()` delta | Lightweight edits with clear reversible operations |
| **Event Sourcing** | Append-only domain events + periodic snapshots | Distributed audit logs & temporal queries |

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Preserves strict encapsulation of private fields | High RAM usage if large objects are snapshotted often |
| Keeps `Originator` focused on domain logic, not history | Caretaker must bound or prune history to prevent leaks |
