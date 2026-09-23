---
name: session-handoff
description: End an implementation session tied to a GitHub kanban board — wraps the base handoff skill and additionally records progress against the issue/card, then moves the card. Use when wrapping up implementation work that started from a GitHub issue.
argument-hint: "issue number or URL this session worked on"
---

1. Produce the base handoff document. **The `handoff` skill has `disable-model-invocation: true` — calling it via the Skill tool is refused every time, not just occasionally.** Ask the user to run `/handoff` themselves (optionally suggesting the argument text to describe what this session did); don't try to replicate its workflow inline instead — that's the same thing the tool's own refusal message says not to do. Once they've run it, locate the resulting document in the OS temp dir before continuing to step 2.

2. Add a `## Board status` section to that document covering: which issue(s)/card(s) this session touched, whether the task is complete / partial / blocked, any deviations from what the issue described, and any innovations or ideas discovered mid-session that aren't in the issue.

3. Move the card to reflect reality:
   - Projects v2: `gh project item-edit --id <item-id> --field-id <status-field-id> --project-id <project-id> --single-select-option-id <option-id>` (look up the IDs via `gh project field-list` / `gh project item-list` first — they're opaque, don't guess them). **`gh project item-list` can return an empty list for items that are genuinely on the board** (verified in testing: stayed empty 2+ minutes after adding items to a freshly created project). If it comes back empty for an item you know is on the board, get its item-id instead via `gh api graphql -f query='query{repository(owner:"<owner>",name:"<repo>"){issue(number:<n>){projectItems(first:5){nodes{id project{id number}}}}}}'` — reliable in testing even when `item-list` wasn't.
   - Label fallback: swap `status:in-progress` for `status:in-review` (complete) or leave as `status:in-progress` (partial/blocked), and add a comment explaining why if blocked.

4. Print the handoff file path, same as the base skill.
