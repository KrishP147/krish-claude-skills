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
- `gitleaks version` — if missing: Windows `winget install --id Gitleaks.Gitleaks -e`; mac/linux `brew install gitleaks` (or GitHub releases). Note the version: v8.19+ uses the `gitleaks git` subcommand; older versions use `gitleaks detect --source`.
- `git filter-repo --version` — if missing: Windows/mac/linux `pip install git-filter-repo`; mac also `brew install git-filter-repo`. **Verify with the version command itself, not pip's exit code** — a `--user` install can land in a Scripts folder that isn't on PATH, in which case the pip install "succeeds" but `git filter-repo` still isn't runnable.

No separate sizing tool is needed — before/after repo size comes from `git count-objects -vH`, which ships with git.

## 2. Confirm target repo

```
gh repo view <owner/repo or current dir> --json name,owner,isPrivate,defaultBranchRef
```

Show this to the user and confirm it's the right repo before touching anything.

## 3. Git LFS check (before scanning)

Check for Git LFS before doing anything else, since a rewrite on an LFS repo isn't safe to attempt in v1:

```
gh api repos/<owner>/<repo>/contents/.gitattributes --jq '.content' | base64 -d | grep -i lfs
```

(Or, once any clone exists: `grep -i lfs .gitattributes`.) A 404 from `gh api` means there is no root `.gitattributes`, so no LFS.

If `.gitattributes` shows Git LFS-tracked paths, **bail with a warning** rather than proceed — `git filter-repo` has no LFS pointer awareness and rewriting an LFS repo blind risks corrupting it. Tell the user this needs manual/LFS-aware handling. Do this before the scan (step 4) — there's no point building a findings report for a repo you already know you can't safely rewrite.

## 4. Full-history scan (throwaway clone #1)

Create a work directory *outside* the clone for scan outputs — this is what gets deleted wholesale at final cleanup (step 14), independent of the clone:

```
mkdir -p <tmp>/scrub-work
git clone <url> <tmp>/scan-clone
cd <tmp>/scan-clone
git count-objects -vH > <tmp>/scrub-work/before-size.txt
gitleaks git . --report-format json --report-path <tmp>/scrub-work/gitleaks-report.json --no-banner
# gitleaks < 8.19: gitleaks detect --source . --log-opts=--all --report-format json --report-path <tmp>/scrub-work/gitleaks-report.json --no-banner
git filter-repo --analyze
```

`gitleaks git` (or `detect` on older installs) exits 1 when it finds something — that's expected, not a tool failure; only treat other exit codes as errors.

`git filter-repo --analyze` writes its findings under `.git/filter-repo/analysis/` inside the clone (`path-all-sizes.txt` and friends) — that part stays put even though the clone itself is throwaway.

