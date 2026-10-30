# Loop Constructs (for, while, do-while)

Iteration statements enable repeated execution of statement blocks.

## The while and do-while Loops
- `while`: Evaluates condition before executing loop body. If false initially, loop never runs.
- `do-while`: Executes body at least once before testing condition.

## Standard for and Enhanced for-each
```java
List<String> items = List.of("A", "B", "C");
for (String item : items) {
    System.out.println(item);
}
```
