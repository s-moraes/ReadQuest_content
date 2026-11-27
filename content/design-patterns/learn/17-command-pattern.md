# Command Pattern

The **Command** pattern turns a request into a **stand-alone object** containing all information needed to execute it. This lets you parameterize methods with requests, queue or log operations, retry failures, and support **undo/redo**.

---

## 1. The Problem It Solves

If UI buttons, keyboard shortcuts, or REST endpoints directly call `document.boldSelection()` or `bankAccount.withdraw(500)`, you lose the ability to:
- Queue or schedule actions on background threads.
- Record a history of executed operations for **undo/redo**.
- Retry or replay failed actions from an audit log.

---

## 2. Structure

```text
  [Invoker] ---> [Command <<interface>>] <--- [ConcreteCommand]
  (History/Queue)  + execute()                  - receiver
                   + undo()                     - args / prevState
                                                + execute() -> receiver.op()
```

- **Command:** Interface declaring `execute()` (and `undo()` if reversible).
- **ConcreteCommand:** Binds a `Receiver` and its parameters into one object.
- **Invoker:** Executes commands and optionally stores them in a queue or undo stack.
- **Receiver:** The domain object that performs the actual work.

---

## 3. Deep-Dive Java Example: Undo / Redo History

```java
public interface EditorCommand {
    void execute();
    void undo();
}

public final class TextBuffer {
    private final StringBuilder sb = new StringBuilder();

    public void append(String text) { sb.append(text); }

    public void deleteTail(int count) {
        int start = Math.max(0, sb.length() - count);
        sb.delete(start, sb.length());
    }

    public String text() { return sb.toString(); }
}

public final class AppendCommand implements EditorCommand {
    private final TextBuffer buffer;
    private final String chunk;

    public AppendCommand(TextBuffer buffer, String chunk) {
        this.buffer = buffer;
        this.chunk = chunk;
    }

    @Override
    public void execute() { buffer.append(chunk); }

    @Override
    public void undo() { buffer.deleteTail(chunk.length()); }
}
```

Now an **Invoker** (`CommandHistory`) manages both undo and redo stacks cleanly:

```java
public final class CommandHistory {
    private final Deque<EditorCommand> undoStack = new ArrayDeque<>();
    private final Deque<EditorCommand> redoStack = new ArrayDeque<>();

    public void run(EditorCommand cmd) {
        cmd.execute();
        undoStack.push(cmd);
        redoStack.clear(); // new action invalidates redo branch
    }

    public void undo() {
        if (!undoStack.isEmpty()) {
            EditorCommand cmd = undoStack.pop();
            cmd.undo();
            redoStack.push(cmd);
        }
    }

    public void redo() {
        if (!redoStack.isEmpty()) {
            EditorCommand cmd = redoStack.pop();
            cmd.execute();
            undoStack.push(cmd);
        }
    }
}
```

---

## 4. Macro Commands & Queuing

Because commands share a single interface, you can group multiple commands into a **MacroCommand** (combining Command + Composite) or serialize command DTOs into a database job queue (`Outbox` pattern) for asynchronous workers.

### Real-World Java Examples
- **`java.lang.Runnable` & `Callable<V>`:** Encapsulate tasks submitted to an `ExecutorService` or `ScheduledExecutorService`.
- **Swing `javax.swing.Action`:** Binds menu items, toolbar buttons, and shortcuts to one command object.
- **Spring `TransactionTemplate` / `JdbcTemplate`:** Pass callback commands to execute inside managed resource/transaction boundaries.

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Enables undo/redo, queuing, and macro batching | Increases class count for simple one-off calls |
| Decouples invoker from receiver implementation | Reversible commands must capture prior state carefully |
| Easy to log or audit every executed operation | Non-idempotent commands need care during retries |
