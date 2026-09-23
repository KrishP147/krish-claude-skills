---
name: session-handoff
description: End an implementation session tied to a GitHub kanban board — wraps the base handoff skill and additionally records progress against the issue/card, then moves the card. Use when wrapping up implementation work that started from a GitHub issue.
argument-hint: "issue number or URL this session worked on"
---

1. Produce the base handoff document. Call the Skill tool with `"handoff-auto"`, passing the issue number/argument as the argument text. Take the path it prints as the resulting document before continuing to step 2.

2. Add a `## Board status` section to that document covering: which issue(s)/card(s) this session touched, whether the task is complete / partial / blocked, any deviations from what the issue described, and any innovations or ideas discovered mid-session that aren't in the issue.

3. Move the card to reflect reality. Locate the board the way `next` §1 does.
   - Projects v2: `gh project item-edit --id <item-id> --field-id <status-field-id> --project-id <project-id> --single-select-option-id <option-id>` (look up the IDs via `gh project field-list` / `gh project item-list` first — they're opaque, don't guess them). `gh project item-list` is eventually consistent and can return empty for items genuinely on the board; if so, get the item id via: `gh api graphql -f query='query{repository(owner:"<owner>",name:"<repo>"){issue(number:<n>){projectItems(first:5){nodes{id project{id number}}}}}}'`
   - Label fallback: swap `status:in-progress` for `status:in-review` (complete) or leave as `status:in-progress` (partial/blocked), and add a comment explaining why if blocked.

4. Print the handoff file path, same as the base skill.

A repo's `CLAUDE.md`/`AGENTS.md` may prescribe a filename prefix or required sections for the handoff; follow them.
