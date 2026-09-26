# Handoff: issue #4 — CONTRIBUTING.md + skill submission template + README lint

Branch: `krish/issue-4-contributing-template-lint` (worktree
`C:\Users\User\source\repos\_worktrees\skills-issue-4`)

## Status: complete

All 9 tasks from the kickoff brief (issue #4, `skilleddocs/orchestrator/scope.md`)
are done and committed. `python scripts/lint.py` exits 0.

## What was done

Commits (oldest to newest), each `Co-Authored-By: Claude Opus 5.5`:

1. `afd42c4` lint: warn on missing README sections; skip templates/
2. `1dd6c23` docs: add CONTRIBUTING.md
3. `5245631` templates: add skill README + SKILL.md submission templates
4. `c9f9e9f` github: add PR template + skill-idea issue template
5. `d899815` install: skip templates/ in both install scripts
6. `cf8b7d3` docs: link CONTRIBUTING.md from README

Files: `CONTRIBUTING.md`, `templates/skill/README.md`, `templates/skill/SKILL.md`,
`.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/skill-idea.md`,
`scripts/lint.py` (added `templates` to `SKIP_DIRS`, added
`warn_missing_readme_sections()` — WARN to stderr, never fails, "Invoke"
accepted as alias of "How to invoke"), `scripts/install-skills.sh` and
`scripts/install-skills.ps1` (both skip anything under `templates/`),
`README.md` (new "Contributing / grow this repo" section + one line in Lint
section about warnings).

No changes to `site/`, `.github/workflows/`, `.gitattributes`, or
`.gitignore` (out of scope per orchestrator instructions).

## Verification done this session

- `python scripts/lint.py`: exit 0. stdout last line `OK: 15 skills, 4 agents`.
  stderr has 15 pre-existing `WARN: ...: missing sections: Design principles,
  Use cases, Tips, Prereqs` lines — expected: existing skill READMEs predate
  this template and were intentionally **not** backfilled per the brief.
- `scripts/install-skills.sh` run with `CLAUDE_SKILLS_DIR`/`CLAUDE_AGENTS_DIR`
  pointed at temp dirs: installed 15 skills, 4 agents, no `templates`/`skill`
  dir present. Temp dirs deleted after.
- `scripts/install-skills.ps1` run the same way (PowerShell temp dirs):
  same result, verified `Test-Path <target>\skill` is `False`. Temp dirs
  deleted after.

## Board status

- Issue: #4 (`CONTRIBUTING.md + skill submission template + README lint`),
  repo `KrishP147/skills`.
- No GitHub Projects board found for this repo when checked (`gh project
  item-list` / `next` conventions) — the orchestrator scope doc describes a
  label-pseudo-board only.
- Label state at session start: `status:in-progress` (branch/card was already
  marked started before this session — worktree name and label indicate a
  prior agent created the branch). This session did not create the branch,
  so per the `implementer` agent rule ("created the branch yourself... mark
  started"), no start-marking action was needed from this session.
- Task is complete: label should move `status:in-progress` -> `status:in-review`.
  Attempted via `gh issue edit 4 --remove-label status:in-progress --add-label
  status:in-review` (see below for outcome) and a completion comment.
- No deviations from the issue body / scope.md. One minor interpretation:
  issue body's checklist item "Invoke" (as a section name) is the alias for
  the brief's canonical "How to invoke" heading — implemented exactly as
  the orchestrator prompt specified (lint accepts both).

## Ideas / notes not in the issue

- The 15 pre-existing skill READMEs are now flagged by lint as missing
  `Design principles`, `Use cases`, `Tips`, `Prereqs`. A natural follow-up
  issue: backfill those four sections across existing skills so the site
  (mentioned in scope.md) has full pages for all of them, and so lint runs
  clean with zero warnings. Not done here — brief explicitly said "do NOT
  backfill existing READMEs."
- `templates/skill/README.md` is the canonical section list; if that list
  ever changes, `scripts/lint.py`'s `REQUIRED_README_SECTIONS` must be
  updated to match (currently duplicated, not derived from the template file).

## Suggested skills for the next session

- `session-handoff` / `update-progress` if a verifier picks this up next —
  the label move may need retrying (see below).
- No implementation skill needed; the issue is done. `consult-plan` only if
  someone wants to dispute the backfill-follow-up idea above before filing it.

## Handoff file

C:\Users\User\source\repos\_worktrees\skills-issue-4\skilleddocs\handoffs\2026-09-26-issue-4-contributing-template-lint.md
