# Side-by-Side Operator Cheat Sheet: Antigravity vs. Claude Code

If you switch between **Google Antigravity** and **Claude Code** across different projects or teams, this quick-reference map translates concepts, file locations, and operator shortcuts directly between both ecosystems.

---

## Configuration & Memory Files

| Concept | Google Antigravity | Claude Code |
| :--- | :--- | :--- |
| **Repo Memory** | `GEMINI.md` or `AGENTS.md` | `CLAUDE.md` |
| **Personal Repo Memory** | Local untracked `.agents/rules/` | `CLAUDE.local.md` (gitignored) |
| **Global User Memory** | `~/.gemini/config/` | `~/.claude/CLAUDE.md` |
| **Scoped Rules** | `.agents/rules/*.md` | `.claude/rules/*.md` |
| **Skills Folder** | `.agents/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` |
| **MCP Configuration** | `mcp_config.json` | `.mcp.json` / `~/.claude.json` |
| **Lifecycle Hooks** | `hooks.json` | `.claude/settings.json` (`hooks`) |
| **CLI Settings** | `~/.gemini/antigravity-cli/settings.json` | `~/.claude/settings.json` |

---

## Operator Commands & Controls

| Action | Google Antigravity | Claude Code |
| :--- | :--- | :--- |
| **Launch Terminal CLI** | `agy` | `claude` |
| **Generate Starter Memory** | Ask agent to inspect & write `AGENTS.md` | `/init` |
| **Enter Planning Mode** | `/plan` (or `/grill-me` for Q&A alignment) | `/plan` (or `Shift+Tab` cycle) |
| **Attach File / Context** | `@` mention in chat / CLI | `@` file path mention |
| **Compact Context** | `/compact` | `/compact [focus instructions]` |
| **Reset Session** | Start New Conversation | `/clear` |
| **Switch Model** | Settings / Model Selection | `/model` |
| **Exit CLI** | `Ctrl+D Ctrl+D`, `/exit`, or `/quit` | `Ctrl+D` or `/exit` |

---

## Execution Policies & Isolation

| Goal | Google Antigravity | Claude Code |
| :--- | :--- | :--- |
| **Prompt Every Time** | `strict` / `request-review` | Default permission mode |
| **Auto-Edit Files Only** | Project file policy + `request-review` | `acceptEdits` mode |
| **Sandboxed Auto-Run** | `proceed-in-sandbox` + Terminal Sandbox | OS sandbox / container + `allow` rules |
| **Unattended CI / Container** | `always-proceed` (in sandbox) | `bypassPermissions` / `--allowedTools` |
| **Git Worktree Isolation** | `workspace: "share"` (subagent/swarm) | `isolation: worktree` / `--worktree` |
| **Non-Interactive Pipe** | Python SDK / `run_workflow` / `/schedule` | `claude -p "prompt" --output-format json` |

---

## Rule of Thumb for Switching Tools

1. **Same Core Mental Model:** Both tools obey context hygiene, progressive disclosure (`SKILL.md`), deterministic hooks, and Git worktree isolation.
2. **Portable Conventions:** Keeping your instructions in `AGENTS.md` / `SKILL.md` and deterministic scripts in `scripts/` makes 80% of your team's setup portable across both agents.
