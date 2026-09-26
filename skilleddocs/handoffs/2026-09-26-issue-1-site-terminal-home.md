# Handoff: issue #1, site terminal home (2026-09-26)

Branch `krish/issue-1-site-terminal-home` (worktree `../_worktrees/skills-site-terminal-home`), base `ee7ba8d`. Not pushed, no PR.
Issue: https://github.com/KrishP147/skills/issues/1. Scope: `skilleddocs/orchestrator/scope.md`.

## Done (commits 7ea5f51..f8052a9)
- `scripts/build_site.py`: stdlib, reuses `lint.py` discovery/frontmatter. Writes `site/dist/` (wiped each run, deterministic): `index.html` with server-rendered grouped list + count line, `skills.json`, `<name>/index.html` placeholder per skill/agent, `404.html`, static css/js.
- `site/src/`: `index.html`, `detail.html`, `404.html` templates; `style.css`; `filter.js` (pure lock/filter/complete/resolve, browser global + CommonJS); `app.js` (DOM wiring, hidden 16px input, beforeinput + input rollback, combobox/listbox/aria-live).
- Tests: `scripts/test_build_site.py` (9 unittest), `site/test/filter.test.mjs` (8 node:test).
- `.github/workflows/ci.yml` (lint, build, unittest, node test), root `vercel.json`, `site/README.md` (build/preview/deploy manual steps + fallback), `.gitignore` += `site/dist/`, `.gitattributes` (no renormalize).

## Verified
- `python scripts/lint.py && python scripts/build_site.py && python -m unittest discover -s scripts -p "test_*.py"` → OK: 15 skills, 4 agents; 9 tests OK.
- `node --test site/test/filter.test.mjs` → 8 pass. (Node 22 on Windows rejects a directory arg; pass the file.)
- Headless Chrome over CDP against `python -m http.server -d site/dist`: `x` ignored, `/pa` → menu `[/pair]`, `/pa`+`x` rejected, Backspace, Esc, Tab `/gr`→`/grill`, second Tab leaves the input (no trap), simulated IME `input` of `/paz` rolled back, Enter on `/pa` → `/pair/` placeholder, 19 no-JS links, no horizontal overflow at 390px.

## Not done / manual
- Vercel import + DNS for skills.krishpunjabi.com: user steps in `site/README.md`.
- CI not yet run on GitHub (runs after push).
- Real-device mobile keyboard test not done (emulated only).

## Next step
Orchestrator: push branch, open PR, confirm CI green, merge. Slice 2 (detail pages) builds on `detail.html` + `skills.json.readme`.

## Suggested skills
- `update-progress` (verifier) with this doc; `next` for slice 2.

## Board status
- Issue #1 (label board). Status: complete, pending review/merge. Label moved `status:in-progress` → `status:in-review`.
- Deviations: vercel config at repo root (`vercel.json`) instead of `site/vercel.json`, since the build reads files outside `site/`; fallback documented. Added `404.html` and `--out DIR` flag to build (used by tests).
- Ideas: dropdown sorts exact match first; global `/` key anywhere on page focuses the terminal; list descriptions clamped to 2 lines (full text stays in the DOM and `skills.json`).
