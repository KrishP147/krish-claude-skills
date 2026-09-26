---
name: sitrep
description: Give a live, conversational status snapshot of the current session, in 10 lines or fewer — not a document. Triggers: "how's it going", "status update", "what's running", "anything for me", "can I close this". Named `sitrep` because `/status` is a built-in command. Covers what's running (background shells, monitors, background agents), git state (worktrees, dirty/unpushed work), open PRs + CI, an asked-vs-done checklist for this conversation, what needs the user, and a close verdict (SAFE/NOT SAFE, with reasons). Unlike `progress-report` (a ledger-scoped document covering everything since the last report), sitrep answers only "right now" and never writes a report file. Read-only unless the user explicitly says yes to closing something.
---

Read-only reconnaissance skill. Do not create, edit, or write files as part
of answering a sitrep — the one exception is §7, and even there the write
happens through the `handoff-auto` skill, never directly.

## 1. What's running

Check for background work, if the relevant tools are available in this
session — say so and skip silently if not:

- `TaskList` / `TaskGet` / `TaskOutput` (if available): every background
  task, whichever tool started it — a `Bash` or `PowerShell` call with
  `run_in_background`, a `Monitor` loop, or a background `Agent` run. Report
  each one's age (time since started) and its last line of output.
- `ListAgents` (if available): other agents/sessions this one can message —
  note any that look stalled (no output in a long while).
- Background `Agent` completions arrive as task notifications in the
  transcript, not as a tool call — scan recent turns for one you haven't
  surfaced yet.
- None of the above available: reason from the visible transcript instead —
  which `run_in_background` shells or `Agent` calls in this conversation
  haven't returned a result yet — and say the check was transcript-only.

## 2. Git state

- `git worktree list` — every worktree tied to this repo.
- Per worktree/branch: does it have an upstream? (`git rev-parse --abbrev-ref
  --symbolic-full-name @{u}` — errors on no upstream, report "never pushed"
  rather than treating it as clean.) If it has one, `git log @{u}.. --oneline`
  for unpushed commits.
- `git status --porcelain` per worktree for uncommitted changes.

## 3. PRs + CI

`gh pr list --author @me --json number,title,url,isDraft,statusCheckRollup`
(add `--repo` per worktree if more than one repo is in play). Summarize each
PR's checks as passing / failing / pending.

## 4. Asked vs. done

Scan this conversation's user messages and build a short checklist: each
distinct thing asked for, marked done / in progress / not started. This is
about *this session's* asks, not the whole backlog — that's what
`progress-report` is for.

## 5. Needs-you items

Anything only the user can supply or decide: missing keys/credentials,
approvals, manual steps, a question left unanswered earlier in the
conversation. Say "none" if there truly are none — don't invent one.

## 6. Close verdict

**SAFE to close** only if all of:
- Nothing is running (§1 came back empty, or everything has finished).
- No dirty or unpushed work anywhere in §2 — or it's intentional and already
  handed off (a `skilleddocs/HANDOFF.md`/handoff doc exists, is committed,
  and is pushed).
- Anything mid-flight has a handoff written, committed, *and* pushed, so a
  fresh session can pick it up.

Otherwise: **NOT SAFE**, and list the specific reasons (which shell/agent is
still running, which branch is dirty/unpushed, which handoff is missing or
uncommitted).

## 7. On "close" / "yes, stop them"

Never act on this without it being asked. When it is:

1. List exactly what will be stopped (task IDs, agent names) and what, if
   anything, will be committed or pushed — and stop there.
2. Wait for an explicit yes. No response, a vague reply, or anything short
   of a clear yes means: do nothing, repeat the list.
3. On yes: stop each listed background task with `TaskStop` (if available;
   otherwise tell the user which ones need manual stopping and how).
4. Never commit or push anything as part of closing unless the user's yes
   specifically covered that too — closing out background work and shipping
   code are separate confirmations.
5. If anything is mid-flight, call the `handoff-auto` skill to write the
   handoff document (it decides the path under `skilleddocs/handoffs/`).
   Print that path. If nothing is mid-flight, say so instead of writing one.

## 8. Output format

Answer in this shape, 10 lines or fewer, no preamble:

```
Running: 2 background (12m, "tests passing") | 1 agent pending
Git: 3 worktrees, 1 dirty, 1 unpushed (feat/x, 2 commits)
PRs: #12 checks passing | #14 CI failing
Asked -> done: 4/5 (in progress: <what>)
Needs you: <item, or "none">
Verdict: NOT SAFE - stop feat/x's background shell and push first
```

Only include lines that have content; drop a line entirely rather than
padding it with "none" more than once.
