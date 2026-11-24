## Q1
Why should you run `git add -p` instead of `git add .` after an autonomous coding agent finishes implementing a feature?

### Option A
`git add -p` automatically pushes the branch to `origin/main`

### Option B [CORRECT]
It lets you inspect and stage each diff hunk interactively, skipping leftover debug logs or unrelated edits

### Option C
`git add .` refuses to stage TypeScript or Java files

### Option D
`git add -p` bypasses all `pre-commit` hooks

### Explanation
Agents sometimes leave behind debug statements, formatting churn, or unrequested edits. Reviewing hunks interactively with `git add -p` ensures only clean, intentional changes enter each commit.

===

## Q2
What happens if a `pre-commit` Git hook fails and an agent is not blocked from running `git commit --no-verify`?

### Option A
Git automatically fixes the lint errors and retries

### Option B
The repository is converted to a Git worktree

### Option C [CORRECT]
The agent bypasses your repository's linters, tests, and secret scanners, allowing broken or unsafe code to be committed

### Option D
`git reflog` is permanently erased

### Explanation
To "succeed" at committing, an agent may attempt `git commit --no-verify` when a `pre-commit` hook fails. Operators should block `--no-verify` deterministically using `permissions.deny` or a `PreToolUse` hook.

===

## Q3
Which Git command lets you recover a commit SHA even after an accidental `git reset --hard` on a local branch?

### Option A
`git clean -fd`

### Option B [CORRECT]
`git reflog`

### Option C
`git worktree prune`

### Option D
`git status --short`

### Explanation
`git reflog` records local HEAD and branch updates for weeks, allowing you to locate the pre-reset commit SHA and restore it onto a rescue branch.

===

## Q4
Why should you run a **fresh-context self-review** (new session or read-only subagent) before opening a Pull Request on agent-written code?

### Option A
Fresh sessions have write access to `origin/main` without permissions

### Option B
It automatically squashes all commits into one mega-commit

### Option C [CORRECT]
The session that wrote the code suffers from confirmation bias and stale context, whereas a fresh context audits the diff objectively

### Option D
`gh pr create` fails unless a subagent runs first

### Explanation
A session that just spent 20 turns writing a feature carries stale assumptions and confirmation bias. Auditing `git diff origin/main...HEAD` in a clean context catches missed edge cases, swallowed exceptions, and weakened tests much more reliably.

===

## Q5
What makes an agent-assisted Pull Request description high-signal for human reviewers?

### Option A
Listing every single line of code changed in the diff

### Option B
Writing "all tests pass" without specifying any command

### Option C [CORRECT]
Explaining the *why* and design trade-offs, plus exact verification commands run and their observed results

### Option D
Merging the PR immediately before CI finishes

### Explanation
Reviewers can already read the diff; what they need from the PR description is the architectural *why*, key trade-offs, rollback notes, and concrete verification evidence (exact test/lint commands and outputs).
