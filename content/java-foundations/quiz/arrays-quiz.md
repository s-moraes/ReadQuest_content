## Q1
How is an array length accessed in Java?

### Option A [CORRECT]
array.length (public final field)

### Option B
array.length() (method call)

### Option C
array.size()

### Option D
array.count

### Explanation
Arrays are objects with a built-in 'length' field, whereas collections use the 'size()' method.
===
## Q2
What exception is thrown when accessing array[5] on an array of length 5?

### Option A [CORRECT]
ArrayIndexOutOfBoundsException

### Option B
IndexOutOfBoundsException

### Option C
NullPointerException

### Option D
ArrayStoreException

### Explanation
Valid indices for an array of length 5 are 0 through 4; index 5 causes ArrayIndexOutOfBoundsException.
===
## Q3
What are the default values in a new boolean[3] array?

### Option A [CORRECT]
false, false, false

### Option B
true, true, true

### Option C
null, null, null

### Option D
0, 0, 0

### Explanation
Elements of a newly allocated boolean array default to false.
===
## Q4
Is int[] a valid subtype of Object[] in Java?

### Option A [CORRECT]
No, int is a primitive type so int[] cannot be cast to Object[].

### Option B
Yes, through autoboxing.

### Option C
Yes, int[] extends Object[].

### Option D
Only in Java 17+.

### Explanation
Primitive arrays cannot be cast to Object[]; however, int[] can be referenced as an Object.
