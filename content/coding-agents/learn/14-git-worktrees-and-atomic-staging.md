# Git Worktree Mastery, Clean Trees & Atomic Staging

Git is the single best safety net for autonomous coding agents. When used intentionally, it lets you run parallel experiments, inspect every line an agent touched, and stage changes with surgical precision.

---

## Pre-Flight Discipline: Always Start Clean

Never launch an autonomous agent task on a dirty working tree. If you already have 6 modified files, `git diff` mixes your human work with the agent's edits—making review and rollback painful.

```bash
# Before starting an agent session:
git status --short
git stash push -m "wip: pre-agent checkpoint"
# Or commit your current checkpoint first
```

### Atomic Staging with `git add -p`

After an agent finishes a feature, avoid running `git add .` blindly. Instead, walk through every hunk interactively:

```bash
git add -p
```

Inside `git add -p`, you can:
- **`y`** (stage) clean feature hunks.
- **`n`** (skip) leftover debug logs or unrelated formatting tweaks.
- **`s`** (split) a large hunk when an agent mixed two concerns in the same file.
- **`e`** (edit) a hunk manually before committing.

---

## Git Worktree Mastery

A **Git worktree** gives you a second working directory linked to the *same* `.git` object store—so you can run an agent on `feat/billing` while your main checkout stays on `main`.

```bash
# Create an isolated worktree + branch
git worktree add ../app-billing -b feat/billing

# List active worktrees
git worktree list

# Remove after merging or discarding
git worktree remove ../app-billing
git worktree prune
```

Both **Claude Code** (`claude --worktree <name>`) and **Google Antigravity** (`workspace: "share"`) automate worktree creation for subagents and swarms.

### Handling Dependencies & Ignored Files

New worktrees start with **no gitignored files** (`node_modules/`, `.venv/`, `.gradle/`, `.env.local`). Plan for this:

| Project Type | Worktree Strategy |
| :--- | :--- |
| **Node / pnpm** | `pnpm install` (content-addressable store makes it near-instant) |
| **Python** | Share a base `.venv` or run `uv sync` in milliseconds |
| **Java / Gradle** | Reuses global `~/.gradle/caches` automatically |
| **Local Configs** | Copy `.env.example` or symlink non-secret local configs |

> **Tip:** Never check out the *same* branch in two worktrees simultaneously—Git forbids it to prevent index corruption. Give each worktree a distinct branch (`agent/<task-name>`).
