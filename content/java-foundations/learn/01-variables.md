# Java Variables & Data Types

Java is a strongly-typed programming language. Every variable must have a declared type before use.

![JVM Architecture Overview](../assets/java-jvm-diagram.webp)

## Primitive Data Types
Java defines 8 primitive data types:
1. `byte`: 8-bit signed two's complement integer (-128 to 127).
2. `short`: 16-bit signed integer (-32,768 to 32,767).
3. `int`: 32-bit signed integer (default integer literal type).
4. `long`: 64-bit signed integer (suffixed with `L` or `l`).
5. `float`: 32-bit single-precision IEEE 754 floating point (suffixed with `f`).
6. `double`: 64-bit double-precision IEEE 754 floating point (default floating literal).
7. `boolean`: Represents logical values `true` or `false`.
8. `char`: 16-bit Unicode character (`\u0000` to `\uffff`).

## Reference Types
Variables of reference types store memory references pointing to objects allocated on the heap rather than values stored directly on the stack.
