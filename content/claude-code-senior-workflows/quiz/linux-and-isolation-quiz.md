## Q1
Why is `claude -p` (`--print` mode) particularly valuable for senior Linux engineers?

### Option A
It opens a graphical Swing window for editing code

### Option B [CORRECT]
It reads `stdin` and writes `stdout` non-interactively, allowing Claude Code to compose with Unix pipes (`journalctl`, `docker logs`, `git diff`, `jq`)

### Option C
It bypasses all Linux file permissions automatically

### Option D
It compiles Bash scripts into native ELF binaries

### Explanation
`claude -p` runs Claude Code non-interactively on `stdin` and writes its output to `stdout`, making it a first-class Unix CLI citizen that composes seamlessly with `journalctl`, `docker logs`, `gh`, `git diff`, and `jq`.

===

## Q2
How can a Linux developer run two parallel Claude Code tasks (e.g., a feature and an urgent hotfix) without file collisions?

### Option A
Open two tabs in the same directory and alternate typing every 10 seconds

### Option B [CORRECT]
Use `tmux` windows paired with isolated Git worktrees (`claude --worktree <name>`)

### Option C
Copy the entire `.git` folder into `/tmp` manually for every prompt

### Option D
Disable `PostToolUse` hooks in both terminals

### Explanation
Running two writer agents in the same directory causes them to overwrite each other's edits. Pairing `tmux` sessions with `claude --worktree <name>` gives each task its own isolated working tree linked to the same repository.

===

## Q3
What is the safest way on Linux to run Claude Code with `--dangerously-skip-permissions` for a large, unattended code migration?

### Option A
Run it as `root` directly in `/home`

### Option B [CORRECT]
Run it inside an ephemeral rootless Docker/Podman container mounting only the isolated project worktree

### Option C
Disable `git` so no commits can be made

### Option D
Delete `~/.ssh` temporarily before starting the session

### Explanation
Even with `deny` rules, running `--dangerously-skip-permissions` on a host Linux machine carries unnecessary risk. Isolating the session inside an ephemeral rootless container that mounts only the target worktree bounds the blast radius completely.

===

## Q4
In `~/.claude/settings.json`, what does adding `"Read(~/.ssh/**)"` and `"Read(~/.aws/**)"` to `permissions.deny` achieve?

### Option A
It encrypts your SSH keys with a new passphrase

### Option B [CORRECT]
It blocks the agent from reading local credentials so they never enter the LLM's context window

### Option C
It automatically rotates AWS IAM keys after every commit

### Option D
It disables `ssh-agent` on the Linux workstation

### Explanation
`Read(...)` deny rules prevent Claude Code from accessing sensitive paths like `~/.ssh/**`, `~/.aws/**`, or `.env*`, ensuring private keys and cloud credentials never enter the model's context window.

===

## Q5
Why combine `--output-format json` with `--allowedTools "Read,Grep,Glob"` when scripting `claude -p` in Linux automation?

### Option A
It forces Claude to write only JSON files in the repository

### Option B
It disables `--max-turns` limits

### Option C [CORRECT]
It produces machine-parseable output for `jq` while restricting the script to read-only inspection tools

### Option D
It replaces the need for `git` in the repository

### Explanation
`--output-format json` lets shell scripts parse structured output cleanly with `jq`, while `--allowedTools "Read,Grep,Glob"` enforces least-privilege read-only execution so automated pipelines cannot mutate files or run arbitrary shell commands.
