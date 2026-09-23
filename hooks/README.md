# hooks/ — optional per-repo hooks

Not installed by `install-skills`; copy what you want into a repo's
`.claude/hooks/` and wire it in that repo's `.claude/settings.json`.
(The agents' own `guard-git.py` lives in [`../agents/hooks/`](../agents/hooks/)
and *is* installed, into `~/.claude/agents/hooks/`.)

## `smartzone.py` — "your context has left the smart zone" warning

`UserPromptSubmit` hook. Prints a one-line warning into the conversation when
the session transcript passes ~1.5 MB (a rough proxy for ~100k tokens), so
both you and Claude see it and can wrap up: `/divide` the rest, then
`/session-handoff` (or, for an orchestrator, the §6 handoff cycle in
`meta-orchestrator`). Heuristic only; `/context` is the precise check.

Install into a repo:

```bash
mkdir -p .claude/hooks
cp <skills repo>/hooks/smartzone.py .claude/hooks/
```

`.claude/settings.json` (merge into an existing `hooks` block if there is one):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/smartzone.py\" || exit 0"
          }
        ]
      }
    ]
  }
}
```

Claude Code asks you to approve the hook once per repo. Tune `THRESHOLD_MB`
at the top of the script if your prompts are unusually large or small.
Global instead of per-repo: put the same block in `~/.claude/settings.json`
with an absolute path to the script.
