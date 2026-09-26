# Decisions register

| ID | Date | Decision | Why | Source |
|---|---|---|---|---|
| D1 | 2026-09-26 | Site: `vercel.json` at repo root, not `site/` | build reads skill files outside `site/`; root-dir-scoped Vercel project can't see them | verifier, on user's behalf (#1, PR #28) |
| D2 | 2026-09-26 | Site: Enter opens highlighted (first) match, not only on exact full name | scope says Claude-Code-style replica; Claude Code's slash menu behaves this way; exact match still sorts first | verifier, on user's behalf (#1, PR #28) |
| D3 | 2026-09-26 | Site: keep extras (404.html, `--out` flag, `/` focuses terminal, 2-line description clamp) | small, no deps, serve the static-site goal | verifier, on user's behalf (#1, PR #28) |
| D4 | 2026-09-26 | spend-guard: inline-prefix approval covering a compound command is accepted | hook is a documented tripwire, not a security boundary; spend-gate skill's explicit yes is the real gate | verifier, on user's behalf (#8, PR #31) |
