"""UserPromptSubmit hook: warn when the session transcript suggests the
context has left the smart zone (~100-120k tokens).

Heuristic only — transcript bytes are a rough proxy for context tokens, and
/context remains the precise check. Stdout from this hook is injected into
the conversation, so both the user and Claude see the warning and can act
(/divide remaining work, then /session-handoff)."""

import json
import os
import sys

THRESHOLD_MB = 1.5  # rough proxy for ~100k tokens of live context


def main() -> None:
    data = json.load(sys.stdin)
    path = data.get("transcript_path") or ""
    if not path or not os.path.exists(path):
        return
    mb = os.path.getsize(path) / 1_000_000
    if mb >= THRESHOLD_MB:
        print(
            f"[smart-zone] Session transcript is ~{mb:.1f} MB - context has likely "
            "left the smart zone (~100-120k tokens; this is a heuristic, verify "
            "with /context). Wrap up: run /divide on the remaining work, then "
            "/session-handoff, and continue in a fresh session."
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a broken heuristic must never break the session
