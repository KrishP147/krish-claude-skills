---
name: consult-plan
description: Grill a proposed change, deviation, or innovation against a repo's existing plan (open GitHub issues, the kanban board, and any roadmap doc if present), then record the outcome. Invoked automatically by update-progress when a handoff records deviations; invoke directly to pitch a new idea.
argument-hint: "the idea, deviation, or innovation to discuss"
---

1. **Gather the baseline** — don't require any of these, just use whatever exists:
   - `gh issue list --state open` for the current open work.
   - The kanban board's current state (`gh project item-list` or the `status:*` labels), if the repo has a board.
   - Any roadmap-like doc if present (`ROADMAP.md`, `docs/roadmap.md`, or similar) — read it if it exists, skip if it doesn't.
   - `skilleddocs/decisions.md` and `skilleddocs/grills/` if present — earlier decisions the idea must be checked against, cited by `D<k>`.

2. **Grill.** Call the Skill tool with `"grilling"`, giving it the baseline above as context and framing the interview around: does this idea fit the existing plan, conflict with it, or extend it — and what does the user actually want to happen.

3. **Record the outcome** once settled, in whichever of these the repo already has (in this priority order, first match wins):
   - A decisions doc the repo already uses (`docs/decisions.md`, an ADR folder) — append an entry.
   - Otherwise `skilleddocs/decisions.md` — append a row (`| D<k> | date | decision | why | source |`); create it with the register header from the `grill-docs` skill if missing.
   - Always also leave a comment on the relevant issue, or open a new issue if there isn't one yet.

   If a new issue was created, add it to the board too, same as `divide` does for its sub-issues: Projects v2 → `gh project item-add` then `gh project item-edit` to set Status=Todo (IDs per `session-handoff` §3 — `item-add` alone leaves Status empty); label fallback → `status:todo` (create first if missing — see `next` §1). Match whatever the repo already uses. An issue born from a plan discussion still belongs on the board; don't leave it to be picked up by a future backfill.
