# safe-delete-advisor

Tired of wasting tens of GB on forgotten AI models, bloated caches, and files you have not touched since the Cold War? Here is the safe, read-only answer.

## Goal

This repository provides a reproducible workflow to:

- scan disk usage on a DGX/Linux host using a system-installed scanner
- compact the raw scan into AI-friendly summaries
- classify large paths by deletion risk
- produce a shortlist for human review before any cleanup

Version `v1` targets DGX/Linux ARM and uses `ncdu` as the initial scan engine.

## Skill Identity

This repository is also packaged as an agent skill.

- skill name: `safe-delete-advisor`
- skill path: `.trae/skills/safe-delete-advisor/SKILL.md`
- agent entrypoint: `AGENTS.md`

The repository, package, and skill now use the same public-facing name: `safe-delete-advisor`.

## Non-Goals

- shipping `ncdu` binaries inside the repository
- automatic deletion in the first version
- broad cross-platform support in the first version
- feeding the complete filesystem dump directly to an LLM

## Architecture

The repository is split into replaceable modules:

- `scan engine`: invokes a system tool such as `ncdu`
- `normalizer`: turns raw scan data into a stable internal shape
- `risk classifier`: labels candidates as `safe to review`, `needs inspection`, or `do not touch`
- `report generator`: emits compact summaries and machine-readable outputs

This keeps the core pipeline reusable even if the scan engine changes later, including a future partial Windows adapter.

## Repository Layout

- `.agent/`: local-only operator memory, ignored from git
- `.trae/skills/`: repository-local agent skills
- `config/`: thresholds, exclusions, policy settings
- `docs/`: specs and longer-form design notes
- `outputs/`: dated audit runs
- `scripts/`: launchers and operational helpers
- `src/`: parsers, classifiers, report generation
- `tests/`: focused tests for parser and policy logic
- `trash/`: temporary or discarded experiments

## What Stays Out Of Git

- `.agent/`: volatile local memory and handoff notes
- `outputs/`: generated audit results
- `trash/`: disposable scratch space

## What Stays In Git

- `tests/`: they prove the parser and risk logic work
- `.trae/skills/`: core part of the product identity
- `AGENTS.md`: public agent entrypoint for the repository

## Planned Workflow

1. Verify `ncdu` availability on the DGX host.
2. Run a read-only scan and save a raw export.
3. Convert the raw export into compact summaries.
4. Let the AI inspect only the top consumers and threshold hits.
5. Run safety checks on shortlisted paths.
6. Produce a reviewable candidate list.
7. Delete nothing until the candidate list is reviewed.

## Token Strategy

The repository is explicitly designed to avoid wasting tokens:

- raw scan files stay on disk
- the AI reads summaries first, not raw dumps
- drill-down is performed one subtree at a time
- reports are limited by top `N`, thresholds, and risk buckets

## Security

- do not store passwords or secrets in this repository
- if system installation requires `sudo` and no passwordless path exists, the workflow must stop and request operator input
- the first implementation must remain read-only

## Commands

- prepare Linux scripts on DGX: `ssh dgx bash /home/jagones/Repositories/safe-delete-advisor/scripts/dgx/prepare_linux_scripts.sh`
- verify `ncdu`: `ssh dgx /home/jagones/Repositories/safe-delete-advisor/scripts/dgx/verify_ncdu.sh`
- guarded install attempt: `ssh dgx /home/jagones/Repositories/safe-delete-advisor/scripts/dgx/install_ncdu.sh`
- live audit run: `ssh dgx /home/jagones/Repositories/safe-delete-advisor/scripts/dgx/run_audit.sh`
- show latest audit outputs: `ssh dgx /home/jagones/Repositories/safe-delete-advisor/scripts/dgx/show_latest_audit.sh`
- find safer deletion candidates: `ssh dgx /home/jagones/Repositories/safe-delete-advisor/scripts/dgx/find_safe_candidates.sh`

## Status

- repository skeleton created
- design spec written
- implementation completed for the current `v1` scope
- Python pipeline implemented and local tests passing: `8 passed`
- DGX verify completed: `ncdu` installed and detected
- live audit run completed successfully
- post-rename DGX verification completed successfully
- latest verified run: `/home/jagones/Repositories/safe-delete-advisor/outputs/20260919_1321_audit`
- safe-candidate helper identifies large cache, partial-download, and trash files
- skill packaging added for agent reuse
