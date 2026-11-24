## Q1
Why does editing `CLAUDE.md` or toggling MCP servers in the middle of an active coding-agent session increase latency and token cost?

### Option A
It forces Git to re-index the entire repository history

### Option B [CORRECT]
It mutates the prompt prefix, invalidating prefix prompt caching from that point forward

### Option C
It deletes the model's weights from local GPU memory

### Option D
It automatically triggers `/clear` and erases all files

### Explanation
Frontier models cache the unchanging prefix of a conversation (system prompt, tool schemas, and always-on memory files). Changing `CLAUDE.md` or adding/removing MCP tool schemas mid-session busts that prefix cache, forcing the provider to recompute the full prompt.

===

## Q2
What is the main purpose of adding `.claudeignore` or `.geminiignore` to a repository?

### Option A
To encrypt sensitive files before pushing to GitHub

### Option B
To disable all lifecycle hooks during unit tests

### Option C [CORRECT]
To prevent agent search and indexing tools from flooding the context window with build outputs, lockfiles, or large test fixtures

### Option D
To block the user from opening files in their IDE

### Explanation
Even when files like `dist/`, `node_modules/`, or large committed test fixtures exist on disk, `.claudeignore` and `.geminiignore` keep them out of agent `grep` and discovery results so they do not waste context tokens.

===

## Q3
Why is adding `"Read(.env*)"` to `permissions.deny` insufficient on its own to protect local secrets from entering an agent's context?

### Option A
`permissions.deny` only applies to Markdown files

### Option B [CORRECT]
If the agent can execute Bash commands, it can still read secrets via `cat .env` or `printenv`

### Option C
`.env` files are automatically uploaded to `catalog.json`

### Option D
Claude Code ignores `permissions.deny` whenever `plan` mode is active

### Explanation
Denying the `Read` tool on `.env*` blocks direct file reads, but an unguarded Bash tool can still print `.env` or environment variables to stdout. True secret isolation requires keeping real secrets out of the workspace, adding Bash hook guards, or running inside a secret-free devcontainer.

===

## Q4
When should an operator prefer a **read-only `research` subagent** over running 10 `grep` searches directly in the main conversation?

### Option A
When changing a single typo on line 4 of a known file

### Option B
When the user wants to run `git push --force`

### Option C [CORRECT]
When surveying many files, so raw search outputs stay isolated and only a concise summary enters the parent context window

### Option D
When the internet access policy is set to `allow`

### Explanation
Offloading broad codebase exploration to a `research` subagent keeps tens of thousands of tokens of intermediate `grep` results and file reads out of the parent session, preventing context distraction and context rot.

===

## Q5
Which isolation tier is safest when running an agent in fully autonomous mode (`always-proceed` or `--dangerously-skip-permissions`) on an untrusted or complex task?

### Option A
Shared workspace with `internet_access: allow`

### Option B [CORRECT]
An ephemeral Docker devcontainer or disposable VM with no host `~/.ssh` or `~/.aws` mounts

### Option C
Running directly in `~/Desktop` with `Read` auto-approved

### Option D
Using `git add -A` before every prompt

### Explanation
OS sandboxes protect against many mistakes, but full-autonomy modes (`always-proceed` / `bypassPermissions`) are safest inside an ephemeral container or VM that mounts only the repository and has zero access to host credentials.
