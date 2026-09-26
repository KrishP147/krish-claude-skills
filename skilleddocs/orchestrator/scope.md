# Orchestrator scope — skills repo publish run

- repo: C:\Users\User\source\repos\claude-skills (github KrishP147/skills, public)
- default branch: master
- branch prefix: krish/
- queue: label pseudo-board (`status:todo` / `status:in-progress` / `status:in-review` / `status:done`), oldest first unless `priority:high`
- execution: pair (manager per issue; worktrees under ../_worktrees/skills-<slug>)
- handoff_budget: 10
- merge style: branch + PR, merge commit; orchestrator pushes + merges after `python scripts/lint.py` (+ site build/tests once site/ exists) green
- interview authorization: yes — verifier answers consult-plan/grilling on user's behalf from this scope + README; every Q→A logged as "decided for you"
- reports folder: skilleddocs/reports/
- time zone: America/Toronto (Eastern)

## Goal
Make the repo publishable: audit ship-readiness, test untested pieces, add skills mined from the user's own sessions, CONTRIBUTING, skills site, launch post draft.

## Decisions (user, 2026-09-26)
- Site: `site/` in this repo, static, generated from repo skill/agent files at build; Vercel free tier at skills.krishpunjabi.com (Vercel import + DNS = user's manual step); portfolio (KrishP147/portfolio) gets a project card via PR, left for user to merge.
- Site design: Claude-Code-style terminal replica. Input locked: only `/` accepted first, then only characters that keep the buffer a prefix of a real skill/agent name; list of all skills with one-line descriptions below; Enter on a full name → `/<name>` detail page (usage, design principles, use cases, tips, worked example); comments at bottom.
- Comments: giscus (GitHub Discussions). Enabling Discussions: orchestrator; installing giscus app: user manual step.
- CONTRIBUTING mandates watching https://www.youtube.com/watch?v=v4F1gFy-hqg ; submissions = skill dir + a use-cases/description md per a template.
- License: MIT (existing).
- New skills: mined from user's past sessions, generic + user-facing only (lint forbids project names); no private data in repo.

## Exclusions
- Never post to Twitter/X; draft only.
- Never spend money; no paid tiers.
- Never merge the portfolio PR.
- Never commit personal data from transcripts.
