# Daily Operator Routine: 5-Minute Triage to Verified PR

How does a senior engineer actually structure their day when Claude Code is part of their Linux + Java toolchain? Here is a realistic, high-leverage daily cadence.

---

## 1. Morning Log & PR Triage (Unix Pipes)

Before opening an IDE, clear your morning queue from the terminal:

```bash
# Summarize overnight staging errors
kubectl logs deploy/billing -n staging --since=12h \
  | grep -E "ERROR|Exception" | tail -n 120 \
  | claude -p "Group by root cause and identify top 2 regressions."

# Pre-screen a teammate's PR before doing your human review
gh pr diff 582 | claude -p "Flag concurrency, SQL, or null-safety risks."
```

---

## 2. Midday Feature Build (`tmux` + Worktree + `/plan`)

1. Spawn a new `tmux` window and start an isolated worktree session:
   `claude --worktree feat-invoice-retry`
2. Switch to `/plan` mode (`Shift+Tab`) and align on the design:
   - Idempotency key handling
   - `@Transactional` boundary placement
   - JUnit 5 + Testcontainers coverage
3. Approve the plan and switch to `acceptEdits` while Spotless `PostToolUse` keeps Java formatting clean.
4. Keep a second `tmux` pane running `watch -n 2 git diff --stat` to monitor which modules are touched.

---

## 3. Afternoon Debug & Audit (IDE + Fresh `/review`)

- If a subtle concurrency or Hibernate lazy-loading bug resists unit tests, open **IntelliJ IDEA** on the worktree and step through it with the live JVM debugger.
- Once tests pass (`./mvnw verify -pl billing-core -q`), run a fresh `/review` or inspect the full diff in IntelliJ's Commit tool window.
- Commit clean, atomic changes, push the branch, and remove the temporary worktree.
