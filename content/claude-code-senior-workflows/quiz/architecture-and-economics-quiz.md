## Q1
Why should you write **characterization tests** *before* refactoring a legacy Java monolith with Claude Code?

### Option A
To delete all existing database tables automatically

### Option B [CORRECT]
To lock down the legacy code's actual current behavior (including edge cases) so you can verify parity during Strangler Fig extraction

### Option C
Because Maven refuses to compile without `@ParameterizedTest`

### Option D
To disable `@Transactional` proxies in Spring

### Explanation
Legacy code often has undocumented edge cases and implicit side effects. Characterization tests capture current behavior as a golden-master safety net before you extract new Hexagonal services behind a Strangler Fig seam.

===

## Q2
What is a common Hibernate pitfall when fixing an N+1 query on a **paginated** (`Pageable`) repository method?

### Option A
`@EntityGraph` deletes foreign keys

### Option B [CORRECT]
Combining `JOIN FETCH` on a collection with `Pageable` forces Hibernate to fetch all rows and paginate in memory (`HHH90003004`)

### Option C
PostgreSQL does not support `JOIN` with `LIMIT`

### Option D
`generate_statistics=true` disables SQL indexes

### Explanation
Using `JOIN FETCH` on a to-many collection alongside `Pageable` triggers Hibernate warning `HHH90003004` (in-memory pagination), which can cause OOM errors on large tables. Using `@BatchSize` or two-step ID pagination avoids this trap.

===

## Q3
Why does a **fresh-context subagent** (`security-auditor`) catch more bugs than asking the main coding session to review its own work?

### Option A
Subagents run on a faster CPU core

### Option B [CORRECT]
A fresh subagent has no memory of implementation compromises and evaluates only the `git diff` against the security checklist

### Option C
The main session cannot run `git diff`

### Option D
Subagents automatically bypass `permissions.deny`

### Explanation
Long coding sessions suffer from context bias and tunnel vision around the code they just wrote. A fresh-context, read-only subagent evaluates the resulting `git diff` objectively against OWASP, concurrency, and resource-leak rules.

===

## Q4
In Claude Code, which model routing strategy gives the best balance of **accuracy, speed, and cost** for a senior team?

### Option A
Use Opus for every `grep` search and Haiku for complex distributed-systems `/plan`

### Option B [CORRECT]
Use Opus for complex `/plan` and hard debugging, Sonnet for daily coding/reviews, and Haiku for fast read-only search or log triage

### Option C
Disable `/clear` and keep one 200-turn session open all week

### Option D
Always run `./mvnw clean install` without `-q`

### Explanation
Matching model capability to task complexity—Opus for deep architectural planning, Sonnet as the fast daily driver, and Haiku for lightweight exploration/log pipes—maximizes quality while keeping latency and token spend low.

===

## Q5
Why do verbose Maven logs (`./mvnw clean install` without `-q`) hurt **both** cost and reasoning quality?

### Option A
Maven logs are encrypted and cannot be read by LLMs

### Option B [CORRECT]
Every line of build output stays in conversation history and is re-processed on every subsequent turn, inflating cost and diluting attention

### Option C
`-q` disables JUnit assertions

### Option D
Claude Code charges per character written to `pom.xml`

### Explanation
In a multi-turn agent loop, conversation history is re-sent on every turn. Dumping thousands of lines of `INFO` logs into context wastes tokens on every turn after it and pushes important `CLAUDE.md` rules into the "lost-in-the-middle" zone.
