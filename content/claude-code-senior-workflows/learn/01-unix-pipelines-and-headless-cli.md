# Claude Code as a Unix Citizen: Pipes, Logs & Headless CLI

For a senior Linux developer, **Claude Code** feels immediately natural because it is not a walled-garden GUI—it is a **Unix-native CLI process**. It reads `stdin`, writes `stdout`, composes cleanly with pipes, respects exit codes, and lives comfortably inside your terminal alongside `git`, `ripgrep`, `jq`, and `gh`.

---

## Composing Claude Code in Unix Pipelines

Instead of copying terminal output into a browser chat, senior operators pipe Linux streams directly into `claude -p` (headless print mode):

```bash
# 1. Triage a failing systemd service from journalctl
journalctl -u order-api.service -n 120 --no-pager \
  | claude -p "Identify the root cause and failing config key."

# 2. Diagnose Docker / Podman container crashes
docker logs --tail 200 payments-worker 2>&1 \
  | claude -p "Summarize the exception chain and affected class."

# 3. Pre-PR self-review of staged changes
git diff --staged \
  | claude -p "Review for race conditions, N+1 queries, and leaks."
```

Because `claude -p` runs non-interactively and exits with standard status codes, you can embed it in shell aliases, `Makefile` targets, and Git hooks.

---

## Structured Automation with `--output-format json`

When scripting around Claude Code on Linux, prose output is brittle to parse. Pass `--output-format json` and pipe into `jq`:

```bash
git diff origin/main...HEAD \
  | claude -p "List risky SQL or concurrency changes." \
    --allowedTools "Read,Grep,Glob" \
    --output-format json \
    --max-turns 5 \
  | jq -r '.result'
```

- **`--allowedTools`:** Enforces least-privilege read-only execution in automated scripts.
- **`--max-turns`:** Caps the tool loop so a stuck pipeline never burns unbounded API credits.

---

## Pairing with `gh`, `ripgrep` & `kubectl`

Senior operators rarely need heavy MCP servers for tools that already have great Linux CLIs. Claude Code natively knows how to invoke `gh`, `rg`, `jq`, and `kubectl` via `Bash`:
- **PR Triage:** `gh pr diff 412 | claude -p "Check backward compatibility."`
- **Pod Crash Analysis:** `kubectl logs deploy/billing -p --tail=150 | claude -p "Why did the container OOMKilled or crash?"`
- **Fast Symbol Search:** Let Claude use `rg` rather than reading entire directories into context.
