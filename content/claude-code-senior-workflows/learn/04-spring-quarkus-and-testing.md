# Spring Boot, Quarkus & Testcontainers with Claude Code

Enterprise Java frameworks rely heavily on runtime proxies, dependency injection, and real database integration tests. Senior developers configure Claude Code to respect framework invariants and avoid "greenwashing" tests.

---

## Test-Driven Bug Fixing with JUnit 5

Java's strong typing makes it ideal for test-first agent loops:
1. Provide Claude Code with the stack trace, failing endpoint, or bug ticket.
2. Instruct it to write a **failing JUnit 5 `@ParameterizedTest`** reproducing the edge case *before* touching production code.
3. Have it run `./mvnw test -Dtest=TargetTest#reproducesBug -q` to confirm the failure.
4. Let it patch the production class and re-run until green.

```text
Reproduce the null currency bug in PricingService by adding a
failing @ParameterizedTest in PricingServiceTest first.
Run it with `-q` to verify it fails, then fix PricingService.
Do not alter any existing test assertions.
```

---

## Guarding Against Classic Framework Pitfalls

Even frontier models make predictable mistakes in Spring Boot and Quarkus if your `CLAUDE.md` does not call them out:

- **Mocking Away Real Bugs:** When a `@SpringBootTest` or Testcontainers test fails due to a SQL or serialization error, an eager agent may replace the integration test with `@MockitoBean` just to make the build pass. Explicitly forbid changing test annotations or weakening assertions without approval.
- **`@Transactional` Proxy Self-Invocation:** Document in `CLAUDE.md` that calling a `@Transactional` or `@Async` method on `this` bypasses the Spring AOP proxy—forcing the agent to extract a collaborator bean instead.
- **Hexagonal / Clean Architecture Boundaries:** State package rules clearly (e.g., *"Classes in `domain/` must never import `jakarta.*` or `org.springframework.*`"*), and back them up with ArchUnit tests so the compiler/test runner catches violations automatically.
- **Lombok vs. Records:** Specify whether the codebase uses Lombok (`@RequiredArgsConstructor`, `@Builder`) or pure Java `record`s so Claude never mixes styles in the same module.

---

## Managing Testcontainers in Agent Loops

Testcontainers spins up real PostgreSQL or Kafka containers, which adds 5–15 seconds per suite run:
- Keep fast unit tests (`*Test.java`) separate from integration tests (`*IT.java` via Maven Failsafe).
- Instruct Claude to iterate rapidly on `*Test`, then run `./mvnw verify -pl <module> -Dit.test=<Class> -q` once before reporting completion.
