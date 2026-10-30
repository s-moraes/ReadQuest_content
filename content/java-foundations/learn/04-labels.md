# Break & Continue Labels

Controlling nested loop execution flows with labeled statements.

## Labeled Break
A labeled `break` terminates the outer loop statement marked with the corresponding label:

```java
OUTER: for (int i = 0; i < 5; i++) {
    for (int j = 0; j < 5; j++) {
        if (i * j > 6) {
            break OUTER;
        }
    }
}
```
