## Q1
What is the difference between & and && in boolean expressions?

### Option A [CORRECT]
&& short-circuits evaluation if the left operand is false; & always evaluates both operands.

### Option B
& is logical; && is bitwise.

### Option C
&& only works with integer operands.

### Option D
There is no difference in boolean contexts.

### Explanation
The conditional-AND operator (&&) does not evaluate the right operand if the left operand is false.
===
## Q2
What does System.out.println(10 + 20 + "Hello") print?

### Option A [CORRECT]
30Hello

### Option B
1020Hello

### Option C
Hello30

### Option D
Compiler error

### Explanation
Evaluation proceeds left to right: 10 + 20 yields 30, then 30 + "Hello" evaluates to "30Hello".
===
## Q3
What is the result of 5 / 2 in Java?

### Option A [CORRECT]
2

### Option B
2.5

### Option C
3

### Option D
2.0

### Explanation
Integer division truncates the fractional part, resulting in integer 2.
===
## Q4
Which operator tests object identity rather than value equality?

### Option A [CORRECT]
==

### Option B
.equals()

### Option C
instanceof

### Option D
compareTo()

### Explanation
The '==' operator checks if two reference variables point to the exact same memory address on the heap.
===
## Q5
What is the output of: int a = 5; int b = ++a;?

### Option A [CORRECT]
a = 6, b = 6

### Option B
a = 6, b = 5

### Option C
a = 5, b = 6

### Option D
a = 5, b = 5

### Explanation
Pre-increment increments 'a' first, then assigns the new value (6) to 'b'.
===
## Q6
Can the ternary operator ? : return different incompatible types without a common supertype?

### Option A [CORRECT]
No, both branches must be compatible with the assigned variable type.

### Option B
Yes, types are coerced to Object automatically.

### Option C
Only if casting at runtime.

### Option D
Only in switch expressions.

### Explanation
Java is statically typed; the result of a ternary expression must evaluate to a type assignable to the target.
===
## Q7
What is the result of (true | false & false)?

### Option A [CORRECT]
true

### Option B
false

### Option C
Compiler error

### Option D
NullPointerException

### Explanation
The bitwise AND (&) has higher operator precedence than bitwise OR (|), so false & false evaluates first to false, then true | false evaluates to true.
