# Bridge Pattern

The **Bridge** pattern splits a large class or closely related set of classes into two separate hierarchies—**Abstraction** and **Implementation**—so that both can vary independently.

---

## 1. The Problem It Solves

Suppose you have two independent dimensions of variation: **Notification Type** (`Alert`, `Digest`, `Promo`) and **Delivery Channel** (`Email`, `Sms`, `Push`). Using inheritance alone produces a combinatorial explosion of subclasses: `EmailAlert`, `SmsAlert`, `PushAlert`, `EmailDigest`, `SmsDigest`, etc. ($M \times N$ classes).

Even worse in Java, single class inheritance means you cannot easily inherit from both `UrgentNotification` and `RetryableSender` at the same time.

---

## 2. Structure

```text
  [Notification (Abstraction)] --------> [Channel <<interface>>]
    # channel : Channel                    + send(title, body)
    + notify(msg)                                  ^
          ^                                        |
    +-----+------+                       +---------+---------+
    |            |                       |                   |
[Alert]      [Digest]              [EmailChannel]      [SmsChannel]
```

Instead of $M \times N$ subclasses, you maintain $M + N$ classes connected by composition (the "bridge").

---

## 3. Deep-Dive Java Example

Here, the **Implementation** hierarchy (`MessageChannel`) handles low-level transport, while the **Abstraction** hierarchy (`Notification`) handles formatting, priority, and workflow:

```java
// Implementation hierarchy
public interface MessageChannel {
    void deliver(String title, String body);
}

public final class EmailChannel implements MessageChannel {
    @Override
    public void deliver(String title, String body) {
        System.out.println("[EMAIL] " + title + ": " + body);
    }
}

public final class SmsChannel implements MessageChannel {
    @Override
    public void deliver(String title, String body) {
        String shortBody = body.substring(
            0, Math.min(body.length(), 140)
        );
        System.out.println("[SMS] " + title + ": " + shortBody);
    }
}
```

Now the **Abstraction** hierarchy holds a `MessageChannel` reference (the bridge) and can evolve independently:

```java
// Abstraction hierarchy
public abstract class Notification {
    protected final MessageChannel channel;

    protected Notification(MessageChannel channel) {
        this.channel = channel;
    }

    public abstract void send(String recipient, String text);
}

public final class UrgentAlert extends Notification {
    public UrgentAlert(MessageChannel channel) {
        super(channel);
    }

    @Override
    public void send(String recipient, String text) {
        String title = "URGENT for " + recipient;
        channel.deliver(title, text.toUpperCase());
    }
}

public final class WeeklyDigest extends Notification {
    public WeeklyDigest(MessageChannel channel) {
        super(channel);
    }

    @Override
    public void send(String recipient, String text) {
        channel.deliver("Weekly Summary", text);
    }
}
```

At runtime, you can mix and match any pair freely—and test `UrgentAlert` with a mock or fake `MessageChannel` in milliseconds:

```java
Notification smsAlert = new UrgentAlert(new SmsChannel());
Notification emailDigest = new WeeklyDigest(new EmailChannel());
```

---

## 4. Real-World Java Examples

- **JDBC (`java.sql`):** `Connection`, `Statement`, and `ResultSet` form the abstraction; vendor drivers (PostgreSQL, MySQL, Oracle) supply the concrete implementation hierarchy.
- **SLF4J:** The `Logger` API is decoupled from logging backends like Logback or Log4j2.

---

## 5. Bridge vs. Adapter (Timing & Intent)

| Dimension | Bridge | Adapter |
| :--- | :--- | :--- |
| **When Applied** | **Up front** during architecture design | **Retroactively** to integrate legacy/3rd-party code |
| **Intent** | Let two hierarchies vary independently | Make incompatible interfaces compatible |
| **Java Shape** | Abstract class + injected interface | Wrapper implementing target, calling adaptee |

---

## 6. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Prevents $M \times N$ class explosion | Adds indirection if one dimension rarely changes |
| Channels can be swapped at runtime | Harder to grasp initially than simple inheritance |
| Both hierarchies follow Open/Closed Principle | |
