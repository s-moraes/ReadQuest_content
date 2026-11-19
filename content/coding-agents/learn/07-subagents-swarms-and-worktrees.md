# Subagents, Swarms & Parallel Worktree Execution

A single agent conversation hits a natural ceiling on large engineering tasks. If you ask one session to research 25 files, refactor 3 backend services, update the frontend, and write end-to-end tests, the context window fills with noisy search outputs and early architectural constraints get pushed out.

The solution is **delegation and isolation**: splitting work across specialized **subagents**, **parallel worktrees**, and **multi-agent swarms**.

---

## Subagents: Isolated Contexts for Focused Work

A **subagent** is an independent agent instance launched with its own fresh context window, a specific prompt, and optionally a restricted set of tools or a different model. Only its **final summary** returns to the parent coordinator—all intermediate `grep` outputs and stack traces stay isolated.

```text
Parent Agent (Clean architectural context)
   |
   +---> Subagent 1: Codebase Researcher (read-only, fast model)
   |        Searches 40 files -> Returns 15-line architecture summary
   |
   +---> Subagent 2: Test Runner / Verifier (isolated shell)
            Runs integration suite -> Returns failure root cause
```

### Subagents in Google Antigravity
Antigravity provides built-in delegation primitives directly to the agent:
- **`research` subagent:** Runs in a read-only sandbox with no network access, ideal for broad codebase surveys without polluting the main context.
- **`self` subagent:** Inherits the parent's full toolset and prompt for parallel implementation tasks.
- **Custom Subagents (`define_subagent` / `invoke_subagent`):** Define specialized roles on the fly with tailored system prompts, model tiers (`flash_lite`, `flash`, `pro`, or `inherit`), and workspace modes.

### Subagents in Claude Code (`.claude/agents/*.md`)
In Claude Code, custom subagents are Markdown files with YAML frontmatter stored in `.claude/agents/` (project) or `~/.claude/agents/` (global):

```markdown
---
name: security-reviewer
description: Audits staged diffs for auth, injection, and secret leaks.
tools: Read, Grep, Glob, Bash
disallowedTools: Edit, Write
model: sonnet
permissionMode: plan
---

Review the current git diff for OWASP Top 10 vulnerabilities,
missing authorization checks, and hardcoded secrets.
Report findings by severity with file and line numbers.
```

---

## Workspace Isolation: `inherit` vs. `worktree` / `share`

When two agents edit files in the *same* directory simultaneously, they overwrite each other's changes and corrupt `git status`. Both platforms solve this with **Git worktree** or **branch isolation**:

| Mode | Antigravity (`Workspace`) | Claude Code (`isolation`) | When to Use |
| :--- | :--- | :--- | :--- |
| **Shared Dir** | `inherit` (default) | Default (no isolation) | Read-only research, verification, or single-writer tasks |
| **Git Worktree** | `share` | `isolation: worktree` (or `claude --worktree`) | Parallel feature authors editing code simultaneously without duplicating `.git` storage |
| **Full Clone** | `branch` | Separate repo clone | Completely isolated experiments or destructive build tests |

When a worktree subagent finishes, you inspect its branch diff and merge or cherry-pick the clean commits back into your main working copy.

---

## Scaling Up: Swarms & Python Workflows

For large projects that benefit from multiple autonomous agents collaborating in parallel, **Google Antigravity** offers two native orchestration layers:

1. **Antigravity Swarms (`swarm` tool):**
   - A **Coordinator** spawns named workers (e.g., `backend-api`, `frontend-ui`, `verifier`) on a **shared message board**.
   - Writers receive `workspace: "share"` so each works in its own copy of the repo.
   - Workers collaborate asynchronously via `@mentions`, sleep at zero cost when `waiting`, and wake automatically when messaged.
   - A `kill` permanently removes a worker and its temporary workspace—so you always land/merge its branch first.

2. **Dynamic Workflows (`run_workflow`):**
   - For deterministic fan-out/fan-in pipelines (e.g., *"Audit all 30 microservices in parallel, then aggregate a single report"*), Antigravity executes a Python orchestration script using `agent()`, `parallel()`, and `pipeline()` primitives.

In **Claude Code**, you achieve parallel fan-out either via **Agent Teams** or by scripting headless worktree workers (`claude -p "..." --worktree`) from your shell or CI runner.

---

## When NOT to Use Multi-Agent Orchestration

Multi-agent setups multiply token consumption and coordination overhead. Keep a **single agent** when:
- The task touches 1–3 tightly coupled files.
- Step B depends sequentially on seeing the exact code written in Step A.
- You are still exploring the problem and haven't finalized the architecture yet.

Reach for **subagents and swarms** when tasks are **read-heavy** (research/review) or **naturally parallelizable** across independent modules, worktrees, or test suites.
