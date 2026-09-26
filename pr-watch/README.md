# pr-watch

*`SKILL.md` is the prompt Claude follows; this file is for you.*

## What it does

Watches your open pull requests (your own repo, or a fork against its upstream) until they merge. It pulls every bot and human review thread (CodeRabbit, Copilot, maintainers), fixes the ones that are actually valid, replies to or resolves the rest, and reports CI — including the fork-specific `action_required` state, which means "needs a maintainer's approval," not "broken."

## When to use

- "Watch my PRs", "check on my open PRs".
- "Address the review comments", "handle the CodeRabbit/Copilot feedback".
- "Drive this PR to merge".
- Not for opening or reviewing PRs from scratch — use [`pair`](../pair/) or a code-review tool for those.

## How to invoke

```
/pr-watch [PR # | owner/repo] [--once]
```

No argument: every open PR authored by you, across repos. `--once` runs a single pass and reports instead of watching.

Model-invocable, so "watch my PRs until they're merged" also works without the slash.

## How it works

1. **List** open PRs (`gh search prs --author @me --state open`, or `gh pr view` for a single one) into a state table: repo, PR #, branch, draft, fork.
2. **Pull review threads** per PR with a GraphQL `reviewThreads` query (paginated), classifying each unresolved one as valid / outdated / disagree / question, citing its thread URL.
3. **Read CI** (`gh pr checks`); a fork PR stuck at `action_required` is reported as waiting on maintainer approval, not as failing.
4. **Fix** the valid threads through [`pair`](../pair/) (one call per PR, every valid thread's path/line/body as the task), which reruns the tests.
5. **GATE** — shows the diff summary and drafted replies and asks before pushing or replying; a force push needs its own fresh yes even if the push itself was already approved.
6. **Push, then reply and resolve**: replies to every thread with the fixing commit's SHA (or, for disagree/question threads, the reasoning); resolves only threads it just fixed or proved outdated by reading the current diff, and only after another explicit yes — never a disagree/question thread, which gets a reply and stays open.
7. **Optional bot re-trigger** (`@coderabbitai review`) only on a fresh yes; notes that bots frequently never run on fork PRs at all.
8. **Watches** (`Monitor` or a bounded poll, never a blind sleep) until merged/closed/stopped, re-reading threads and CI every pass.
9. **Logs** every pass to `skilleddocs/pr-watch/<local-date>-<repo>.md`.
10. **Ends** with one line per PR: merged (link), waiting-on-maintainer (and why), or needs-you (an open gate or a thread only you can answer) — every PR/thread/CI run linked.

## Design principles

- **Outward actions are always gated.** Push, thread reply, thread resolve, and bot re-trigger each need an explicit yes; a force push needs its own, never reused from an earlier approval.
- **Evidence over assertion.** Every claim about a thread or a CI state cites its URL, SHA, or run link — never "should be fine now."
- **Fork PRs are a different shape, not a broken one.** `action_required` CI and silent bots are normal fork behavior, reported as such instead of treated as failures.

## Use cases

- A PR sat open overnight with CodeRabbit comments; run this in the morning to triage and fix the real ones before you look at it yourself.
- A fork PR that never gets picked up by CI bots — confirm it's waiting on a maintainer, not broken.
- Keeping a stack of PRs moving without babysitting each one's review thread by hand.

## Tips

- Run `--once` first on an unfamiliar repo to see the classification before letting it push anything.
- Reviewer threads it can't resolve (no write access, not the PR opener) are left open and reported — that's expected on some forks, not a failure of the skill.
- The log under `skilleddocs/pr-watch/` is the audit trail; read it before re-running if you're not sure what already happened.

## Example

```
/pr-watch 128 --once
```

Reads PR #128, finds three unresolved threads (two valid CodeRabbit nits, one outdated Copilot comment on since-changed code), fixes the two valid ones via `pair`, asks before pushing, pushes, replies to all three with the fixing SHA or the outdated explanation, asks again and resolves the two it fixed plus the outdated one, reports CI green, and logs the pass to `skilleddocs/pr-watch/2026-09-26-myrepo.md`.

## Related

- Calls [`pair`](../pair/) to fix valid review threads.
- [`meta-orchestrator`](../meta-orchestrator/) drives a whole backlog; this drives one PR (or your open set) to merge.

## Prereqs

`gh` authenticated with `repo` scope (write access where you expect to resolve threads); `pair`'s agents installed for the fix step.
