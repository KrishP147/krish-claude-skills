---
name: next
description: Show the next work-session task(s) from a repo's GitHub kanban board (Projects v2, or label-based fallback). Use when starting a work session or asking what to work on next.
disallowed-tools: Edit, Write, NotebookEdit
---

## 1. Find the board

*Canonical board-lookup — other kanban skills point back here.*

```
gh project list --owner <owner> --format json
```

This returns *every* project the owner has, not just ones tied to this repo — several returned is not automatic ambiguity. Filter to a title match (`"<repo> Board"`, matching `kanban-setup`'s naming) or to boards whose items link back to this repo. Exactly one match: use it. More than one: ask the user. None: check for a label-based pseudo-board (`status:todo`, `status:in-progress`, `status:done` labels). Neither exists: fall back to a **roadmap doc** (`ROADMAP.md`, `docs/roadmap.md`) whose ordering section ("Execution order" or similar) links issues — that ordering is the queue. Nothing at all: tell the user to run `kanban-setup` first.

## 2. Check for a burning priority first

```
gh run list --branch <default-branch> --status failure --limit 1
```

A red default branch outranks everything else — surface it as priority #1 if found.

## 3. Pull candidate tasks

- Projects v2: `gh project item-list <number> --owner <owner> --format json`, filter to the "Todo"/"Ready" status. `gh project item-list` is eventually consistent and can return an empty list minutes after items were added. If empty, cross-check with `gh issue list --repo <owner>/<repo> --state open --json number,title,projectItems` before concluding the board is empty; only then fall through to "run kanban-setup".
- Label fallback: first `gh issue list --label "status:in-review" --state open --json number,title,labels` — list these ahead of everything else, tagged "awaiting update-progress / verification" (finished sessions nobody has verified yet); then `gh issue list --label "status:todo" --state open --json number,title,labels`.
- Roadmap-doc fallback: walk the doc's execution order; a linked issue that is still open is a candidate, in doc order. Skip items the doc marks as gated/blocked unless nothing else remains.

Sort by a priority label if one exists (`priority:high` etc.), else by roadmap order, else by issue age (oldest first).

A repo's `CLAUDE.md`/`AGENTS.md` may override any of this (source of truth, gating rules, output format). Project rules win.

## 4. Present

Show the top 1–3 candidates: title, issue number, a size estimate if a `size:S/M/L`-style label exists (else say "unestimated"), and a suggested model — well-specified, narrowly-scoped work suits a fast model; ambiguous, architecture-heavy, or explicitly `needs-design`-labeled work suits a stronger reasoning model. Ask the user which to start, or take "go" as picking the top one.
