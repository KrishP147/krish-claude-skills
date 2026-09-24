---
name: pair
description: Run one task (a GitHub issue number or free text) in an isolated git worktree via a manager subagent that owns its own implementer and retry loop — you stay a single interactive session and only push / open the PR at the end. Use for one task on any repo, including OSS forks with no kanban board, when "implement issue #n with a manager + implementer" or "pair on this" is asked.
argument-hint: "<issue # | task text> [--no-worktree] [--push] [--model opus|sonnet]"
---

You run **one task** through a `manager` subagent. The manager spawns and
reviews an `implementer`; you never implement, and neither agent ever pushes.
You are the only one who touches the remote.

Flags: `--no-worktree` (work in the current checkout on a new branch),
`--push` (push + open the PR without asking), `--model` (implementer model
override; default lets the manager choose, sonnet for mechanical work).

## 1. Resolve the task

- Number → `gh issue view <n>` (title, body, acceptance criteria, labels).
  Text → use as-is; write a 3–6 item acceptance checklist yourself.
- Repo facts: default branch, branch prefix (from the user's `CLAUDE.md`,
  else `feat`), test command, `CONTRIBUTING.md` / `AGENTS.md` path if any.
- **Fork?** (`git remote -v` shows `upstream`): `git fetch upstream`, fast-
  forward the local default branch to `upstream/<default>` before branching,
  and `ls`/`grep` every file or symbol the issue names. Stale trackers cite
  code that has moved or gone; note what's missing in the brief instead of
  letting the implementer chase it.

## 2. Isolate

Default: worktree, so the manager can't disturb your checkout.

```
slug = issue-<n>-<kebab-title>  (or kebab of the task text, ≤6 words)
git worktree add ../_worktrees/<repo>-<slug> -b <prefix>/<slug> <default>
```

`--no-worktree`: `git switch -c <prefix>/<slug> <default>` in place.
If the worktree or branch already exists, reuse it (say so).

## 3. Delegate

One call. Do not `fork` (ignores the model override and cannot nest).

```
Agent(subagent_type="manager", prompt=
  working directory: <absolute worktree path>
  task: <issue #n: title> + body/acceptance checklist
  key files (verified present): …   missing/moved: …
  rules: prefix=<p>, protected=<default>, test cmd=<cmd>,
         commit style=<from CLAUDE.md / CONTRIBUTING>, read <AGENTS.md path>
  implementer model: <--model or "your call">
  max_rounds: 3
  never push, merge, or open a PR — the caller does.)
```

While it runs, do nothing in the worktree.

## 4. On return

0. A report titled **INTERIM** (implementer still running) is not a result.
   Wait for the same manager's next handback; do not push, rerun, or judge
   the branch from an interim report.
1. Show the manager's report verbatim (branch, commits, tests, findings,
   rounds, unfinished).
2. Rerun the tests yourself in the worktree if the report is thin or the
   task touched anything risky. One-line fixes: commit them.
3. **Unfinished** (`skilleddocs/HANDOFF.md` present): say what's left; offer a second
   `pair` round from the handoff, or leave the branch for the user.
4. **Push** if `--push` or the user says go:
   ```
   git -C <worktree> push -u origin <branch>
   gh pr create --head <branch> --title "<issue title>" --body "<summary>\n\nCloses #<n>"
   ```
   Some environments flag the push as destructive for subagents; that's why
   it's yours. Never merge.
5. Review feedback later ("address the PR comments") → step 3 again with the
   comments as the task, same worktree.

## 5. Print

Branch, worktree path, PR URL (or "not pushed"), test result, rounds used,
`skilleddocs/HANDOFF.md` path if any. Then stop; don't offer to clean up the worktree
until the PR is merged (`git worktree remove <path>`).
