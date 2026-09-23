# kanban

General-purpose versions of a roadmap-driven workflow I originally built for one specific project (`praxic`), rebuilt to run against **GitHub Issues + a GitHub Projects (v2) board** instead of that project's own `docs/roadmap.md` / `docs/STATUS.md` / `docs/decisions.md` files — so it works on any repo, not just that one.

## Prerequisite: the `project` OAuth scope

These skills use `gh project ...` commands, which need scopes your `gh` token may not have by default:

```bash
gh auth refresh -s project -s read:project
```

Each skill checks for this and tells you if it's missing, but it's a one-time interactive step (opens a browser), so do it up front.

## The loop

```
next  →  (you implement, in a fresh session)  →  session-handoff  →  update-progress
 ↑                                                                          │
 └──────────────────── (prints "run next" when done) ───────────────────────┘
```

- **[`next`](next/)** — what to work on, pulled from the board.
- **[`session-handoff`](session-handoff/)** — run when you're wrapping up an implementation session.
- **[`update-progress`](update-progress/)** — run in a fresh session afterward: verifies the handoff's claims, updates docs + the board + the issue.
- **[`consult-plan`](consult-plan/)** — grill a new idea or a deviation against the existing plan before it goes in. `update-progress` calls this automatically if the handoff mentions deviations/innovations; call it directly to pitch something new.
- **[`divide`](divide/)** — split a task that's too big into session-sized issues.
- **[`kanban-setup`](kanban-setup/)** — bootstrap: creates the board if a repo doesn't have one yet, and can backfill issues from whatever's already documented in the repo (`mode=current` for open/planned work, `mode=retroactive` for already-done work, `mode=both`).

If a repo has no board yet, start with `kanban-setup`.
