# Claude Code on Linux: Shell Composition, tmux & Worktree Mastery

For a senior Linux developer, **Claude Code** feels immediately natural because it is not a walled-garden GUI—it is a **Unix-native CLI process**. It reads `stdin`, writes `stdout`, composes with pipes, respects exit codes, and lives comfortably inside `tmux` alongside `git`, `ripgrep`, `jq`, and `gh`.

---

## Composing Claude Code in Unix Pipelines

Instead of copying terminal output into a browser chat, senior operators pipe Linux streams directly into `claude -p` (headless print mode):

```bash
# 1. Triage a failing systemd service from journalctl
journalctl -u order-api.service -n 120 --no-pager \
  | claude -p "Identify the root cause and failing config key."

# 2. Diagnose Docker container crashes
docker logs --tail 200 payments-worker 2>&1 \
  | claude -p "Summarize the exception chain and affected class."

# 3. Pre-PR self-review of staged changes
git diff --staged \
  | claude -p "Review for race conditions, N+1 queries, and leaks."
```

For shell scripts and CI jobs, combine `-p` with `--output-format json` and `jq` to extract structured fields cleanly without fragile regexes.

---

## The `tmux` + Git Worktree Power Workflow

Senior engineers rarely work on one linear task at a time: you might be building a feature while an urgent production bug or PR review lands. Combining **`tmux`** with **Git worktrees** lets you run multiple isolated Claude Code sessions concurrently without them ever colliding on disk:

```text
tmux session: "work"
  ├── Window 1 (main checkout)   --> nvim / git status / manual review
  ├── Window 2 (worktree-feat)   --> claude --worktree feat-idempotency
  └── Window 3 (worktree-hotfix) --> claude --worktree fix-hikari-leak
```

```bash
# Launch Claude Code directly in an isolated Git worktree
claude --worktree feat-idempotency

# Inside tmux:
#   Pane A: Claude Code implementing + running tests
#   Pane B: `watch -n 2 git diff --stat` to monitor blast radius live
```

When Window 2 finishes, you inspect its diff, merge or cherry-pick the clean branch, and let Claude clean up the temporary worktree—keeping your primary working directory untouched.

---

## Linux Security & Sandboxing Hygiene

On a Linux workstation, your user account often holds SSH keys, cloud credentials, GPG keys, and kubeconfigs. Never run an autonomous agent with broad permissions without locking down sensitive paths in `~/.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)",
      "Read(~/.kube/**)",
      "Read(~/.gnupg/**)",
      "Read(.env*)",
      "Bash(rm -rf *)",
      "Bash(sudo *)",
      "Bash(curl * | sh)"
    ]
  }
}
```

### When You Need Full Autonomy: Ephemeral Containers
If you want `--dangerously-skip-permissions` (`bypassPermissions`) for a massive automated migration, **do not run it on your host Linux OS**. Run it inside an ephemeral, rootless Docker/Podman container mounting *only* the project worktree:

```bash
podman run --rm -it \
  -v "$(pwd):/workspace:Z" -w /workspace \
  -e ANTHROPIC_API_KEY \
  my-dev-image claude --dangerously-skip-permissions \
  -p "Migrate all JUnit 4 @Test annotations to JUnit 5."
```

This gives the agent full speed inside the container while guaranteeing zero blast radius on your host machine.
