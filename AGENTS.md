# AGENTS.md

## Primary Skill

For disk-space triage and safe deletion suggestions, load:

- `.trae/skills/safe-delete-advisor/SKILL.md`

## Start Here

Before doing anything else, read:

- `README.md`
- `.agent/HANDOFF.md`

## Core Rule

This repository suggests what can be deleted to reclaim storage.

It does **not** delete automatically.

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
