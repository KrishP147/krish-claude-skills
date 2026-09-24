# skills

Krish's Claude Code skills, subagents and dev config.

A personal collection of [Claude Code](https://claude.com/claude-code) skills, subagents and dev config, shared here so you (or I, on another machine) can install and use them too.

A **skill** is a directory with a `SKILL.md` that Claude Code loads into the current conversation when it decides the skill applies (or when you type `/<name>`). A **subagent** is a `.md` file that defines a separate worker with its own context window, model, tool allowlist and preloaded skills; Claude spawns it for isolated work. Skills are "how to do X"; agents are "who does X, with what permissions".

## How to read this repo

Every skill folder has two files: `SKILL.md` is the prompt Claude follows (frontmatter + instructions), and `README.md` is for you: what it does, when to use it, how to invoke it, how it works step by step, and an example. Agents are documented together in [`agents/README.md`](agents/README.md); each `agents/<name>.md` is the definition Claude loads. Start with the READMEs; open a `SKILL.md` only to see or change exact behaviour.

## Three ways to run work

| Tier | You type | Sessions | For |
|---|---|---|---|
| **Solo** | `/next` → implement yourself → `/session-handoff` → `/update-progress` | you, a fresh terminal per step | learning the loop; small repos |
| **Pair** | `/pair <issue # or task>` | one interactive session; a `manager` agent and its `implementer` run inside it | one task on any repo (OSS forks included), no board needed |
| **Orchestrated** | `/meta-orchestrator <repo>` | one top-level session looping planner → manager → merge gate → verifier, handing off to a fresh orchestrator every N merges | a whole backlog, unattended |

Each tier builds on the one above: `pair` is one orchestrator loop without the board, and the orchestrator's default `execution: pair` runs `pair`'s manager once per issue.

## What's here

| Skill | What it does | Prereqs |
|---|---|---|
| [`repo-scrub`](repo-scrub/README.md) | Scans a GitHub repo's full git history for secrets and oversized files, lets you pick exactly what to scrub, rewrites history safely, and only then flips the repo private → public. User-invoked only (`/repo-scrub`). | `gh`, [`gitleaks`](https://github.com/gitleaks/gitleaks), [`git-filter-repo`](https://github.com/newren/git-filter-repo), [`git-sizer`](https://github.com/github/git-sizer) |
| [`grilling`](grilling/README.md) *(Matt Pocock)* | Interviews you relentlessly, one round of questions at a time with a recommendation attached to each, until a plan or decision is fully stress-tested. | none |
| [`grill-me`](grill-me/README.md) *(Matt Pocock)* | Short alias for `grilling`. | none |
| [`handoff`](handoff/README.md) *(Matt Pocock)* | Compacts the current conversation into a handoff document so a fresh session can pick up where it left off. User-invoked only (`/handoff`). | none |
| [`handoff-auto`](handoff-auto/README.md) *(derived from Pocock's `handoff`)* | Same document, but callable by the model, so other skills and subagents can end a session unattended. Prints the file path as its last line. | none |
| [`pair`](pair/README.md) | Runs one task in an isolated git worktree: resolves the issue (syncs upstream first on a fork, checks the cited files still exist), spawns the `manager` agent, shows its report, and only then pushes and opens the PR itself. Agents never touch the remote. | `gh`; `manager` + `implementer` agents installed |
| [`meta-orchestrator`](meta-orchestrator/README.md) | Runs a repo's backlog unattended: spawns `planner` → `manager` (or `implementer`, `execution: flat`) → `verifier` in a loop, holds the merge gate itself (tests + CI green or no merge), appends every event to a ledger, and writes `orchestrator-handoff.md` after a budget of merges so `/meta-orchestrator <repo> resume` continues in a fresh session. | `gh`; the four agents installed; a repo with a kanban board |
| [`progress-report`](progress-report/README.md) | Turns the orchestrator's ledger into a short report covering only what happened since the last one (watermarked, never overlapping): done, what worked, what didn't, concerns, decisions made on your behalf, manual steps for you. Markdown by default, `.docx` on request. | `docx` skill or `python-docx` for the Word option |

### [`kanban/`](kanban/) — GitHub-Issues-as-kanban-board workflow

| Skill | What it does |
|---|---|
| [`next`](kanban/next/README.md) | Shows the next work-session task(s), pulled from the board. Read-only. |
| [`session-handoff`](kanban/session-handoff/README.md) | Ends a session: calls `handoff-auto`, records progress against the board, moves the card |
| [`update-progress`](kanban/update-progress/README.md) | Verifies a handoff's claims, updates docs/board/issue from it |
| [`consult-plan`](kanban/consult-plan/README.md) | Grills a new idea or deviation against the existing plan before it goes in |
| [`divide`](kanban/divide/README.md) | Splits an oversized issue into session-sized ones |
| [`kanban-setup`](kanban/kanban-setup/README.md) | Bootstraps a GitHub Projects board for a repo; can backfill issues from what's already documented. User-invoked only (`/kanban-setup`) because it creates real issues. |

Needs `gh auth refresh -s project -s read:project` once (see [`kanban/README.md`](kanban/README.md)).

### [`agents/`](agents/) — subagents `pair` and the orchestrator spawn

| Agent | Model | Preloads | Guard rails |
|---|---|---|---|
| [`planner`](agents/README.md#planner) ([def](agents/planner.md)) | opus | `next`, `divide` | no Edit/Write; proposes splits, never creates issues; returns a ≤40-line kickoff brief |
| [`manager`](agents/README.md#manager) ([def](agents/manager.md)) | opus | `handoff-auto` | spawns its own `implementer`, reviews the diff and reruns tests itself, restarts a fresh implementer from `HANDOFF.md` when one stalls (≤3 rounds); same guard hook as the implementer; never pushes |
| [`implementer`](agents/README.md#implementer) ([def](agents/implementer.md)) | sonnet | `handoff-auto`, `session-handoff` | a `PreToolUse` hook ([`guard-git.py`](agents/hooks/guard-git.py)) blocks pushes to `main`/`master`, force-pushes and `gh pr merge`; writes `HANDOFF.md` in the repo when stuck or past the smart zone; ends with the handoff path |
| [`verifier`](agents/README.md#verifier) ([def](agents/verifier.md)) | opus | `update-progress`, `consult-plan`, `next` | verifies against git log/tests/CI, reviews the diff, lists every question it answered on your behalf |

Full explainer (inputs, outputs, procedure, guard hook): [`agents/README.md`](agents/README.md). They also work on their own: "use the planner agent to brief the next issue" is a fine prompt without the orchestrator. Set `GUARD_PROTECTED_BRANCHES=main,develop` to change what the hook protects. Agents can spawn agents (`manager` → `implementer`); only the built-in `fork` type can't nest.

### [`hooks/`](hooks/) — optional per-repo hooks

Not auto-installed. [`smartzone.py`](hooks/smartzone.py) is a `UserPromptSubmit` hook that warns in-conversation when the transcript suggests context has left the smart zone (~100k tokens), so a session wraps up instead of degrading. Copy + settings snippet in [`hooks/README.md`](hooks/README.md).

`grilling`, `grill-me`, and `handoff` are by [Matt Pocock](https://github.com/mattpocock/skills) (MIT, see [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md)), included verbatim; `handoff-auto` is his `handoff` with one frontmatter line removed. `npx skills add mattpocock/skills` pulls his full set directly if you want more than these. Everything else here is original.

## Install

```bash
git clone https://github.com/KrishP147/skills.git
cd skills
./scripts/install-skills.sh        # bash/git-bash/mac/linux
# or
.\scripts\install-skills.ps1       # Windows PowerShell
```

This lints the repo, then copies every skill into `~/.claude/skills/<name>/` and every agent into `~/.claude/agents/` (personal, global: works in every repo, every terminal, no need to clone this repo inside your project). Re-running it is safe; each skill and agent is replaced fresh.

## Update

```bash
cd skills
git pull
./scripts/install-skills.sh        # or .\scripts\install-skills.ps1
```

The install copies files rather than symlinking, so a `git pull` alone changes nothing in `~/.claude/` until you re-run the script. Open a new Claude Code session afterwards; agents and skills are read at startup.

Prefer to install by hand, or just one skill? Copy the folder yourself:

```bash
cp -r repo-scrub ~/.claude/skills/repo-scrub
cp agents/planner.md ~/.claude/agents/
```

(`.claude/skills/<name>/` or `.claude/agents/` inside a specific repo installs it project-only, for that repo alone.)

For `repo-scrub`, also install its CLI prerequisites:

```bash
# Windows
winget install --id Gitleaks.Gitleaks -e
pip install git-filter-repo
winget install --id GitHub.git-sizer -e
# mac / linux
brew install gitleaks git-filter-repo git-sizer
```

For anything under `kanban/`:

```bash
gh auth refresh -s project -s read:project
```

## Lint

```bash
python scripts/lint.py
```

Checks every `SKILL.md` and agent file (`agents/README.md` is docs, skipped by lint and install): frontmatter present, `name` matches the folder, description present and ≤1024 chars, no project-specific names leaking in, every skill an agent preloads exists and is model-invocable. The install scripts run this first and stop on failure.

## My `CLAUDE.md`

[`dotfiles/CLAUDE.md`](dotfiles/CLAUDE.md) is my global Claude Code config, adapted from Matt Pocock's (commit-message style, GitHub CLI first, how I want plans formatted; the branch prefix is mine). Install it with:

```bash
./scripts/setup-claude-md.sh merge     # append to your existing ~/.claude/CLAUDE.md
./scripts/setup-claude-md.sh replace   # overwrite/create ~/.claude/CLAUDE.md from scratch
# or, on Windows:
.\scripts\setup-claude-md.ps1 -Mode merge
.\scripts\setup-claude-md.ps1 -Mode replace
```

`merge` just appends with a timestamped separator; it won't dedupe against your existing file, so skim the result afterward.

## Author

[Krish Punjabi](https://github.com/KrishP147). Public, MIT; use whatever's useful.

## License

MIT (see [`LICENSE`](LICENSE)) for everything original in this repo. Matt Pocock's skills carry his own MIT notice; see [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md).
