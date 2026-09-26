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
