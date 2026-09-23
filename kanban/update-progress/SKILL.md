---
name: update-progress
description: Update a repo's docs and GitHub kanban board from a work-session handoff document. Run in a fresh session after session-handoff, with the handoff doc as input.
argument-hint: "path to handoff doc (auto-finds newest matching file in the OS temp dir if omitted)"
---

1. **Locate the handoff.** Use the path given, or find the newest handoff-looking file in the OS temp dir if none was given.

2. **Verify its claims.** `git log` since the session's start commit, and run the repo's test suite if it has an obvious one (detect from `package.json` scripts, `pytest.ini`/`pyproject.toml`, etc. — don't assume a specific runner exists). Don't take the handoff's word for "tests pass" — check.

3. **Code review, if code changed.** If product code (not just docs) changed, call the Skill tool with `"code-review"` over the session's commits before treating anything as done.

4. **Update docs, if the repo has them.** A roadmap doc gets its checkboxes ticked; a status doc gets its component rows and dated "what changed" entry; a decisions doc gets a row only if the handoff records a decision. Otherwise: Check for a README "Status"/"Progress" section, a `CHANGELOG.md`, or a `docs/` folder — update whatever actually exists. Don't invent doc structure the repo doesn't have.

5. **Update the board.** Comment on the relevant issue(s) with a summary. If complete and verified, close the issue and move its card to Done. If incomplete, leave it open and set the card/label to reflect where it actually stands.

6. **Escalate deviations.** If the handoff's `## Board status` section lists deviations or innovations, automatically call the Skill tool with `"consult-plan"` to reconcile them before finishing.

7. **Hand off the loop.** End by calling (or telling the user to call) the `next` skill.
