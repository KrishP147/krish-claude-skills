---
name: consult-plan
description: Grill a proposed change, deviation, or innovation against a repo's existing plan (open GitHub issues, the kanban board, and any roadmap doc if present), then record the outcome. Invoked automatically by update-progress when a handoff records deviations; invoke directly to pitch a new idea.
argument-hint: "the idea, deviation, or innovation to discuss"
---

1. **Gather the baseline** — don't require any of these, just use whatever exists:
   - `gh issue list --state open` for the current open work.
   - The kanban board's current state (`gh project item-list` or the `status:*` labels).
   - Any roadmap-like doc if present (`ROADMAP.md`, `docs/roadmap.md`, or similar) — read it if it exists, skip if it doesn't.

2. **Grill.** Call the Skill tool with `"grilling"`, giving it the baseline above as context and framing the interview around: does this idea fit the existing plan, conflict with it, or extend it — and what does the user actually want to happen.

3. **Record the outcome** once settled, in whichever of these the repo already has (in this priority order, first match wins):
   - A decisions doc (e.g. `docs/decisions.md`) — append an entry.
   - Otherwise, a comment on the relevant issue, or a new issue if there isn't one yet.

   Don't invent a decisions-doc convention the repo doesn't already have.
