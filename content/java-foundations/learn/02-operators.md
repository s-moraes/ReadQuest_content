# Using Operators and Decision Constructs

Control flow statements allow Java programs to conditionally execute code blocks based on boolean expressions.

## Primitive Equality vs Object Equality
- **Primitives:** Evaluated using the `==` operator for direct value equality.
- **Objects:** Evaluated using `.equals()` method; `==` compares reference memory addresses.

```java
package com.exam.oca;

public class EqualityCheck {
    public static void main(String[] args) {
        String s1 = "Hello";
        String s2 = new String("Hello");
        System.out.println(s1 == s2);      // false (different references)
        System.out.println(s1.equals(s2));  // true (same content)
    }
}
```

## Switch Expressions in Modern Java
Modern Java supports enhanced switch expressions with arrow syntax, preventing fallthrough bugs:
```java
String description = switch (statusCode) {
    case 200 -> "OK";
    case 404 -> "Not Found";
    default -> "Unknown Code";
};
```
