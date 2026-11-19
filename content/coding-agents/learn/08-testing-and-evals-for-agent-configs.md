# Testing & Evaluating Custom Rules, Skills & Hooks

As your team accumulates `CLAUDE.md` rules, `GEMINI.md` overrides, `SKILL.md` playbooks, and `hooks.json` / `settings.json` scripts, your agent configuration becomes **production code**. Changing one rule can silently break another workflow.

Mature agent operators test and evaluate their customizations systematically rather than guessing.

---

## 1. Unit-Testing Deterministic Hooks

Hooks are standard scripts (`PreToolUse`, `PostToolUse`, `Stop`) that read JSON from `stdin` and return exit codes (`0` allow, `2` block). Treat them like any other utility script—write fast unit tests for them!

```bash
# Test that our PreToolUse hook blocks force-push (expects exit code 2)
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}' \
  | python3 .claude/hooks/guard_git.py
echo "Exit code: $?" # Must be 2
```

Run your hook tests in CI whenever `.claude/hooks/` or `.agents/hooks.json` changes.

---

## 2. Evaluating `SKILL.md` & Rule Changes (Before/After Evals)

When you edit `CLAUDE.md` or a `SKILL.md` file:
1. **Define 3–5 Representative Prompts:** Include both *positive triggers* (prompts that should activate the skill) and *negative triggers* (unrelated prompts that should **not** load it).
2. **Run Headless Baseline vs. Candidate:** Use `claude -p` (or Antigravity workflows) in an isolated worktree to compare behavior before and after your edit.
3. **Check Token Overhead:** Measure whether a new always-on rule actually improved pass rates enough to justify its per-turn token cost.

---

## 3. Auditing Progressive Disclosure

Periodically review your repo's `CLAUDE.md` / `GEMINI.md` files:
- Move task-specific checklists (migrations, release checklists, incident templates) out of always-loaded memory files and into on-demand **Skills** (`SKILL.md`).
- Keep always-loaded rules crisp, non-contradictory, and under ~150 lines.
