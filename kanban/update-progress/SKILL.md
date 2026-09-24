---
name: update-progress
description: Update a repo's docs and GitHub kanban board from a work-session handoff document. Run in a fresh session after session-handoff, with the handoff doc as input.
argument-hint: "path to handoff doc (auto-finds newest matching file in the OS temp dir if omitted)"
---

1. **Locate the handoff.** Use the path given; else the newest file in the repo's `skilleddocs/handoffs/`; else the newest handoff-looking file in the OS temp dir.

2. **Verify its claims.** `git log` since the session's start commit, and run the repo's test suite if it has an obvious one (detect from `package.json` scripts, `pytest.ini`/`pyproject.toml`, etc. — don't assume a specific runner exists). Don't take the handoff's word for "tests pass" — check.

3. **Code review, if code changed.** If product code (not just docs) changed, call the Skill tool with `"code-review"` over the session's commits before treating anything as done.

4. **Update docs, if the repo has them.** A roadmap doc gets its checkboxes ticked; a status doc gets its component rows and dated "what changed" entry; a decisions doc (`skilleddocs/decisions.md`, or `docs/decisions.md` / an ADR folder if the repo uses one) gets a row only if the handoff records a decision. Otherwise: Check for a README "Status"/"Progress" section, a `CHANGELOG.md`, or a `docs/` folder — update whatever actually exists. Don't invent doc structure the repo doesn't have.
   A roadmap/README **"current phase" marker follows where merges are landing, not where the last checkbox is.** If this session's merges belong to a later phase than the marker, move it and mark the earlier phase "done except gated (#…)" listing its open gated/parked items — a phase with gated leftovers never "finishes", so waiting for that leaves the marker stale for months. Status summaries and README feature lists must name every capability merged in the current phase; a merged feature the README doesn't mention is docs drift, fix it here.

5. **Update the board, if there is one.** Locate it the way `next` §1 does; a repo whose queue is a roadmap doc has no card to move — skip the card step, keep the issue comment/close. Comment on the relevant issue(s) with a summary. If complete and verified, close the issue and move its card to Done. If incomplete, leave it open and set the card/label to reflect where it actually stands.
   - Projects v2: move the card with `gh project item-edit` exactly as `session-handoff` §3 does (look up the IDs first; don't guess them).
   - Label fallback: complete and verified → swap `status:in-review` for `status:done` (or `status:in-progress` for `status:done` if the card was never moved to review); partial/blocked → leave the label as is.

6. **Escalate deviations.** If the handoff's `## Board status` section lists deviations or innovations, automatically call the Skill tool with `"consult-plan"` to reconcile them before finishing.

7. **Hand off the loop.** End by calling (or telling the user to call) the `next` skill.
