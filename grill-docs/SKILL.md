---
name: grill-docs
description: Grill the user about a plan or decision (same interview as grilling) and leave a paper trail in the repo — the full Q→A transcript under skilleddocs/grills/ and every settled decision appended to skilleddocs/decisions.md — so a later session, agent, or teammate can read what was decided and why. Use when the user says "grill me and document it", "grill with docs", or wants a grilling session recorded.
argument-hint: "the plan, decision, or doc path to grill; optional short slug for the file name"
---

Run the `grilling` interview and write it down as you go. Nothing about the
interview changes: rounds, one recommendation per question, wait for answers.
The difference is that the session leaves files in the repo.

## 1. Where things land

All output goes under `skilleddocs/` at the repo root (see the skills repo
README, "Where skills write"). Create the directory and files lazily.

| What | Path |
|---|---|
| The session transcript | `skilleddocs/grills/<YYYY-MM-DD>-<slug>.md` |
| The decision register | `skilleddocs/decisions.md` (append; create with a header if missing) |

A repo's `AGENTS.md` / `CLAUDE.md` may name a different decisions doc
(`docs/decisions.md`, an ADR folder). If it does, append there instead and
say so in the transcript header.

Slug: the user's argument if they gave one, else 2–4 kebab-case words from
the topic. Date: the user's local date (`date +%F`, or
`python -c "import datetime as d;print(d.date.today())"`), never UTC.

## 2. Start the transcript before the first round

Write the file header immediately so a crashed or abandoned session still
leaves something:

```markdown
# Grill: <topic>

Date: <local date> · Subject: <doc path or one-line description> · Status: in progress

## Rounds
```

## 3. Record each round as it settles

After the user answers a round, append to the transcript, one block per
question:

```markdown
### Q<n> — <question title>
- Asked: <one-line restatement of the question and the options>
- Recommended: <your recommendation, one line>
- Answer: <what the user chose, verbatim where short>
- Why: <the user's reason if given, else "not stated">
```

Do not wait for the end. A round is written before the next round is asked.
Questions the user delegated ("go with your recs for the rest") are recorded
with `Answer: (delegated) <your recommendation>`.

## 4. Register every decision

When a question settles, also append one row to `skilleddocs/decisions.md`:

```markdown
| D<k> | <local date> | <decision, one sentence> | <why, one clause> | grills/<file>#Q<n> |
```

Create the register with this header if it does not exist:

```markdown
# Decisions

Append-only register of decisions made in grilling sessions, consult-plan
reviews, and orchestrator runs. Reverse a decision by adding a new row that
says so; never edit an old row.

| # | Date | Decision | Why | Source |
|---|------|----------|-----|--------|
```

Number `D<k>` continues from the last row in the file. Every answer counts
as a decision, including delegated ones; the register is the thing a
`planner`, `verifier`, or `consult-plan` reads later, so a decision that only
exists in the transcript is invisible to them.

## 5. Close

When the frontier is empty and the user confirms shared understanding:

1. Set the transcript header to `Status: settled` and add a `## Summary`
   section: 3–8 bullets of what was decided, then `## Open` for anything
   deliberately left unresolved (or "none").
2. Print the two file paths on their own lines.
3. Do not commit unless the user asks; say the files are uncommitted.

If the session ends early, set `Status: abandoned at Q<n>` and still print
the paths.
