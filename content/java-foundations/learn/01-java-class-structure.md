# Java Source File & Class Structure

Every `.java` source file follows a strict ordering rule enforced by the Java compiler (`javac`). Memorizing the **PIC** acronym (**P**ackage, **I**mport, **C**lass) makes source structure questions effortless.

---

## 1. Required Order of Elements (PIC)

| Element | Required? | Rule / Position |
| :--- | :---: | :--- |
| **Comments** | No | Can appear anywhere in the file (before, between, or inside declarations). |
| **1. `package` statement** | No | At most **one**, and it **must be the very first non-comment statement** in the file. |
| **2. `import` statements** | No | Must appear **after** the `package` statement and **before** any `class`, `interface`, or `record` declaration. |
| **3. Type declarations (`class`)** | Yes | At most one `public` top-level type per file, and its name must match the filename (`Printer.java`). |

---

## 2. Valid vs. Invalid Examples

```java
/* Comments can always go at the very top! */
package com.exam.oca;

import java.util.*;

public class Printer {
    private String model;
}
```

Placing `package` inside a class body or after an `import` statement results in an immediate compilation error.
