# Java Engineering with Claude Code: Maven/Gradle, Spring & Test Loops

Java ecosystems—with multi-module Maven/Gradle builds, annotation processors, Spring Boot or Quarkus DI, and Testcontainers—present unique challenges for coding agents. Left unguided, an agent will run `./mvnw clean install` on 12 modules and dump 4,000 lines of logs into its context window.

Senior Java engineers tune `CLAUDE.md`, test commands, and hooks to keep the feedback loop **fast, quiet, and compiler-verified**.

---

## Solving Java's Context-Window Bottleneck

Verbose build logs are the #1 killer of agent reasoning quality in Java repos. Enforce **quiet, targeted commands** in your project's `CLAUDE.md`:

| Anti-Pattern (Context Bloat) | Senior Operator Pattern (Lean & Fast) |
| :--- | :--- |
| `./mvnw clean test` (rebuilds all modules) | `./mvnw test -pl order-service -Dtest=OrderServiceTest -q` |
| `./gradlew test` (verbose info logs) | `./gradlew :order-service:test --tests "*OrderTest" -q` |
| Reading entire 800-line Spring startup log | Pipe or inspect `target/surefire-reports/*.txt` on failure |
| Running full Testcontainers suite on every edit | Run unit tests first; run `*IT` integration tests at the end |

Add this explicit instruction to `CLAUDE.md`:
> *"Always pass `-q` (quiet) and `-Dtest=<Class>#<method>` for targeted JUnit runs. Never run `clean install` unless dependencies or generated sources changed."*

---

## High-Leverage Java Workflows

### 1. Enforcing Architecture & Style Automatically
Senior Java teams rely on strict boundaries (Hexagonal/Clean Architecture, ArchUnit) and formatters (Spotless, Checkstyle).
- **In `CLAUDE.md`:** Document package boundaries (e.g., *"Classes in `com.acme.domain` must have zero `jakarta.*` or `org.springframework.*` imports"*).
- **In `PostToolUse` Hooks:** Trigger `./mvnw spotless:apply -DspotlessFiles=...` or `google-java-format` automatically after `Edit|Write` on `*.java` files so Claude never wastes turns fixing indentation or import order.

### 2. Test-Driven Bug Fixing & Parameterized JUnit 5
Java's strong typing makes it ideal for test-first agent loops:
1. Give Claude the stack trace or bug ticket.
2. Instruct it to write a **failing JUnit 5 `@ParameterizedTest`** reproducing the edge case first.
3. Have it run `./mvnw test -Dtest=TargetTest#reproducesBug -q` to confirm the failure.
4. Let it patch the production code and re-run until green.

### 3. Boilerplate-Heavy Refactors
Claude Code excels at mechanical Java tasks that are tedious by hand:
- Migrating POJOs to Java `record` types + updating MapStruct mappers.
- Generating Flyway `V<N>__*.sql` migrations aligned with JPA `@Entity` changes.
- Upgrading JUnit 4 (`@Before`, `Assert.*`) to JUnit 5 (`@BeforeEach`, `Assertions.*`) across dozens of test classes.

---

## Guarding Against Classic Java Agent Pitfalls

Even strong models make predictable Java mistakes if you don't guard against them:
- **Mocking Away Real Bugs:** In Spring Boot tests, agents sometimes replace a failing `@SpringBootTest` or Testcontainer test with `@MockitoBean` just to make it green. Explicitly forbid changing test annotations or weakening assertions without approval.
- **Spring Proxy Traps:** Remind Claude in `CLAUDE.md` about `@Transactional` / `@Async` self-invocation rules (calling a `@Transactional` method on `this` bypasses the Spring proxy).
- **Lombok vs. Records:** State clearly whether the repo uses Lombok (`@RequiredArgsConstructor`, `@Builder`) or pure Java 21+ `record`s so the agent doesn't mix styles.
