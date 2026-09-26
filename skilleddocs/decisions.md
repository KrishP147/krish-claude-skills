# Decisions register

| ID | Date | Decision | Why | Source |
|---|---|---|---|---|
| D1 | 2026-09-26 | Site: `vercel.json` at repo root, not `site/` | build reads skill files outside `site/`; root-dir-scoped Vercel project can't see them | verifier, on user's behalf (#1, PR #28) |
| D2 | 2026-09-26 | Site: Enter opens highlighted (first) match, not only on exact full name | scope says Claude-Code-style replica; Claude Code's slash menu behaves this way; exact match still sorts first | verifier, on user's behalf (#1, PR #28) |
| D3 | 2026-09-26 | Site: keep extras (404.html, `--out` flag, `/` focuses terminal, 2-line description clamp) | small, no deps, serve the static-site goal | verifier, on user's behalf (#1, PR #28) |
| D4 | 2026-09-26 | spend-guard: inline-prefix approval covering a compound command is accepted | hook is a documented tripwire, not a security boundary; spend-gate skill's explicit yes is the real gate | verifier, on user's behalf (#8, PR #31) |
| D5 | 2026-09-26 | guard-git hook matcher is `Bash\|PowerShell`, not just `Bash` | PowerShell tool otherwise bypasses the guard; scope deviation accepted | verifier, on user's behalf (#17, PR #34) |
| D6 | 2026-09-26 | guard-git stays conservative: blocks `gh api .../pulls/N/merge` even as GET, expands quoted braces; allows `echo git push ...` unless piped to a shell | false positives are cheap for a guardrail, false negatives are not | verifier, on user's behalf (#17, PR #34) |
| D7 | 2026-09-26 | Don't rewrite history to remove the old forbidden word from past `scripts/lint.py` commits | project codename in a blocklist, no secret; rewrite + force-push would break every branch/PR on a public repo; user can still run repo-scrub before launch | verifier, on user's behalf (#19/#20, PR #37) |
| D8 | 2026-09-26 | Site detail pages: unmatched README sections render after Prereqs; README "SKILL.md is the prompt" line dropped; agent pages built from agents/README.md with generated invoke block; kanban skills inherit kanban/README.md prereqs | keeps pages uniform, avoids duplicate credit line; no per-agent README exists | verifier, on user's behalf (#2, PR #40) |
| D9 | 2026-09-26 | Status labels get fixed colors (`gh label create --force --color`) | `--force` without `--color` re-randomizes color every run | verifier, on user's behalf (#23, PR #36) |