Run `scripts/summarize_findings.py` against `gitleaks-report.json` and the `analysis/` directory to produce one merged `findings.json`, written to `<tmp>/scrub-work/findings.json` (**not** inside the clone), with stable IDs: `S1, S2, …` for secrets — deduped by rule + secret value, so the same leaked value across multiple commits/files is one ID, not one per occurrence — and `L1, L2, …` for large blobs, sized by bytes accumulated across every version of that path in history (not a single blob's size). Use the script rather than hand-parsing the analysis files yourself — the size/path tables are easy to misread and getting them wrong means scrubbing (or keeping) the wrong thing. `findings.json` never contains a raw secret value, only a `secret_sha256` fingerprint per secret finding — the value stays recoverable only from `gitleaks-report.json` in `scrub-work`.

**This clone is spent after `--analyze` runs** — `git filter-repo` marks the clone with `.git/filter-repo/already_ran` and refuses a second real run without `--force`. Discard `scan-clone` entirely once `findings.json` is written to `scrub-work`. Do not reuse it for the rewrite in step 9 — use a second, fresh clone there. Keep `gitleaks-report.json` in `scrub-work` until final cleanup (step 14) — the rewrite step needs it to recover secret values by fingerprint.

## 5. Report

Show the user a table built from `findings.json`:

```
ID  | Type   | Path(s)                  | Detail (rule / accum. size, all versions) | Commits
S1  | secret | config/dev.env (+1 more) | AWS Access Key (gitleaks rule)            | 3
L1  | large  | assets/demo.mov          | 340 MB (accum., all versions)             | -
```

Summary line up top, e.g. "3 secrets across 2 files, 2 large blobs totaling 410 MB (accumulated across history, not current working-tree size)."

Don't print raw secret values in this table — fingerprint/rule/paths/lines only. To reveal a specific secret's value on request, look it up by `secret_sha256` in `gitleaks-report.json` (in `scrub-work`) — never print it unprompted.

## 6. Interactive selection

Ask the user which findings to scrub. They can answer per-ID, or in bulk ("all secrets", "everything over 50MB", by path glob). Always echo back the final explicit list of **what will be scrubbed** and **what will be kept** before moving on — never assume "scrub everything" from silence.

## 7. Rotate/revoke every selected secret first (mandatory)

**Before any rewrite step below (step 9 onward)**: history rewrite doesn't un-leak a secret that was ever pushed. Once a secret hits a public or even a shared-private remote, it may already be cached in forks, clones, PR diffs, CI logs, or scrapers — rewriting history removes it going forward, it does not undo the leak. Tell the user every secret finding they're scrubbing (and, honestly, every one they're keeping too, if it was ever actually live) needs to be rotated or revoked at its source before the rewrite is worth anything.

Checklist by type:

- **Cloud provider keys** (AWS/GCP/Azure/etc. access keys): deactivate/delete the key in the provider console or CLI, issue a new one, update every consumer (CI secrets, deploy configs, local `.env` files).
- **API tokens** (GitHub PAT, Stripe, other SaaS vendor tokens): revoke in the issuing service's dashboard, generate a replacement, redistribute to consumers.
- **Private keys / certs** (SSH, TLS, code-signing): revoke/reissue the cert if applicable, generate a new key pair, redeploy to every host or service that trusted the old one.
- **DB passwords / connection strings**: rotate the password at the database, update every service's connection string, bounce affected connections/pools.
- **Webhook URLs** with an embedded secret token (Slack, Discord, CI callbacks): delete/regenerate the webhook in the source app, update whatever posts to it.

**Hard gate**: do not proceed to step 9 until the user confirms rotation is done. The rewrite is cleanup after the fact, not the fix.

## 8. Collaborator + open-PR safety

History rewrite invalidates every existing clone, fork, and open PR against the old history. Before doing anything destructive:

```
gh api repos/{owner}/{repo}/collaborators --jq '.[].login'
gh api repos/{owner}/{repo}/invitations
gh pr list --state open --json number,title,headRefName,author
gh api repos/{owner}/{repo}/forks --jq length
```

If there are collaborators, pending invitations, or open PRs, draft a short notice: what happened, why, and that everyone needs to re-clone from scratch (and which PRs will need to be recreated against the new history). Let the user choose to post it (`gh issue create`, paste it themselves in whatever channel they use) or skip if there's genuinely no one to notify. Forks can't be messaged directly — just surface the count so the user knows they exist.

**Hard gate here**: do not run anything in step 9 onward without explicit confirmation, especially if collaborators/PRs exist.

## 9. Rewrite (throwaway clone #2)

Fresh clone, separate from the one used in step 4:

```
git clone <url> <tmp>/rewrite-clone
cd <tmp>/rewrite-clone
```

For selected secrets, run `scripts/build_replace_text.py` — it re-derives each value from `gitleaks-report.json` by matching the fingerprint stored in `findings.json`, and writes `expressions.txt` for `--replace-text` without ever printing a raw value to stdout or a shell command:

```
python scripts/build_replace_text.py \
  --gitleaks <tmp>/scrub-work/gitleaks-report.json \
  --findings <tmp>/scrub-work/findings.json \
  --ids S1 S3 \
  --out <tmp>/scrub-work/expressions.txt
```

For selected large blobs, ask the user per finding: strip from history entirely, or strip old history but keep the current version working (the latter needs a follow-up commit re-adding the file after the rewrite, since `--path`/`--strip-blobs-bigger-than` removes the blob from **every** version including HEAD's).

Run one combined `git filter-repo` call — don't call it twice on the same clone. Only include the flags for what was actually selected:

```
git filter-repo --replace-text <tmp>/scrub-work/expressions.txt --path <selected-large-file-paths> --invert-paths
```

- No secrets selected: omit `--replace-text <file>` entirely.
- No large paths selected: omit `--path <paths> --invert-paths` entirely.
- (Use `--strip-blobs-bigger-than <size>` instead of/alongside `--path --invert-paths` if the selection is better expressed as a size threshold.)

## 10. Verify before pushing

Still fully reversible at this point — nothing has been pushed:

```
git log --oneline -10
gitleaks git . --no-banner   # confirm selected secrets are gone
# gitleaks < 8.19: gitleaks detect --source . --log-opts=--all --no-banner
git count-objects -vH
```

Spot-check that stripped large files are actually gone from history and sizes look right. Show the user before/after commit count and repo size — before from `<tmp>/scrub-work/before-size.txt` (step 4), after from the `git count-objects -vH` just run. **Confirm gate** before the next step.

## 11. Force-push

`git filter-repo` removes the `origin` remote as a safety measure — re-add it:

```
git remote add origin <url>
git push origin --force --all
git push origin --force --tags
```

Only do this after the collaborator notice from step 8 has actually been sent (or confirmed unnecessary).

## 12. Post-push

```
gh pr list --state open
```

Any PRs still open against the old history need to be closed and recreated. Tell the user which ones.

**Tell the user**: even after a clean force-push, the *old* commits aren't immediately gone from GitHub — they stay reachable via `refs/pull/*` on any PR that referenced them, and by direct SHA or cached diff/blame view, until GitHub Support garbage-collects them (not automatic, no fixed schedule). Rotation (step 7) is what actually protects a leaked secret; the force-push is history hygiene, not a guarantee of removal.

## 13. Visibility flip

```
gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences
```

Before running this, tell the user the consequences `gh` itself warns about: losing stars/watchers (affects repo ranking), existing forks get detached from the network, push rulesets get disabled, and Actions run history/logs become publicly visible. This is a **separate confirmation gate** from step 9/11 — it's a distinct, largely-irreversible visibility event, not just another git operation.

Verify afterward:

```
gh repo view <owner>/<repo> --json isPrivate
```

## 14. Cleanup

Delete the work directory from step 4 — it still holds `gitleaks-report.json`, `findings.json`, and `expressions.txt`, all of which are secret-bearing (the report has raw values; the others reference them):

```
rm -rf <tmp>/scrub-work <tmp>/scan-clone <tmp>/rewrite-clone
```

Run this cleanup too if the workflow stops early (user aborts, LFS bail, a failed gate) — never leave `scrub-work` on disk.

## Scope limits (v1)

Git LFS repos are out of scope — see step 3.
