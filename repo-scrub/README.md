# repo-scrub

*`SKILL.md` is the prompt Claude follows; this file is for you.*

## What it does

Scans a GitHub repo's **full git history** for secrets and oversized files, lets you choose exactly what to scrub, rewrites history safely in a throwaway clone, force-pushes, and only then flips the repo private → public. Every step with side effects has an explicit confirmation gate.

## When to use

- Making a private repo public / open-sourcing it.
- Cleaning secrets or huge blobs out of history before publishing.

## How to invoke

```
/repo-scrub [owner/repo]
```

Defaults to the current repo. User-invoked only (`disable-model-invocation: true`) because it rewrites history and force-pushes.

Prereqs: `gh` (authenticated), [`gitleaks`](https://github.com/gitleaks/gitleaks), [`git-filter-repo`](https://github.com/newren/git-filter-repo), [`git-sizer`](https://github.com/github/git-sizer). Install commands are in the [top README](../README.md#install).

## How it works

0. Confirms the target repo and that you accept a history rewrite + force-push.
1. **Prereq check** — version-checks each tool; stops with the install command if one is missing.
2. **Confirm target** — `gh repo view … --json name,owner,isPrivate,defaultBranchRef`.
3. **Scan (throwaway clone #1)** — `gitleaks detect` over all history, `git filter-repo --analyze`, `git-sizer --json`. [`scripts/summarize_findings.py`](scripts/summarize_findings.py) merges them into `findings.json` with IDs `S1…` (secrets) and `L1…` (large blobs). The clone is then discarded.
4. **Report** — table of every finding (no raw secret values) + summary line.
5. **Select** — you pick per ID or in bulk; Claude echoes back scrub vs keep lists.
6. **Collaborator / open-PR safety** — lists collaborators, invitations, open PRs, fork count; drafts a re-clone notice. Hard gate.
7. **Rewrite (fresh clone #2)** — [`scripts/build_replace_text.py`](scripts/build_replace_text.py) writes `expressions.txt` without echoing secrets; one `git filter-repo --replace-text … --path … --invert-paths` call. For large files you choose: strip entirely, or strip history and re-add the current version.
8. **Verify** — re-run gitleaks, spot-check sizes, before/after counts. Confirm gate.
9. **Force-push** — re-adds `origin`, `push --force --all` and `--tags`.
10. **Post-push** — lists PRs that must be recreated.
11. **Visibility flip** — `gh repo edit --visibility public …` after a separate gate explaining the consequences; verifies `isPrivate`.

Bails out on Git LFS repos. Never scans or rewrites your working clone.

## Related

Standalone; no other skills or agents.

## Example

```
/repo-scrub myorg/tool
```

Finds `S1` (an API key in `config/dev.env`, 3 commits) and `L1` (a 340 MB demo video). You scrub both; Claude warns about 1 open PR, you approve, it rewrites clone #2, verifies gitleaks is clean, force-pushes, lists the PR to recreate, then asks separately before making the repo public.
