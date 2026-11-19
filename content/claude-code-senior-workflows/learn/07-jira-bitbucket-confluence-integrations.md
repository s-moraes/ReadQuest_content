# Jira, Bitbucket & Confluence with Claude Code

In enterprise engineering, requirements live in **Jira**, architecture docs and runbooks live in **Confluence**, and code reviews happen in **Bitbucket**. Wiring Claude Code to the Atlassian suite eliminates manual copy-pasting between browser tabs and your terminal.

---

## Integration Architecture: MCP vs. CLI/REST

You can connect Claude Code to Atlassian in two ways:
1. **Atlassian MCP Server (Official Rovo MCP / Community MCP):** Connects via Streamable HTTP (OAuth) or `stdio` (API token) so Claude can read Jira issues, search Confluence pages, and inspect Bitbucket PRs natively.
2. **Lightweight CLI / `curl` + `jq` Scripts:** For teams that prefer zero MCP context bloat, a small shell script or Skill (`SKILL.md`) calling the Jira/Bitbucket REST API via `curl` gives deterministic, low-token output.

---

## 1. Jira: Ticket-to-Plan & Status Hygiene

Instead of summarizing a ticket manually, let Claude Code pull the acceptance criteria directly before entering `/plan` mode:

```text
Fetch Jira issue PAY-1428 (including subtasks and comments).
Compare the acceptance criteria against @src/main/java/com/acme/billing/.
Propose an implementation plan and list any missing edge cases.
```

### High-Value Jira Workflows
- **Pre-Implementation Scoping:** Read epic + linked bugs + comments to catch hidden requirements buried in discussion threads.
- **Subtask Breakdown:** Draft technical subtasks with affected modules and test criteria for human review before creating them.
- **Scoped Subagents:** If your Jira MCP exposes 20+ tools, attach it only to a dedicated `ticket-reader` subagent so those schemas don't bloat your main coding session.

---

## 2. Confluence: Grounding Agents in Internal Standards

Every senior engineer knows the pain of an agent inventing patterns that violate your company's internal RFCs. Connecting Confluence lets Claude Code read your **ADRs (Architecture Decision Records)**, error-code standards, and deployment runbooks on demand:

```text
Search Confluence in the "PLATFORM" space for "Idempotency Key RFC".
Verify that our new REST endpoint in OrderController follows
the header naming and TTL rules defined there.
```

**Operator Tip:** Never paste huge Confluence pages into `CLAUDE.md`. Fetch them on demand only for tasks that need them, or distill key invariants into a concise `.claude/skills/` playbook.

---

## 3. Bitbucket: PR Diffs, Pipelines & Review Loops

Whether you use Bitbucket Cloud or Bitbucket Data Center (Server):
- **Automated Pre-Review:** Have Claude fetch open PR comments or pipeline failures, reproduce the failing Maven/Gradle test locally, and propose fixes.
- **Review Assistant:** Pipe a Bitbucket PR diff (or fetch via MCP) into a read-only `code-reviewer` subagent that checks for SQL injection, missing `@Transactional` boundaries, and backward-incompatible API changes.

---

## Enterprise HITL Guardrails for Atlassian

Never grant an autonomous agent unrestricted write access to Jira, Confluence, or Bitbucket without human sign-off:
- **Read-Only by Default:** Use read-only API tokens or `--allowedTools` for automated/CI runs.
- **Human-Gated Mutations:** Keep interactive approval required before posting PR comments, transitioning Jira tickets to *Done*, or editing shared Confluence pages.
- **Prompt Injection Defense:** External Jira comments and Confluence pages can contain untrusted text; never combine Atlassian MCP tools with `--dangerously-skip-permissions`.
