# Model Routing, Token Economics & Cost Control

Using the largest frontier reasoning model for every trivial rename or log summary wastes both money and wall-clock time. Senior operators treat **model selection and context size** as engineering trade-offs.

---

## Routing Tasks to the Right Model Tier

Claude Code lets you switch models mid-session (`/model`), via CLI flag (`--model`), or per subagent (`model:` in `.claude/agents/*.md`):

| Task Profile | Recommended Tier | Why |
| :--- | :--- | :--- |
| **Deep architecture, subtle race conditions, multi-module `/plan`** | **Opus** (Heavy Reasoning) | Highest multi-step planning accuracy; worth the extra latency/cost |
| **Daily feature implementation, Spring/JUnit coding, PR reviews** | **Sonnet** (Balanced Default) | Fast, strong coding accuracy, best cost-to-speed ratio |
| **Read-only file search, log summarization, subagent grep** | **Haiku** (Fast & Cheap) | Sub-second responses for high-volume exploration and pipe triage |

**Pro Tip:** Pair an **Opus** coordinator for `/plan` and final verification with **Haiku/Sonnet** subagents for codebase search and test log parsing.

---

## Four Rules to Cut Token Waste by 50%+

1. **Kill Verbose Build Output:** Never let `./mvnw` or `./gradlew` dump 3,000 lines of `INFO` logs—always use `-q` and targeted `-Dtest=...`. Every 10,000 wasted log tokens are re-billed on *every subsequent turn* of that conversation.
2. **`/clear` Between Unrelated Tasks:** Prompt caching and small contexts make fresh sessions dramatically cheaper than 60-turn mega-threads.
3. **Compact Deliberately (`/compact`):** Summarize once exploration is done so you don't carry 40KB of raw file reads into the implementation phase.
4. **Monitor with `/cost`:** Run `/cost` periodically in interactive sessions (and always set `--max-turns` in headless CI scripts) to catch runaway loops early.
