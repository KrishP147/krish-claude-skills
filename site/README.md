# site

Static site for this repo's skills and agents: a Claude Code style terminal
home with a locked slash input, plus a plain list of every skill and agent.
No framework, no npm install, no runtime deps.

## Layout

| Path | What |
|---|---|
| `src/index.html` | home template (`{{COUNT}}`, `{{LIST}}`, `{{DATA}}` filled at build) |
| `src/detail.html` | per-skill placeholder page template |
| `src/404.html`, `src/style.css` | not-found page, all styles |
| `src/filter.js` | pure slash-input logic (browser global `SkillFilter`, CommonJS in node) |
| `src/app.js` | DOM wiring: events, dropdown, navigation |
| `test/filter.test.mjs` | node:test suite for `filter.js` |
| `dist/` | build output, git-ignored |

Build script: [`../scripts/build_site.py`](../scripts/build_site.py) (stdlib
only). It reuses `scripts/lint.py`'s discovery, so the site lists exactly what
lint counts. Groups: top-level skill dirs = core, `kanban/*` = kanban,
`agents/*.md` (minus README) = agents.

Never add a file named `SKILL.md` under `site/`: lint globs `*/SKILL.md` and
`*/*/SKILL.md` and would treat it as a skill.

## Build, test, preview

```sh
python scripts/lint.py
python scripts/build_site.py              # wipes + writes site/dist/
python -m unittest discover -s scripts -p "test_*.py"
node --test site/test/filter.test.mjs
python -m http.server -d site/dist 8000   # http://localhost:8000
```

Output: `index.html`, `skills.json` (name, description, summary, group,
source, readme), `<name>/index.html` per skill/agent (so `/pair` resolves
statically), `404.html`, `style.css`, `filter.js`, `app.js`. The build is
deterministic.

## Deploy (Vercel free tier) — manual steps

Config lives in the repo-root [`vercel.json`](../vercel.json)
(`buildCommand: python3 scripts/build_site.py`, `outputDirectory: site/dist`,
`cleanUrls`). It is at the root because the build needs files outside `site/`.

1. vercel.com → Add New → Project → import `KrishP147/skills`.
2. Leave **Root Directory** as the repo root (`./`). Framework preset: Other.
   Build/output settings come from `vercel.json`; don't override them.
3. Deploy. Check `/`, `/pair`, and a bad path (404 page).
4. Domain: Project → Settings → Domains → add `skills.krishpunjabi.com`.
   At the DNS provider for `krishpunjabi.com` add a `CNAME` record
   `skills` → `cname.vercel-dns.com` (use whatever target Vercel shows).
   Wait for Vercel to mark it valid (HTTPS is automatic).

Fallback, if Root Directory must be `site/`: move the config to
`site/vercel.json` with `"buildCommand": "python3 ../scripts/build_site.py"`
and `"outputDirectory": "dist"`, and keep "Include source files outside of
the Root Directory" enabled (Vercel's default) so `scripts/` and the skill
dirs are available at build time.
