# Skills, Slash Commands & Progressive Disclosure

A common mistake when teams scale their use of coding agents is dumping every runbook, migration guide, PR checklist, and deployment procedure into `CLAUDE.md` or `GEMINI.md`. Within weeks, the memory file balloons to 2,000 lines, burning context tokens on every turn and diluting the rules that actually matter.

The solution in both **Google Antigravity** and **Claude Code** is **Skills**—modular, on-demand playbooks powered by **progressive disclosure**.

---

## How Progressive Disclosure Works

Instead of loading every instruction upfront, the agent harness splits knowledge into two tiers:

1. **Metadata Tier (Always Loaded):** At session start, the agent sees *only* each skill's `name` and short `description` (a few dozen tokens per skill).
2. **Execution Tier (Loaded on Demand):** When your prompt matches a skill's description—or when you invoke it explicitly—the agent reads the full `SKILL.md` body and any helper scripts or reference docs inside that skill folder.

```text
Session Start:
  System Prompt <-- [Skill A: name + 1-line description]
                <-- [Skill B: name + 1-line description]
                <-- [Skill C: name + 1-line description]

User says: "Run a database migration for orders"
  Agent matches Skill B --> Loads skills/db-migration/SKILL.md
                        --> Reads skills/db-migration/references/naming.md
                        --> Runs skills/db-migration/scripts/validate.sh
```

---

## Anatomy of a Skill (`SKILL.md`)

Both Antigravity and Claude Code follow the open **Agent Skills** folder convention:

```text
.agents/skills/flyway-migration/     # Antigravity (or .claude/skills/ in Claude Code)
├── SKILL.md                         # Required: YAML frontmatter + instructions
├── scripts/
│   └── check_naming.py              # Deterministic validation script
├── references/
│   └── zero-downtime-patterns.md    # Heavy docs loaded only if needed
└── templates/
    └── V__migration.sql.tmpl        # Boilerplate template
```

### Example `SKILL.md`

```markdown
---
name: flyway-migration
description: >-
  Creates and validates Flyway SQL migrations for PostgreSQL.
  Use when adding tables, columns, or indexes to db/migration/.
---

# Flyway Migration Playbook

1. Inspect the highest existing version in `src/main/resources/db/migration/`.
2. Create `V<next>__<snake_case_description>.sql`.
3. Never use `ADD COLUMN ... NOT NULL` without a `DEFAULT` on large tables.
4. Run `python3 scripts/check_naming.py` to verify filename and SQL lint rules.
5. Verify locally with `./mvnw flyway:validate`.
```

**Pro Tip:** Put deterministic checks (regexes, schema validators, formatters) inside `scripts/` and instruct the skill to execute them. Don't ask the LLM to mentally lint SQL when a 20-line Python script does it with 100% accuracy.

---

## Where Skills Live & Precedence

| Scope | Google Antigravity | Claude Code |
| :--- | :--- | :--- |
| **Project / Team (Git)** | `.agents/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` |
| **User Global (Machine)** | `~/.gemini/config/skills/<name>/SKILL.md` | `~/.claude/skills/<name>/SKILL.md` |
| **Explicit Registry / Plugins** | `skills.json`, `plugins/<name>/plugin.json` | Installed plugins (`~/.claude/plugins/`) |

In Antigravity, workspace customizations in `.agents/` take highest priority over global `~/.gemini/config/` and built-in skills, allowing teams to override default behaviors cleanly per repository.

---

## Slash Commands: Operator Shortcuts

Slash commands (`/command`) are user-triggered shortcuts in the chat UI or CLI that either manage the session or launch specialized agent behaviors.

### Essential Antigravity Slash Commands
- `/plan` — Forces careful step-by-step planning before any code execution.
- `/grill-me` — Launches an interactive interview where the agent challenges assumptions and resolves design decisions with you before building.
- `/compact` — Summarizes conversation history to free context window space.
- `/goal` — Configures thorough, long-running execution until the objective is verified.
- `/teamwork` — Coordinates a multi-agent team for large projects.
- `/learn` — Persists a solved setup or operator correction for future sessions.
- `/schedule` — Sets up recurring cron jobs or one-time delayed timers.

### Essential Claude Code Slash Commands
- `/init` — Scans the repo and generates a tailored `CLAUDE.md`.
- `/compact [focus]` — Compresses history, optionally keeping specific context.
- `/clear` — Wipes the current conversation for a fresh start.
- `/model` — Switches active model (e.g., Sonnet for speed, Opus for deep reasoning).
- `/cost` — Displays token usage and session cost so far.
- `/review` — Runs a structured code review on current changes or a PR.
- **Custom Commands:** Drop a Markdown file in `.claude/commands/deploy-check.md` (use `$ARGUMENTS` for parameters) and invoke it as `/deploy-check staging`.
