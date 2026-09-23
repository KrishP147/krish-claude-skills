---
name: divide
description: Split a GitHub issue (or a described task) into two or more session-sized issues, and update the kanban board. Use when a task is too big for one session, or context is running low and remaining work needs to be split off.
argument-hint: "issue number or description of the task to divide"
---

1. Read the target: `gh issue view <n>` if given a number, or take the user's description directly.

2. Propose a split into 2+ session-sized pieces (or use the split the user specifies). Show the proposed breakdown before creating anything.

3. On confirmation, create the sub-issues:
   ```
   gh issue create --title "<piece>" --body "Part of #<n>. <details>"
   ```
   Add a task-list checkbox for each new issue to the parent issue's body, so the parent becomes a tracking issue.

4. Add each new issue to the kanban board's Todo column (`gh project item-add`) or `status:todo` label, matching whatever the repo already uses.

5. If the parent issue is now purely a tracker (no remaining standalone work), say so and offer to relabel/close it once all children land.
