# safe-delete-advisor-skill Design

## Goal

Build a standalone repository that audits disk usage on a DGX/Linux host in a read-only way, produces compact AI-friendly summaries, and identifies large deletion candidates without guessing about safety.

## Scope

The first version is:

- DGX/Linux-first
- driven by a system-installed scan engine
- read-only
- optimized for low-token AI review

The first version is not responsible for deleting files automatically.

## Supported Runtime Model

- host machine for orchestration: Windows workstation with `Z:` mapped to the DGX home
- target machine for scan execution: DGX/Linux ARM
- repository location: `Z:\Repositories\safe-delete-advisor-skill`

## Core Principles

1. Separate repository logic from system-installed tools.
2. Keep raw scan data on disk and out of LLM context by default.
3. Only inspect large consumers first.
4. Run safety checks before any deletion recommendation.
5. Keep the architecture modular enough to swap scan engines later.

## High-Level Architecture

The system consists of four layers:

- `scan engine adapter`
  - calls the installed tool on DGX
  - saves raw output
- `normalizer`
  - converts raw output into a stable internal structure
- `risk classifier`
  - applies rules that detect sensitive paths, probable runtime ownership, and obvious danger zones
- `report generator`
  - emits compact outputs for AI and human review

Only the `scan engine adapter` is platform-specific in `v1`.

## Initial Scan Engine Choice

`ncdu` is the first engine because it is mature, widely packaged, and suitable for headless Linux workflows.

The repository does not vendor `ncdu`. The tool must exist on the DGX host as a system dependency.

## Token Strategy

Token control is a first-class design requirement.

The workflow must:

- keep raw exports on disk
- generate compact summaries before AI review
- limit first-pass analysis to top `N` and size thresholds
- support path-by-path drill-down instead of whole-tree ingestion

The workflow must not:

- paste the complete raw scan into the LLM
- recursively expand all subtrees by default

## Proposed Repository Layout

- `.agent/`
  - `HANDOFF.md`
  - operational memory and research artifacts
- `config/`
  - thresholds, exclusions, risk rules
- `scripts/`
  - operational wrappers for scan and reporting
- `src/`
  - parsing, normalization, classification, and report logic
- `tests/`
  - focused tests for parser and policy behavior
- `outputs/`
  - dated run folders
- `trash/`
  - temporary experiments

## Output Contract

Each audit run should create a dated folder under `outputs/` containing at least:

- raw scan export
- `summary.md`
- `top_dirs.csv`
- `top_files.csv`
- `candidates.json`

This allows the AI to start from the smallest useful surface and expand only when needed.

## Risk Model

Each shortlisted path should be placed into one of three buckets:

- `safe to review`
- `needs inspection`
- `do not touch`

Classification should consider:

- size
- path sensitivity
- probable package ownership or system area
- likely runtime usage
- references in config, service units, scripts, or symlinks

## Installation and Privilege Policy

If `ncdu` is missing, installation may be attempted only through supported system package paths.

If installation requires `sudo` and passwordless elevation is not available, the workflow must stop and request operator input. The repository must never store the sudo password.

## Error Handling

The implementation must fail loudly when:

- the scan engine is missing
- the raw export format is unsupported
- the output directory cannot be created
- privilege escalation is required but unavailable

## Testing Strategy

The first implementation should include tests for:

- raw-to-normalized conversion on small sample exports
- threshold filtering
- risk bucket assignment
- summary generation correctness

Manual verification should confirm:

- scan wrapper creates outputs in the expected location
- summaries remain compact
- no delete operation is performed in `v1`

## Recommended Next Step

Write a detailed implementation plan for the repository skeleton, `ncdu` verification path, raw export handling, compact summarization, and safety classification.


