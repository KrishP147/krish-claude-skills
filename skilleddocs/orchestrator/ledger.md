# Ledger — skills publish run

Times: America/Toronto (EDT).

### 001 · 2026-09-26 00:12 EDT · decision
- issue/PR: none
- what: scope.md committed; label pseudo-board created; Discussions enabled for giscus; issues #1-#5 filed (site slices #1-#3, CONTRIBUTING #4, portfolio card #5). Research in flight: session mining, ship-readiness audit, Linux install test.
- verified by: not verified: setup only
- decided for you: board = status labels, not Projects v2 → cheaper, `next` supports it; README.md per skill = site page source (submission md) → reuses existing convention instead of a new file

### 002 · 2026-09-26 00:25 EDT · plan
- issue/PR: #1, #4, #5
- what: planner briefed #1 (opus impl, no divide) and #4 (sonnet, no divide); managers launched in worktrees for #1, #4; #5 run via `/pair` in portfolio (first real pair-wrapper use).
- verified by: not verified: in progress
- decided for you: #1 build on Vercel w/ python3 (not committed dist) → no generated files in git; `.gitattributes eol=lf` added w/o renormalize → small diff; template SKILL.md excluded from lint/install (not renamed) → template stays copyable; README heading "How to invoke" kept (matches existing)

### 003 · 2026-09-26 00:40 EDT · decision
- issue/PR: #6-#13, #14, #15, #17-#25
- what: session mining (65 sessions, 396 subagent transcripts) → 8 new-skill issues #6-#13 + fixes #14, #15. Ship audit → launch blockers #17-#25. Linux install test (docker + WSL): all pass; gaps folded into #19. Repo description/topics/homepage set.
- verified by: research reports (local, not committed: contain transcript-derived text)
- decided for you: new skill `status` renamed `sitrep` → `/status` is built in; score-loop kept, hackathon-submit/visual-iterate/paste-answer dropped → low value or overlap; skipped planner for audit-derived issues → bodies already file-level

### 004 · 2026-09-26 00:45 EDT · merge
- issue/PR: #4 / PR #16
- what: CONTRIBUTING (mandatory Pocock video), skill templates, PR/issue templates, lint WARN on missing README sections, templates/ skipped by lint+install.
- verified by: lint OK 15 skills 4 agents; manager ran install to temp dirs (sh + ps1)

### 005 · 2026-09-26 00:50 EDT · implement
- issue/PR: #5 / portfolio PR #1
- what: `/pair` run end-to-end to a PR for the first time (portfolio card). Manager 1 round; orchestrator dropped a committed handoff (portfolio has no skilleddocs) → evidence for #24. Manager handed back twice (duplicate final).
- verified by: npm run build green (manager)
- manual step for user: merge KrishP147/portfolio PR #1 after skills.krishpunjabi.com is live

### 006 · 2026-09-26 01:00 EDT · merge
- issue/PR: #14, #15 / PR #26
- what: Windows-safe worktree teardown (links first); manager spawns implementer blocking, no sleep-poll.
- verified by: lint OK after merging master into branch

### 007 · 2026-09-26 01:05 EDT · verify
- issue/PR: PR #16, PR #26
- what: verifier: claims match git log; #4 #14 #15 closed status:done; filed #27 (lint counts headings in code fences); flagged untracked `.lint-forbidden.txt` risk → orchestrator added it to .git/info/exclude.
- verified by: lint OK on 286c9a5
- decided for you: keep PR #16's committed handoff → repo opts into skilleddocs/; fence bug → issue #27; .gitignore fix → left to #20

### 008 · 2026-09-26 01:15 EDT · merge
- issue/PR: #1 / PR #28
- what: site slice 1 — stdlib build, Claude-Code-style terminal home, locked `/` input, grouped list, placeholder pages, first CI workflow, vercel.json.
- verified by: CI run 36218781515 green; local lint + 9/9 unittest + 8/8 node; desktop screenshot reviewed
- manual step for user: Vercel import repo (build `python3 scripts/build_site.py`, out `site/dist`) + DNS CNAME skills → cname.vercel-dns.com
