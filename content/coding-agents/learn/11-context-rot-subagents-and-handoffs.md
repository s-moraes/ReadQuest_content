# Preventing Context Rot: Subagents, Compaction & Handoffs

Even with a lean system prompt, long debugging or refactoring sessions accumulate dead ends, stack traces, and superseded file versions. Left unmanaged, this causes **context rot**.

---

## Three Context Failure Modes

| Failure Mode | Symptom | Root Cause |
| :--- | :--- | :--- |
| **Context Poisoning** | Agent repeats the same broken fix 4 times | Failed attempts and wrong hypotheses stay in history |
| **Context Distraction** | Agent forgets an early architectural rule | Attention is diluted across 80k+ tokens of grep logs |
| **Context Confusion** | Agent edits files from an unrelated module | You pivoted to a new task without clearing history |

When you notice any of these symptoms, adding *more* corrective prompts rarely helps—you are competing against thousands of tokens of contradictory history.

---

## Offloading Exploration to Subagents

The cleanest way to keep your main context sharp is **never letting raw search noise enter it in the first place**.

Use a read-only **subagent** (`research` in Antigravity, or a `plan`-mode subagent in Claude Code) whenever you need to survey more than 3–5 files:

```text
Parent Agent (12k tokens - Architecture & Plan)
   |
   +--> Research Subagent (Fresh 0-token start)
           Reads 28 files + runs 6 greps (45k tokens)
           Returns ONLY a 15-line interface summary
```

The 45,000 tokens of intermediate file reads and dead-end searches are **discarded** when the subagent finishes. Your parent agent stays focused and fast.

---

## Compaction vs. Clean Handoffs

When a single session grows long, you have three recovery levers:

1. **`/rewind` (`Esc Esc` in Claude Code):** Best when the last 1–3 turns went down a wrong path. Rewinds both conversation state and file edits back to a clean checkpoint.
2. **`/compact` (with Focus Instructions):** Compresses history into a summary so you can continue the *same* task. Always tell the model what must survive:

```text
/compact preserve the Postgres connection pool limits,
the failing integration test name, and the agreed API schema
```

3. **`/clear` + Structured Handoff (`HANDOFF.md`):** Best when transitioning from **research/planning** to **implementation**, or when context poisoning has already set in.

### The Handoff Pattern

Before running `/clear` (or starting a new Antigravity conversation), ask the agent to write a concise handoff artifact—or use `/handoff`:

```markdown
# Handoff: Rate Limiter Middleware

## Goal & Decisions
- Implement token-bucket rate limiter in `src/api/rateLimit.ts`.
- Fail-open if Redis is unreachable; key by `apiKey` then `IP`.

## Verified State
- Baseline tests pass: `npm test -- auth`
- Next step: write failing tests in `tests/rateLimit.test.ts`.
```

Start a fresh session, attach `@HANDOFF.md`, and execute with a 100% clean context window.
