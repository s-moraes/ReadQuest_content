## Q1
What critical guardrail should you add to `CLAUDE.md` when using Claude Code alongside **Apache NetBeans** on a Swing desktop project?

### Option A
Tell Claude Code to delete all `.java` files before NetBeans opens

### Option B [CORRECT]
Forbid editing `*.form` files, `//GEN-BEGIN` / `//GEN-END` guarded blocks, and `nbproject/private/`

### Option C
Disable Maven in NetBeans and run Ant only

### Option D
Run `claude --dangerously-skip-permissions` on `nbproject/`

### Explanation
Apache NetBeans' GUI Builder (Matisse) manages `*.form` XML files and `//GEN-BEGIN` / `//GEN-END` guarded blocks automatically. Letting an agent hand-edit those blocks corrupts the visual form designer, so `CLAUDE.md` should explicitly forbid touching them.

===

## Q2
When working with **Android Studio** and Claude Code, why should `CLAUDE.md` direct the agent to run `testDebugUnitTest` before `connectedDebugAndroidTest`?

### Option A
`connectedDebugAndroidTest` cannot run Kotlin code

### Option B [CORRECT]
JVM unit tests run in seconds without booting an emulator or packaging an APK, keeping the agent's feedback loop fast

### Option C
Android Studio deletes unit tests if instrumentation tests run first

### Option D
`testDebugUnitTest` automatically opens the Layout Inspector

### Explanation
Packaging APKs and running instrumented tests on an emulator/device is slow. Directing Claude Code to iterate on fast JVM unit tests (`testDebugUnitTest`) and `lintDebug` first keeps the feedback loop tight, reserving `connectedDebugAndroidTest` for final verification.

===

## Q3
What is the safest way to connect Claude Code to **Jira, Bitbucket, and Confluence** in an enterprise environment?

### Option A
Enable `--dangerously-skip-permissions` with an admin Atlassian API token

### Option B
Paste every Confluence page into `CLAUDE.md` at the repo root

### Option C [CORRECT]
Use read-only tokens by default, require human approval for mutations (comments, transitions), and scope heavy MCP servers to subagents

### Option D
Store the Atlassian password in a committed `.mcp.json` file

### Explanation
External Jira comments and Confluence pages can contain untrusted text (indirect prompt injection risk) and large MCP schemas bloat context. Using read-only credentials by default, gating mutations behind human-in-the-loop approval, and scoping MCPs to subagents keeps the workflow safe and lean.

===

## Q4
When should a senior engineer prefer a **native Linux CLI** (like `gh` or `psql`) over adding a new **MCP server**?

### Option A
When they want to inject 40 extra JSON tool schemas into every prompt

### Option B [CORRECT]
When a standard CLI already exists in the shell—avoiding startup MCP schema bloat while letting Claude pipe and filter output with `jq` or `grep`

### Option C
When the tool requires browser OAuth popups

### Option D
Never; MCP servers always use zero context tokens

### Explanation
Every active MCP server injects its tool schemas into the context window at session start. When a standard Linux CLI like `gh`, `psql`, or `kubectl` is already available, Claude Code can invoke it directly via `Bash` and filter output with `jq`/`grep` at zero schema overhead.

===

## Q5
Which credential policy should **always** be enforced when connecting Claude Code to a PostgreSQL MCP server or `psql` for schema inspection?

### Option A
Superuser role with `DROP TABLE` privileges

### Option B
The production migration user (`flyway_admin`)

### Option C [CORRECT]
A `SELECT`-only read-only database role (`default_transaction_read_only = on`)

### Option D
Blank password over public internet

### Explanation
Giving an LLM read-only (`SELECT`-only) database credentials lets it inspect live schemas, indexes, and `EXPLAIN ANALYZE` plans safely while making accidental `UPDATE`, `DELETE`, or `DROP` mutations impossible at the database layer.
