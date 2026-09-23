#!/usr/bin/env python3
"""Merge gitleaks JSON + git-filter-repo --analyze output + git-sizer JSON
into one findings list with stable IDs (S1, S2... secrets / L1, L2... large blobs).

Usage:
    python summarize_findings.py \
        --gitleaks gitleaks-report.json \
        --analysis-dir .git/filter-repo/analysis \
        --sizer sizer-report.json \
        --out findings.json \
        [--large-threshold-bytes 1000000]

Writes findings.json and prints a human-readable table to stdout.
Never prints raw secret values - only rule name, file, and line.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def load_gitleaks(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    findings = []
    for entry in raw:
        findings.append(
            {
                "type": "secret",
                "path": entry.get("File", "unknown"),
                "rule": entry.get("RuleID", "unknown-rule"),
                "line": entry.get("StartLine"),
                "commits": [entry.get("Commit")] if entry.get("Commit") else [],
                # kept out of the table on purpose - only surfaced if the
                # user explicitly asks for this finding's ID by name.
                "_secret_value": entry.get("Secret", ""),
            }
        )
    return findings


def load_filter_repo_analysis(analysis_dir: Path, threshold_bytes: int) -> list[dict]:
    """Parse path-all-sizes.txt (or path-all-sizes-and-checkouts.txt) from
    `git filter-repo --analyze` output. Format is whitespace-columned; the
    exact column set has shifted across filter-repo versions, so this looks
    for a size-like integer column and a trailing path column defensively.
    """
    candidates = [
        analysis_dir / "path-all-sizes.txt",
        analysis_dir / "path-all-sizes-and-checkouts.txt",
    ]
    report = next((c for c in candidates if c.exists()), None)
    if report is None:
        return []

    findings = []
    size_re = re.compile(r"^\s*([\d,]+)\s+([\d,]+)\s+(.+)$")
    with report.open(encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[1:]:  # skip header row
        m = size_re.match(line)
        if not m:
            continue
        max_size = int(m.group(1).replace(",", ""))
        path = m.group(3).strip()
        if max_size >= threshold_bytes:
            findings.append(
                {
                    "type": "large",
                    "path": path,
                    "size_bytes": max_size,
                    "commits": [],
                }
            )
    return findings


def load_sizer_overview(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.0f}TB"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gitleaks", type=Path, required=True)
    ap.add_argument("--analysis-dir", type=Path, required=True)
    ap.add_argument("--sizer", type=Path, required=False)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--large-threshold-bytes", type=int, default=1_000_000)
    args = ap.parse_args()

    secrets = load_gitleaks(args.gitleaks)
    large = load_filter_repo_analysis(args.analysis_dir, args.large_threshold_bytes)
    sizer = load_sizer_overview(args.sizer) if args.sizer else {}

    findings = {}
    for i, s in enumerate(secrets, start=1):
        findings[f"S{i}"] = s
    for i, entry in enumerate(large, start=1):
        findings[f"L{i}"] = entry

    args.out.write_text(json.dumps(findings, indent=2), encoding="utf-8")

    # human-readable table - never print _secret_value here
    print(f"{'ID':<5}{'Type':<8}{'Path':<40}{'Detail':<30}Commits")
    for fid, entry in findings.items():
        if entry["type"] == "secret":
            detail = entry["rule"]
        else:
            detail = human_size(entry["size_bytes"])
        commits = len(entry.get("commits", []))
        path = entry["path"][:38]
        print(f"{fid:<5}{entry['type']:<8}{path:<40}{detail:<30}{commits}")

    n_secrets = len(secrets)
    n_large = len(large)
    total_large_bytes = sum(e["size_bytes"] for e in large)
    print(
        f"\n{n_secrets} secret(s), {n_large} large blob(s) "
        f"totaling {human_size(total_large_bytes)}."
    )
    if sizer:
        print("git-sizer overview available in", args.sizer)

    return 0


if __name__ == "__main__":
    sys.exit(main())
