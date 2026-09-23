#!/usr/bin/env python3
"""Build a git-filter-repo --replace-text expressions file from findings.json
and a list of user-selected secret IDs.

Reads the raw secret values straight out of findings.json and writes them to
expressions.txt - the values never pass through stdout, a shell argument, or
the calling conversation.

Usage:
    python build_replace_text.py --findings findings.json --ids S1 S3 --out expressions.txt
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--findings", type=Path, required=True)
    ap.add_argument("--ids", nargs="+", required=True, help="Finding IDs to redact, e.g. S1 S3")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--replacement", default="REDACTED")
    args = ap.parse_args()

    findings = json.loads(args.findings.read_text(encoding="utf-8"))

    lines = []
    skipped = []
    for fid in args.ids:
        entry = findings.get(fid)
        if entry is None:
            skipped.append((fid, "not found in findings.json"))
            continue
        if entry.get("type") != "secret":
            skipped.append((fid, "not a secret finding - large-file removal uses --path, not --replace-text"))
            continue
        value = entry.get("_secret_value", "")
        if not value:
            skipped.append((fid, "no captured value - gitleaks report may be missing the Secret field"))
            continue
        lines.append(f"literal:{value}==>{args.replacement}")

    args.out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    print(f"Wrote {len(lines)} replacement rule(s) to {args.out}")
    if skipped:
        print("Skipped:")
        for fid, reason in skipped:
            print(f"  {fid}: {reason}")

    return 0 if lines else 1


if __name__ == "__main__":
    sys.exit(main())
