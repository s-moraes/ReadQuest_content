# Decorator Pattern

The **Decorator** pattern attaches additional responsibilities to an object **dynamically** by wrapping it inside another object that implements the **same interface**. It is a flexible alternative to subclassing for extending functionality.

---

## 1. The Problem It Solves

Imagine a `DataSource` that reads and writes payloads. You want optional compression, encryption, and metrics logging—in any combination. Subclassing (`CompressedEncryptedDataSource`, `LoggedCompressedDataSource`) creates a combinatorial explosion of rigid classes that cannot be reconfigured at runtime.

---

## 2. Structure

```text
  [Client] ---> [DataSource <<interface>>]
                          ^
               +----------+----------+
               |                     |
      [FileDataSource]      [DataSourceDecorator]
                             # wrappee : DataSource
                                     ^
                          +----------+----------+
                          |                     |
               [EncryptionDecorator] [CompressionDecorator]
```

Every decorator implements `DataSource`, holds a reference to an inner `DataSource`, and delegates to it before or after adding its own behavior.

---

## 3. Deep-Dive Java Example: Stackable Stream Pipeline

Consider a `PayloadStore` interface with a base implementation and two composable Java decorators:

```java
public interface PayloadStore {
    void write(String key, byte[] data);
    byte[] read(String key);
}

public final class MemoryPayloadStore implements PayloadStore {
    private final Map<String, byte[]> db = new HashMap<>();

    @Override
    public void write(String key, byte[] data) {
        db.put(key, data);
    }

    @Override
    public byte[] read(String key) {
        return db.getOrDefault(key, new byte[0]);
    }
}
```

Now create a base decorator and concrete decorators that transform data on the way in and out:

```java
public abstract class PayloadDecorator implements PayloadStore {
    protected final PayloadStore delegate;

    protected PayloadDecorator(PayloadStore delegate) {
        this.delegate = Objects.requireNonNull(delegate);
    }
}

public final class XorEncryptionDecorator extends PayloadDecorator {
    private final byte secret;

    public XorEncryptionDecorator(PayloadStore delegate, byte secret) {
        super(delegate);
        this.secret = secret;
    }

    @Override
    public void write(String key, byte[] data) {
        delegate.write(key, xor(data));
    }

    @Override
    public byte[] read(String key) {
        return xor(delegate.read(key));
    }

    private byte[] xor(byte[] input) {
        byte[] out = new byte[input.length];
        for (int i = 0; i < input.length; i++) {
            out[i] = (byte) (input[i] ^ secret);
        }
        return out;
    }
}
```

---

## 4. Why Wrapping Order Matters in Java

When stacking decorators, **execution order changes the outcome**:

```java
// Correct: compress first (inner), then encrypt (outer)
PayloadStore store = new XorEncryptionDecorator(
    new GzipCompressionDecorator(
        new MemoryPayloadStore()
    ),
    (byte) 0x5A
);
```

- **Compress then Encrypt:** Structured text compresses well; encrypted bytes are then stored securely.
- **Encrypt then Compress:** Encrypted output looks like random noise, so GZIP cannot find patterns and may even *increase* payload size.

### Java Standard Library Examples
- **`java.io` Streams:** `new BufferedReader(new InputStreamReader(new GZIPInputStream(fileIn)))`
- **`java.util.Collections`:** `Collections.unmodifiableList(list)` and `Collections.synchronizedList(list)` wrap a `List` while preserving the `List` contract.

---

## 5. Java Caveats & Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Stack behaviors at runtime in any order | Deeply nested wrappers complicate stack traces |
| Avoids subclass explosion | Removing a middle wrapper at runtime is awkward |
| Respects Single Responsibility Principle | Identity checks (`==` or `instanceof`) break on wrappers |
