# Commit Hygiene: Splitting Diffs, Why-First Messages & Guardrails

Coding agents can modify 12 files in 30 seconds. Without commit discipline, that speed turns into **unreviewable mega-commits** and noisy Git history.

---

## Splitting Mega-Commits

Agents naturally bundle everything they touched—refactoring, feature logic, tests, formatting, and accidental lockfile edits—into a single commit.

Instead, enforce **logical, bisectable commits**:
1. **Commit 1 (`refactor:`):** Structural prep or interface extraction (no behavior change).
2. **Commit 2 (`feat:`):** The new capability + its unit/integration tests.
3. **Commit 3 (`chore:` / `docs:`):** Config or documentation updates, if needed.

### Prompting for Clean Commits

```text
Review `git status` and `git diff`.
Group the changes into logical commits (refactor separate from feat).
Stage each group explicitly by file path—never use `git add -A`.
Show me the staged diff summary before committing.
```

---

## Conventional Commits & "Why-First" Messages

When asked to *"write a commit message,"* LLMs often produce a robotic list of files changed. Good commit messages explain **why** the change exists and any non-obvious invariants.

```text
# Weak (describes the diff)
feat: update RateLimiter.ts and add redis.ts check

# Strong (explains intent and behavior)
feat(api): enforce per-key token bucket rate limiting

Fail open when Redis times out (>50ms) so transient cache
outages do not block authenticated checkout traffic.

Verified: `npm test -- rate_limit` (14 passed).
```

### Conventional Commit Prefixes

| Prefix | When to Use |
| :--- | :--- |
| `feat:` | New user-facing capability or API behavior |
| `fix:` | Bug fix (include root cause in body) |
| `refactor:` | Code restructuring with zero behavior change |
| `test:` | Adding or fixing tests only |
| `chore:` / `ci:` | Build scripts, deps, or CI workflows |

---

## Gating Dangerous Git Ops & Attribution

Even trusted agents should **never** rewrite shared history or force-push autonomously. Lock these down in `.claude/settings.json` or Antigravity command denylists:

- **Block `git push --force` / `-f`:** Prevents overwriting teammates' commits on shared branches.
- **Block `git commit --amend` on pushed commits:** Only amend local unpushed commits, and prefer a new fixup commit during review.
- **Block `git reset --hard`:** Require human confirmation before discarding commits.

### Attribution (`Co-Authored-By`)

Some teams add a `Co-Authored-By:` trailer to indicate agent assistance, while others prefer clean human-only trailers. Check your team's policy—and in Claude Code, you can configure `includeCoAuthoredBy: false` in `settings.json` if your org's DCO/CLA check requires human-only sign-off.
