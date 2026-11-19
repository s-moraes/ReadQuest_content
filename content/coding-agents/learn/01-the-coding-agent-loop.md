# The Coding Agent Loop: From Autocomplete to Autonomous Operator

If you already know how to build software, adopting a **coding agent** is less like learning a new IDE shortcut and more like becoming a technical lead managing a fast, literal-minded junior engineer.

Inline autocomplete (like Copilot ghost text) predicts the next few tokens in the file you are currently editing. A **chat assistant** answers questions about snippets you paste into a browser. A **coding agent**, such as **Google Antigravity** or **Claude Code**, operates directly inside your repository and shell: it searches files, reads symbols, edits code across modules, runs your test suite, reads compiler errors, and iterates until the task is complete.

---

## Inside the Agent Execution Loop

Every modern coding agent runs on a **ReAct-style tool loop** (Reason -> Act -> Observe). Instead of generating a single static answer, the model emits structured tool calls that the host harness executes on your machine.

```text
+-------------------------------------------------------------------+
|                     Coding Agent Harness                          |
|                                                                   |
|  1. Prompt + Rules + Conversation History                         |
|           |                                                       |
|           v                                                       |
|  +------------------+      Tool Call       +-------------------+  |
|  |   LLM Reasoner   | -------------------> |  Policy / Hook    |  |
|  | (Plan next step) |                      |  Gatekeeper       |  |
|  +------------------+                      +---------+---------+  |
|           ^                                          |            |
|           |                                   Allowed / Approved  |
|           | Observation                              v            |
|           | (stdout, file diff,            +-------------------+  |
|           |  exit code, errors)            |  Tool Execution   |  |
|           +------------------------------- | (fs, bash, grep,  |  |
|                                            |  browser, MCP)    |  |
|                                            +-------------------+  |
+-------------------------------------------------------------------+
```

Because each observation feeds back into the context window, the agent can recover from mistakes:
1. It writes a migration or function.
2. It executes `./gradlew test` or `pytest`.
3. A test fails with a stack trace.
4. It reads the stack trace, inspects the failing assertion, patches the code, and re-runs the test.

**Your job as the operator** is to shape the inputs, constrain the tools, and verify the outputs—not to micromanage every keystroke.

---

## The Operator Mindset Shift

Experienced developers often struggle with coding agents at first because they treat them like either magic wands or passive search engines. Effective operators adopt four habits:

- **Specify Outcomes and Verification, Not Just Edits:** Instead of saying *"Add a rate limiter to AuthController"*, specify *"Add a token-bucket rate limiter to AuthController (10 req/min per IP), return HTTP 429 with Retry-After, and verify with MockMvc integration tests."*
- **Give the Agent Eyes:** An agent without a feedback loop (compiler, linter, unit test, curl check) is flying blind. Always ensure it knows how to run fast verification commands.
- **Control the Blast Radius:** Use Git branches, worktrees, and sandboxes so a bad refactor can be discarded in one command (`git checkout` or deleting a worktree).
- **Review Diffs, Not Promises:** Never trust *"All tests pass!"* at face value without checking which tests ran and inspecting `git diff`.

---

## Repository-Level Engineering Agents

Both **Google Antigravity** and **Claude Code** are **repository-level engineering agents**, not file-level assistants. That distinction changes how they reason about software:

- **Cross-File & Dependency Awareness:** Instead of seeing only the active editor tab, they traverse your entire repository—reading build manifests (`pom.xml`, `package.json`, `Cargo.toml`), tracing call sites across modules with `grep`/`ripgrep`, inspecting Git history, and checking test suites.
- **Environment & Tool Coupling:** They operate directly against your local toolchain (compilers, linters, Docker, database migrations, test runners), treating exit codes and stack traces as first-class observations.
- **Stateful Multi-Turn Execution:** A single user request can trigger 10 to 50+ autonomous tool calls (search -> read -> plan -> edit -> test -> fix) before the agent hands control back to you.

---

## The Planning & Execution Loops

Effective operators separate **planning** from **execution**. Letting an agent jump straight from a vague prompt into editing 12 files is the fastest way to burn tokens and introduce architectural drift. Both platforms enforce a two-phase loop:

```text
+-------------------------------------------------------------------+
| Phase 1: Read-Only Discovery & Planning Loop                      |
|                                                                   |
|  Search Repo (glob/grep) -> Read Key Files -> Draft Plan          |
|         ^                                         |               |
|         +--- Ask Clarifying Questions (HITL) <----+               |
|                                                   |               |
|                                          Human Approves Plan      |
+---------------------------------------------------|---------------+
                                                    v
+-------------------------------------------------------------------+
| Phase 2: Incremental Execution & Verification Loop                |
|                                                                   |
|  Edit Files -> Run Build / Tests -> Read Errors / Exit Code       |
|       ^                                           |               |
|       +--------- Patch & Retry (if failed) <------+               |
|                                                   |               |
|                                       Tests Pass + Diff Review    |
+-------------------------------------------------------------------+
```

