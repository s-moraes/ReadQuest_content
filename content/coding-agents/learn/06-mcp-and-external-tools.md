# Model Context Protocol (MCP): Connecting External Systems

Coding agents are natively great at reading local files and running shell commands. However, real engineering work lives across **external systems**: PostgreSQL schemas, Jira/Linear tickets, GitHub PRs, Sentry stack traces, Figma specs, or internal documentation wikis.

Before **MCP (Model Context Protocol)**, integrating an agent with Jira or Postgres meant writing brittle custom glue scripts or asking the developer to copy-paste JSON into the chat. MCP standardizes how agents discover and invoke external tools, read structured resources, and use domain prompts.

---

## MCP Architecture: Client, Server & Transports

MCP follows a clean client-server architecture:

```text
+--------------------------------+          +----------------------------+
|  Coding Agent (MCP Host/Client)|  JSON-   |  MCP Server (e.g. Postgres |
|  Google Antigravity /          |  RPC     |  GitHub, Playwright, Jira) |
|  Claude Code                   | <======> |                            |
+--------------------------------+          +----------------------------+
                                  stdio OR Streamable HTTP
```

- **`stdio` Transport (Local):** The agent spawns the MCP server as a local child process (e.g., `npx -y @modelcontextprotocol/server-postgres ...`) and communicates over `stdin`/`stdout`. Ideal for local databases, filesystem bridges, or CLI wrappers.
- **Streamable HTTP / SSE Transport (Remote):** The agent connects over HTTPS to a hosted MCP server (e.g., remote GitHub, Linear, or internal company API gateway) using OAuth or bearer tokens.

### What an MCP Server Exposes
1. **Tools:** Executable functions with JSON Schemas (e.g., `query_readonly_sql`, `get_sentry_issue`, `create_pull_request`).
2. **Resources:** Read-only data URIs (e.g., `postgres://schema/orders`, `file://logs/app.log`) that can be attached to context.
3. **Prompts:** Reusable workflow templates exposed by the server.

---

## Configuring MCP in Antigravity vs. Claude Code

### Google Antigravity (`mcp_config.json`)
In Antigravity, MCP servers are configured in `mcp_config.json` (project-scoped or global in `~/.gemini/config/`), or bundled inside a **Plugin** (`plugins/<name>/plugin.json`).

```json
{
  "mcpServers": {
    "postgres-local": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://readonly:pass@localhost:5432/app"
      }
    }
  }
}
```

In the Antigravity 2.0 Desktop App, you can also type `@` in the chat canvas to explicitly mention and attach an MCP server or specific tool to your prompt.

### Claude Code (`.mcp.json` & CLI)
In Claude Code, project-shared MCP servers live in `.mcp.json` at the repo root (committed to Git without secrets—use `${ENV_VAR}` expansion), while personal/local servers are managed via `claude mcp add`:

```bash
# Add a local stdio MCP server scoped to the project
claude mcp add --scope project github -- npx -y @modelcontextprotocol/server-github

# Add a remote HTTP MCP server
claude mcp add --transport http linear https://mcp.linear.app/mcp
```

---

## The Operator's Two Biggest MCP Traps

### 1. Context Bloat (Tool Schema Overload)
Every active MCP server injects its **entire list of tool definitions and JSON schemas** into the model's context window at session start. Connecting 8 MCP servers with 40 tools each can silently burn 20,000+ tokens before you even type `"hello"`, degrading reasoning quality.

**Fix:**
- Enable only the MCP servers needed for the current project.
- Prefer **CLI tools** (`gh`, `kubectl`, `psql`) when a tool already exists in your shell—the agent already knows how to run `gh pr view` without needing 30 GitHub MCP schemas in context.
- In Claude Code, scope specialized MCP servers to specific **subagents** (`mcpServers` field) so the main session stays lean.

### 2. Prompt Injection & Least-Privilege Access
When an MCP server fetches an external GitHub issue or web page written by an untrusted user, that text enters the agent's context. Hidden instructions inside an issue comment (indirect prompt injection) can trick a careless agent into running a destructive local command.

**Fix:**
- Use **read-only credentials** for database MCP servers (`SELECT`-only roles).
- Never pair unreviewed external-data MCP tools with `bypassPermissions` / `always-proceed` auto-execution.
- Keep human approval (`request-review` / default prompts) active for state-mutating MCP actions like sending emails, merging PRs, or writing to production systems.
