# next

*`SKILL.md` is the prompt Claude follows; this file is for you. Loop overview: [`kanban/README.md`](../README.md).*

## What it does

Shows the next 1–3 tasks to work on, pulled from the repo's GitHub kanban board, with a size and a suggested model for each. Read-only (Edit/Write disallowed).

## When to use

- Starting a work session: "what should I work on next?"
- End of `update-progress` and `verifier` runs, to surface the following task.

## How to invoke

`/next`, or ask what's next — model-invocable.

## How it works

1. **Find the board** (the canonical lookup other kanban skills reuse): `gh project list --owner <owner>`, filtered to the title `<repo> Board` or boards linking this repo's issues. One match → use it; several → asks you. None → `status:todo` / `status:in-progress` / `status:done` labels. None → a roadmap doc (`ROADMAP.md`, `docs/roadmap.md`) whose execution order links issues. Nothing → tells you to run `/kanban-setup`.
2. **Burning priority:** a failing CI run on the default branch is surfaced as #1.
3. **Candidates:** Todo/Ready items (cross-checks `gh issue list` if the eventually-consistent `gh project item-list` returns empty), or (labels) `status:in-review` issues first, tagged "awaiting update-progress / verification", then `status:todo` issues, or open issues in roadmap order. Sorted by priority label, else roadmap order, else oldest first. A repo's `CLAUDE.md`/`AGENTS.md` rules override all of this.
4. **Present:** top 1–3 with title, number, size (`size:*` label or "unestimated"), suggested model (fast for well-specified, strong for ambiguous/`needs-design`). "go" picks the top one. Picking doesn't claim the card; the `implementer` agent or `pair` moves it to In Progress when it creates the branch, so a Todo card may have been picked but never started.

## Related

- [`kanban-setup`](../kanban-setup/) creates the board it reads.
- Called by [`update-progress`](../update-progress/); preloaded by the `planner` and `verifier` agents.
- Board lookup reused by `session-handoff`, `update-progress`, `kanban-setup`.

## Example

```
/next
```

→ "1. #31 Add CSV export (size:M, fast model) 2. #28 Rework auth flow (unestimated, strong model — needs-design). Which one?"
