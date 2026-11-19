# Sentry, Databases, Slack & Custom Enterprise Integrations

Beyond Atlassian, a senior developer's workflow spans **error tracking**, **live databases**, **team chat**, and **CI/CD**. Connecting Claude Code to these systems turns it from a code editor into an end-to-end operational assistant—provided you enforce strict least-privilege boundaries.

---

## High-Impact Developer Integrations

| System | How to Connect | High-Leverage Senior Workflow |
| :--- | :--- | :--- |
| **Sentry / Datadog** | MCP Server or REST CLI | Pull stack trace + breadcrumbs + release tag for a production alert, locate the exact commit via `git log`, and write a failing JUnit test |
| **PostgreSQL / MySQL** | Read-only MCP (`server-postgres`) or `psql` | Inspect real table schemas, indexes, and `EXPLAIN ANALYZE` plans before writing Flyway migrations or optimizing slow JPA queries |
| **GitHub / GitLab** | `gh` / `glab` CLI (preferred) or MCP | Fetch PR diffs, check CI run logs (`gh run view --log-failed`), and draft release notes |
| **Slack / Teams** | MCP (read-only / draft) | Summarize an incident channel thread into a post-mortem draft or extract reproduction steps from a bug report |
| **Playwright / Browser** | Playwright MCP | Reproduce frontend regressions, capture console/network errors, and verify end-to-end flows |
| **Swagger / OpenAPI** | Local spec file + `jq` or MCP | Validate DTOs and client code against the canonical `openapi.yaml` contract |

---

## Choosing Between MCP and Native Linux CLIs

Senior operators avoid adding an MCP server when a battle-tested Linux CLI already exists:

- **Prefer CLI (`gh`, `psql`, `kubectl`, `aws`, `curl`):** Zero startup context bloat! Claude Code already knows standard CLI flags, and you can pipe output through `head`, `grep`, or `jq` to keep context tiny.
- **Prefer MCP (`Sentry`, `Jira`, `Confluence`, `Playwright`):** When authentication requires OAuth flows, complex pagination, or structured binary/DOM interactions that are painful in raw `curl`.

---

## Three Rules for Safe Production Integrations

1. **Read-Only Credentials Always:** Database MCP servers must connect with a `SELECT`-only PostgreSQL role (`default_transaction_read_only = on`), never a superuser or migration role.
2. **Scrub PII & Secrets:** Never pipe raw production customer payloads into cloud LLM prompts; strip tokens, emails, and headers first.
3. **Scope MCP Servers to Subagents:** Keep your main `.mcp.json` minimal and attach heavy integrations (like Sentry or Jira) only to specialized subagents when needed.
