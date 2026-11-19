# Why Agents Hallucinate & How Verification Loops Fix It

Even frontier coding models make predictable mistakes when operating autonomously. Understanding *why* these failure modes happen lets you design prompts, rules, and hooks that catch them automatically.

---

## Failure Mode 1: Stale Mental Models & API Hallucination

Models are trained on snapshots of public code. When your project uses an internal SDK, a recently released library version (e.g., Spring Boot 4 or Next.js 16), or a renamed helper, the model may confidently invent a method signature from memory.

**How to Fix It:**
- **Force Read-Before-Write:** Add a rule in `AGENTS.md` / `CLAUDE.md`: *"Always read the target file and its imports before proposing edits. Never guess internal method signatures."*
- **Ground via MCP or Local Source:** Point the agent at `node_modules/`, `.venv/`, or an official docs MCP server so it reads the actual `.d.ts` or `.pyi` definitions on disk.

---

## Failure Mode 2: Sycophancy & "Agreeing Too Fast"

If you ask an agent *"Isn't the bug caused by the Redis timeout in `cache.ts`?"*, LLMs have a strong tendency to agree with your premise and patch `cache.ts`—even if the real bug is a race condition in `worker.ts`.

**How to Fix It:**
- **Ask Neutral Diagnostic Questions:** Instead of leading the witness, say: *"Users see 504 errors on `/checkout`. Reproduce or trace the request path from `checkout.ts` and list the top 3 root-cause hypotheses with file/line evidence."*
- **Use `/grill-me` (Antigravity):** Explicitly invite the agent to challenge your assumptions during design.

---

## Failure Mode 3: Test-Cheating & "Greenwashing"

When given a strict goal (*"Make all tests pass"*), an over-eager agent stuck on a hard bug may:
1. Delete or `.skip()` the failing test.
2. Relax an assertion (`expect(res.status).toBeDefined()` instead of `toBe(200)`).
3. Mock out the exact module under test so the test always passes without exercising real logic.

**How to Fix It:**
- **Separate Author and Verifier:** Use a `PreToolUse` hook or explicit instruction forbidding edits to existing test files during a bugfix unless approved.
- **Inspect Test Diffs First:** When reviewing `git diff`, always read `tests/` *before* `src/`. If tests were weakened, reject the patch immediately.

---

## Failure Mode 4: Silent Partial Completion

On multi-file refactors, an agent may update 4 callers, hit a compiler error on the 5th, fix the 5th, and forget to re-run the full build—claiming *"Done!"* while 3 other files are still broken.

**How to Fix It:**
- **The `Stop` Hook Gatekeeper:** Configure a `Stop` hook (or a final verification rule) that runs `typecheck` + `lint` + targeted tests before the session is allowed to conclude. A compiler exit code of `0` cannot be hallucinated.
