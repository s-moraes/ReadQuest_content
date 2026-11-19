# The IDE Shift: Terminal-First Orchestration vs. IntelliJ & VS Code

The biggest workflow change for a senior developer adopting **Claude Code** (or **Google Antigravity**) is not how fast you type—it is **where your attention lives**.

For two decades, the IDE (IntelliJ IDEA, Eclipse, VS Code) was the center of gravity: you navigated files, wrote implementations line-by-line, and ran tests from an IDE panel. With repository-level coding agents, **the terminal becomes the control plane**, and the IDE shifts into a **high-precision inspection and debugging workbench**.

---

## How the Senior Daily Loop Changes

```text
Traditional IDE-Centric Loop:
  Read Ticket -> Navigate Files -> Type Code -> Fix Imports -> Run Test -> Repeat

Agent-Orchestrated Senior Loop:
  Read Ticket -> Scope & /plan in Terminal -> Agent Implements + Runs Tests
       ^                                                |
       +--- Step-Debug / Diff Review in IDE <-----------+
```

Instead of spending 80% of your energy on syntax and boilerplate, you spend it on:
1. **Problem Framing & Invariants:** Defining acceptance criteria, edge cases, and architectural constraints.
2. **Context & Guardrail Design:** Maintaining `CLAUDE.md`, skills, and hooks so the team's agent gets faster every week.
3. **Critical Code Review:** Auditing `git diff` and test coverage with the skepticism of a staff reviewer.

---

## Division of Labor: Claude Code vs. Your IDE

Using Claude Code does **not** mean abandoning IntelliJ IDEA or VS Code. It means using each tool where it has an unfair advantage:

| Task | Best Tool | Why |
| :--- | :--- | :--- |
| **Cross-module boilerplate & test scaffolding** | **Claude Code** | Generates 5 files + tests in seconds across packages |
| **Log, stacktrace & git-history triage** | **Claude Code** | Pipes `journalctl` / `git log` directly into reasoning |
| **PR diff review & edge-case hunting** | **Claude Code** | Fresh-context `/review` catches missed null/auth checks |
| **Step-through debugging (breakpoints/watches)** | **IDE (IntelliJ/VS Code)** | Inspecting live JVM heap, threads, and variable state beats guessing from logs |
| **Compiler-guaranteed AST refactors** | **IDE (IntelliJ)** | *Change Signature*, *Move Class*, or *Safe Delete* across 100 callers is 100% deterministic in IntelliJ's PSI tree |
| **Visual 3-way merge conflict resolution** | **IDE** | Side-by-side semantic diffing reduces human merge errors |
| **CPU / Memory profiling (JFR, Async-Profiler)** | **IDE / Profiler** | Flame graphs and allocation trees require visual analysis |

---

## Pairing Claude Code with IntelliJ or VS Code

You don't have to choose one window over the other:
- **IDE Companion Integration:** Claude Code's VS Code and JetBrains integrations let the CLI see your active file, cursor selection, and IDE linter/compiler diagnostics—and show inline diff previews directly in the editor.
- **Dual-Monitor / Split Layout:** Keep **Claude Code** in a dedicated terminal (or `tmux` pane) for orchestration, and keep **IntelliJ IDEA** open on the same repo solely for:
  - Running the interactive debugger when a tricky concurrency bug resists unit tests.
  - Reviewing the final `Commit` / `Git Diff` tree with full syntax highlighting and jump-to-definition.
  - Executing large-scale deterministic AST refactors before handing the next step back to Claude.

---

## Avoiding Senior Skill Atrophy

A real risk of delegating implementation to agents is **losing touch with the codebase's internals**. Senior engineers prevent this with three habits:
1. **Never Merge Code You Cannot Explain:** If Claude writes a clever stream pipeline or SQL query you don't immediately follow, ask it to simplify or explain before committing.
2. **Write the Core Abstraction Yourself Sometimes:** Hand-craft critical domain interfaces, concurrency primitives, or security boundaries, then let Claude wire the adapters and tests around them.
3. **Debug Live Bugs in the Debugger:** When a subtle race condition hits, step through it in IntelliJ yourself—building mental models of runtime behavior is what separates a senior engineer from a prompt operator.
