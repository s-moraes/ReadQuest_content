# Interpreter Pattern

The **Interpreter** pattern defines a grammatical representation for a **mini-language (DSL)** and provides an interpreter that evaluates sentences written in that grammar using an **Abstract Syntax Tree (AST)**.

---

## 1. The Problem It Solves

Applications frequently need user-configurable business rules—such as search filters (`tier:PRO AND (country:BR OR country:PT)`), feature-flag targeting, or pricing formulas—without recompiling or redeploying Java code every time a rule changes.

---

## 2. Structure (AST Evaluation)

```text
                [RuleExpr <<sealed interface>>]
                + eval(Map<String, String> ctx) : boolean
                              ^
           +------------------+------------------+
           |                  |                  |
     [EqualsExpr]         [AndExpr]          [NotExpr]
     (Terminal)         (Non-Terminal)     (Non-Terminal)
```

- **Context:** Holds runtime variables or facts (`Map<String, String>`).
- **Terminal Expression:** Leaf nodes evaluating atomic tokens (`EqualsExpr`).
- **Non-Terminal Expression:** Composite nodes combining child expressions (`AndExpr`, `OrExpr`, `NotExpr`).

---

## 3. Deep-Dive Java Example: Sealed AST + Mini Parser

Using Java 17+ `sealed interface` and `record`, the AST is concise, immutable, and thread-safe:

```java
public sealed interface RuleExpr
    permits EqualsExpr, AndExpr, OrExpr, NotExpr {
    boolean eval(Map<String, String> ctx);
}

public record EqualsExpr(String key, String value)
    implements RuleExpr {
    @Override
    public boolean eval(Map<String, String> ctx) {
        return value.equals(ctx.get(key));
    }
}

public record AndExpr(RuleExpr left, RuleExpr right)
    implements RuleExpr {
    @Override
    public boolean eval(Map<String, String> ctx) {
        return left.eval(ctx) && right.eval(ctx);
    }
}

public record OrExpr(RuleExpr left, RuleExpr right)
    implements RuleExpr {
    @Override
    public boolean eval(Map<String, String> ctx) {
        return left.eval(ctx) || right.eval(ctx);
    }
}

public record NotExpr(RuleExpr inner) implements RuleExpr {
    @Override
    public boolean eval(Map<String, String> ctx) {
        return !inner.eval(ctx);
    }
}
```

A simple parser turns a flat rule string like `"tier:PRO AND country:BR"` into an AST once, then evaluates it thousands of times cheaply:

```java
public final class RuleParser {
    public static RuleExpr parseAnd(String dsl) {
        String[] parts = dsl.split("\\s+AND\\s+");
        RuleExpr current = parseTerm(parts[0]);
        for (int i = 1; i < parts.length; i++) {
            current = new AndExpr(current, parseTerm(parts[i]));
        }
        return current;
    }

    private static RuleExpr parseTerm(String term) {
        String[] kv = term.trim().split(":", 2);
        return new EqualsExpr(kv[0], kv[1]);
    }
}
```

---

## 4. When to Stop & Use a Real Parser Generator

The GoF Interpreter pattern does **not** include a full lexer/parser—it only models the AST evaluation. If your grammar grows beyond simple boolean or arithmetic rules (operator precedence, parentheses, functions, loops), switch to **ANTLR** or **Spring Expression Language (SpEL)**.

### Real-World Java Examples
- **`java.util.regex.Pattern`:** Compiles regex strings into an internal node tree for matching.
- **Spring Expression Language (SpEL):** Evaluates dynamic expressions like `#{user.tier == 'PRO' and order.total > 100}`.
- **JPA Criteria API:** Builds type-safe query ASTs translated to SQL.

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Cleanly maps small grammars to immutable classes | Class-per-rule explodes for large grammars |
| Easy to extend with new operators (`NotExpr`) | Parsing text into an AST must be built separately |
| Safe sandboxed execution (no arbitrary code injection) | Slower than compiled bytecode for heavy loops |
