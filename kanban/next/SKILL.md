---
name: next
description: Show the next work-session task(s) from a repo's GitHub kanban board (Projects v2, or label-based fallback). Use when starting a work session or asking what to work on next.
---

## 1. Find the board

```
gh project list --owner <owner> --format json
```

`gh project list` returns *every* project the owner has, not just ones tied to this repo — an owner with other, unrelated boards is common, so don't treat "several returned" as automatic ambiguity. First filter to a title match for this repo (`"<repo> Board"`, matching `kanban-setup`'s naming) or to boards whose items link back to this repo. If exactly one matches, use it without asking. Only ask the user when more than one still matches after that filter. If none match, check for a label-based pseudo-board instead (`status:todo`, `status:in-progress`, `status:done` labels on issues). If neither exists, tell the user to run the `kanban-setup` skill first — there's nothing to pull "next" from yet.

## 2. Check for a burning priority first

```
gh run list --branch <default-branch> --status failure --limit 1
```

A red default branch outranks everything else — surface it as priority #1 if found.

## 3. Pull candidate tasks

- Projects v2: `gh project item-list <number> --owner <owner> --format json`, filter to the "Todo"/"Ready" status. **Verified unreliable in testing**: on a freshly created project this returned `{"items":[],"totalCount":0}` for 2+ minutes even though items were genuinely on the board (confirmed via `gh issue view` showing the project/status, and via GraphQL node lookup). If it comes back empty, don't conclude the board is empty — cross-check with `gh issue list --repo <owner>/<repo> --state open --json number,title,projectItems` first (reads project status per-issue and was reliable in testing even when `item-list` wasn't), and only fall through to "run kanban-setup" if that's *also* empty.
- Label fallback: `gh issue list --label "status:todo" --state open --json number,title,labels`.

Sort by a priority label if one exists (`priority:high` etc.), else by issue age (oldest first).

## 4. Present

Show the top 1–3 candidates: title, issue number, a size estimate if a `size:S/M/L`-style label exists (else say "unestimated"), and a suggested model — well-specified, narrowly-scoped work suits a fast model; ambiguous, architecture-heavy, or explicitly `needs-design`-labeled work suits a stronger reasoning model. Ask the user which to start, or take "go" as picking the top one.
