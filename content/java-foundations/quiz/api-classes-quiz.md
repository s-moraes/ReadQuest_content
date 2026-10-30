## Q1
Are String objects mutable in Java?

### Option A [CORRECT]
No, Strings are immutable; methods return new String instances.

### Option B
Yes, Strings can be modified directly via setCharAt().

### Option C
Mutable only when created with new String().

### Option D
Mutable until passed to another method.

### Explanation
Java Strings are immutable for thread safety, security, and string interning pool efficiency.
===
## Q2
Which class should you use for thread-safe mutable string concatenation?

### Option A [CORRECT]
StringBuffer

### Option B
StringBuilder

### Option C
StringJoiner

### Option D
StringFormatter

### Explanation
StringBuffer has synchronized methods for thread safety, whereas StringBuilder is unsynchronized and faster for single-threaded use.
===
## Q3
Which package is automatically imported into every Java compilation unit?

### Option A [CORRECT]
java.lang

### Option B
java.util

### Option C
java.io

### Option D
java.net

### Explanation
All classes in java.lang (like String, System, Math, Object) are imported by default.
===
## Q4
What does Math.floor(3.9) return?

### Option A [CORRECT]
3.0 (double)

### Option B
3 (int)

### Option C
4.0 (double)

### Option D
3.5 (double)

### Explanation
Math.floor returns the largest double value that is less than or equal to the argument and equal to a mathematical integer.
