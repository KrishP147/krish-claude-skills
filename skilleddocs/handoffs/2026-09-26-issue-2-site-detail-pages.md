# Handoff: issue #2, site detail pages (2026-09-26)

Branch `krish/issue-2-site-detail-pages` (worktree `../_worktrees/skills-issue-2`), base `8334369`. Not pushed, no PR.
Issue: https://github.com/KrishP147/skills/issues/2. Prev slice: `skilleddocs/handoffs/2026-09-26-issue-1-site-terminal-home.md`.

## Done (commits 3653f04..a9e7bc5)
- `scripts/md_render.py`: stdlib Markdown renderer. Supports headings (unique id slugs), paragraphs, nested lists, fences, inline code, links, bold/italic, tables (wrapped in `.table-wrap`), blockquotes, hr. Escapes all raw HTML. Drops links whose scheme isn't http/https/mailto, including entity-encoded and whitespace-split `javascript:` URLs. Tests: `scripts/test_md_render.py` (24).
- `scripts/site_detail.py`: builds the detail pages. `build_site.py` calls it, and `skills.json` keeps the same public fields because the build-only `_x` data is stripped.
- `site/data/meta.json`: levels + `levels_source` ("usage in the author's sessions, Sep 2026"), level labels, `default_author` Krish, and the `authors` map (grilling/grill-me = Matt Pocock, handoff/handoff-auto = derived from Matt Pocock). Names not listed get level `new`.
- `site/src/detail.html` (rewritten): sticky top bar (`~/skills` + the same locked slash input + dropdown), `> /<name>` echo, header card with chips, sections, Source, prev/next, `<section id="comments">` placeholder, per-page title/description/canonical/og:*. `app.js`: `data-autofocus="false"` turns off autofocus on detail pages. `style.css`: detail and top-bar styles. `pre` and tables scroll inside their own box.
- Tests: `scripts/test_site_detail.py` (13): every page has its description, meta and OG tags; no relative/`.md` hrefs left; exactly 3 `<script>` per page; mapped sections in order, Source last, no empty sections; chips; agent page source; prev/next order; deterministic build; meta authors == THIRD_PARTY_LICENSES.md credits; tolerant heading mapping.
- `site/README.md`: documents the new files and the detail-page rules.

## Decisions made (not spelled out in the issue)
- **Unmatched README sections** render after the mapped ones (after Prereqs) and before Source, under their original heading (class `sec-extra`).
- **Preamble**: the "*... `SKILL.md` is the prompt Claude follows ...*" note line is dropped, which also drops its attribution text. The author chip covers attribution. Any other preamble text goes to the top of "What it does".
- **Agents**: the `- **Label:**` bullets of the `## <name>` section become sections. Role maps to What it does and You pass maps to How to invoke (with a generated `Agent(subagent_type=...)` block). How it works maps as-is. "You get back" and "Guard" become extra sections. All agents share `agents/README.md`'s `## Example`. Related is generated from the preloads plus a "Linked from" list: every page whose README links to that agent's page.
- **Prereqs**: a skill with no Prereqs section inherits its parent group README's section (kanban/* gets `kanban/README.md`'s "Prerequisite: the `project` OAuth scope"). The chip text comes from the text after the heading's colon, otherwise from the section's first line truncated to 48 chars. Only kanban skills show a prereqs chip today, because no skill README has a `## Prereqs` section yet (lint wants one; other lanes are adding them).
- **Design principles**: when a page has this section, it gets a trailing link to the Matt Pocock video, read from CONTRIBUTING.md. No page has the section yet.
- Links to `agents/README.md` without an anchor (e.g. meta-orchestrator's Related) go to GitHub, not to a page. Links to directories use `tree/`, files use `blob/`.
- The author check runs as a unit test (it fails CI on a mismatch), not as a build error.

## Verified
- `python scripts/lint.py && python scripts/build_site.py && python -m unittest discover -s scripts -p "test_*.py" && node --test site/test/filter.test.mjs`: lint OK (15 skills, 4 agents), 46 unittest OK, node 8/8 pass.
- Visual QA with headless Chrome against `python -m http.server -d site/dist 8765` (server stopped afterwards). PNGs are in `C:\Users\User\AppData\Local\Temp\claude\C--Users-User\7653a15d-436c-495d-9d78-f7517d997a8a\scratchpad\site2\` (home-1280, home-390, pair-1280, pair-390, plus planner-*).
- Gotcha: headless Chrome on Windows clamps the window to at least 504px wide, so a plain `--window-size=390,...` renders at 504 and crops the result. The 390 shots load the page in a 390px iframe harness (script `scratchpad/shots.sh`).
- An automated overflow check (iframe harness, `scrollWidth > clientWidth`) at 390px found no horizontal overflow on all 20 pages.
- Chrome `--screenshot` never exits on its own here; `timeout` ends it after 60-70s.

## Not done / manual
- CI has not run on GitHub yet (after push). No new node tests, so `ci.yml` is unchanged.
- The detail page dropdown and keyboard flow were not tested interactively (same `app.js` as home, only the autofocus flag was added).
- Slice 3: wire giscus into `#comments`.

## Next step
Orchestrator: push branch, open PR (`Closes #2`), confirm CI green, merge. When new skills (pr-watch, sitrep, spend-gate) land, add them to `meta.json` levels if they aren't "new".

## Suggested skills
- `update-progress` (verifier) with this doc; `next` for slice 3.

## Board status
- Issue #2 (label board, no Projects card). Status: complete, pending review/merge. Label `status:in-progress` → `status:in-review`.
- Deviations: agent pages built from README label bullets plus generated invoke/related (see Decisions). The author cross-check is a test, not a build failure. The parent-group Prereqs fallback is new.
- Ideas: backlinks ("Linked from") could also go on skill pages; add `## Prereqs` to each skill README so every page gets a prereqs chip; for 390px QA, use the iframe harness instead of `--window-size`.
