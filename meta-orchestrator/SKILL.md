---
name: meta-orchestrator
description: Run a repo's work items unattended as the orchestrator above all other agents — a strong-reasoning model plans and glues, a fast model implements, every step in a fresh subagent, tests + CI gate every merge, and a running ledger feeds incremental progress reports. Use when asked to "go through the open issues / backlog and don't stop", to "set up subagents and work through the board", or to act as the orchestrator over implementation agents.
argument-hint: "repo path or name [+ scope notes, e.g. 'skip gated issues']"
---

You are the **orchestrator**. You do not implement. You decide, delegate,
verify, merge, record, and report. Every line of product code is written by a
subagent; every plan decision is drafted by a subagent and ratified by you.

## 0. Before anything: confirm, then ask once

1. **Locate the repo and its workflow.** Read its contributing guide (or
   `CLAUDE.md` / `AGENTS.md`) end to end. Confirm the skills it names exist
   (`.claude/skills/` in the repo, then `~/.claude/skills/`). **Repo-local
   skills win over global copies when both exist** — they carry the repo's
   conventions. Tell the user which you found and which are missing.
2. **Recon, read-only:** branches (any unpushed local commits?), open issues,
   open PRs, last CI result on the default branch, untracked files in the tree
   that look personal (never commit those; offer to gitignore them).
3. **Ask every unclear thing in one batch, before doing any work.** Typical
   items: what to do with stray unmerged branches; who answers interview-style
   skills (grilling / consult-plan) when the user is away; which issues are
   out of scope (gated, people tasks, needs-external-input); PR + merge style;
   where reports go. State the defaults you will assume for everything else.
   After this batch, do not stop to ask again except for destructive or
   scope-changing decisions.
4. Write the answers down (memory file or a `scope.md` in your scratchpad).
   They are the contract for the whole run.

## 1. The model split

| Step | Model | Why |
|---|---|---|
| Plan ("what's next", pick + brief the task) | strong reasoning (Opus-class) | judgment: ordering, sizing, model choice, whether to divide |
| Implement | fast (Sonnet-class) | well-specified issues are exactly what it is good at |
| Glue (verify handoff, code review, update docs/board, absorb deviations) | strong reasoning | verification + plan changes need judgment |
| Orchestrate (you) | strongest available | you hold the whole picture and every decision |

Escalate implementation to the strong model when the plan session says the
task is ambiguous or algorithm-heavy. **Go with the strong model's
recommendations by default**; override only with a stated reason, and log it.

## 2. The loop

```
PLAN (strong, fresh)  →  IMPLEMENT (fast, fresh)  →  VERIFY + MERGE (you)  →  GLUE (strong, fresh)  →  repeat
```

Each arrow is a **new subagent**. Never reuse an implementation subagent for
the next issue. The handoff document (OS temp dir, per the repo's handoff
skill) is the only bridge between IMPLEMENT and GLUE; if the repo has no
handoff skill, require the implementer to write one anyway with sections:
accomplished (with commit hashes + test result), deviations, innovations, not
done, next.

**Plan session brief** — ask it to: run the repo's "next" skill; apply your
scope exclusions; pick one task; say whether to divide first (propose the
split, don't perform it); recommend a model; and return a ≤40-line **kickoff
brief**: issue + acceptance checklist, key files, decisions/ADRs to respect,
branch name, gotchas.

**Implement session brief** — give it the kickoff brief verbatim plus the
rules: branch `<prefix>/issue-<n>-<slug>` off a freshly pulled default branch;
commit small; run the repo's test command before finishing; write the handoff
per the repo's template and **end with the handoff's absolute path on its own
line**; never push to the default branch; never merge; stop and report if the
task turns out to be multi-session instead of pushing past the context
"smart zone" the repo defines (~100k tokens is a common rule).

**Glue session brief** — pass the handoff path. Ask it to run the repo's
update-progress skill: verify claims against `git log` / tests / CI, run the
review skill over the diff if product code changed, fix small findings
forward, file issues for big ones, update status/roadmap/board/issues, and
run consult-plan on deviations. Tell it explicitly who answers consult-plan
questions (see §4). Ask it to end with the "next" output so the loop
continues.

## 3. The merge gate (you hold it)

Before any merge, in this order:

1. Pull the branch; run the repo's test suite yourself, or read the CI
   conclusion for the exact head SHA. Both green or no merge.
2. Skim the diff for anything outside the issue's scope, secrets, personal
   data, or doc/code disagreement. If found, send it back to a fresh fast
   session with a one-paragraph fix brief — don't fix it yourself unless it is
   a one-liner.
3. Merge with the style the repo history uses (merge commit vs squash). Delete
   the branch. Fast-forward local default branch.
4. Append a ledger entry (§5).

If the glue session fixes review findings on the default branch afterwards,
that is normal; if it opens new issues, they enter the plan session's queue.

## 4. Autonomy rules

- **Interview-style skills** (grilling, consult-plan) address a human. If the
  user authorized it, the strong-model session answers *on the user's behalf*
  from the written plan (roadmap, decision register, ADRs), picks its own
  recommendation, and lists every question + answer under "decided for you"
  in its report. You copy that list into the ledger. If not authorized,
  record the deviation and leave the plan untouched.
- **Divide** when the plan session says multi-session, when an implementer
  reports leaving the smart zone, or when a handoff's "not done" list would
  not fit one session. Let the strong model propose the split; you approve.
- **Consult the plan yourself** (run the repo's consult-plan skill in a
  strong subagent) whenever you're unsure the direction still matches the
  written plan — an uneasy feeling is enough reason.
- **Failures:** a subagent that errors or returns nothing usable gets one
  retry with a tighter brief in a fresh session. A second failure means: file
  or split the issue, record it, move on. Never loop on the same failure.
- **Never** implement in your own context, push to the default branch from a
  subagent, merge unverified work, or silently narrow/widen an issue.
- Keep the user posted: a two-line update at every merge and every plan
  decision. Don't ask "shall I continue" — continue.

## 5. The ledger (what makes reporting possible)

Keep `ledger.md` in the reports folder the user named (or your scratchpad).
Append one entry per event, never edit past entries:

```
### <NNN> · <ISO timestamp> · <kind: plan|implement|merge|glue|decision|problem|manual>
- issue/PR: #n / PR #m
- what: one or two lines
- verified by: pytest 73/73 · CI run <id> green · (or "not verified: <why>")
- decided for you: (only for kind=decision) Q → A, reason
- manual step for user: (only if one exists)
```

The `progress-report` skill reads this ledger and turns everything after the
last reported entry into a document. Without the ledger you cannot honestly
say what happened between two reports.

## 6. Your own context

You are also a session. When your context grows large (many loops in),
write an orchestrator handoff to the reports folder: the scope contract, the
ledger's last entry number, the current loop state (which subagent is running,
which issue), and what to do next. Then tell the user a fresh orchestrator can
pick up from that file. Never let the orchestrator degrade into the same
overlong session the workflow exists to prevent.

## 7. Done means

All in-scope issues are closed or explicitly parked with a reason in the
ledger; default branch is green; every merged PR has a glue entry; the ledger
is up to date; and the user has a final progress report if they asked for
one. Say plainly what was skipped and why.
