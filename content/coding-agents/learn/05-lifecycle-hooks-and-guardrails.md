# Deterministic Guardrails with Lifecycle Hooks

Rules in `CLAUDE.md` or `GEMINI.md` are **probabilistic suggestions**: the model tries hard to follow them, but under heavy context load or tricky edge cases, it can still forget to run the formatter or accidentally attempt a restricted shell command.

**Hooks** solve this by moving critical guardrails out of the LLM prompt and into **deterministic code** that executes automatically at fixed points in the agent lifecycle.

Think of a hook as middleware (or a turnstile) around tool calls.

---

## Core Lifecycle Events

Both Claude Code (via `.claude/settings.json`) and Google Antigravity (via `hooks.json`) intercept key moments of an agent's execution loop:

| Lifecycle Event | When It Fires | Common Operator Use Case |
| :--- | :--- | :--- |
| **`SessionStart`** | When a session begins or resumes | Inject dynamic context (current git branch, open tickets, env checks) |
| **`UserPromptSubmit`** | Before the user's prompt reaches the model | Validate input, inject team reminders, or block sensitive patterns |
| **`PreToolUse`** | *Before* a tool executes (receives tool name + JSON args) | Block dangerous commands (`rm -rf`, `git push`), protect `.env` or lockfiles |
| **`PostToolUse`** | *After* a tool succeeds | Auto-run `prettier` / `gofmt` / `ruff` after every `Edit` or `Write` |
| **`Stop`** | When the agent attempts to finish its turn | Verify tests pass before allowing the agent to declare "done" |

---

## How Hooks Communicate (`stdin` + Exit Codes)

In Claude Code (and shell-based hook runners), a hook is typically a lightweight script (Bash, Python, or Node) that reads a JSON payload from `stdin` and signals its decision via exit codes or structured JSON on `stdout`:

- **Exit `0`:** Allow the tool call to proceed (any `stdout` can be fed back as context).
- **Exit `2` (Blocking Error):** **Block** the tool call immediately and feed `stderr` back to the agent as an error message so it knows *why* it was blocked and can self-correct.

```text
Agent requests: Bash("git push --force origin main")
       |
       v
+-----------------------------------+
| PreToolUse Hook (guard_git.py)    |
| Reads JSON from stdin             |
| Detects "--force" -> Exit Code 2  |
+-----------------------------------+
       |
       v (Blocked! Tool never executes)
Agent receives stderr:
  "BLOCKED: Force-pushing is prohibited by repo policy."
```

---

## Practical Operator Recipes

### Recipe 1: Auto-Format on Every File Edit (`PostToolUse`)
Instead of wasting LLM tokens asking the agent to fix indentation, let a `PostToolUse` hook run your formatter automatically whenever `Edit` or `Write` touches a file.

In `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs -r npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

### Recipe 2: Block Destructive Commands (`PreToolUse`)
Even if an agent runs with elevated auto-approval inside a dev container, a `PreToolUse` hook acts as an unbypassable safety rail:

```python
#!/usr/bin/env python3
import json, sys, re

payload = json.load(sys.stdin)
cmd = payload.get("tool_input", {}).get("command", "")

BLOCKED = [
    r"rm\s+-rf\s+/",
    r"git\s+push\s+.*--force",
    r"DROP\s+TABLE",
]

for pattern in BLOCKED:
    if re.search(pattern, cmd, re.IGNORECASE):
        print(f"Blocked by PreToolUse policy: {pattern}", file=sys.stderr)
        sys.exit(2)
```

### Recipe 3: Dynamic Session Context (`SessionStart`)
Instead of hardcoding volatile state in `CLAUDE.md`, run a `SessionStart` hook that prints the current Git branch, recent commits, and whether Docker/DB services are running. That state is injected fresh at turn 0.

---

## Antigravity `hooks.json` & Best Practices

In Google Antigravity, hooks are defined in `hooks.json` inside `.agents/` (project-scoped) or `~/.gemini/config/` (global) and can also be bundled inside **Plugins** alongside skills and rules.

### Golden Rules for Writing Hooks
1. **Keep Hooks Fast (< 200ms):** A `PostToolUse` hook runs after *every* edit. Running a 30-second full integration suite on every single file edit will stall your agent. Run fast linters/formatters in `PostToolUse`, and reserve heavy test suites for `Stop` hooks or explicit verification steps.
2. **Make Block Messages Actionable:** When exiting with code `2`, tell the agent *what to do instead* (e.g., *"Use `git push --force-with-lease` on feature branches, never push to `main`"*).
3. **Never Trust Unsanitized Shell Interpolation:** Parse the JSON payload with `jq` or Python `json.load(sys.stdin)` rather than concatenating raw strings into shell commands.
