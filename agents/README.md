# agents/ — subagents

*Each `<name>.md` here is the agent definition Claude Code loads (frontmatter + system prompt); this file is for you. `README.md` itself is skipped by the install scripts and the linter.*

A subagent runs in its own context window with its own model, tool allowlist and preloaded skills. Claude spawns one with `Agent(subagent_type="<name>", prompt=…)`. [`pair`](../pair/) and [`meta-orchestrator`](../meta-orchestrator/) spawn these, but each also works on its own ("use the planner agent to brief the next issue").

Installed by `scripts/install-skills.*` into `~/.claude/agents/`, with `hooks/` into `~/.claude/agents/hooks/`.

| Agent | Model | Preloads | Spawned by |
|---|---|---|---|
| [`planner`](#planner) | opus | `next`, `divide` | `meta-orchestrator` |
| [`manager`](#manager) | opus | `handoff-auto` | `pair`; `meta-orchestrator` (`execution: pair`) |
| [`implementer`](#implementer) | sonnet | `handoff-auto`, `session-handoff` | `manager`; `meta-orchestrator` (`execution: flat`) |
| [`verifier`](#verifier) | opus | `update-progress`, `consult-plan`, `next` | `meta-orchestrator` |

## planner

- **Role:** picks the next single unit of work from the board and writes the kickoff brief. Read-only: `disallowedTools: Edit, Write, NotebookEdit`; never creates issues. `maxTurns: 40`.
- **You pass:** repo path + scope contract (exclusions such as gated issues / people tasks / labels, ordering rule).
- **How it works:** runs `next` → drops excluded items → picks exactly one task → uses `divide` to *propose* a split if it looks multi-session → if nothing is left, says so and stops.
- **You get back (≤40 lines):** issue + acceptance checklist, key files, decisions/ADRs to respect, branch name `<prefix>/issue-<n>-<slug>`, gotchas, recommended model (and why), divide yes/no + proposed split.

## manager

- **Role:** owns one task end to end in a worktree. Never implements itself: briefs an implementer, then reviews its work as if it didn't trust it. `maxTurns: 150`.
- **You pass:** working directory (absolute, usually a worktree on the task branch), task + acceptance checklist, rules (branch prefix, protected branch, commit style, `CONTRIBUTING.md`/`AGENTS.md` path), `max_rounds` (default 3).
- **How it works:**
  1. Orients read-only; confirms every file the task cites exists; detects the test command.
  2. Writes a ≤40-line brief (includes "if stuck, write `skilleddocs/HANDOFF.md`, commit, stop").
  3. Spawns an `implementer` (not `fork`, no `isolation`) and keeps a wait alive until it finishes; if forced to report early, titles the report **INTERIM — implementer still running** (callers must not act on it).
  4. Reviews every round itself, inline: commit scope, `git diff <base>...HEAD`, reruns tests + lint. Fixes one-liners; larger gaps go to the next round. Never spawns reviewer subagents.
  5. Retries with a **fresh** implementer + `skilleddocs/HANDOFF.md`/findings, up to `max_rounds`.
- **You get back:** branch + base/head SHA, commits, tests (command + counts) and lint run by it, review findings and who fixed each, rounds used, `skilleddocs/HANDOFF.md` path if unfinished, manual steps (e.g. the push).
- **Guard:** same `guard-git.py` hook as the implementer. Never pushes, merges or opens PRs — the caller does. Never deletes links or worktrees either, and never a recursive delete through a linked `node_modules`/`.venv` — teardown is the caller's job.

## implementer

- **Role:** implements one well-specified issue from a kickoff brief on its own branch. `maxTurns: 200`.
- **You pass:** the kickoff brief verbatim + branch prefix + protected branch (from `manager` or the orchestrator).
- **How it works:** branches `<prefix>/issue-<n>-<slug>` off a freshly pulled default; if it created the branch, marks the issue started (card → In Progress, or `status:todo` → `status:in-progress`; skipped with no board) and comments "Started on branch …", fail-soft (an error goes in the handoff, never blocks); commits small; runs the repo's detected test command before claiming done. Multi-session task or low turns → writes the handoff early. Stuck or past ~100k tokens → writes `skilleddocs/HANDOFF.md` (done / not done / next step / failed attempts), commits it, stops, so a manager can restart a fresh implementer from it.
- **You get back:** calls `session-handoff` (which wraps `handoff-auto`); final message ends with the handoff document's absolute path on its own line.
- **Guard:** `guard-git.py` hook (below).

## verifier

- **Role:** verifies an implementation session and closes the loop. `maxTurns: 120`. No guard hook.
- **You pass:** handoff path (or saved manager report path), whether it may answer interview-style questions on your behalf, `review-done=yes|no` (default no; `yes` = a manager already reviewed and reran tests).
- **How it works:**
  1. Runs `update-progress` end to end: claims vs `git log`, tests, CI, code review (skipped if `review-done=yes`), docs/board/issue updates. Code review is inline, two axes (standards + spec), no reviewer subagents.
  2. Deviations: if authorized, answers `consult-plan` itself from the written plan and lists every Q → A; if not, records the deviation and leaves the plan untouched.
  3. Calls `next`.
- **You get back:** verified-by (tests + CI run id), findings fixed / issues filed, decided-for-you list, manual steps for you, then `next`'s output unedited.

## hooks/guard-git.py

`PreToolUse` hook on `Bash`, wired in the `implementer` and `manager` frontmatter as `python "$HOME/.claude/agents/hooks/guard-git.py"`. Reads the hook JSON, splits the command on `&&` / `||` / `;`, and exits 2 (blocks, reason on stderr) for:

- `git push` with `--force` / `-f` / `--force-with-lease`, `--delete` / `-d`, or `--mirror`
- `git push` naming a protected branch (incl. `HEAD:main`), or a bare `git push` while on one
- `gh pr merge`, `gh repo delete`
- `git branch -D/-d/--delete <protected>`

Protected branches: `GUARD_PROTECTED_BRANCHES` (comma list), default `main,master`. A block is working as intended, not something for the agent to route around. Self-test: `python agents/hooks/guard-git.py --self-test`.

## Example

```
Agent(subagent_type="planner", prompt="~/code/myrepo; exclusions: label needs-design; order: priority label")
```

→ a brief for #31 (branch `feat/issue-31-csv-export`, recommended model sonnet, divide: no). Pass it verbatim to a `manager`, which returns commits + `pytest 118/118` + "rounds used 1/3"; you push, merge, then hand the saved report to a `verifier` with `review-done=yes`.
