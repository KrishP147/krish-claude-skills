---
name: kanban-setup
description: Set up a GitHub Projects kanban board for a repo and populate it with issues from documented work — current planned work, already-completed work (retroactive backfill), or both. Use when a repo has no GitHub kanban board yet, or its issue history needs backfilling from docs/git history.
argument-hint: "mode: current | retroactive | both (default: current)"
---

**This creates real, visible GitHub issues.** Always show the user the full preview list of issues about to be created and wait for confirmation before creating anything — don't create blind, and don't skip items silently.

## 1. Prerequisite

`gh project` commands need the `project` scope. Check `gh auth status`; if `project` isn't listed, tell the user to run `gh auth refresh -s project -s read:project` (interactive, opens a browser) and stop until it's done.

## 2. Board setup (idempotent — skip if it already exists)

```
gh project list --owner <owner> --format json
```

If none exists: `gh project create --owner <owner> --title "<repo> Board"`. Projects v2 ships a default Status field with Todo/In Progress/Done — confirm via `gh project field-list` rather than assuming; only add custom columns if the user asks for something different.

## 3. Scan the repo for documented work

Look at whatever actually exists — don't require any specific file:
- README sections like "Roadmap" or "TODO"
- `TODO`/`FIXME` code comments
- `CHANGELOG.md`
- a `docs/` folder or any plan-like doc

## 4. Build the candidate list, per mode

- **`current`** (default): items that read as planned/undone. For each, search existing issues first (`gh issue search` / `gh issue list`) to avoid duplicates.
- **`retroactive`**: items that read as already finished (CHANGELOG entries, git log messages describing completed work, resolved TODOs). These get created *and immediately closed* — the point is a clean historical record, not new work.
- **`both`**: run both passes, clearly separated in the preview.

## 5. Preview, then create

Show the full list — title, mode (current/retroactive), and which board column it'll land in — before creating anything. On confirmation:
- `current` items → `gh issue create`, add to board's Todo column.
- `retroactive` items → `gh issue create`, then `gh issue close`, add to board's Done column.
