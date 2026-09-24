# grill-me

*By Matt Pocock (MIT), included verbatim. `SKILL.md` is the prompt Claude follows; this file is for you.*

## What it does

Short alias for [`grilling`](../grilling/): a relentless interview to sharpen a plan or design.

## When to use

When you want to type something short to start a grilling session.

## How to invoke

`/grill-me <plan or idea>`. User-invoked only (`disable-model-invocation: true`): Claude never picks it on its own; it auto-invokes `grilling` instead.

## How it works

1. Calls the Skill tool with `grilling`.
2. Everything else is `grilling` — see its [README](../grilling/README.md).

## Related

[`grilling`](../grilling/).

## Example

`/grill-me my plan to split the monolith into three services` → identical to `/grilling …`.
