#!/usr/bin/env python3
"""PreToolUse hook (Bash matcher): blocks pushes/merges/deletes that would
touch protected branches or GitHub. Stdlib only, Python 3.8+.

Reads PreToolUse hook JSON from stdin (tool_input.command, cwd). Exits 2 with
a one-line reason on stderr to block; exits 0 to allow. Never raises on
malformed input.

Protected branches: env GUARD_PROTECTED_BRANCHES (comma list), default
"main,master".
"""
import json
import os
import re
import subprocess
import sys


def protected_branches():
    raw = os.environ.get("GUARD_PROTECTED_BRANCHES", "main,master")
    return [b.strip() for b in raw.split(",") if b.strip()]


def split_chain(command):
    """Split a shell command on &&, ||, ; into individual segments.
    Not a full shell parser - good enough for guardrail purposes."""
    parts = re.split(r"&&|\|\||;", command)
    return [p.strip() for p in parts if p.strip()]


def current_branch(cwd):
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def is_git_push(tokens):
    return len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "push"


def push_targets_protected(tokens, protected):
    """Look for an explicit refspec/branch arg in a git push command that
    names a protected branch, e.g. `git push origin main`,
    `git push origin HEAD:main`, `git push origin main:main`."""
    for tok in tokens[2:]:
        if tok.startswith("-"):
            continue
        # refspec forms: <src>:<dst>, or a bare branch name
        dst = tok.split(":")[-1] if ":" in tok else tok
        if dst in protected:
            return True
    return False


def has_push_flag(tokens, flags):
    for tok in tokens:
        if tok in flags:
            return True
        # combined short flags like -fu (rare for push, but be safe)
        if tok.startswith("-") and not tok.startswith("--") and "f" in tok[1:]:
            return True
    return False


def check_segment(segment, cwd, protected):
    """Return a block reason string, or None if the segment is fine."""
    try:
        tokens = segment.split()
    except Exception:
        return None
    if not tokens:
        return None

    # git push variants
    if is_git_push(tokens):
        if has_push_flag(tokens, {"--force", "-f", "--force-with-lease"}):
            return "Blocked: git push with --force/-f/--force-with-lease is not allowed."
        if has_push_flag(tokens, {"--delete", "-d"}):
            return "Blocked: git push --delete is not allowed."
        if "--mirror" in tokens:
            return "Blocked: git push --mirror is not allowed."
        if push_targets_protected(tokens, protected):
            return "Blocked: push to a protected branch (%s) is not allowed." % ",".join(protected)
        # bare `git push` (no explicit branch) while on a protected branch
        non_flag_args = [t for t in tokens[2:] if not t.startswith("-")]
        if not non_flag_args:
            branch = current_branch(cwd)
            if branch and branch in protected:
                return "Blocked: bare git push while on protected branch '%s'." % branch

    # gh pr merge
    if len(tokens) >= 3 and tokens[0] == "gh" and tokens[1] == "pr" and tokens[2] == "merge":
        return "Blocked: gh pr merge is not allowed."

    # gh repo delete
    if len(tokens) >= 3 and tokens[0] == "gh" and tokens[1] == "repo" and tokens[2] == "delete":
        return "Blocked: gh repo delete is not allowed."

    # git branch -D/-d <protected>
    if len(tokens) >= 3 and tokens[0] == "git" and tokens[1] == "branch":
        if any(t in ("-D", "-d", "--delete") for t in tokens[2:]):
            branch_args = [t for t in tokens[2:] if t not in ("-D", "-d", "--delete") and not t.startswith("-")]
            if any(b in protected for b in branch_args):
                return "Blocked: deleting protected branch (%s) is not allowed." % ",".join(protected)

    return None


def main():
    if "--self-test" in sys.argv:
        run_self_test()
        return

    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
        tool_name = data.get("tool_name")
        if tool_name != "Bash":
            sys.exit(0)
        command = (data.get("tool_input") or {}).get("command")
        cwd = data.get("cwd")
        if not command:
            sys.exit(0)
        protected = protected_branches()
        for segment in split_chain(command):
            reason = check_segment(segment, cwd, protected)
            if reason:
                sys.stderr.write(reason + "\n")
                sys.exit(2)
        sys.exit(0)
    except SystemExit:
        raise
    except Exception:
        # Never crash on malformed input.
        sys.exit(0)


def run_self_test():
    protected = ["main", "master"]
    cases = [
        ("git push origin main", True, "explicit protected branch"),
        ("git push origin feature/foo", False, "non-protected branch"),
        ("git push --force origin feature/foo", True, "--force flag"),
        ("git push -f origin feature/foo", True, "-f flag"),
        ("git push origin --force-with-lease feature/foo", True, "--force-with-lease"),
        ("git push origin --delete old-branch", True, "--delete"),
        ("git push --mirror origin", True, "--mirror"),
        ("gh pr merge 123", True, "gh pr merge"),
        ("gh repo delete owner/repo", True, "gh repo delete"),
        ("git branch -D main", True, "delete protected branch"),
        ("git branch -D feature/foo", False, "delete non-protected branch"),
        ("git status && git push origin feature/x", False, "chained safe commands"),
        ("git add -A && git push origin main", True, "chained command hits protected push"),
        ("echo hello", False, "unrelated command"),
        ("git push origin HEAD:main", True, "HEAD:main refspec"),
    ]
    passed = 0
    failed = 0
    for cmd, expect_block, label in cases:
        for seg in split_chain(cmd):
            reason = check_segment(seg, None, protected)
            if reason:
                break
        else:
            reason = None
        blocked = reason is not None
        ok = blocked == expect_block
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print("%s: %-45s expected_block=%s got_block=%s (%s)" % (
            status, cmd, expect_block, blocked, label))
    print("\n%d passed, %d failed" % (passed, failed))
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
