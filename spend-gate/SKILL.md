---
name: spend-gate
description: Gate any billable action (GPU pods/instances, paid APIs, paid tiers, cloud credits) behind a cost estimate, a live balance/credit check, and an explicit yes for that specific action - a standing budget or spend cap is never itself approval. Use before running a known billable CLI or MCP tool call (runpodctl create, vultr-cli instance create, aws ec2 run-instances, gcloud compute instances create, az vm create, modal deploy, a cloud-provider MCP create-*/deploy-* tool) or any other paid API/tier action, and whenever a hooks/spend-guard.py PreToolUse hook blocks one.
---

Never run a billable action on a budget cap, an earlier "go ahead", or a
guess. Every billable action gets its own gate, every time: estimate,
balance, explicit yes, log.

## 1. Classify

Decide whether the action about to run is billable before running it.
Known billable surfaces: cloud GPU/CPU pod or instance creation
(`runpodctl create`, `vultr-cli instance create`, `aws ec2 run-instances`,
`gcloud compute instances create`, `az vm create`), paid deploys
(`modal deploy`), MCP tools whose name matches a provider's `create-*` or
`deploy-*` (e.g. `mcp__*runpod*__create-pod`), and any per-token/per-request
paid API call (LLM APIs, paid SaaS APIs). If it's ambiguous, treat it as
billable and ask rather than assume it's free.

## 2. Estimate (dry run)

Before touching anything billable: unit price x hours (or tokens/requests)
= total estimate. Cite the price source - a URL to the provider's current
pricing page, or the tool's own quote/dry-run output plus the date you read
it (prices drift; don't estimate from memory of a price you can't currently
verify). Use the tool's dry-run or quote path if it has one instead of
hand-computing from a remembered rate card.

## 3. Check live balance/credit

Where the provider exposes a read-only balance/credit/billing call, call it
before asking - never guess remaining budget from a cap mentioned earlier
in the conversation. Only use read-only calls here (list-billing,
get-account, and similar) - never a call that provisions, spends, or
mutates state, even to "just check" something.

## 4. Gate: show the number, wait for yes

Show: what you're about to run, the unit price and its source, the
estimated total, and the live balance if step 3 could read one. Then stop
and wait for an explicit yes to *this* action. A previously-agreed budget,
a spend cap, or "go ahead with the plan" from earlier is not approval for
this specific spend - ask again, every time, for every billable action,
even repeats of something already approved once.

## 5. Log the approval

Once approved and before running the action, append a row to
`skilleddocs/spend.md` (create it with a one-line header if it doesn't
exist yet):

```markdown
| when (local) | amount | purpose | price source | resource id |
|---|---|---|---|---|
| 2026-09-26 14:03 | $0.34 est (0.5h x $0.68/h) | RTX4090 pod, eval run | runpodctl list-gpu-types output, read 2026-09-26 | pod-abc123 |
```

If the resource id isn't known until the action returns one, log the row
with it blank and fill it in right after - don't add a second row for the
same approval.

## 6. Run it, then remind about teardown

Run the approved action. If it created anything that keeps billing while
idle (a pod, an instance, a running endpoint, a reserved volume), tell the
user how to tear it down or set an auto-stop/idle-timeout now, and remind
them again once the task that needed it is finished.

## 7. If a spend-guard hook blocks the action

`hooks/spend-guard.py` (optional, per-repo `PreToolUse` hook) blocks known
billable commands and MCP tool calls before they run. A block from it is
working as intended, not something to route around - if you've already
gated the action through steps 1-5 and gotten an explicit yes, write the
approval token so the hook lets the same action through:

```bash
mkdir -p skilleddocs/spend-approvals
touch skilleddocs/spend-approvals/runpod-pod-2026-09-26   # any filename
```

Any file in that directory is a one-shot approval: the hook deletes the
first one it finds and allows the next matching command, then the approval
is gone. The filename is only a label for your own audit trail - contents
are ignored by the hook, but copying the same amount/purpose you logged in
`spend.md` into the file's contents costs nothing and helps later.

For a single Bash command you can instead prefix it:
`SPEND_GATE_APPROVED=<label> <command>` (covers that one invocation only).
For an MCP tool call use the approval file - `export` in a Bash tool call
does not reach the hook's environment.

Never write an approval file or set `SPEND_GATE_APPROVED` before step 4's
explicit yes has actually happened - the hook only enforces that a token
exists, it can't tell whether you actually asked first.
