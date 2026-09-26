# sitrep

*`SKILL.md` is the prompt Claude follows; this file is for you.*

## What it does

Answers "how's it going" in **10 lines or fewer**: what's running right now,
git state (worktrees, dirty/unpushed work), open PRs and their CI, an
asked-vs-done checklist for this conversation, anything that needs you, and
a verdict on whether it's safe to close the session. It's a live, spoken
answer, not a document.

## When to use

- "How's it going", "status update", "what's running", "anything for me",
  "can I close this".
- Named `sitrep` rather than `/status` because `/status` is already a
  built-in Claude Code command.
- Not for a written record of a long run — that's
  [`progress-report`](../progress-report/), which is scoped to everything
  since the last report and produces a file. `sitrep` never writes a report
  and only answers for right now.

## How to invoke

```
/sitrep
```

Model-invocable, so any of the trigger phrases above work without typing the
slash command.

## How it works

1. **What's running.** If the tools are available in this session: lists
   background tasks (`Bash`/`PowerShell` with `run_in_background`, `Monitor`
   loops, background `Agent` runs) via `TaskList`/`TaskGet`/`TaskOutput`,
   with age and last output line; checks `ListAgents` for other addressable
   agents; scans recent turns for background-agent task notifications not
   yet surfaced. Tools not available → says so and reasons from the visible
   transcript instead.
2. **Git.** `git worktree list`; per worktree, whether it has an upstream
   and, if so, unpushed commits (`git log @{u}..`); `git status --porcelain`
   for dirty trees.
3. **PRs + CI.** `gh pr list --author @me` with checks status.
4. **Asked vs. done.** A short checklist built from this conversation's user
   messages — not the whole backlog.
5. **Needs-you items.** Missing keys/approvals/manual steps/unanswered
   questions, or "none".
6. **Verdict.** SAFE to close only if nothing's running, nothing's
   dirty/unpushed (or it's intentional and already handed off), and any
   mid-flight work has a handoff written, committed, and pushed. Otherwise
   NOT SAFE, with the specific reasons.
7. **On "close" / "yes, stop them":** lists exactly what will be stopped and
   what (if anything) would be committed/pushed, and waits for an explicit
   yes before doing either. On yes, stops background tasks with `TaskStop`
   (if available); calls `handoff-auto` to write the handoff if anything was
   mid-flight, and prints its path.

Reads: background-task tools (if available), `git`, `gh`, this conversation.
Writes: nothing, except a handoff document via `handoff-auto` when closing
mid-flight work, saved under `skilleddocs/handoffs/`.

## Design principles

- **Live and conversational, not a document.** `progress-report` already
  covers the ledger-scoped, written case; `sitrep` fills the gap of "just
  tell me, right now, in chat."
- **Read-only by default.** Reconnaissance only reads state; the one path
  that changes anything (stopping background work, writing a handoff) is
  gated behind an explicit yes.
- **Short on purpose.** A status check that takes longer to read than the
  work itself defeats the point — hence the 10-line cap and "drop empty
  lines rather than padding them."

## Use cases

- Mid-session, checking whether a background agent or long shell command has
  finished.
- Before stepping away, to see whether anything is unpushed or uncommitted
  across several worktrees.
- Before closing a session or terminal, to get a SAFE/NOT SAFE verdict
  instead of guessing.
- After a flurry of asks, to see which ones are still outstanding.

## Tips

- If background-task tools (`TaskList`, `ListAgents`, etc.) aren't enabled in
  your session, `sitrep` still works — it just reasons from the transcript
  and says so, so you know the check is weaker than usual.
- "Can I close this?" and "close this" are different asks: the former is a
  read-only verdict (§6); only the latter (or an explicit "yes, stop them")
  triggers the gated stop-and-handoff flow in §7.
- Ask again after fixing a NOT SAFE reason — it's cheap and re-checks
  everything, not just the item you fixed.

## Example

```
/sitrep
```

```
Running: 1 background (8m, "3 tests failing") | 0 agents pending
Git: 2 worktrees, 1 dirty, 1 unpushed (fix/date-parse, 3 commits)
PRs: #21 checks passing
Asked -> done: 3/4 (in progress: fixing date parser)
Needs you: none
Verdict: NOT SAFE - background test run still failing, fix/date-parse unpushed
```

## Related

- [`progress-report`](../progress-report/) — the written, ledger-scoped
  counterpart; use it for "what's been done" over a whole run, not "right
  now".
- [`handoff-auto`](../handoff-auto/) — writes the handoff document `sitrep`
  points at when it closes mid-flight work.
- [`session-handoff`](../kanban/session-handoff/) — same handoff, plus board
  bookkeeping, for a full end-of-session wrap-up rather than a quick check.

## Prereqs

`gh` for the PR/CI check. Background-task tools (`TaskList`, `TaskOutput`,
`ListAgents`, `TaskStop`, `Monitor`) are optional — used when available,
skipped with a note otherwise.
