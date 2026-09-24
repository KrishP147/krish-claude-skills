# grilling

*By Matt Pocock (MIT), included verbatim. `SKILL.md` is the prompt Claude follows; this file is for you.*

## What it does

Interviews you, one round at a time, until a plan or decision has no unexamined branches left. Every question comes with Claude's recommended answer, so you can just say "yes" to most.

## When to use

- You have a plan, design or decision and want it stress-tested before acting.
- You say "grill me", "grill this plan", "poke holes in this".
- Other skills call it: `consult-plan` uses it to test an idea against a repo's plan.

## How to invoke

- `/grilling <the plan or idea>`, or just ask to be grilled; Claude auto-invokes it (model-invocable).
- `/grill-me` is a user-only alias.

## How it works

1. Maps the topic as a **design tree**: each decision branches into the decisions that depend on it.
2. Asks the whole **frontier** (every question answerable now, with prerequisites settled) in one numbered round: `❓ Q1 …` then `➡️ recommended answer`.
3. Waits for your answers, recomputes the frontier, asks the next round. Questions that depend on an open question wait for a later round.
4. Looks up facts itself (dispatching a sub-agent for filesystem/tool lookups) instead of asking you; only decisions go to you.
5. Ends when the frontier is empty, and does nothing with the result until you confirm shared understanding.

Reads/writes no files by itself.

## Related

- [`grill-me`](../grill-me/) — alias.
- [`consult-plan`](../kanban/consult-plan/) — calls this with the repo's plan as context.
- `verifier` agent — may answer its questions on your behalf when authorized (see [`agents/README.md`](../agents/README.md)).

## Example

```
/grilling move auth from sessions to JWTs
```

Round 1 asks ~4 numbered questions (token lifetime, refresh strategy, revocation, migration of live sessions), each with a recommendation. You answer; round 2 follows up on revocation storage because you chose short-lived tokens. Stops when nothing is left open.
