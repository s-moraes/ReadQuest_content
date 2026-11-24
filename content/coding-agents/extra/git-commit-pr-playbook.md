# Git, Commit & PR Operator Playbook

A copy-pasteable reference for running clean Git worktrees, crafting logical commits, and shipping reviewer-friendly Pull Requests with coding agents.

---

## 1. Worktree Setup & Teardown

```bash
# Start from clean main
git checkout main && git pull origin main

# Spin up an isolated worktree
git worktree add ../repo-feat-auth -b feat/auth

# After PR merges, clean up
git worktree remove ../repo-feat-auth
git branch -d feat/auth
git worktree prune
```

---

## 2. Atomic Commit Prompt Template

Run `git add -p` yourself or instruct the agent to split logical units:

```text
Inspect `git status` and `git diff`.
1. Do NOT stage unrelated lockfiles or debug logs.
2. Group changes into logical commits (refactor vs feat).
3. Write Conventional Commit messages that explain WHY,
   including the exact test command verified.
4. Never use `--no-verify` or `--amend` on pushed commits.
```

---

## 3. Fresh-Context PR Self-Review Prompt

Open a **new** conversation (or `research` subagent) before requesting human review:

```text
Run `git diff origin/main...HEAD` and audit for:
- Edge cases, null handling, and missing error paths
- Weakened test assertions or skipped tests
- Leftover console.log / print statements
- Unrequested edits outside the feature scope
List findings by severity with file and line numbers.
```

---

## 4. `gh` PR Creation & Review Loop

```bash
# Open a draft PR with structured evidence
gh pr create --draft \
  --title "feat(auth): enforce JWT audience validation" \
  --body-file .github/pr_body.md

# Pull reviewer feedback into a focused session
gh pr view --comments
```

### Pre-PR Final Audit Checklist
- [ ] PR diff is scoped (`< 400` lines where practical)
- [ ] Every commit builds and passes tests cleanly
- [ ] PR body lists exact verification commands run
- [ ] Fresh-context self-review completed with zero open blockers
