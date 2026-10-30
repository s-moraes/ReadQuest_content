## Q1
Which of the following correctly defines class Printer?

### Option A
```java
public class Printer {
}
package com.exam.oca;
```

### Option B [CORRECT]
```java
/* Java Developer Comments. */
package com.exam.oca;
public class Printer {
}
```

### Option C
```java
public class Printer {
    package com.exam.oca;
}
```

### Option D
```java
import java.util.*;
package com.exam.oca;
public class Printer {
}
```

### Explanation
In a Java source file, the `package` statement must always be the very first non-comment statement, appearing before any `import` or `class` declarations (PIC rule: Package, Import, Class).

===

## Q2
Which of the following is a valid `main` method signature that acts as the entry point for executing a standard Java class from the command line?

### Option A
```java
public void main(String[] args)
```

### Option B
```java
private static void main(String[] args)
```

### Option C [CORRECT]
```java
public static final void main(String... args)
```

### Option D
```java
public static int main(String[] args)
```

### Explanation
The standard JVM entry point must be `public`, `static`, return `void`, and accept a single `String` array or varargs (`String...`) parameter. Adding `final` is optional and completely valid.

===

## Q3
How many `public` top-level classes can be defined inside a single `.java` source file named `OrderService.java`?

### Option A
Unlimited, as long as each class has a unique name.

### Option B [CORRECT]
At most one, and its name must be `OrderService`.

### Option C
Exactly two: one `public class` and one `public interface`.

### Option D
None, unless the file is inside a named package.

### Explanation
A Java source file can contain multiple package-private top-level classes, but at most one `public` top-level type, and its exact case-sensitive name must match the `.java` filename.

===

## Q4
What is the output of the following code snippet?
```java
Integer n1 = 100;
Integer n2 = 100;
Integer n3 = 200;
Integer n4 = 200;
System.out.println((n1 == n2) + " " + (n3 == n4));
```

### Option A
`true true`

### Option B
`false false`

### Option C [CORRECT]
`true false`

### Option D
Compilation fails due to incompatible operand types.

### Explanation
Autoboxing uses `Integer.valueOf()`, which caches values between `-128` and `127`. Therefore, `n1` and `n2` reference the same cached instance (`true`), while `n3` and `n4` create distinct heap objects (`false`).
