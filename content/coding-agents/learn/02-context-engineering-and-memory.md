# Context Engineering & Memory: CLAUDE.md, GEMINI.md & AGENTS.md

The single most important skill for an agent operator is **context engineering**: controlling what enters the model's context window, when it enters, and when it gets cleared.

An LLM's context window is not free infinite RAM. As a conversation grows past tens of thousands of tokens—filled with raw compiler logs, entire files, and failed tool attempts—two things happen:
1. **Context Rot ("Lost in the Middle"):** The model starts ignoring rules from the top of the prompt and forgets constraints you stated 15 turns ago.
2. **Latency & Cost Spike:** Every subsequent turn re-processes the entire accumulated history.

---

## Hierarchical Project Memory

Both Google Antigravity and Claude Code solve the "cold start" problem—having to re-explain your build commands, architecture, and style conventions every session—using **Markdown memory files** checked into your repository.

### Claude Code: `CLAUDE.md`

Claude Code automatically discovers and loads `CLAUDE.md` files at session start in a clear hierarchy:

```text
~/.claude/CLAUDE.md              <-- Global user preferences (all repos)
  └── repo-root/CLAUDE.md        <-- Shared team project memory (git tracked)
        ├── CLAUDE.local.md      <-- Personal repo overrides (gitignored)
        └── services/billing/
              └── CLAUDE.md      <-- Subdirectory-specific rules (loaded on demand)
```

- Run `/init` inside Claude Code to scan your codebase and scaffold a starter `CLAUDE.md`.
- Press `#` during an interactive session to append a new rule to `CLAUDE.md` on the fly whenever you catch the agent making a repeated mistake.

### Google Antigravity: `GEMINI.md`, `AGENTS.md` & `.agents/rules/`

Antigravity supports both universal `AGENTS.md` files and `GEMINI.md`, plus structured rule files inside `.agents/rules/` (or `.agent/rules/`).

1. **Global Configuration (`~/.gemini/config/`):** Machine-local rules and customizations that apply across every workspace.
2. **Workspace Discovery (`.agents/` & Root Files):** As you work on files in a directory, Antigravity walks **upward** from the current working directory to the Git repository root, loading matching `GEMINI.md`, `AGENTS.md`, and `.agents/rules/*.md`.
3. **Precedence:** Workspace-level rules override global configurations if there is a naming conflict, and Antigravity deduplicates rule files by resolved path so a rule is never injected twice in the same turn.

---

## What Belongs in Memory Files (and What Does Not)

Treat `CLAUDE.md` / `GEMINI.md` like a **concise onboarding sheet**, not an encyclopedia. Every line you put in an always-loaded memory file consumes context on *every single turn*.

| Include (High Signal) | Exclude (Context Bloat) |
| :--- | :--- |
| Exact build, test, and lint commands | Long prose explaining what your company does |
| Non-obvious architectural boundaries | Standard language syntax or framework basics |
| Repo-specific gotchas (e.g., "use `pnpm`, never `npm`") | Exhaustive API docs (put those in `references/` or MCP) |
| File layout map for key modules | Rules that only apply to one rare migration task |

### Example: A Crisp, High-Signal `AGENTS.md` / `CLAUDE.md`

```markdown
# Project: OrderFlow API (Java 21 + Quarkus)

## Commands
- Unit tests: `./mvnw test -Dtest=ClassName`
- Full verify: `./mvnw verify`
- Format code: `./mvnw spotless:apply`

## Architecture Rules
- Strictly follow Hexagonal Architecture: `domain/` must NEVER
  import `jakarta.*`, `io.quarkus.*`, or `infrastructure.*`.
- All DB schema changes require a new Flyway migration in
  `src/main/resources/db/migration/V<N>__<desc>.sql`.

## Verification
- Always run `./mvnw spotless:check` and targeted tests before
  reporting a task complete.
```

---

## Progressive Disclosure & Scoped Rules

Loading 500 lines of React styling rules when the agent is editing a Terraform file wastes tokens and confuses attention. Both platforms support **scoped loading**:

- **Glob-Scoped Rules:** In Antigravity `.agents/rules/*.md` (and Claude Code `.claude/rules/*.md`), you can attach YAML frontmatter specifying file globs (e.g., `paths: ["src/frontend/**/*.tsx"]`). The rule only loads when the agent touches matching files.
- **Model-Decision Rules:** In Antigravity, rules with `trigger: model_decision` expose only their short description upfront and load their full body only when relevant—unlike `always_on` rules which are injected unconditionally.

---

## Context Hygiene: Compaction, `@` Mentions, and Resets

As an operator, actively manage the context window during long sessions:

1. **Pin Context Precisely with `@`:** In both Antigravity and Claude Code, typing `@` lets you attach specific files, folders, or symbols directly instead of making the agent run 5 broad `grep` searches.
2. **Compact Deliberately (`/compact`):** When a session gets long after exploring a bug, run `/compact` to summarize the conversation history while preserving key decisions and file paths. In Claude Code, you can even pass focus instructions: `/compact preserve the API schema decisions and failing test output`.
3. **Clear Between Unrelated Tasks (`/clear` or New Conversation):** Never pivot from fixing a CSS bug to refactoring a database pool in the same thread. Start a clean session so stale context never leaks into the new task.
