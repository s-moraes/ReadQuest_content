# Singleton Pattern

The **Singleton** pattern ensures that a class has **only one instance** across the application and provides a **global point of access** to it.

---

## 1. The Problem It Solves

Certain components represent shared, singular resources—such as a hardware device driver, an in-memory metrics registry, or a connection pool manager. Creating multiple instances wastes memory, duplicates state, or causes conflicting writes to the same underlying resource.

---

## 2. Structure & Implementation

A classic Singleton hides its constructor (`private`), stores the single instance in a `static` field, and exposes a `static getInstance()` method.

```text
+-----------------------------------+
|            Singleton              |
+-----------------------------------+
| - instance : Singleton            |
+-----------------------------------+
| - Singleton()                     |
| + getInstance() : Singleton       |
+-----------------------------------+
```

### Thread-Safe Approaches in Java

1. **Initialization-on-Demand Holder (Bill Pugh):** Lazy-loaded and thread-safe without `synchronized` overhead, relying on JVM class-loading guarantees.

```java
public final class ConfigRegistry {
    private ConfigRegistry() {}

    private static final class Holder {
        private static final ConfigRegistry INSTANCE =
            new ConfigRegistry();
    }

    public static ConfigRegistry getInstance() {
        return Holder.INSTANCE;
    }
}
```

2. **Enum Singleton:** Concise, thread-safe, and immune to reflection or deserialization attacks.

```java
public enum AppClock {
    INSTANCE;

    public long nowEpochMs() {
        return System.currentTimeMillis();
    }
}
```

---

## 3. Trade-Offs & Why It Is Controversial

| Pros | Cons |
| :--- | :--- |
| Controlled single instance | Acts like global mutable state |
| Lazy initialization possible | Hides dependencies in callers |
| Saves memory for heavy objects | Hard to mock or isolate in unit tests |

### Modern Alternative: Dependency Injection
In modern frameworks (Spring, Quarkus, Dagger), you rarely hand-code Singletons. Instead, you write a normal class and let the DI container manage a **singleton scope**, keeping the class easy to test and swap.

---

## 4. When to Use

- Only when there is a **strict domain or hardware requirement** for a single instance and DI container scoping is unavailable.
- Avoid using Singleton merely as a convenient global variable bag.
