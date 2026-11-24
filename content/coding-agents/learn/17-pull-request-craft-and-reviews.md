# Pull Request Craft: Sizing, `gh` Evidence & Fresh-Context Reviews

AI coding agents make generating a 1,500-line diff effortless—which shifts the bottleneck from *writing* code to *reviewing* it. Great operators design PRs for human reviewers.

---

## PR Sizing & Reviewer Ergonomics

Large AI-generated PRs suffer from **"LGTM fatigue"**: reviewers skim 40 files, miss subtle bugs, and approve blindly.

- **Target `< 300–400` changed lines** per PR whenever possible.
- **Stack or split big features:** Land the schema migration + domain model in PR 1, the API endpoint in PR 2, and the UI in PR 3.
- **Strip noise first:** Revert unrelated whitespace changes, unused imports, and unrequested lockfile bumps before opening the PR.

---

## High-Signal PR Descriptions with `gh`

Use the GitHub CLI (`gh`)—not a heavy MCP server—to let the agent draft a structured, evidence-backed PR description directly from your branch diff:

```bash
# Inspect commits and diffstat before drafting
git log origin/main..HEAD --oneline
git diff --stat origin/main...HEAD

# Create a draft PR first for self-review
gh pr create --draft --title "feat(api): add token-bucket rate limiter" \
  --body-file .github/pr_body.md
```

### What Every Agent-Assisted PR Body Must Include

1. **Why & Context:** Link to the issue/ticket and explain the problem solved.
2. **Design Trade-offs:** Briefly note alternatives considered (e.g., *"Chose Redis Lua script over in-memory map for multi-pod consistency"*).
3. **Verification Evidence:** Exact test/lint commands executed and their observed results—never write *"tests pass"* without naming the command.
4. **Risk & Rollback:** Feature flags, migration reversibility, or config toggles.

---

## Fresh-Context Self-Review & Feedback Loops

Never ask the **same** session that wrote the code to review its own PR—it suffers from confirmation bias and stale context.

Instead, run a **fresh-context review** *before* requesting human reviewers:

```text
# In a brand-new session or read-only subagent:
Run `git diff origin/main...HEAD`.
Audit for:
1. Edge cases, null/empty handling, and race conditions.
2. Weakened test assertions or swallowed exceptions.
3. Unrequested file edits or leftover debug logs.
Report findings by severity with file and line numbers.
```

### Addressing PR Review Comments

When human reviewers leave comments, pull them cleanly into a focused session with `gh`:

```bash
gh pr view 142 --comments
```

Fix each comment in a dedicated commit, run the full test suite, and reply with the exact commit SHA so reviewers can verify the fix in seconds.
