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
What is the safest way on Linux to run Claude Code with `--dangerously-skip-permissions` for a large, unattended code migration?

### Option A
Run it as `root` directly in `/home`

### Option B [CORRECT]
Run it inside an ephemeral rootless Docker/Podman container mounting only the isolated project worktree

### Option C
Disable `git` so no commits can be made

### Option D
Delete `~/.ssh` temporarily before starting the session

### Explanation
Even with `deny` rules, running `--dangerously-skip-permissions` on a host Linux machine carries unnecessary risk. Isolating the session inside an ephemeral rootless container that mounts only the target worktree bounds the blast radius completely.

===

## Q3
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

## Q4
How can a Linux developer run two parallel Claude Code tasks (e.g., a feature and an urgent hotfix) without file collisions?

### Option A
Open two tabs in the same directory and alternate typing every 10 seconds

### Option B [CORRECT]
Use `tmux` windows paired with isolated Git worktrees (`claude --worktree <name>`)

### Option C
Copy the entire `.git` folder into `/tmp` manually for every prompt

### Option D
Disable `PostToolUse` hooks in both terminals

### Explanation
Running two writer agents in the same directory causes them to overwrite each other's edits. Pairing `tmux` sessions with `claude --worktree <name>` gives each task its own isolated working tree linked to the same repository.

===

## Q5
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
