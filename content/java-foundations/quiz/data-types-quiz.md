## Q1
What is the range of a Java byte primitive?

### Option A [CORRECT]
-128 to 127

### Option B
0 to 255

### Option C
-32768 to 32767

### Option D
-2147483648 to 2147483647

### Explanation
A Java byte is an 8-bit signed integer ranging from -128 (-2^7) to 127 (2^7 - 1).
===
## Q2
Which primitive type does NOT have an exact literal representation?

### Option A [CORRECT]
byte and short

### Option B
int

### Option C
long

### Option D
double

### Explanation
Integer literals are typed as 'int' by default unless suffixed with L for 'long'. Byte and short rely on compile-time narrowing.
===
## Q3
What happens when you execute: float f = 3.14;?

### Option A [CORRECT]
Compiler error: possible lossy conversion from double to float.

### Option B
Compiles and assigns 3.14f.

### Option C
Runtime ClassCastException.

### Option D
Assigns 3.0f.

### Explanation
Floating-point literals default to 'double'. Suffixing with 'f' (3.14f) is required for float literals.
===
## Q4
Which wrapper class uses a cached pool for values from -128 to 127?

### Option A [CORRECT]
Integer

### Option B
Float

### Option C
Double

### Option D
Void

### Explanation
Integer.valueOf() caches instances for values between -128 and 127 to optimize memory for autoboxing.
===
## Q5
Can a char type store negative numeric values in Java?

### Option A [CORRECT]
No, char is an unsigned 16-bit integer (0 to 65535).

### Option B
Yes, char ranges from -32768 to 32767.

### Option C
Yes, but only if explicitly cast from byte.

### Option D
Only in Java 21+.

### Explanation
char is the only unsigned primitive numeric type in Java, representing 16-bit Unicode characters.
