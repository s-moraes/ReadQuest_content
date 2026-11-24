# Token Budgeting, Prompt Caching & Ignore Rules

Every turn with a coding agent sends the **entire active context window** back to the model. Understanding how that budget is spent—and how prompt caching works—turns slow, expensive sessions into fast, predictable ones.

---

## Anatomy of a Context Window

Before you type your first prompt, a coding agent already occupies a slice of the context window with **fixed overhead**:

```text
[ System Prompt & Safety Instructions      ]  ~2k - 4k tokens
[ Built-in Tool Schemas (Read, Edit, Bash) ]  ~2k - 5k tokens
[ Active MCP Server Tool Definitions       ]  ~1k - 25k+ tokens
[ Always-On Memory (CLAUDE.md / GEMINI.md) ]  ~500 - 3k tokens
---------------------------------------------------------------
[ Dynamic Turn History (Messages, Files,   ]  Grows every turn
[   Grep Output, Compiler Logs, Diffs)     ]
```

If your fixed overhead is 30,000 tokens because 7 MCP servers and a 1,500-line `CLAUDE.md` are loaded unconditionally, you pay that tax on **every single turn**.

### High-Leverage Budget Rules

| Context Layer | Target Budget | How to Keep It Lean |
| :--- | :--- | :--- |
| **Memory Files** | `< 200` lines | Keep only build/test commands and repo gotchas |
| **MCP Tools** | Only active task | Disable unused servers or scope to subagents |
| **File Reads** | Targeted ranges | Use `@file` or line ranges instead of whole logs |
| **Command Output** | Filtered stdout | Pipe noisy builds through `tail -n 40` or `grep` |

---

## Prompt Caching & Prefix Stability

Modern frontier models (Claude and Gemini) use **prefix prompt caching** to avoid recomputing attention keys for the unchanged beginning of your conversation.

A cache hit is **up to 80–90% cheaper** and noticeably faster—but only if the **prefix remains byte-for-byte identical** across turns:

```text
Turn 1: [ System + Tools + Memory ] + [ User Msg 1 ]  --> Cache Write
Turn 2: [ System + Tools + Memory ] + [ Msg 1 + 2 ]   --> Cache HIT!
```

### What Busts the Prefix Cache?

1. **Editing `CLAUDE.md` / `GEMINI.md` mid-session:** Modifying an always-loaded file invalidates the prefix from that point forward.
2. **Toggling MCP servers mid-conversation:** Adding or removing tool schemas changes the tool block near the top of the prompt.
3. **Injecting dynamic timestamps or random IDs** into system-level hooks or rules.

Keep your static instructions and toolset **frozen** for the duration of a task, and append new context at the *end* of the conversation (via `@` mentions or tool outputs).

---

## Search & Ignore Hygiene

When an agent runs `grep`, `find`, or codebase indexing, build artifacts and lockfiles can flood the context window with tens of thousands of useless lines.

Both **Claude Code** (`.claudeignore`) and **Google Antigravity** (`.geminiignore`, alongside `.gitignore`) let you hide noisy directories from agent search tools:

```text
# .claudeignore / .geminiignore
node_modules/
dist/
build/
.gradle/
target/
*.lock
package-lock.json
coverage/
*.min.js
```

### Why `.gitignore` Alone Is Not Enough

- Some generated assets or large test fixtures are committed to Git (for example, `snapshots/`, `vendor/`, or `testdata/*.json`) even though an agent rarely needs to search them.
- Putting them in `.claudeignore` / `.geminiignore` keeps them tracked by Git while preventing the agent from accidentally ingesting 50,000 lines of fixture JSON during a broad search.

> Always verify that critical source directories are **not** accidentally excluded, and keep secrets (`.env*`) protected with `permissions.deny` rather than relying solely on ignore files.
