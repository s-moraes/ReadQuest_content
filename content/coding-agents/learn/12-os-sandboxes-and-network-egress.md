# OS-Level Sandboxes, Filesystem Jails & Network Egress

Permission prompts (`ask` / `allow`) protect individual tool calls, but **OS-level sandboxing** enforces boundaries in the kernel so even a buggy command or prompt injection cannot escape.

---

## How OS-Level Sandboxes Work

Both **Google Antigravity** (`proceed-in-sandbox`) and **Claude Code** (built-in Bash sandbox) wrap shell commands in OS-native isolation primitives rather than relying on LLM obedience:

| Platform | Underlying Mechanism | What It Restricts |
| :--- | :--- | :--- |
| **macOS** | Seatbelt (`sandbox-exec`) | Filesystem writes outside workspace; outbound sockets |
| **Linux** | Namespaces / `bubblewrap` | Mounts workspace R/W, host `/` R/O; filters network |

Because the OS enforces the boundary, a command like `rm -rf ~/.ssh` or `cat ~/.aws/credentials > /tmp/leak` fails at the syscall level—even if the agent was tricked into running it.

```text
Agent Bash Tool
   |
   v
[ OS Sandbox Boundary ]
   |-- Workspace (./repo) : Read + Write allowed
   |-- Host Secrets (~/.ssh, ~/.aws) : Blocked
   |-- Outbound Network : Blocked or Allowlisted
```

---

## Network Egress & Supply-Chain Safety

Unrestricted outbound network access inside an agent shell introduces two real risks:

1. **Data Exfiltration via Prompt Injection:** A malicious comment in an external issue or dependency `README` can instruct the agent to `curl` local files to an attacker server.
2. **Unintended Dependency Drift:** An agent may run `npm install` or `pip install` to pull unvetted packages instead of using libraries already in your lockfile.

### Practical Egress Policies

- **Offline Test Execution (`deny`):** For unit tests, linting, and local builds, disable network access completely (`internet_access: deny` in Antigravity).
- **Registry-Only Allowlists:** When dependency resolution is required, allow only your internal artifact proxy (e.g., Artifactory, Nexus) or official registries (`registry.npmjs.org`, `pypi.org`, `repo.maven.apache.org`).
- **Human Gate for Installs:** Keep `npm install`, `pip install`, and `curl` set to `ask` so the operator approves every new dependency.

---

## Auditing Sandbox Escape Hatches

Some legitimate workflows **cannot** run inside a strict OS sandbox:
- Connecting to a local Docker daemon (`/var/run/docker.sock`) for Testcontainers.
- Running database migrations against a staging host over VPN.
- Pushing Git branches to a remote (`git push`).

### The Rule for Escapes

Never turn off the sandbox globally just because one command needs host access. Instead:
1. Keep **`proceed-in-sandbox`** as your default policy for 95% of edit/test loops.
2. Let the harness prompt (`ask`) on the rare commands that must escape the sandbox.
3. Review the exact command string before approving—never approve chained `&&` commands blindly.
