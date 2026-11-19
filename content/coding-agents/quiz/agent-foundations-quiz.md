## Q1
Why does dumping 2,000 lines of prose and rare edge-case instructions into `CLAUDE.md` or `GEMINI.md` degrade a coding agent's performance?

### Option A
The agent refuses to start if a memory file exceeds 500 lines

### Option B [CORRECT]
Always-loaded memory files consume context tokens on every turn, increasing latency, cost, and "lost-in-the-middle" instruction drift

### Option C
Markdown files cannot be parsed unless they are converted to JSON first

### Option D
Memory files are only read when the user manually types `/compact`

### Explanation
`CLAUDE.md` and always-on `GEMINI.md` rules are injected into the context window on every turn. Bloating them wastes tokens, increases latency/cost, and dilutes model attention across too many competing instructions—which is why rare or task-specific procedures belong in on-demand Skills (`SKILL.md`).

===

## Q2
In Google Antigravity, which tool execution policy allows terminal commands to run automatically *inside* a restricted OS environment while still prompting if an action needs to escape the sandbox?

### Option A
`strict`

### Option B
`always-proceed`

### Option C [CORRECT]
`proceed-in-sandbox`

### Option D
`bypassPermissions`

### Explanation
Antigravity's `proceed-in-sandbox` policy auto-approves commands that stay inside the Terminal Sandbox (restricting outside-workspace writes and unauthorized network access) and prompts the operator only when escaping the sandbox. `bypassPermissions` is a Claude Code permission mode, not an Antigravity policy.

===

## Q3
Which Claude Code command lets you compress a long conversation's history while explicitly instructing the agent which critical details to keep?

### Option A
`/clear --keep`

### Option B
`/init`

### Option C [CORRECT]
`/compact [focus instructions]`

### Option D
`/rewind`

### Explanation
Running `/compact` summarizes conversation history to free up context window space. In Claude Code, you can append focus instructions (e.g., `/compact preserve the API schema decisions`) so key context survives compaction. `/clear` wipes the session, `/init` generates a `CLAUDE.md`, and `/rewind` reverts edits to a checkpoint.

===

## Q4
In `.claude/settings.json`, what is the primary security benefit of adding `"Read(.env*)"` and `"Read(~/.ssh/**)"` to `permissions.deny`?

### Option A
It encrypts `.env` files on disk using AES-256

### Option B [CORRECT]
It blocks the agent from reading secret files so credentials never enter the LLM's context window

### Option C
It automatically rotates API keys after every Git commit

### Option D
It prevents Git from tracking `.gitignore` files

### Explanation
`permissions.deny` rules prevent the agent from invoking `Read` on sensitive paths like `.env*` or `~/.ssh/**`, ensuring local secrets and private keys are never loaded into the context window or sent to external model APIs.

===

## Q5
What is the safest Git habit to follow *before* starting an autonomous refactoring task with a coding agent?

### Option A
Run `git push --force` to back up the remote branch

### Option B
Enable `always-proceed` and disable all `deny` rules

### Option C [CORRECT]
Start from a clean working tree (commit or stash changes) or use an isolated Git worktree

### Option D
Delete `.git/` so the agent cannot run git commands

### Explanation
Starting from a clean working tree—or isolating the agent in a dedicated Git worktree—ensures `git diff` reflects *only* the agent's changes and lets you discard a failed refactor in seconds without losing your own prior work.
