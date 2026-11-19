# Permissions, Sandboxing & Blast-Radius Control

Giving an LLM read/write access to your filesystem and a live Bash shell is powerful—and dangerous if misconfigured. A single hallucinated `rm -rf`, an accidental `git push --force`, or a prompt injection hidden inside an untrusted README can damage your local environment.

Mature operators do not rely on "hoping the model behaves." They configure **layered permission boundaries** and **Git-based blast-radius control**.

---

## Google Antigravity Permission & Sandbox Model

Antigravity separates permissions into **Global Settings** (applying across all projects) and **Project-Level Overrides** (taking priority when a specific workspace is active).

### 1. Tool Execution Policies
Controls whether terminal commands and state-changing tools require human approval:
- **`strict` / `request-review`:** Prompts the operator before running terminal commands or risky actions. Best when learning a codebase or operating on sensitive environments.
- **`proceed-in-sandbox`:** Allows commands to execute automatically *inside* the OS-level **Terminal Sandbox** (which restricts filesystem writes outside the workspace and blocks unauthorized network calls), prompting only when escaping the sandbox.
- **`always-proceed`:** Auto-approves tool execution without prompting. Reserve this for isolated containers, disposable worktrees, or trusted workflows.

### 2. Granular Access Boundaries
In Antigravity Settings (or per-project overrides), you can lock down four independent axes:
- **Non-Workspace File Access (`allow` / `ask` / `deny`):** Prevents an agent from reading `~/.ssh`, `~/.aws`, or modifying files outside the active project root.
- **Internet Access Policy (`allow` / `ask` / `deny`):** Controls whether commands/tools can make outbound network requests.
- **Command Allowlist / Denylist:** Pre-approve safe read-only or test commands (`git status`, `pytest`, `./mvnw test`) while permanently blocking destructive commands.
- **Browser Allowlist:** Restricts which domains Antigravity's browser automation tools are allowed to visit.

---

## Claude Code Permission Model

Claude Code follows a **conservative-by-default** posture: read-only operations (reading files, searching with glob/grep) are permitted automatically, while file edits and Bash commands require explicit approval unless configured otherwise.

### Permission Modes
You can switch modes interactively (e.g., via `Shift+Tab` in the CLI) or configure them per subagent:
- **Default:** Prompts on every file edit and shell command.
- **`acceptEdits`:** Auto-approves file edits (`Edit`, `Write`) within the workspace while still prompting for Bash commands.
- **`plan`:** Read-only exploration and planning mode. The agent cannot modify files or run mutating commands until you approve the plan and exit plan mode.
- **`bypassPermissions`:** Skips all permission prompts (equivalent to `--dangerously-skip-permissions`). **Only** use this inside ephemeral Docker containers, CI runners, or isolated sandboxes.

### Declarative Rules in `settings.json`
Team-shared rules live in `.claude/settings.json` (committed to Git), while personal overrides live in `.claude/settings.local.json` (gitignored):

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Read(src/**)"
    ],
    "deny": [
      "Read(.env*)",
      "Read(~/.ssh/**)",
      "Bash(rm -rf *)",
      "Bash(git push --force *)",
      "Bash(curl *)"
    ]
  }
}
```

Notice how `deny` rules protect secrets (`.env*`, `~/.ssh/**`) from even entering the LLM's context window—preventing accidental credential leakage to cloud model APIs.

---

## Human-in-the-Loop (HITL) Boundaries

A permission model is only useful if it defines **where the agent runs autonomously and where a human must intervene**. Good HITL design avoids two extremes: *prompt fatigue* (clicking "Approve" 40 times for harmless `git status` or `pytest` runs) and *blind autonomy* (letting an agent push to `main` or drop a database).

### The Four HITL Checkpoints

| Boundary | What Happens Here | Antigravity Mechanism | Claude Code Mechanism |
| :--- | :--- | :--- | :--- |
| **1. Scope & Intent Gate** | Agent clarifies ambiguous requirements before editing | `/plan`, `/grill-me`, `ask_question`, Plan Artifacts | `plan` mode (`/plan`), interactive Q&A |
| **2. Tool & Action Gate** | Harness pauses before risky commands or external calls | `strict` / `request-review`, `internet_access: ask`, `hooks.json` | Default mode, `permissions.ask`, `PreToolUse` hooks |
| **3. Blast-Radius Boundary** | Agent runs freely inside a safe sandboxed box | `proceed-in-sandbox` + Terminal Sandbox + `workspace: "share"` | `acceptEdits` + `permissions.allow` + `--worktree` |
| **4. Final Merge / Deploy Gate** | Human audits diffs, tests, and commits before shipping | Files Changed pane + `git diff` review | `/review`, `Esc Esc` / `/rewind` checkpoints, `git diff` |

### Calibrating Your Autonomy Dial

As you gain confidence in a repository's test suite and hooks, gradually shift low-risk actions to **auto-approve** while keeping high-impact actions **human-gated**:

- **Safe to Auto-Approve:** Read-only file search (`Read`, `Grep`, `Glob`), running unit tests, formatting code, and editing files inside an isolated Git worktree.
- **Keep Human-Gated:** Installing new dependencies (`npm install`, `pip install`), modifying CI/CD or infrastructure-as-code (`Dockerfile`, Terraform), database migrations against shared environments, `git push`, and outbound network/API mutations.
- **Always Deny:** Reading local secrets (`.env*`, `~/.ssh`, `~/.aws`), `git push --force`, and destructive recursive deletes outside temp/worktree paths.

---

## Git as Your Operational Safety Net

Even with perfect permissions, an agent can take a wrong turn mid-refactor and touch 14 files before you realize it. Follow these three Git habits:

1. **Start Clean:** Never launch an autonomous agent task on a dirty working tree. Commit or stash your work first so `git diff` shows *only* what the agent changed.
2. **Use Checkpoints & Rewind:** Claude Code automatically snapshots edits so you can rewind (`Esc Esc` or `/rewind`) to an earlier turn if an experiment goes sideways.
3. **Isolate Risky Work in Worktrees:** Instead of letting an agent mutate your main checkout, run it in a dedicated Git worktree (`git worktree add` or `--worktree` / `workspace: "share"`). If the experiment fails, delete the worktree; your main branch remains untouched.

```text
Main Repo (clean)  --->  Worktree A (Agent building Feature X)
                   --->  Worktree B (Agent investigating Bug Y)
```
