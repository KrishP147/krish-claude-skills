# consult-plan

*`SKILL.md` is the prompt Claude follows; this file is for you. Loop overview: [`kanban/README.md`](../README.md).*

## What it does

Grills a proposed change, deviation or new idea against the repo's existing plan (open issues, board, roadmap doc), then records the outcome where the repo already keeps decisions.

## When to use

- Pitching a new idea: "does this fit the plan?"
- Automatically, from [`update-progress`](../update-progress/), when a handoff lists deviations or innovations.

## How to invoke

`/consult-plan <the idea, deviation, or innovation>` — model-invocable.

## How it works

1. **Baseline** (whatever exists): `gh issue list --state open`, board state (`gh project item-list` or `status:*` labels), a roadmap doc (`ROADMAP.md`, `docs/roadmap.md`, …).
2. **Grill:** calls [`grilling`](../../grilling/) with that baseline, framed as fit / conflict / extension and what you want to happen.
3. **Record**, first match wins: append to an existing decisions doc (e.g. `docs/decisions.md`); else comment on the relevant issue, or open a new one. A new issue also goes on the board (Projects v2: `item-add` + `item-edit` to Todo; label: `status:todo`, created first if missing). Never invents a decisions-doc convention.

## Related

- Calls [`grilling`](../../grilling/); called by [`update-progress`](../update-progress/).
- Preloaded by the `verifier` agent, which may answer the questions on your behalf when authorized.

## Example

```
/consult-plan add a plugin system instead of hard-coding exporters
```

Reads 12 open issues and `ROADMAP.md`, asks a round of questions (does it replace #31? scope for v1?), you settle it, and it appends an entry to `docs/decisions.md` (or comments on #31 if there's no decisions doc).
