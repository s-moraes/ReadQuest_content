# Context Budgeting & Sandbox Hardening Cheat Sheet

Use this quick-reference sheet to keep agent context windows fast, cheap, and isolated from host secrets.

---

## Starter `.claudeignore` / `.geminiignore`

Place this at your repository root so agent `grep` and file-discovery tools skip generated noise:

```text
# Dependencies & build outputs
node_modules/
dist/
build/
target/
.gradle/
.venv/

# Lockfiles & minified assets
package-lock.json
yarn.lock
pnpm-lock.yaml
*.min.js
*.map

# Large test fixtures
coverage/
**/snapshots/**
```

---

## Context Recovery Decision Matrix

| Situation | Best Action | Command |
| :--- | :--- | :--- |
| Last 1–2 turns broke code | Rewind turn + edits | `Esc Esc` / `/rewind` |
| Long session, same task | Targeted compaction | `/compact preserve <key facts>` |
| Need broad 20-file survey | Offload to read-only agent | `research` subagent |
| Switching tasks or context rot | Write handoff + wipe | `/handoff` then `/clear` |

---

## Sandbox Hardening Checklist

Before enabling `proceed-in-sandbox` or `acceptEdits`, verify these 5 controls:

- [ ] **No real secrets in `.env`:** Keep only `.env.example` inside the workspace.
- [ ] **Deny secret paths:** Block `Read(.env*)`, `Read(~/.ssh/**)`, `Read(~/.aws/**)`.
- [ ] **Block Bash secret dumps:** Guard `printenv`, `env`, and `cat .env` in `PreToolUse` hooks.
- [ ] **Restrict network egress:** Keep `internet_access: deny` for unit-test loops; allowlist registries only when needed.
- [ ] **Use ephemeral containers for full autonomy:** Reserve `always-proceed` / `--dangerously-skip-permissions` for disposable devcontainers or CI VMs.
