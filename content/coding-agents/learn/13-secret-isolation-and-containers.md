# Credential Isolation, Devcontainers & Ephemeral Environments

A common security mistake is assuming `permissions.deny` on `Read(.env*)` keeps your secrets safe. If the agent can run Bash commands, **denying `Read` is not enough**.

---

## The `.env` and Bash Bypass Trap

Consider a `.claude/settings.json` rule that blocks `Read(.env*)`. While the model cannot call the `Read` tool on `.env`, an unrestricted Bash tool can still execute:

```bash
# Any of these bypasses a Read-tool-only deny rule:
cat .env
grep API_KEY .env.local
printenv | grep SECRET
```

Once printed to stdout, the secret enters the LLM's context window—and gets sent to the model provider's API.

### Closing the Gap

1. **Keep Real Secrets Out of the Workspace:** Store only `.env.example` with dummy values (`DB_PASS=local_dev_only`) inside the repo.
2. **Use OS Sandbox + Hook Guards:** Block `printenv`, `env`, and `.env` reads inside `PreToolUse` Bash hooks as defense-in-depth.
3. **Inject Secrets at Runtime Only:** Use a secret manager (`op run`, `doppler run`, or local vault wrappers) outside the agent's shell.

---

## Devcontainers & Ephemeral Environments

When you want **high autonomy** (`always-proceed` in Antigravity or `--dangerously-skip-permissions` in Claude Code) for long refactors or headless CI tasks, an OS sandbox on your laptop is still sharing your host kernel and local files.

The gold standard is an **ephemeral Docker Devcontainer** or **disposable cloud VM**:

```dockerfile
# Minimal agent-safe devcontainer concept
FROM mcr.microsoft.com/devcontainers/base:ubuntu
RUN apt-get update && apt-get install -y git ripgrep
USER vscode
WORKDIR /workspace
```

### Container Hardening Checklist

- **Mount only the repo:** Never mount `~/.ssh`, `~/.aws`, or `/var/run/docker.sock` into an autonomous agent container.
- **Drop capabilities & non-root user:** Run as a non-root user (`vscode`) with `--cap-drop=ALL` where possible.
- **Ephemeral Git credentials:** Use a scoped, short-lived GitHub token with write access *only* to feature branches—never `main`.

---

## Blast-Radius Tiers Matrix

Choose the lightest isolation tier that matches the risk of your task:

| Tier | Mechanism | Best For | Safe Autonomy Level |
| :--- | :--- | :--- | :--- |
| **1. Plan Only** | `/plan` / `research` subagent | Architecture, codebase audits | Read-only (zero writes) |
| **2. OS Sandbox** | `proceed-in-sandbox` / Bash sandbox | Daily coding & unit tests | Auto-approve inside workspace |
| **3. Git Worktree** | `workspace: "share"` / `--worktree` | Parallel features & risky refactors | Auto-approve edits on branch |
| **4. Ephemeral VM** | Docker devcontainer / CI runner | Headless `-p` runs, untrusted repos | `bypassPermissions` / `always-proceed` |
