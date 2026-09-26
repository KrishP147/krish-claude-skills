---
name: repo-showcase
description: Make a repo public-facing — rewrite its README around outcome and demo, prune stale/internal docs, fix claims the code has outdated, scan for secrets and private names, propose GitHub metadata, then hand off to `/repo-scrub` for the history scan and visibility flip. Never changes repo visibility itself. Use when asked to "make this repo public-facing", "showcase this repo", "polish the README for public", "get this ready to open-source", or "prep this repo for a portfolio/public link".
argument-hint: "[owner/repo] (defaults to current repo)"
---

You get a repo ready to be seen, on its working tree only. History and
visibility are `/repo-scrub`'s job, not yours — never run `gh repo edit
--visibility` and never rewrite git history from here. Every outward action
(secret redaction, README rewrite, metadata change, commit, push) is gated on
an explicit yes.

## 1. Ask up front — one batch

Ask all three together, each with a recommended default, before touching
anything:

1. **Outcome** — what should a stranger do after reading this? (recommended:
   "try it in under 5 minutes")
2. **Audience** — who's landing here? (recommended: other developers
   evaluating whether to use or contribute)
3. **What to emphasize** — the one thing that makes this worth a look
   (recommended: whatever the most-recently-merged feature or the README's
   current headline claim already emphasizes, confirmed rather than
   invented).

Proceed on their answers, or the recommended defaults if they just say "go".

## 2. Inventory docs

List every doc in the repo (`README*`, `docs/**`, `CONTRIBUTING*`, stray
`NOTES.md`/`TODO.md`/`*.txt`, etc). Build a table:

```
Path              | Verdict | Reason
docs/old-plan.md  | delete  | superseded by docs/architecture.md, last touched 2024
docs/setup.md     | merge   | quickstart already covers this, fold the one extra step in
docs/api.md       | keep    | still accurate, useful reference
```

Show the table. **Nothing gets deleted or merged without an explicit yes** —
per-row or "all deletes", but always echoed back before acting.

## 3. Grep claims against reality

Claims rot faster than docs get updated. For every factual claim in the
README and kept docs (supported languages, install steps, commands, badges,
"currently in beta", version numbers, architecture descriptions), check it
against the actual code, config files, and `git log` — not against what the
doc says about itself. Report contradictions as `file:line` for the claim
plus `file:line` (or commit) for the contradicting evidence, e.g.:

```
README.md:12 claims "Python 3.8+" — pyproject.toml:3 sets requires-python = ">=3.11"
README.md:40 says "no tests yet" — tests/ has 40 files, last commit 3 weeks ago
```

Don't silently fix these yet — they feed the README rewrite in §4 and get
shown in the diff gate (§7).

## 4. Rewrite the README — lean by default

Default to short; add a section only if this repo actually needs it. In
order:

1. **One-line pitch** — what it is, in a sentence a stranger understands.
2. **Result** — what using it produces, before the how.
3. **Demo media slot(s)** — a placeholder the user fills in themselves, e.g.
   `<!-- screenshot: paste path/URL here -->` or `<!-- demo GIF/video: paste
   path/URL here -->`. Never fabricate a screenshot, GIF, or video, and never
   invent metrics/testimonials to fill the gap.
4. **Quickstart** — the fewest steps from clone to the result in §2, verified
   against §3's findings rather than copied from the stale doc.
5. **Architecture** — only if the audience from §1 needs it to evaluate or
   contribute; a diagram slot is fine, same placeholder convention as §3.
6. **Credits** — authors, prior art, license.

Draft the full replacement text before the gate in §7; don't touch the file
yet.

## 5. Scan for secrets and private names

Working tree only (history is `/repo-scrub`'s job):

- Secrets: grep for common patterns (API keys, tokens, connection strings,
  `.env` files not gitignored) across tracked files.
- Private people's names: emails and full names in docs/comments/config that
  aren't repo authors (`git shortlog -sne`) or already public in the
  license/credits — e.g. a teammate's name left in a code comment or a test
  fixture.

Report every hit as `file:line`. Redact only on an explicit yes, per-item or
"redact all".

## 6. GitHub metadata proposal

Propose a repo description, topics, and homepage URL from what §1–§4
established. Show the exact command before running it:

```
gh repo edit <owner/repo> --description "<one-line pitch>" --add-topic <topic> --homepage <url>
```

Apply only on explicit yes. Skip entirely if the user doesn't want it touched.

## 7. GATE — diff, commit, push

Show a diff summary (files touched, one line each) covering the README
rewrite, any doc deletes/merges from §2, and any redactions from §5.

- Commit only on yes, one logical change per commit (e.g. `docs: rewrite
  README for public release`, `chore: prune stale docs`, `chore: redact
  private name in <file>`), on a branch — never straight to the default
  branch.
- Push only on a separate yes, even if the commit was just approved.

## 8. Hand off to /repo-scrub

Once the working tree is public-ready and pushed (or the user says to move
on regardless), tell them the next step is `/repo-scrub` for the full git
history scan and the actual private → public flip. State plainly: this skill
never changes visibility and never rewrites history — that's `/repo-scrub`'s
job, on purpose, so the destructive step stays a separate, explicit decision.

## 9. Write the report

Save the doc inventory (§2), contradicted-claims list (§3), and secret/name
findings (§5) — plus what was actually done about each — to
`skilleddocs/showcase/<local-date>.md` (local date, not UTC). This is the
paper trail `/repo-scrub` and any teammate can read afterward.
