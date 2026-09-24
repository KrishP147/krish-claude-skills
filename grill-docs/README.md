# grill-docs

*Original. Wraps Matt Pocock's `grilling` (MIT). `SKILL.md` is the prompt Claude follows; this file is for you.*

## What it does

Runs the `grilling` interview on a plan or decision and leaves a paper trail in the repo: the full question → recommendation → answer transcript, and one row per settled decision in an append-only register. Everything else about the interview is unchanged.

## When to use

- You want a grilling session that a teammate, a later session, or an orchestrator can read.
- A plan doc exists and its open questions need settling on the record.
- Before running `meta-orchestrator`, so its planner and verifier can cite decision ids.

## How to invoke

`/grill-docs <plan, decision, or doc path> [slug]`, or "grill me on X and document it". Model-invocable.

## How it works

1. Creates `skilleddocs/grills/<YYYY-MM-DD>-<slug>.md` with a header (`Status: in progress`) before the first round.
2. Asks rounds exactly as `grilling` does (numbered questions, one recommendation each, then waits).
3. After each answered round, appends a `### Q<n>` block (asked / recommended / answer / why) to the transcript, and one `| D<k> | date | decision | why | source |` row to `skilleddocs/decisions.md` (created with a header if missing). Delegated answers ("go with your recs") are recorded as `(delegated)`.
4. When the frontier is empty and you confirm: sets `Status: settled`, adds `## Summary` and `## Open`, prints both paths. Nothing is committed unless you ask.

Writes: `skilleddocs/grills/<date>-<slug>.md`, `skilleddocs/decisions.md`. Honours an `AGENTS.md` / `CLAUDE.md` override naming a different decisions doc.

## Related

- [`grilling`](../grilling/) — the interview itself, no files.
- [`consult-plan`](../kanban/consult-plan/) — grills a *deviation* against the existing plan and appends to the same register.
- [`meta-orchestrator`](../meta-orchestrator/) — reads the register and transcripts as the design record.

## Example

```
/grill-docs docs/backend-extension-plan.md backend-plan
```

Produces `skilleddocs/grills/2026-09-23-backend-plan.md` with 14 Q→A blocks and appends D1–D14 to `skilleddocs/decisions.md`.
