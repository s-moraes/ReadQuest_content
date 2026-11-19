# Senior Java + Linux `CLAUDE.md` Blueprint

Below is a production-ready starter `CLAUDE.md` and `.claude/settings.json` tailored for a senior Java + Linux engineering team. Drop these at your repository root and customize the module names.

---

## 1. `CLAUDE.md` (Repository Root)

```markdown
# Project: Billing Platform (Java 21 + Spring Boot 3 + PostgreSQL)

## Build & Test Commands (Always Use Quiet Mode)
- Targeted unit test:
  `./mvnw test -pl <module> -Dtest=<ClassName>#<method> -q`
- Module unit suite:
  `./mvnw test -pl <module> -q`
- Integration test (Testcontainers):
  `./mvnw verify -pl <module> -Dit.test=<ClassName> -q`
- Format code:
  `./mvnw spotless:apply -q`

## Hard Rules
- Never run `./mvnw clean install` unless `pom.xml` changed.
- Hexagonal boundaries: `domain/` must NEVER import
  `org.springframework.*`, `jakarta.*`, or `infrastructure.*`.
- Prefer Java `record`s for DTOs and value objects; do not mix
  with Lombok `@Data` on new classes.
- Never modify existing test assertions or replace `@SpringBootTest`
  with mocks to make a failing test pass.

## Verification Before Reporting Done
1. Run targeted unit tests for every modified class.
2. Run `./mvnw spotless:check -q`.
3. Inspect `git diff --stat` to ensure no unrelated files changed.
```

---

## 2. `.claude/settings.json` (Linux Guardrails + Auto-Format Hook)

```json
{
  "permissions": {
    "allow": [
      "Bash(./mvnw test *)",
      "Bash(./mvnw spotless:check *)",
      "Bash(git status)",
      "Bash(git diff *)"
    ],
    "deny": [
      "Read(.env*)",
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)",
      "Bash(rm -rf *)",
      "Bash(git push --force *)"
    ]
  },
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
