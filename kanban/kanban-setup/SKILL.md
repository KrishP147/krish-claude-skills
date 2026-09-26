---
name: kanban-setup
description: Set up a GitHub Projects kanban board for a repo and populate it with issues from documented work — current planned work, already-completed work (retroactive backfill), or both. Use when a repo has no GitHub kanban board yet, or its issue history needs backfilling from docs/git history.
argument-hint: "mode: current | retroactive | both (default: current)"
disable-model-invocation: true
---

User-invoked only (`/kanban-setup`) because it creates real GitHub issues.

**This creates real, visible GitHub issues.** Always show the user the full preview list of issues about to be created and wait for confirmation before creating anything — don't create blind, and don't skip items silently.

## 1. Prerequisite

`gh project` commands need the `project` scope. Check `gh auth status`; if `project` isn't listed, tell the user to run `gh auth refresh -s project -s read:project` (interactive, opens a browser) and stop until it's done.

## 2. Board setup (idempotent — skip if it already exists)

```
gh project list --owner <owner> --format json
```

Locate the board the way `next` §1 does (title match `<repo> Board`, then label fallback). An unrelated existing board on the owner's account is not evidence this repo has one — don't treat any non-empty list as "done."

If no title match exists: `gh project create --owner <owner> --title "<repo> Board"`.

**Status field must have an "In Review" option** — `session-handoff` moves cards there. Projects v2's default Status field ships with only Todo/In Progress/Done. Check with `gh project field-list <number> --owner <owner> --format json` (look at the `Status` field's `options`); don't assume.

- Missing "In Review": `gh` has no command to add an option to an *existing* single-select field — `field-create` only makes new fields (verified via `gh project field-create --help`). The only CLI-level fix is the GraphQL mutation `updateProjectV2Field`, which replaces the whole option list, so pass back every existing option (with its `id`, to keep it and anything already set to it) plus the new one (no `id`):
  ```
  gh api graphql -f query='
  mutation {
    updateProjectV2Field(input: {
      fieldId: "<status-field-id>",
      singleSelectOptions: [
        {id: "<todo-id>", name: "Todo", color: GRAY, description: ""},
        {id: "<in-progress-id>", name: "In Progress", color: YELLOW, description: ""},
        {name: "In Review", color: PURPLE, description: ""},
        {id: "<done-id>", name: "Done", color: GREEN, description: ""}
      ]
    }) { projectV2Field { ... on ProjectV2SingleSelectField { id options { id name } } } }
  }'
  ```
  Field and option ids come from the `field-list` call above. If you'd rather not script it, say so plainly and tell the user to add the "In Review" option by hand in the project UI (Status field → edit → add option) — don't claim the CLI did it when it can't.
- Already has it: nothing to do.

If the repo will use label mode instead of (or because Projects v2 isn't available): create the four status labels up front — `gh label create status:todo --color EDEDED --force`, and the same for `status:in-progress`, `status:in-review`, `status:done` with the colors in `next` §1 — so nothing downstream has to discover one is missing.

## 3. Scan the repo for documented work

Look at whatever actually exists — don't require any specific file:
- README sections like "Roadmap" or "TODO"
- `TODO`/`FIXME` code comments
- `CHANGELOG.md`
- a `docs/` folder or any plan-like doc

## 4. Build the candidate list, per mode

- **`current`** (default): items that read as planned/undone. For each, search existing issues first (`gh issue search` / `gh issue list`) to avoid duplicates.
- **`retroactive`**: items that read as already finished (CHANGELOG entries, git log messages describing completed work, resolved TODOs). These get created *and immediately closed* — the point is a clean historical record, not new work.
- **`both`**: run both passes, clearly separated in the preview.

## 5. Preview, then create

Show the full list — title, mode (current/retroactive), and which board column it'll land in — before creating anything. On confirmation, add to the board with `gh project item-add`, then set Status explicitly with `gh project item-edit --id <item-id> --field-id <status-field-id> --project-id <project-id> --single-select-option-id <option-id>` (IDs from `gh project field-list --format json` and item-add's own `--format json`, never guessed — `item-add` alone leaves Status empty, per `session-handoff` §3):
- `current` items → `gh issue create`, `item-add`, `item-edit` to Todo.
- `retroactive` items → `gh issue create`, `gh issue close`, `item-add`, `item-edit` to Done.
