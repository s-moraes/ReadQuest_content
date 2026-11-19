# Safe Feature Delivery: Plan, Worktrees & Verification

Knowing individual features like `CLAUDE.md` or `hooks.json` is useful, but true productivity comes from chaining them into a repeatable **operator workflow**. Below is a battle-tested, 6-step blueprint for shipping a non-trivial feature with either Google Antigravity or Claude Code.

---

## Step 1: Start from a Clean Git State & Isolated Worktree

Never run an autonomous feature build on top of uncommitted experiments.

```bash
# Ensure main is clean and up to date
git status
git pull origin main

# Option A: Claude Code native worktree
claude --worktree feat-rate-limiter

# Option B: Manual Git worktree for any agent (agy or claude)
git worktree add ../repo-rate-limiter -b feat/rate-limiter
cd ../repo-rate-limiter
agy
```

If anything goes wrong, you can delete the worktree in two seconds with zero risk to your primary checkout.

---

## Step 2: Research First (Read-Only Pass)

Before asking the agent to write a single line of code, force a read-only exploration pass—or delegate it to a `research` subagent so search noise stays out of your main context.

```text
Inspect @src/api/middleware/ and @src/config/redis.ts.
Explain how request context and Redis clients are wired today.
Do NOT modify any files yet.
```

This catches wrong assumptions early (e.g., discovering the repo uses a custom Redis wrapper instead of `ioredis`).

---

## Step 3: Align on Architecture with `/plan` or `/grill-me`

Invoke `/plan` (or `/grill-me` in Antigravity) to surface edge cases before implementation:
- What happens if Redis is unreachable—fail-open or fail-closed?
- Should rate limits be keyed by `userId`, `IP`, or `API key`?
- Which HTTP headers (`X-RateLimit-Remaining`, `Retry-After`) are required?

Review the generated plan like a PR design doc. Editing a 10-line plan takes 15 seconds; undoing 12 wrong files takes 15 minutes.

---

## Step 4: Test-First Execution Loop

Give the agent a **verifiable target** rather than an open-ended coding prompt:

```text
Implement the approved rate limiter plan:
1. Write failing unit + integration tests in tests/rate_limit.test.ts first.
2. Implement the middleware in src/api/middleware/rateLimit.ts.
3. Run `npm test -- rate_limit` and `npm run lint` until both pass.
Do not alter existing test assertions.
```

Notice the explicit constraint (*"Do not alter existing test assertions"*)—this prevents the agent from weakening tests to make them pass.

---

## Step 5: Independent Diff Audit

Once the agent reports completion, **do not merge blindly**. Perform a fast, structured review:

```bash
git status
git diff --stat
git diff
```

Check for common agent anti-patterns:
- Unrequested edits to unrelated files or lockfiles.
- Debug `console.log` / `print` statements left behind.
- Swallowed exceptions (`catch (e) {}`) or hardcoded fallback values.
- Missing edge-case tests.

Optionally, run a fresh `/review` or a read-only `security-reviewer` subagent on the diff—a fresh context window is far better at spotting bugs than the session that wrote the code.

---

## Step 6: Commit, Clean Up & Reset

Commit the verified work, merge or open a PR from the worktree branch, remove the temporary worktree, and start a fresh agent session for your next task.
