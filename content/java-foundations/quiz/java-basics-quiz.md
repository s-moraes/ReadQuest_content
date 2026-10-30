## Q1
Which of the following correctly defines class Printer?

### Option A
public class Printer {
}
package com.exam.oca;

### Option B [CORRECT]
/* Java Developer Comments. */
package com.exam.oca;
public class Printer {

}

### Option C
public class Printer {
    package com.exam.oca;
}

### Option D
import java.util.*;
package com.exam.oca;
public class Printer {

}

### Explanation
A package statement must be the first non-comment statement in a Java source file. Import statements and class declarations must follow the package declaration.
===
## Q2
What is the output of compiling and executing a class with the method: public static void main(String args[])?

### Option A [CORRECT]
Compiles and runs successfully as an application entry point.

### Option B
Compiler error: args[] cannot follow the parameter name in Java.

### Option C
Runtime error: NoSuchMethodError.

### Option D
Compiles but is not recognized by the JVM launcher.

### Explanation
In Java, both 'String[] args' and 'String args[]' are valid syntax for the main method argument array.
===
## Q3
Which keyword prevents a class from being inherited in Java?

### Option A
static

### Option B
abstract

### Option C [CORRECT]
final

### Option D
sealed

### Explanation
The 'final' keyword on a class declaration prevents any subclass from extending it.
===
## Q4
What is the default value of an uninitialized instance variable of type boolean?

### Option A
true

### Option B [CORRECT]
false

### Option C
0

### Option D
null

### Explanation
In Java, boolean instance and class variables default to 'false'.
