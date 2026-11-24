# Checkpoints, `reflog` Recovery, Rebasing & Git Hooks

Even with a great plan, an agent can take a wrong turn mid-refactor. Knowing how to **rewind**, **recover**, and **resolve conflicts** cleanly keeps you in control.

---

## Agent Checkpoints vs. Git Recovery

Use the lightest rollback tool that matches how far the mistake went:

| Scope of Mistake | Tool to Use | What It Does |
| :--- | :--- | :--- |
| **Last 1–2 turns** | `/rewind` (`Esc Esc` in Claude Code) | Restores files + conversation to a turn checkpoint |
| **Unstaged agent edits** | `git restore <file>` or `git restore .` | Discards working-tree edits (keeps untracked files) |
| **Untracked junk files** | `git clean -fd` (preview with `-nd` first) | Removes newly created untracked files/dirs |
| **Bad local commits** | `git reset --soft HEAD~1` | Undoes the commit while keeping changes staged |
| **Lost branch / hard reset** | `git reflog` | Recovers any commit SHA from the last 30+ days |

```bash
# Preview untracked files before deleting
git clean -nd

# Recover a commit after an accidental reset --hard
git reflog -n 10
git checkout -b rescue-branch <commit-sha>
```

---

## Agent-Assisted Rebasing & Conflict Resolution

Agents are surprisingly good at resolving merge conflicts—**if** you give them the intent behind both sides.

Never ask an agent to *"fix conflicts"* blindly, or it may run `git checkout --ours` and silently delete a teammate's bugfix. Instead:

```text
Rebase feat/rate-limiter onto origin/main.
For any conflict:
1. Read both sides of the conflict markers and git log -n 3 on main.
2. Preserve main's new auth header check AND our rate-limit middleware.
3. After `git rebase --continue`, run `npm test` to verify.
```

Always inspect the resulting `git diff origin/main...HEAD` after an agent resolves a rebase.

---

## Git Hooks vs. Agent Lifecycle Hooks

Local Git hooks (`pre-commit`, `commit-msg`) and agent lifecycle hooks (`PreToolUse`, `PostToolUse`) solve different parts of the pipeline:

- **Agent Hooks (`PreToolUse` / `PostToolUse`):** Run *during* the coding loop (e.g., auto-formatting after `Edit`, blocking `rm -rf` or `git push --force`).
- **Git Hooks (`pre-commit` / `pre-push`):** Run *at commit/push time* as the final repository gate (linting, secret scanning with `gitleaks`, conventional commit validation).

### The Golden Rule: Block `--no-verify`

When a `pre-commit` hook fails, an autonomous agent might try to "solve" the error by running `git commit --no-verify`—bypassing your linter or secret scanner!

Prevent this deterministically by adding `Bash(git commit *--no-verify*)` to `permissions.deny` (or blocking `--no-verify` in a `PreToolUse` hook).
