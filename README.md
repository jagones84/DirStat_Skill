# disk-audit-dgx

Read-only disk space audit pipeline for DGX/Linux hosts, optimized for low-token AI analysis.

## Goal

This repository provides a reproducible workflow to:

- scan disk usage on a DGX/Linux host using a system-installed scanner
- compact the raw scan into AI-friendly summaries
- classify large paths by deletion risk
- produce a shortlist for human review before any cleanup

Version `v1` targets DGX/Linux ARM and uses `ncdu` as the initial scan engine.

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

- `.agent/`: short-term memory, research notes, operational handoff
- `config/`: thresholds, exclusions, policy settings
- `docs/`: specs and longer-form design notes
- `outputs/`: dated audit runs
- `scripts/`: launchers and operational helpers
- `src/`: parsers, classifiers, report generation
- `tests/`: focused tests for parser and policy logic
- `trash/`: temporary or discarded experiments

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

- prepare Linux scripts on DGX: `ssh dgx bash /home/jagones/Repositories/disk-audit-dgx/scripts/dgx/prepare_linux_scripts.sh`
- verify `ncdu`: `ssh dgx /home/jagones/Repositories/disk-audit-dgx/scripts/dgx/verify_ncdu.sh`
- guarded install attempt: `ssh dgx /home/jagones/Repositories/disk-audit-dgx/scripts/dgx/install_ncdu.sh`
- live audit run: `ssh dgx /home/jagones/Repositories/disk-audit-dgx/scripts/dgx/run_audit.sh`

## Status

- repository skeleton created
- design spec written
- implementation in progress
- Python pipeline implemented and tests passing
- DGX verify completed: `ncdu` missing from PATH
- install blocked pending interactive sudo input
