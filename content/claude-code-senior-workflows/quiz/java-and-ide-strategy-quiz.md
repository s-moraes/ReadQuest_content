## Q1
Why should a Java `CLAUDE.md` instruct Claude Code to use `./mvnw test -pl <module> -Dtest=ClassName -q` instead of `./mvnw clean install`?

### Option A
`clean install` is deprecated in Maven 3

### Option B [CORRECT]
Verbose multi-module logs flood the context window, slow down feedback loops, and degrade model attention

### Option C
Claude Code cannot parse XML `pom.xml` files

### Option D
`-q` automatically fixes compilation errors

### Explanation
Running a full `clean install` across all modules dumps thousands of lines of build output into the context window, increasing latency, token cost, and "lost-in-the-middle" instruction drift. Targeted, quiet (`-q`) module runs keep the feedback loop fast and the context lean.

===

## Q2
Why do senior Java teams wire `spotless:apply` into a `PostToolUse` hook (`Edit|Write`) instead of relying only on a style rule in `CLAUDE.md`?

### Option A
Hooks compile Java bytecode faster than `javac`

### Option B
`CLAUDE.md` cannot mention Maven commands

### Option C [CORRECT]
A `PostToolUse` hook enforces formatting deterministically after every `.java` edit without spending LLM turns or tokens on style fixes

### Option D
Spotless only runs when triggered by JSON `stdin`

### Explanation
Asking the LLM to format imports and indentation wastes tokens and can still be forgotten under heavy context load. A `PostToolUse` hook runs Spotless deterministically whenever a `.java` file is edited, keeping code clean at zero reasoning cost.

===

## Q3
What is a common Spring Boot "test-cheating" anti-pattern that senior developers must guard against in `CLAUDE.md`?

### Option A
Using JUnit 5 `@ParameterizedTest` for edge cases

### Option B [CORRECT]
Replacing a failing `@SpringBootTest` or Testcontainers test with `@MockitoBean` just to make the build green

### Option C
Running unit tests before integration tests (`*IT.java`)

### Option D
Separating `domain/` from `infrastructure/` with ArchUnit

### Explanation
When an integration test fails due to a SQL, serialization, or wiring bug, an eager agent may swap out real beans for `@MockitoBean` mocks to force a green build. Explicitly forbidding test-weakening keeps verification honest.

===

## Q4
In a senior Java developer's workflow, which task is **better suited to IntelliJ IDEA** than to Claude Code?

### Option A
Generating parameterized JUnit 5 tests for a new service

### Option B
Triaging 150 lines of `journalctl` crash logs via a Unix pipe

### Option C [CORRECT]
Step-through debugging live JVM threads/heap and performing compiler-guaranteed PSI refactors like *Change Signature* across 100 callers

### Option D
Reviewing a staged `git diff` for missing null checks

### Explanation
IntelliJ IDEA excels at interactive step-through debugging (live breakpoints, watches, thread/heap inspection) and deterministic PSI/AST refactors (*Change Signature*, *Move Class*) across large codebases. Claude Code excels at cross-file generation, log triage, and diff review.

===

## Q5
Which habit best prevents **senior skill atrophy** when delegating implementation to Claude Code?

### Option A
Always running `--dangerously-skip-permissions` on every repository

### Option B
Never reading `git diff` once unit tests pass

### Option C [CORRECT]
Never committing code you cannot explain, occasionally hand-crafting core abstractions, and using the live debugger for subtle runtime bugs

### Option D
Deleting `CLAUDE.md` every Friday

### Explanation
Staying sharp as a senior engineer means treating the agent as leverage rather than a black box: audit every diff, understand every line before merging, design critical domain abstractions deliberately, and use the IDE debugger to build deep runtime mental models.
