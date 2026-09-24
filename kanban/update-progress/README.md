# update-progress

*`SKILL.md` is the prompt Claude follows; this file is for you. Loop overview: [`kanban/README.md`](../README.md).*

## What it does

Takes a handoff document, **verifies** its claims (git log, tests, code review), then updates the repo's docs, the board and the issue to match what actually happened.

## When to use

In a fresh session after [`session-handoff`](../session-handoff/). The `verifier` agent runs it end to end.

## How to invoke

`/update-progress [path to handoff doc]` — omit the path to use the newest handoff-looking file in the OS temp dir. Model-invocable.

## How it works

1. **Locate the handoff** (given path, or newest in temp dir).
2. **Verify claims:** `git log` since the session start; runs the repo's test suite if one is detectable. Doesn't trust "tests pass".
3. **Code review** via the `code-review` skill if product code changed.
4. **Update docs that exist:** roadmap checkboxes, status doc rows + dated entry, decisions doc (only if a decision was recorded), else README status section / `CHANGELOG.md` / `docs/`. Moves a "current phase" marker to where merges are landing; fixes README feature lists that miss merged capabilities. Never invents doc structure.
5. **Update the board:** comments on the issue; closes it and moves the card to Done if complete and verified, otherwise sets the card/label to where it stands.
6. **Escalate deviations:** if the handoff's `## Board status` lists deviations/innovations, calls [`consult-plan`](../consult-plan/).
7. Ends by calling (or telling you to call) [`next`](../next/).

## Related

- Input from [`session-handoff`](../session-handoff/); calls `code-review`, [`consult-plan`](../consult-plan/), [`next`](../next/).
- Preloaded by the `verifier` agent (which can skip step 3 with `review-done=yes`).

## Example

```
/update-progress
```

Finds the latest handoff for #31, sees 3 commits, runs `npm test` (green), reviews the diff, ticks #31 in `ROADMAP.md`, comments on #31 and moves it to Done, runs `consult-plan` on the "streaming writer" deviation, then shows `next`.
