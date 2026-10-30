# Why `127 == 127` is true, but `128 == 128` is false

One of the most famous Java interview and certification traps involves comparing wrapper `Integer` objects using `==` instead of `.equals()`.

---

## The Mystery Snippet

```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b); // true!

Integer x = 128;
Integer y = 128;
System.out.println(x == y); // false!
```

---

## How `Integer.valueOf()` Works Under the Hood

When you assign an `int` literal to an `Integer` reference (`Integer a = 127;`), the compiler autoboxes it into `Integer.valueOf(127)`.

According to the **Java Language Specification (JLS §5.1.7)**, the JVM caches `Integer` instances in the range **`-128` to `127`** by default:
* Because `127` falls within `-128..127`, both `a` and `b` point to the **exact same cached object reference** in memory.
* Because `128` is outside that range, `Integer.valueOf(128)` allocates a `new Integer(128)` on the heap each time, making `x == y` evaluate to `false`.

> **Rule of Thumb:** Always use `.equals()` (or unbox to primitive `int`) when comparing wrapper values!
