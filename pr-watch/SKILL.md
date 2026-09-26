---
name: pr-watch
description: Watch the user's open pull requests until merged — pulls bot and human review threads (CodeRabbit, Copilot, maintainers), fixes the valid ones via `pair`, replies to or resolves the rest with evidence, and reports CI. Every outward action (push, thread reply, thread resolve, bot re-trigger) is gated on an explicit yes; force-with-lease needs a fresh one. Use when asked to "watch my PRs", "address the review comments", "handle the coderabbit/copilot feedback", "drive this PR to merge", or "check on my open PRs".
argument-hint: "[PR # | repo] [--once]"
---

You watch **open PRs** (own repo or fork→upstream) to merge. You read every
review thread and CI state yourself; you never push, reply, resolve, or
re-trigger a bot without an explicit yes first.

No argument: all of the user's open PRs, across repos. A PR # or `owner/repo`
scopes to one. `--once`: one pass, then report and stop (no watch loop).

## 1. List open PRs

```
gh search prs --author @me --state open --json number,title,url,repository,isDraft,headRefName
```

Scoped run: `gh pr view <n> --repo <owner/repo> --json number,title,url,headRefName,isCrossRepository`.
Build a state table: repo, PR #, title, branch, draft?, fork (`isCrossRepository`)?

## 2. Per PR: pull review threads

Unresolved (and resolved, for the log) review threads via GraphQL — verified
by introspecting the live schema and running this exact query read-only
against a real public PR (`cli/cli#14337`, returned a Copilot review
comment):

```
gh api graphql -f query='
query($owner:String!,$repo:String!,$pr:Int!){
  repository(owner:$owner, name:$repo){
    pullRequest(number:$pr){
      reviewThreads(first:100){
        nodes{
          id
          isResolved
          isOutdated
          path
          line
          comments(first:20){
            nodes{ author{login} body url createdAt }
          }
        }
      }
    }
  }
}' -F owner=<owner> -F repo=<repo> -F pr=<n>
```

Paginate with `reviewThreads(first:100, after:$cursor)` if `pageInfo.hasNextPage`
(add `pageInfo{hasNextPage endCursor}` to the query) — don't silently drop
threads past 100.

Classify each unresolved thread:
- **valid** — a real bug/style issue the bot or reviewer is right about.
- **outdated** — code has since changed; `isOutdated: true` is a strong
  signal, but read the diff yourself before calling it outdated.
- **disagree** — the suggestion is wrong or out of scope for this PR.
- **question** — needs an answer, not a code change.

Cite the thread URL (from the first comment's `url`) for every claim you make
about it.

## 3. CI state

```
gh pr checks <n> --repo <owner/repo> --json name,state,link,workflow
```

Fork PR stuck at `action_required` is **not failing** — it means a
maintainer must approve the workflow run (GitHub docs: this is a genuine
status-check state, distinct from `failure`). Say so explicitly in the
report; don't call it broken.

## 4. Fix the valid threads

One `pair` call per PR (not per thread) with every **valid** thread's path/
line/body as the task text, working in the PR's own branch/worktree. Let
`pair` rerun the repo's tests. Do not fix **disagree** or **question**
threads — those get a reply, not a diff.

## 5. GATE — before any push

Show: diff summary (files, one-line-per-file), commit list, test result.
Ask explicitly before pushing. A force push needs `--force-with-lease` and
its own fresh yes even if push was already approved this session — never
reuse an earlier approval for it.

## 6. Push, reply, resolve

Push only after §5's yes. Then, per thread:

- **Reply** with the commit SHA that addresses it (or, for disagree/question,
  the reasoning/answer):

  ```
  gh api graphql -f query='
  mutation($id:ID!,$body:String!){
    addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId:$id, body:$body}){
      comment{ url }
    }
  }' -F id=<threadId> -F body="Fixed in <sha>: <one line>"
  ```

  (Field confirmed by schema introspection: `AddPullRequestReviewThreadReplyInput`
  takes `pullRequestReviewThreadId` + `body`, not `id`.)

- **GATE**, then **resolve** — only threads you just fixed, or proved
  outdated by reading the current diff. Say which threads and why before
  resolving any:

  ```
  gh api graphql -f query='
  mutation($id:ID!){
    resolveReviewThread(input:{threadId:$id}){
      thread{ isResolved }
    }
  }' -F id=<threadId>
  ```

  Anyone who opened the PR, or has write access to the repo it was opened
  in, can resolve — confirmed from GitHub's docs ("You can resolve a
  conversation in a pull request if you opened the pull request or if you
  have write access to the repository where the pull request was opened").
  On a fork PR you almost always qualify as the opener; don't assume it
  fails without trying, but if it does, say so and leave the thread for a
  maintainer instead of guessing why.

  Never resolve a **disagree** or **question** thread — reply only, and
  leave it open for the reviewer.

## 7. Optional bot re-trigger

Only with a fresh yes:

```
gh pr comment <n> --repo <owner/repo> --body "@coderabbitai review"
```

Fork PRs may never get a bot re-run at all (bots are frequently disabled for
first-time/external contributors) — say so instead of waiting on it forever.

## 8. Watch

Loop until merged/closed or the user says stop:

```
gh pr view <n> --repo <owner/repo> --json state,mergedAt,mergeable
```

Use the Monitor tool or a bounded poll loop, not a blind sleep chain. Re-run
steps 2–3 each pass — new threads or a new CI run can appear between polls.

## 9. Log

Append every pass to `skilleddocs/pr-watch/<local-date>-<repo>.md` (local
date, not UTC — `python -c "import datetime as d; print(d.date.today())"` or
`date +%F`). One entry per pass: timestamp (local zone, named once at the
top), PR #, threads seen/fixed/replied/resolved (with URLs), CI state, gate
decisions and the user's answer to each.

## 10. End

One line per PR: **merged** (link to the merge commit) / **waiting-on-
maintainer** (approval, review, or a bot that won't run — say which) /
**needs-you** (an unresolved gate, a disagree/question thread awaiting the
user's own answer, or a failing check). Link every PR, thread, and CI run
you mention.
