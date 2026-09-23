---
name: repo-scrub
description: Scan a GitHub repo's full git history for secrets and large files, let the user pick what to scrub, safely rewrite history, and flip the repo from private to public. Use when making a repo public, open-sourcing a repo, or cleaning git history before publishing.
argument-hint: "[owner/repo] (defaults to current repo)"
disable-model-invocation: true
---

User-invoked only (`/repo-scrub`) because it rewrites history and force-pushes.

Making a GitHub repo public is effectively one-way — once it's public, forks/caches/scrapers can have already copied the history within minutes. GitHub gives no hook to intercept its own visibility toggle, so never rely on it: do all cleanup *before* the repo goes public, then flip visibility yourself via `gh`.

This is a destructive, multi-step workflow. **Never proceed past a numbered gate without the user's explicit go-ahead. Never silently drop a finding from the report — every secret and every large blob found must be shown, even if the user ends up choosing to keep it.**

## 0. Before starting

Confirm with the user which repo this is for if not obvious from context or the `owner/repo` argument. Confirm they understand this will rewrite git history (if they choose to scrub anything) and force-push — not a small operation.

## 1. Prerequisite check

Run each version check; if missing, tell the user the install command and stop until it's installed (don't try to silently work around a missing tool):

- `gh auth status` — should already be authenticated. If not, tell the user to run `gh auth login`.
- `gitleaks version` — if missing: Windows `winget install --id Gitleaks.Gitleaks -e`; mac/linux `brew install gitleaks` (or GitHub releases).
- `git filter-repo --version` — if missing: Windows/mac/linux `pip install git-filter-repo`; mac also `brew install git-filter-repo`. **Verify with the version command itself, not pip's exit code** — a `--user` install can land in a Scripts folder that isn't on PATH, in which case the pip install "succeeds" but `git filter-repo` still isn't runnable.
- `git-sizer --version` — if missing: Windows `winget install --id GitHub.git-sizer -e`; mac/linux `brew install git-sizer` (or GitHub releases).

## 2. Confirm target repo

```
gh repo view <owner/repo or current dir> --json name,owner,isPrivate,defaultBranchRef
```

Show this to the user and confirm it's the right repo before touching anything.

## 3. Full-history scan (throwaway clone #1)

Clone the repo into a fresh temp directory — **never scan the user's actual working clone**:

```
git clone <url> <tmp>/scan-clone
cd <tmp>/scan-clone
gitleaks detect --source . --log-opts=--all --report-format json --report-path gitleaks-report.json --no-banner
git filter-repo --analyze
git-sizer --json > sizer-report.json
```

`gitleaks detect` exits 1 when it finds something — that's expected, not a tool failure; only treat other exit codes as errors.

`git filter-repo --analyze` writes its findings under `.git/filter-repo/analysis/` (`path-all-sizes.txt` and friends).

Run `scripts/summarize_findings.py` against `gitleaks-report.json`, the `analysis/` directory, and `sizer-report.json` to produce one merged `findings.json` with stable IDs: `S1, S2, …` for secrets, `L1, L2, …` for large blobs. Use the script rather than hand-parsing the analysis files yourself — the size/path tables are easy to misread and getting them wrong means scrubbing (or keeping) the wrong thing.

**This clone is spent after `--analyze` runs** — `git filter-repo` marks the clone with `.git/filter-repo/already_ran` and refuses a second real run without `--force`. Discard `scan-clone` entirely once you have `findings.json`. Do not reuse it for the rewrite in step 7 — use a second, fresh clone there.

## 4. Report

Show the user a table built from `findings.json`:

```
ID  | Type   | Path            | Detail                  | Commits affected
S1  | secret | config/dev.env  | AWS Access Key (gitleaks rule) | 3
L1  | large  | assets/demo.mov | 340 MB                  | 1
```

Summary line up top, e.g. "3 secrets across 2 files, 2 large blobs totaling 410 MB."

Don't print raw secret values in this table — file/rule/line only. Only reveal a specific value if the user explicitly asks for that ID by name.

## 5. Interactive selection

Ask the user which findings to scrub. They can answer per-ID, or in bulk ("all secrets", "everything over 50MB", by path glob). Always echo back the final explicit list of **what will be scrubbed** and **what will be kept** before moving on — never assume "scrub everything" from silence.

## 6. Collaborator + open-PR safety

History rewrite invalidates every existing clone, fork, and open PR against the old history. Before doing anything destructive:

```
gh api repos/{owner}/{repo}/collaborators --jq '.[].login'
gh api repos/{owner}/{repo}/invitations
gh pr list --state open --json number,title,headRefName,author
gh api repos/{owner}/{repo}/forks --jq length
```

If there are collaborators, pending invitations, or open PRs, draft a short notice: what happened, why, and that everyone needs to re-clone from scratch (and which PRs will need to be recreated against the new history). Let the user choose to post it (`gh issue create`, paste it themselves in whatever channel they use) or skip if there's genuinely no one to notify. Forks can't be messaged directly — just surface the count so the user knows they exist.

**Hard gate here**: do not run anything in step 7 onward without explicit confirmation, especially if collaborators/PRs exist.

## 7. Rewrite (throwaway clone #2)

Fresh clone, separate from the one used in step 3:

```
git clone <url> <tmp>/rewrite-clone
cd <tmp>/rewrite-clone
```

Run `scripts/build_replace_text.py` with `findings.json` and the user's selected secret IDs — it writes `expressions.txt` for `--replace-text` without ever printing the raw secret values to stdout or into a shell command.

For selected large blobs, ask the user per finding: strip from history entirely, or strip old history but keep the current version working (the latter needs a follow-up commit re-adding the file after the rewrite, since `--path`/`--strip-blobs-bigger-than` removes the blob from **every** version including HEAD's).

Run one combined `git filter-repo` call — don't call it twice on the same clone:

```
git filter-repo --replace-text expressions.txt --path <selected-large-file-paths> --invert-paths
```

(Use `--strip-blobs-bigger-than <size>` instead of/alongside `--path --invert-paths` if the selection is better expressed as a size threshold.)

## 8. Verify before pushing

Still fully reversible at this point — nothing has been pushed:

```
git log --oneline -10
gitleaks detect --source . --log-opts=--all --no-banner   # confirm selected secrets are gone
```

Spot-check that stripped large files are actually gone from history and sizes look right. Show the user before/after commit count and repo size. **Confirm gate** before the next step.

## 9. Force-push

`git filter-repo` removes the `origin` remote as a safety measure — re-add it:

```
git remote add origin <url>
git push origin --force --all
git push origin --force --tags
```

Only do this after the collaborator notice from step 6 has actually been sent (or confirmed unnecessary).

## 10. Post-push

```
gh pr list --state open
```

Any PRs still open against the old history need to be closed and recreated. Tell the user which ones.

## 11. Visibility flip

```
gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences
```

Before running this, tell the user the consequences `gh` itself warns about: losing stars/watchers (affects repo ranking), existing forks get detached from the network, push rulesets get disabled, and Actions run history/logs become publicly visible. This is a **separate confirmation gate** from step 7/9 — it's a distinct, largely-irreversible visibility event, not just another git operation.

Verify afterward:

```
gh repo view <owner>/<repo> --json isPrivate
```

## Scope limits (v1)

If `.gitattributes` shows Git LFS-tracked paths, **bail with a warning** rather than proceed — `git filter-repo` has no LFS pointer awareness and rewriting an LFS repo blind risks corrupting it. Tell the user this needs manual/LFS-aware handling.
