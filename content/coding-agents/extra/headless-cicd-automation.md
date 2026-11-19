# Headless & CI/CD Agent Automation

Interactive chat is only half of what coding agents can do. Both **Claude Code** and **Google Antigravity** can run **headlessly** (non-interactively) inside CI/CD pipelines, cron jobs, and shell scripts to triage issues, review PRs, or run overnight maintenance.

---

## Claude Code in Headless & Pipe Mode (`-p`)

Claude Code's `-p` (`--print`) flag runs a single prompt non-interactively, prints the result to `stdout`, and exits—making it composable with standard Unix tools.

### 1. Unix Pipe Diagnostics
Pipe logs or diffs straight into Claude Code:

```bash
# Summarize a failing CI log
cat build-failure.log | claude -p "Identify the root cause and failing test."

# Generate release notes from recent commits
git log v1.4.0..HEAD --oneline | claude -p "Group into Features and Fixes."
```

### 2. Structured JSON & Scoped Permissions for CI
In GitHub Actions or GitLab CI, you must avoid interactive prompts while still keeping least-privilege boundaries using `--allowedTools` and `--output-format json`:

```bash
claude -p "Review the PR diff for security and null-safety issues." \
  --allowedTools "Read,Grep,Glob,Bash(git diff *)" \
  --output-format json \
  --max-turns 10
```

- `--allowedTools` whitelists *only* read-only inspection and `git diff`, ensuring the CI agent cannot mutate files or run arbitrary shell commands.
- `--max-turns` caps the agent loop so a stuck job never burns unlimited API credits.

---

## Google Antigravity Automation Surfaces

Google Antigravity provides three native ways to automate work without babysitting a chat window:

### 1. Scheduled Tasks (`/schedule` & Cron)
In Antigravity 2.0 and `agy`, you can register recurring **Scheduled Tasks** using standard 5-field cron expressions (e.g., `0 9 * * 1-5` for weekday mornings) or one-time delayed timers:
- Daily dependency / CVE audit summaries.
- Morning triage of newly opened GitHub issues.
- Nightly flaky-test investigation in an isolated worktree.

### 2. Dynamic Python Workflows (`run_workflow`)
When an automation task needs deterministic fan-out/fan-in—like auditing 20 repositories or running a 3-stage `Analyze -> Patch -> Verify` pipeline across 50 files—Antigravity runs Python workflow scripts with `agent()`, `parallel()`, and `pipeline()` primitives.

### 3. Antigravity Python SDK
For custom internal developer platforms (IDPs), Slack bots, or backend services, the official **Antigravity Python SDK** (`antigravity-sdk-python`) lets your Python code lease agents programmatically, expose custom Python functions as agent tools, and stream structured orchestration events.

---

## CI/CD Safety Checklist

Before enabling any headless agent in CI:
1. **Pin `--max-turns` / timeouts** to bound worst-case token spend.
2. **Use read-only tokens** for PR reviewers; never grant push-to-`main` credentials to an autonomous agent.
3. **Never pass untrusted PR titles/bodies raw into shell `eval`**—pass them via environment variables or files to prevent command injection.
4. **Always require human merge approval** for agent-opened PRs.
