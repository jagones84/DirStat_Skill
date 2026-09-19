# AGENTS.md

## Primary Skill

For disk-space triage and safe deletion suggestions, load:

- `.trae/skills/safe-delete-advisor-skill/SKILL.md`

## Start Here

Before doing anything else, read:

- `README.md`

If a local `.agent/HANDOFF.md` exists in the working copy, use it as volatile operator memory only. Do not depend on it for the public repository workflow.

## Core Rule

This repository suggests what can be deleted to reclaim storage.

It does **not** delete automatically.

If the user sounds like this:

- "I am tired of huge AI caches"
- "Which old models can I remove?"
- "What is wasting disk space?"

then this repo and skill are the intended path.

## Runtime Scope

- primary target: DGX/Linux
- primary scan engine: `ncdu`
- primary workflow scripts: `scripts/dgx/`

## Expected Behavior

- use repo scripts instead of inventing ad hoc shell flows
- read compact outputs before raw exports
- classify findings into:
  - `delete first`
  - `inspect before delete`
  - `do not touch`
- prefer partial downloads, trash, and cache as first deletion candidates
- do not suggest deleting Docker storage, swap, or obvious system paths blindly
