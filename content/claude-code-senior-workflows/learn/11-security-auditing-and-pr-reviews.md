# Security Auditing & Pre-PR Subagent Reviews

An agent that writes code in a 40-turn session often develops **tunnel vision**—it is focused on making tests pass and can overlook subtle security or concurrency regressions. Senior engineers counter this by running a **fresh-context reviewer subagent** before opening a PR.

---

## Why Fresh-Context Reviews Catch More Bugs

A brand-new subagent has **zero memory** of the compromises made during implementation. It sees only the `git diff` and your security/architecture checklist.

Create `.claude/agents/security-auditor.md`:

```markdown
---
name: security-auditor
description: Audits staged or branch diffs for security, concurrency, and resource leaks.
tools: Read, Grep, Glob, Bash
disallowedTools: Edit, Write
model: sonnet
permissionMode: plan
---

Inspect `git diff origin/main...HEAD`. Check specifically for:
1. Missing authorization checks on new controller/endpoint methods.
2. SQL injection (string concatenation in native/JdbcTemplate queries).
3. Unbounded queries (missing pagination/LIMIT) or N+1 loops.
4. Resource leaks (unclosed streams, missing try-with-resources).
5. Thread-safety issues (shared mutable state in Spring singletons).
6. Hardcoded secrets, tokens, or PII in logs.

Report findings by severity (CRITICAL / HIGH / MEDIUM) with file and line.
```

---

## Integrating into Your Bitbucket / GitHub Workflow

You can invoke this audit interactively (`/agents` or asking Claude to run `security-auditor`) or from a Linux shell before pushing:

```bash
git diff origin/main...HEAD \
  | claude -p "Run a strict OWASP + Java concurrency review on this diff." \
    --allowedTools "Read,Grep,Glob" \
    --max-turns 6
```

Treat the agent's review like a fast, tireless first-pass reviewer: fix any valid findings, dismiss false positives, and then request human peer review.
