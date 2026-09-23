# Krish's Claude Skills

My personal collection of [Claude Code](https://claude.com/claude-code) skills and dev config, shared here so you (or I, on another machine) can install and use them too.

A "skill" is a directory with a `SKILL.md` file that Claude Code picks up automatically and follows when it decides the skill applies to what you're doing.

## What's here

| Skill | What it does | Prereqs |
|---|---|---|
| [`repo-scrub`](repo-scrub/) | Scans a GitHub repo's full git history for secrets and oversized files, lets you pick exactly what to scrub, rewrites history safely, and only then flips the repo private → public. | `gh`, [`gitleaks`](https://github.com/gitleaks/gitleaks), [`git-filter-repo`](https://github.com/newren/git-filter-repo), [`git-sizer`](https://github.com/github/git-sizer) |
| [`grilling`](grilling/) *(Matt Pocock)* | Interviews you relentlessly, one round of questions at a time with a recommendation attached to each, until a plan or decision is fully stress-tested. | none |
| [`grill-me`](grill-me/) *(Matt Pocock)* | Short alias for `grilling`. | none |
| [`handoff`](handoff/) *(Matt Pocock)* | Compacts the current conversation into a handoff document so a fresh session can pick up where it left off. | none |

### [`kanban/`](kanban/) — GitHub-Issues-as-kanban-board workflow

| Skill | What it does |
|---|---|
| [`next`](kanban/next/) | Shows the next work-session task(s), pulled from the board |
| [`session-handoff`](kanban/session-handoff/) | Ends a session: wraps `handoff`, records progress against the board, moves the card |
| [`update-progress`](kanban/update-progress/) | Verifies a handoff's claims, updates docs/board/issue from it |
| [`consult-plan`](kanban/consult-plan/) | Grills a new idea or deviation against the existing plan before it goes in |
| [`divide`](kanban/divide/) | Splits an oversized issue into session-sized ones |
| [`kanban-setup`](kanban/kanban-setup/) | Bootstraps a GitHub Projects board for a repo; can backfill issues from what's already documented (current work, completed work, or both) |

Needs `gh auth refresh -s project -s read:project` once (see [`kanban/README.md`](kanban/README.md)).

`grilling`, `grill-me`, and `handoff` are by [Matt Pocock](https://github.com/mattpocock/skills) (MIT-licensed — see [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md)), included here verbatim. `npx skills add mattpocock/skills` pulls his full set directly if you want more than these three. Everything else in this repo is original.

## Install the skills

```bash
git clone https://github.com/KrishP147/krish-claude-skills.git
cd krish-claude-skills
./scripts/install-skills.sh        # bash/git-bash/mac/linux
# or
.\scripts\install-skills.ps1       # Windows PowerShell
```

This copies every skill in the repo into `~/.claude/skills/<name>/` (personal, global — works in every repo, every terminal). Re-running it is safe; it just replaces each skill fresh with whatever's in the repo.

Prefer to install by hand, or just one skill? Copy the folder yourself:

```bash
cp -r repo-scrub ~/.claude/skills/repo-scrub
```

(`.claude/skills/<name>/` inside a specific repo instead of `~/.claude/skills/` installs it project-only, for that repo alone.)

For `repo-scrub`, also install its CLI prerequisites:

```powershell
winget install --id Gitleaks.Gitleaks -e
pip install git-filter-repo
winget install --id GitHub.git-sizer -e
```

For anything under `kanban/`:

```bash
gh auth refresh -s project -s read:project
```

## My `CLAUDE.md`

[`dotfiles/CLAUDE.md`](dotfiles/CLAUDE.md) is my actual global Claude Code config — commit-message style, GitHub/git conventions, how I want plans formatted. Install it with:

```bash
./scripts/setup-claude-md.sh merge     # append to your existing ~/.claude/CLAUDE.md
./scripts/setup-claude-md.sh replace   # overwrite/create ~/.claude/CLAUDE.md from scratch
# or, on Windows:
.\scripts\setup-claude-md.ps1 -Mode merge
.\scripts\setup-claude-md.ps1 -Mode replace
```

`merge` just appends with a timestamped separator — it won't try to dedupe sections against your existing file, so skim the result afterward.

## Author

[Krish Punjabi](https://github.com/KrishP147). Private for now, published here in case it's useful to someone else later.

## License

MIT (see [`LICENSE`](LICENSE)) for everything original in this repo. Matt Pocock's three skills carry his own MIT notice — see [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md).