### How Claude Code Runs the Loop
- **Exploration Pass:** Claude Code starts by invoking read-only tools (`Glob`, `Grep`, `Read`) to map symbols and conventions without mutating disk state.
- **Explicit `plan` Mode (`/plan` or `Shift+Tab`):** In `plan` mode, mutating tools (`Edit`, `Write`, state-changing `Bash`) are blocked by the harness. Claude writes a structured implementation plan—listing target files, interfaces, and test strategy—and pauses until you approve and transition into execution.
- **Execution & Self-Correction:** Once approved, Claude applies edits, runs targeted tests via `Bash`, reads failures, and loops until tests pass or `--max-turns` / human interruption stops it.

### How Google Antigravity Runs the Loop
- **Multi-Surface Planning:** In `agy` CLI or Antigravity 2.0, `/plan` structures a step-by-step execution blueprint, while `/grill-me` runs an interactive alignment interview to resolve ambiguous design trade-offs before any file is touched.
- **Artifact-Backed Plans:** Antigravity can persist plans, task lists, and architecture summaries as **Artifacts** in the Auxiliary Pane, allowing the operator to review and give feedback (`Proceed` or revise) before execution begins.
- **Delegated Loops:** When discovery is heavy, Antigravity can offload read-only exploration to a `research` subagent (isolated, read-only, no network) so raw search output never pollutes the main planning context.

---

## Google Antigravity vs. Claude Code: Two Philosophies

Both **Google Antigravity** and **Claude Code** are top-tier agentic coding platforms, but they expose different surfaces and strengths for the operator.

| Dimension | Google Antigravity | Claude Code |
| :--- | :--- | :--- |
| **Primary Surfaces** | `agy` CLI, Antigravity 2.0 Desktop App, Antigravity IDE, Python SDK | `claude` CLI (terminal-first), VS Code / JetBrains extensions, Web/Headless CI |
| **Core Models** | Gemini models (e.g., Flash, Pro, Hydrogen) selectable per task/worker | Claude models (Sonnet, Opus, Haiku) selectable via `/model` or flags |
| **Project Memory** | `GEMINI.md`, `AGENTS.md`, `.agents/rules/*.md` | `CLAUDE.md` (project, parent dirs, `~/.claude/CLAUDE.md`) |
| **On-Demand Workflows** | Skills (`SKILL.md`), Slash Commands, `run_workflow` Python scripts | Skills (`SKILL.md`), Custom Slash Commands (`.claude/commands/`) |
| **Multi-Agent Model** | Subagents (`invoke_subagent`), **Swarms** (shared message board), Python workflows | Subagents (`.claude/agents/*.md`), Agent Teams, Worktree isolation |
| **Deterministic Hooks** | `hooks.json` lifecycle hooks | `settings.json` lifecycle hooks (`PreToolUse`, `PostToolUse`, etc.) |
| **Visual / Aux Tooling** | Desktop App Auxiliary Pane (Artifacts, Files Changed, Terminals, Browser) | Terminal diff previews, checkpoints, `--output-format json` for pipes |

### When Each Shines

- **Google Antigravity** excels when you want **multi-surface orchestration**: jumping from the `agy` terminal to the Antigravity 2.0 Desktop App (with visual Artifacts, browser automation, scheduled cron tasks, and parallel Swarms) or driving agents programmatically via the Python SDK.
- **Claude Code** excels as a **Unix-native terminal powerhouse**: lightweight, composable in shell pipelines (`cat error.log | claude -p "diagnose"`), deeply integrated with Git worktrees, and highly scriptable in CI/CD via headless mode.

---

## Anatomy of a Productive First Session

Whether you launch `agy` or `claude` in your repository root, follow this 4-step operator cadence:

1. **Orient the Agent First:** Ask it to explore before editing.
   ```text
   Explore src/auth/ and explain how JWT validation and refresh
   tokens currently work. Do not edit any files yet.
   ```
2. **Align on a Plan:** Use `/plan` (available in both platforms) or ask for a step-by-step plan for non-trivial changes. Catching a wrong architectural assumption before any file is touched saves 90% of wasted tokens.
3. **Execute with Verification:** Let the agent implement in small, testable increments and run the test suite after each step.
4. **Audit & Reset:** Review `git diff`, run final checks, commit, and start a fresh conversation (`/clear` or new session) before moving to an unrelated task.
