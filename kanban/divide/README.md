# divide

*`SKILL.md` is the prompt Claude follows; this file is for you. Loop overview: [`kanban/README.md`](../README.md).*

## What it does

Splits an issue (or a described task) that's too big for one session into two or more session-sized issues, links them from the parent, and puts them on the board.

## When to use

- A task is clearly multi-session.
- Context is running low mid-task and the rest must be split off (the `smartzone.py` hook suggests this).
- The `planner` agent uses it to *propose* splits (it never creates them).

## How to invoke

`/divide <issue number or task description>` — model-invocable.

## How it works

1. Reads the target (`gh issue view <n>` or your description).
2. Proposes 2+ pieces (or uses your split) and **shows it before creating anything**.
3. On confirmation: `gh issue create` per piece ("Part of #n"), and adds a task-list checkbox per child to the parent's body.
4. Adds each child to the board: Projects v2 → `gh project item-add` then `gh project item-edit` to set Status=Todo (`item-add` alone leaves Status empty); label fallback → `status:todo` (created first if missing).
5. If a roadmap doc links the parent, adds `#n → #a, #b` inline and commits `docs: divide #n into #a/#b`.
6. If the parent is now only a tracker, says so and offers to close it once children land.

## Related

- Preloaded by the `planner` agent (proposal only).
- [`consult-plan`](../consult-plan/) adds its new issues to the board the same way.

## Example

```
/divide 28
```

Proposes "#28a auth token model", "#28b migrate sessions", "#28c remove old middleware"; you confirm; creates #40–#42, turns #28 into a tracking checklist, adds them to Todo.
