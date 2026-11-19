# Parallel Workspaces: tmux, Git Worktrees & Linux Containers

Senior engineers rarely work on one linear task at a time: you might be building a feature while an urgent production bug or PR review lands. Combining **`tmux`** with **Git worktrees** and **rootless Linux containers** lets you run multiple isolated Claude Code sessions concurrently without file collisions or host risk.

---

## The `tmux` + Git Worktree Power Workflow

If two agent sessions edit files in the *same* working directory, they overwrite each other's changes and corrupt `git status`. **Git worktrees** give each session its own working tree linked to the same `.git` repository:

```text
tmux session: "work"
  ├── Window 1 (main checkout)   --> nvim / git status / manual review
  ├── Window 2 (worktree-feat)   --> claude --worktree feat-idempotency
  └── Window 3 (worktree-hotfix) --> claude --worktree fix-hikari-leak
```

```bash
# Launch Claude Code directly in an isolated Git worktree
claude --worktree feat-idempotency

# Inside a split tmux pane, watch the agent's blast radius live:
watch -n 2 git diff --stat
```

When Window 2 finishes, you review its branch diff, merge or cherry-pick the clean commits into your main branch, and remove the temporary worktree—keeping your primary checkout spotless.

---

## Linux Security & Sandboxing Hygiene

On a Linux workstation, your user account often holds SSH keys, cloud credentials, GPG keys, and kubeconfigs. Always lock down sensitive paths in `~/.claude/settings.json`:

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

Notice that `Read(...)` deny rules prevent secrets from ever entering the model's context window.

---

## Full Autonomy Inside Ephemeral Containers

If you want `--dangerously-skip-permissions` (`bypassPermissions`) for a large, unattended refactoring or migration, **never run it directly on your host Linux OS**. Run it inside an ephemeral, rootless Docker or Podman container mounting *only* the isolated worktree:

```bash
podman run --rm -it \
  -v "$(pwd):/workspace:Z" -w /workspace \
  -e ANTHROPIC_API_KEY \
  my-java-dev-image claude --dangerously-skip-permissions \
  -p "Migrate all JUnit 4 @Test annotations to JUnit 5."
```

The agent gets maximum speed inside the container while your host filesystem, `~/.ssh`, and other repositories remain completely unreachable.
