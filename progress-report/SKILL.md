---
name: progress-report
description: Produce a readable, non-verbose progress report (Markdown by default, .docx on request) of what an orchestrated or long-running session has done since the LAST report — never overlapping a previous one — with what worked, what didn't, concerns, decisions made on the user's behalf, and manual steps for the user. Use when the user asks for "an update doc", "what's been done", "make a report", or "write up progress".
argument-hint: "reports folder [+ 'docx' for a Word file instead of Markdown] [+ 'full' to ignore the watermark]"
---

Turn the run's ledger into a document the user can read in two minutes.

## 1. Find the source and the watermark

1. **Reports folder:** the one the user named (ask once if unknown; default
   `./reports/`). All reports and the watermark live there so they survive
   across sessions.
2. **Ledger:** `ledger.md` in that folder, written by the `meta-orchestrator`
   skill (numbered `### NNN · timestamp · kind` entries). If there is no
   ledger, reconstruct one now from `git log`, `gh pr list --state merged`,
   `gh issue list --state all`, and your own conversation — and say in the
   report that it was reconstructed.
3. **Watermark:** `.last-reported` in the folder holds the number of the last
   ledger entry already documented (and the filename of that report). No file
   means this is report #1 and it covers everything.

**The non-overlap rule:** the new report covers ledger entries
`watermark + 1 … latest`, nothing earlier. If report 1 covered entries 1–5 and
the user asks again at entry 22, report 2 covers 6–22, not 1–22. The one
exception: if something *already reported* was later changed (a merged PR
reverted, a decision reversed, a "done" that turned out broken), include it
under **Revisions to earlier reports**, citing the earlier report's number.
Do not re-describe it otherwise. If the user says `full`, ignore the
watermark, cover everything, and title it "Full report".

## 2. Structure (fixed order; drop a section only if truly empty, and say "none")

- **Header:** `Progress report #N · <date> · covers <start time> → <end time>
  (<zone>, ledger NNN–MMM)`; one line naming the repo/branch and the previous
  report. **Timestamps are the user's local time zone**, and the header
  states the zone. Never estimate a time: take it from `date`,
  `git log --date=format-local:'%Y-%m-%d %H:%M'`, or PR `createdAt` /
  `mergedAt` (UTC — convert). A ledger stamped in UTC gets converted too.

  **Detect the zone, don't assume it.** The machine's zone is the user's
  zone unless they say otherwise. Run one of these once and reuse the answer
  for every timestamp in the report and the filename:

  ```
  python -c "import datetime as d; n=d.datetime.now().astimezone(); print(n.tzname(), n.strftime('%z'), n.strftime('%Y-%m-%d %H:%M'))"
  date +'%Z %z %Y-%m-%d %H:%M'                 # POSIX / Git Bash
  (Get-TimeZone).Id; Get-Date -Format 'yyyy-MM-dd HH:mm'   # PowerShell
  ```

  Convert UTC values (`gh ... --json createdAt,mergedAt`, CI logs, `Z`-suffixed
  ISO strings) with `python -c "...fromisoformat(s).astimezone()"` — never by
  subtracting a guessed offset. If the ledger header names a zone, use that.
- **Summary** — 3–6 bullets. What moved, in plain words.
- **Done** — one bullet per issue/PR: `#n <title> — merged PR #m · tests
  <result> · CI green/red`. Link with full GitHub URLs.
- **What worked** — practices or decisions that paid off (short bullets).
- **What didn't** — failures, retries, reverted work, flaky tools. Facts, with
  what was done about each.
- **Concerns** — risks the user should know before trusting the result.
  Rank them. Say which are blocking.
- **Decisions made on your behalf** — every interview question answered by an
  agent instead of the user: `Q → A · reason · where it landed (doc/D-number/
  issue)`. The user must be able to reverse any of these.
- **Manual steps for you** — numbered checklist of things only the user can
  do (sign-offs, credentials, external accounts, people tasks).
- **Revisions to earlier reports** — see §1. "none" if none.
- **Next up** — what the loop will do next, 2–4 bullets.

Style: bullets over prose, one idea per bullet, no filler, no restating the
issue bodies. Numbers go in the Done table, not in sentences. Aim for one to
two pages.

## 2b. Link every reference (all sections, not just Done)

The reader will click. Every issue, PR, commit and decision mentioned anywhere
in the report is a hyperlink, in Markdown and in .docx alike.

1. Resolve the repo URL once: `gh repo view --json url -q .url`, or from
   `git remote get-url origin` (strip `.git`, turn `git@github.com:` into
   `https://github.com/`). If the ledger names a different repo for some
   entries, resolve that one too.
2. Turn references into links with these rules, applied to the whole text of
   every section (header, summary, concerns, decisions, next up — not only
   the Done table):
   - `#123` → `<repo>/issues/123` (GitHub redirects if it is really a PR)
   - `PR #123` / `pull #123` → `<repo>/pull/123`
   - a 7–40 char hex commit hash → `<repo>/commit/<hash>`
   - `D-12`, `ADR-0005`, `Q6`-style decision ids → the repo's decision
     register / ADR file if the repo has one (`docs/decisions.md`,
     `docs/adr/0005-*.md`), otherwise leave as text
   - leave alone anything already inside a link, a code span, or a URL
3. Link text stays short (`#123`, `PR #123`, `a1b2c3d`); the URL carries the
   detail. Do not print bare URLs in prose.
4. Implementation hint: build the document from plain strings and run one
   regex pass (`(?<![\w/])(PR )?#(\d+)\b`, `\b[0-9a-f]{7,40}\b`) that emits a
   link node per match — in Markdown `[#123](url)`, in python-docx a
   `w:hyperlink` run. Apply it in one helper used by every paragraph and
   table cell, so no section can forget.
5. Read the file back and confirm the count of links is at least the count of
   `#n` mentions in the ledger range. Fewer means a section was written
   without the helper.

## 3. Build the document

**Default: Markdown.** Write a plain `.md` file with real headings (`##` per
section), bullet lists, and a Markdown table for **Done** (Issue · Title ·
PR · Tests · CI). Use full GitHub URLs for every issue/PR/commit reference
(Markdown links, not bare `#n`). Filename: `NNN-YYYY-MM-DD-<short-slug>.md`
(zero-padded report number; the **local** date from `date`, not UTC), saved
in the reports folder. Never overwrite an earlier report.

**If the user passed `docx`:** build the .docx exactly as before — use the
`docx` skill if available (docx-js path), otherwise `python-docx`. Heading
styles for sections, real bullet lists (not "-" text), a small table for
**Done**, hyperlinks for every issue/PR/commit reference. Filename:
`NNN-YYYY-MM-DD-<short-slug>.docx`, saved in the reports folder. Never
overwrite an earlier report.

Either way: open the file once after writing (convert to text or read back)
to check nothing is empty or malformed.

## 4. Advance the watermark

Write `.last-reported` with the latest ledger entry number and the new
report's filename. Append a `### NNN · … · report` entry to the ledger noting
the report was produced and which range it covered — so the next report can
start cleanly after it.

Finish with one line: the report's path and the entry range it covers.
