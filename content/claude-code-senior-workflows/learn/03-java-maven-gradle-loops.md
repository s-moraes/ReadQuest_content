# Taming Maven & Gradle: Fast, Quiet Java Feedback Loops

Java ecosystems—with multi-module Maven/Gradle builds, annotation processors, and long framework startup logs—present a specific trap for coding agents. Left unguided, an agent runs `./mvnw clean install` across 12 modules and dumps 4,000 lines of logs into its context window.

Senior Java engineers tune `CLAUDE.md` and test commands to keep the agent's feedback loop **fast, quiet, and compiler-verified**.

---

## Solving Java's Context-Window Bottleneck

Verbose build output is the #1 killer of agent reasoning quality in Java repositories. Enforce **quiet, targeted commands** in your project's `CLAUDE.md`:

| Anti-Pattern (Context Bloat) | Senior Operator Pattern (Lean & Fast) |
| :--- | :--- |
| `./mvnw clean test` (rebuilds all modules) | `./mvnw test -pl order-service -Dtest=OrderServiceTest -q` |
| `./gradlew test` (verbose info logs) | `./gradlew :order-service:test --tests "*OrderTest" -q` |
| Reading 800-line Spring startup logs | Inspect `target/surefire-reports/*.txt` on failure |
| Running full Testcontainers on every edit | Run unit tests first; run `*IT` integration tests last |

Add this explicit rule to your Java `CLAUDE.md`:
> *"Always pass `-q` (quiet) and `-Dtest=<Class>#<method>` for targeted JUnit runs. Never run `clean install` unless `pom.xml` or generated sources changed."*

---

## Automatic Formatting with `PostToolUse` Hooks

Senior Java teams enforce formatting with **Spotless** or **Checkstyle**. Asking an LLM to manually fix import ordering and indentation wastes tokens and turns.

Instead, wire a `PostToolUse` hook in `.claude/settings.json` that runs Spotless automatically whenever `Edit` or `Write` touches a `.java` file:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | grep '\\.java$' | xargs -r ./mvnw spotless:apply -q"
          }
        ]
      }
    ]
  }
}
```

Now formatting is **100% deterministic** at zero reasoning cost.

---

## High-Leverage Mechanical Java Refactors

Claude Code shines at tedious, cross-file Java migrations where typing by hand is slow:
- Converting legacy POJOs to Java 21 `record` types and updating MapStruct mappers.
- Upgrading JUnit 4 (`@Before`, `Assert.*`) to JUnit 5 (`@BeforeEach`, `Assertions.*`) across dozens of test files.
- Aligning JPA `@Entity` columns with new Flyway `V<N>__*.sql` migrations.
