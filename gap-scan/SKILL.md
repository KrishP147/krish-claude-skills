---
name: gap-scan
description: Survey one or more repos (code, recent commits, docs) and return a ranked list of gaps, bugs, and extension ideas as issue-ready items, each cited with evidence. Read-only: writes only its own report under skilleddocs/gaps/, never creates issues or comments without explicit yes. Triggers: "what's missing", "find gaps", "what should I work on in this repo", "scan for bugs/extensions", "survey this repo", "what should I do next here".
argument-hint: "[repo path or owner/repo, ...] [--commits N]"
---

Read-only survey skill. The only file it writes is its own report under
`skilleddocs/gaps/`. Creating issues, commenting, or editing labels/boards is
never done here without an explicit yes for that specific action (§7).

No argument: the current repo. Multiple repos: run §1–§4 per repo, then one
combined report. `--commits N` overrides the default of ~20 recent commits.

## 1. Sync each repo

Per repo, before reading anything:

- `git status --porcelain`. Dirty: do **not** `git pull` — say "dirty,
  skipped pull" and survey the working tree as-is.
- Clean: `git pull --ff-only`. A non-fast-forward result (diverged history)
  is reported like a dirty tree — don't merge or rebase to force it through.
- Fork (has an `upstream` remote, or `gh repo view --json parent` shows one):
  `git fetch upstream`, then compare (`git log HEAD..upstream/<default>
  --oneline`, `git log upstream/<default>..HEAD --oneline`) so the report
  says how far ahead/behind upstream this fork is. Also pull
  `gh issue list -R <upstream-owner>/<upstream-repo> --label "good first
  issue" --state open --json number,title,url` — upstream's own labeled
  starter work is worth surfacing alongside home-grown gaps.

## 2. Survey

For each repo:

- **README + docs.** Read the top-level README and any `docs/`/roadmap
  files. Note anything a doc promises that the code doesn't do, or vice
  versa (doc/code drift) — cite the doc's file:line next to the code that
  contradicts it.
- **Recent commits.** `git log --oneline -n <N>` (default ~20). Skim for
  reverted work, repeated fixes to the same area (signals a fragile spot),
  and commit messages that admit a shortcut ("hack", "temporary", "quick
  fix").
- **TODO/FIXME.** Grep code (not just docs describing the convention) for
  `TODO|FIXME|XXX`. Each hit is a candidate item, cited by file:line.
- **Tests.** Detect the repo's test command (package.json scripts,
  pytest/tox, cargo test, a Makefile target, README's own instructions). If
  it looks cheap (single package, no network/GPU/paid calls, past
  experience with the repo says fast), run it and report failures with
  file:line or test name. If it looks expensive, needs credentials, or you
  can't tell, don't run it — say "tests not run: <why>" instead of
  skipping silently.
- **Open issues.** `gh issue list --state open --json number,title,labels`.
  Cross-check every candidate gap against this list *before* it goes in the
  ranked output — a gap that matches an open issue is marked **already
  tracked: #<n>**, not re-proposed as new. Don't duplicate the board.
- **Doc/code drift.** Anything the survey turned up above that falls in
  this bucket (stale command examples, a described feature with no matching
  code, a renamed thing the docs still call by the old name) — fold it into
  the ranked list rather than a separate section.

## 3. Optional visual/UX pass

Only run this for a repo that is a web or UI app (a frontend framework,
`index.html` + served assets, a rendered site/dashboard) — skip it for
libraries, CLIs, and backend-only services, and say "visual pass: skipped
(not a UI app)" rather than leaving it unmentioned.

When it applies and the tooling is available (the `run` skill, or a
screenshot capability in this session): launch/preview the app, capture
screenshots of its main views, and note visual or UX inconsistencies
(mismatched spacing, inconsistent button styles, broken layout at common
widths, dead links in the rendered UI). Cite each with the screenshot and
the file/component responsible. If the tooling isn't available, say "visual
pass: skipped (no run/screenshot tool in this session)" instead of
guessing from source alone.

## 4. Rank and tag

For every candidate gap that survived §2 (matched an open issue → keep it,
tagged already-tracked, but still listed so the report is a complete
picture):

- **Rank by value/effort** — highest value-for-effort first. State the
  trade-off in one clause, not a formula.
- **Size tag**: `S` (a focused session, one area of the code) or `L` (spans
  multiple files/areas, or needs a design decision first — a candidate for
  `divide`).
- **Evidence, mandatory.** Every item cites at least one of: `file:line`,
  a commit SHA, or an issue `#n`. **No evidence → drop the item.** A vague
  "this could probably be improved" without something to point at doesn't
  belong in an issue-ready list.

## 5. Write the report

One file per run (multi-repo: still one file, one section per repo):
`skilleddocs/gaps/<local-date>.md` (local date, not UTC —
`date +%F` or `python -c "import datetime as d; print(d.date.today())"`).
Create the `skilleddocs/gaps/` directory if it doesn't exist. This is the
**only** write this skill makes. Never commit it unless the user asks.

Each item in the file uses this shape:

```markdown
### <title>

- Why: <one or two sentences — what's missing/broken and why it matters>
- Evidence: <file:line, commit SHA, or issue #, at least one>
- Size: S | L
- Suggested labels: <e.g. bug, enhancement, status:todo>
- Status: new | already tracked: #<n>
```

## 6. Output format

Chat reply: a short summary (repo(s) scanned, sync result, counts), then the
top few items inline. Full detail lives in the file. Shape:

```
Scanned <repo> (synced clean / dirty, pull skipped).
12 candidates -> 5 after evidence + already-tracked filter.
Report: skilleddocs/gaps/2026-09-26.md

1. [S] <title> - <why, one line> (evidence: path/file.py:42)
2. [L] <title> - <why, one line> (evidence: commit a1b2c3d)
3. [S] <title> - already tracked: #17

Tests: <ran, N passed/failed | not run: <why>>
Visual pass: <ran, findings | skipped, <why>>
```

## 7. GATE — before any outward action

This skill only reports. Creating issues, commenting, editing labels, or
touching the board needs an **explicit yes for that specific action** — a
vague reply ("looks good", "sure") means do nothing further, just leave the
report as-is and say so.

Offer, don't run, these hand-offs once the report is shown:

- **`kanban-setup`** — backfill a board/issues from this list, if the repo
  doesn't already have one worth using.
- **`divide`** — split an `L` item into session-sized issues before anyone
  starts it.
- **`grill-docs`** — stress-test a candidate before committing to it, when
  it's a bigger call than "just do it" (a rewrite, a new dependency, a
  breaking change).
