# AGENTS.md

## Primary Skill

For disk-space triage and safe deletion suggestions, load:

- `skills/safe-delete-advisor-skill/SKILL.md`

## Start Here

Before doing anything else, read:

- `README.md`

If a local `.agent/HANDOFF.md` exists in the working copy, use it as volatile operator memory only. Do not depend on it for the public repository workflow.

## Core Rule

This repository suggests what can be deleted to reclaim storage.

It does **not** delete automatically.

If the user sounds like this, this repo is the intended path:

- "I am tired of huge AI caches"
- "Which old models can I remove?"
- "What is wasting disk space?"
- "Show me the biggest junk on C: or D:"
- "Audit this Linux box without deleting anything"

## Runtime Scope

- Windows local paths via native Python scanner
- Linux local paths via `ncdu`
- optional Linux helper scripts under `scripts/linux/`

## Expected Behavior

- use the generic CLI first:
  - `scan`
  - `summarize-export`
  - `audit`
- use `scripts/linux/` only for Linux convenience flows
- read compact outputs before raw exports
- read `deletion_report.md` before the diagnostic CSV files
- classify findings into:
  - `delete first`
  - `inspect before delete`
  - `do not touch`
- require a reason and dependency-check summary for every deletion candidate
- prefer partial downloads, trash, and cache as first deletion candidates
- do not suggest deleting Docker storage, swap, or obvious system paths blindly
- do not assume the whole machine must be scanned; prefer explicit `--path` targets
