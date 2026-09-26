---
name: teammate-brief
description: Write a handoff document for a teammate joining or picking up a project — what it is, verified setup steps, which env vars/keys they need and where to get them (names only, never values), numbered tasks with a "done when" each, who owns what, and what not to touch. Triggers: "brief my teammate", "write an onboarding doc for X", "hand this project to someone", "what does the new person need to know". Different from `handoff` (agent/conversation state) and `sitrep` (live status, no document) — this is for a person joining the work, not an agent resuming it.
argument-hint: "[teammate name or role]"
---

Produces one Markdown document for a human teammate — not an agent, not the
public. Every outward action (commit, push, share) is gated on an explicit
yes.

## 1. Ask up front — one batch

Ask all three together, each with a recommended default, before touching
anything:

1. **Audience** — who's receiving this? A name or role is enough.
   (recommended: whoever the user just named, or "the next person on this")
2. **Role** — what will they own or do here? (recommended: infer from
   context — e.g. "pick up the open issues" — and confirm rather than guess
   silently)
3. **Stack experience** — new to this codebase/stack, or already familiar?
   (recommended: assume new — write more, not less)

Proceed on their answers, or the recommended defaults if they just say "go".
A newcomer default means spelling out steps a familiar teammate would skip;
adjust once you know which one you're writing for.

## 2. What it is, then setup

Open the brief with two or three sentences: what the project does, who uses
it, and its current state (shipping, prototype, paused). Take it from the
README and recent `git log`, not from memory.

Then gather setup steps from whatever the repo actually has: `README*`,
`package.json`/`pyproject.toml`/`Gemfile`/etc. scripts, `Makefile`,
`docker-compose*`, CI config. Next, **run each step yourself, in the current
environment** — install, build, test, start — and only write down what you
watched succeed.

- A step you didn't run (destructive, needs credentials you don't have, too
  slow to run here) goes in the doc marked **"unverified — <reason>"**. Never
  claim a step works without having run it.
- Note the actual result (build passed, tests passed N/M, server started on
  port X) next to each verified step, not just the command.

## 3. Env vars and keys — names only

Build a table of every environment variable / key the project reads (grep
`.env.example`, config loaders, `os.environ`/`process.env` usage, CI
secrets):

```
Variable       | What it's for            | Where to get it
PAYMENTS_KEY   | payment API calls        | payment provider's dashboard, API keys page
DB_URL         | local database connection| <owner from §5>, or .env.example default
```

**Never** put a value in this table, and never open or read an actual
`.env`/secrets file to fill it in — names and sourcing instructions only. If
you can't tell where a key comes from, write "ask <owner from §5>" rather
than guessing.

## 4. Numbered tasks

List the concrete tasks this teammate is picking up, each with a "done
when" that's checkable without asking you:

```
1. Fix the flaky upload test — done when it passes 10x in a row locally.
2. Add pagination to the list endpoint — done when a request with ?page=2
   returns the second page and existing callers still pass.
```

Pull these from open issues/tickets if the repo has them; ask the user for
the rest rather than inventing scope.

## 5. Ownership map

A short table of area/path -> who to ask:

```
Area / path      | Owner
api/payments/     | <name/role>
infra/            | <name/role>
```

"Owner" means who to ask, not necessarily who wrote it. Say "unclear — ask
the user" for anything you can't attribute rather than guessing a name.

## 6. Don't-touch list

Anything the teammate should leave alone, with the reason each:

```
- migrations/ — reviewed and applied by <owner> only, breaks staging if run twice
- vendor/ — generated, never edit by hand
```

Empty is a valid answer — say "nothing off-limits" rather than padding it.

## 7. Draft, then write

Show the full draft (all sections above) before writing anything. On
confirmation, save it to
`skilleddocs/briefs/<name>-<local-date>.md` (local date, not UTC; `<name>` =
the teammate's name or role slug from §1, lowercased and hyphenated).
Create the directory if needed.

Plain language throughout — write for a person reading this once, not an
agent. No skill/tool/session jargon; say "run this command" not "invoke",
"file" not "artifact".

## 8. GATE — commit, push, share

- Commit only on an explicit yes, one commit for the brief.
- Push only on a separate explicit yes, even if the commit was just
  approved.
- Never send, post, or share the document anywhere (chat, email, Slack) —
  this skill only writes the file. Sharing it is the user's call, made
  outside this skill.
