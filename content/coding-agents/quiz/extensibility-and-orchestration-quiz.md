## Q1
How do **Skills** (`SKILL.md`) in Google Antigravity and Claude Code avoid bloating the context window at session start?

### Option A
They are compiled into binary executables before the session begins

### Option B [CORRECT]
Progressive disclosure: only each skill's `name` and short `description` load upfront, while the full `SKILL.md` loads on demand

### Option C
They are stored in a remote database and never enter the context window

### Option D
Only one skill can exist per repository

### Explanation
Both Antigravity and Claude Code use progressive disclosure for Skills. At session start, only the lightweight YAML metadata (`name` and `description`) is injected; the full `SKILL.md` instructions, scripts, and references load only when the task matches or the user invokes the skill.

===

## Q2
Why should critical guardrails—such as blocking `git push --force` or auto-formatting edited files—be implemented as **Hooks** rather than prose rules in `CLAUDE.md`?

### Option A
Hooks reduce the model's temperature to zero

### Option B
Hooks allow the agent to skip unit tests automatically

### Option C [CORRECT]
Hooks execute deterministically in code at lifecycle events (`PreToolUse`/`PostToolUse`), whereas prompt rules are probabilistic

### Option D
Hooks do not require any configuration files

### Explanation
Prompt rules are probabilistic guidance that an LLM can overlook under heavy context load. Hooks (`hooks.json` in Antigravity, `settings.json` hooks in Claude Code) run deterministic scripts around tool calls; for example, a `PreToolUse` hook returning exit code `2` guarantees a dangerous command is blocked before execution.

===

## Q3
What is the main risk of connecting 8 different MCP servers (each exposing dozens of tools) to a single coding agent session?

### Option A
MCP servers automatically delete local `.git` history

### Option B [CORRECT]
Context bloat: every active MCP server injects its tool schemas into the prompt, consuming thousands of tokens before work begins

### Option C
MCP servers only work when `internet_access` is set to `deny`

### Option D
MCP forces the agent to switch from `stdio` to SQL

### Explanation
Each enabled MCP server injects its tool definitions and JSON schemas into the model's context window at session start. Loading too many unused MCP tools wastes context tokens and degrades reasoning—so operators should enable only needed servers, prefer existing CLI tools like `gh`, or scope MCP servers to specific subagents.

===

## Q4
When running two coding agents simultaneously to implement two different features in the same repository, which workspace isolation mode prevents them from overwriting each other's files?

### Option A
`inherit` (shared working directory)

### Option B
`plan` mode for both writers

### Option C [CORRECT]
Git worktree isolation (`workspace: "share"` in Antigravity or `isolation: worktree` in Claude Code)

### Option D
Disabling `PostToolUse` hooks

### Explanation
If two writer agents share the same working directory (`inherit`), their edits collide and corrupt `git status`. Git worktree isolation (`workspace: "share"` in Antigravity, `isolation: worktree` / `--worktree` in Claude Code) gives each writer an independent working copy linked to the same `.git` repository.

===

## Q5
Which statement best describes the difference between a **Subagent** and an **Antigravity Swarm**?

### Option A
Subagents can only run Bash commands, while Swarms can only edit Markdown

### Option B [CORRECT]
A Subagent runs an isolated delegated task and reports back to its parent, whereas a Swarm coordinates multiple parallel workers via a shared message board

### Option C
Swarms cannot use `workspace: "share"`

### Option D
Subagents share the exact same conversation history as the parent by default

### Explanation
A subagent executes an isolated task in a fresh context window and returns a summary to its parent. An Antigravity Swarm spawns multiple named workers that collaborate asynchronously on a shared message board (using `@mentions`), sleeping when `waiting` and waking when messaged.
