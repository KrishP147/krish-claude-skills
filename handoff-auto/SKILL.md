---
name: handoff-auto
description: Model-invocable variant of handoff — writes the handoff document without waiting for the user to type /handoff. Use from other skills or subagents that must end a session unattended.
argument-hint: "What will the next session be used for?"
---

Derived from Matt Pocock's `handoff` skill (MIT, see THIRD_PARTY_LICENSES.md); only the frontmatter differs.

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

Finish by printing the handoff file's absolute path on its own line as the very last line of output — orchestrators parse it.
