# claude-skills

A personal collection of [Claude Code](https://claude.com/claude-code) skills — reusable, model-invocable workflows that live as a `SKILL.md` file (plus, occasionally, a small script) and get picked up automatically when Claude decides one applies.

## What's here

| Skill | What it does | Prereqs |
|---|---|---|
| [`repo-scrub`](repo-scrub/) | Scans a GitHub repo's full git history for secrets and oversized files, lets you pick exactly what to scrub, rewrites history safely, and only then flips the repo private → public. | `gh`, [`gitleaks`](https://github.com/gitleaks/gitleaks), [`git-filter-repo`](https://github.com/newren/git-filter-repo), [`git-sizer`](https://github.com/github/git-sizer) |
| [`grilling`](grilling/) | Interviews you relentlessly, one round of questions at a time with a recommendation attached to each, until a plan or decision is fully stress-tested. | none |
| [`grill-me`](grill-me/) | Short alias for `grilling`. | none |
| [`handoff`](handoff/) | Compacts the current conversation into a handoff document so a fresh session can pick up where it left off. | none |

`grilling`, `grill-me`, and `handoff` are by [Matt Pocock](https://github.com/mattpocock/skills) — included here verbatim, credited to him, not authored by me. (`npx skills add mattpocock/skills` pulls the full set directly if you want more than these three.)

## How a Claude Code skill works

A skill is a directory containing a `SKILL.md` with YAML frontmatter and a prose body:

```yaml
---
name: my-skill
description: One or two sentences describing what it does and when to use it — this is what Claude matches against to decide whether the skill applies.
argument-hint: "optional hint text shown when invoked with arguments"
disable-model-invocation: true   # optional - set this if the skill should only run when explicitly called
---

Instructions for Claude to follow, in prose.
```

The convention in this repo is a **single self-contained `SKILL.md`** per skill. The one exception is `repo-scrub`, which ships a `scripts/` folder — see [`repo-scrub/SKILL.md`](repo-scrub/SKILL.md) for why (short version: a couple of its steps need deterministic parsing/handling that shouldn't be left to free-form prose, particularly around not leaking raw secret values into a conversation transcript).

## Installing a skill

Claude Code looks for skills in two places:

- **Personal** — `~/.claude/skills/<name>/` (on Windows, `%USERPROFILE%\.claude\skills\<name>\`). Available in every repo, every terminal, all the time.
- **Project** — `<repo>/.claude/skills/<name>/`. Available only inside that repo, and only for people who have it checked out.

To install a skill from this repo for yourself, clone the repo and copy the skill folder into whichever location fits:

```bash
git clone <this repo's URL>
cp -r claude-skills/repo-scrub ~/.claude/skills/repo-scrub
```

(On Windows, a plain copy is the simplest option — `New-Item -ItemType SymbolicLink` works too if you want a live symlink instead, but it needs Developer Mode or admin rights.)

For `repo-scrub` specifically, also install its prerequisite CLI tools before first use:

```powershell
winget install --id Gitleaks.Gitleaks -e
pip install git-filter-repo
winget install --id GitHub.git-sizer -e
gh auth login   # if you haven't already
```

The skill itself checks for these on every run and tells you what's missing if you skipped a step.
