# safe-delete-advisor-skill

Tired of wasting tens of GB on forgotten AI models, bloated caches, and files you have not touched since the Cold War? This is the safe, read-only answer.

## Goal

`safe-delete-advisor-skill` is a public, cross-platform disk-audit skill and repository.

It helps humans and agents:

- scan one or more explicit paths on Windows or Linux
- keep raw scan data on disk instead of dumping it into an LLM
- generate compact summaries first
- follow dominant branches recursively with an 80/20 walk
- classify deletion candidates into `delete first`, `inspect before delete`, and `do not touch`
- produce a full deletion dossier with reasons and dependency-check notes before any cleanup

It does **not** delete automatically.

## Platforms

- Windows: native Python scanner, no mandatory third-party dependency
- Linux: `ncdu` engine when available
- Linux ARM64 DGX: supported through the same Linux engine plus helper scripts

## Skill Identity

- skill name: `safe-delete-advisor-skill`
- skill path: `skills/safe-delete-advisor-skill/SKILL.md`
- repository agent entrypoint: `AGENTS.md`
- Python package: `safe_delete_advisor`

## Token Strategy

This repo is explicitly built to avoid stupid token burn:

- raw exports stay on disk
- the first pass reads `deletion_report.md`, `deletion_candidates.csv`, `summary.md`, and `candidates.json`
- reviews start from dominant branches, not from a flat global top-10
- drill-down happens path by path with a recursive 80/20 walk
- agents should read raw exports only when the compact outputs are missing or inconsistent

## Output Contract

Every audit run writes a bundle under `outputs/<stamp>_audit/`:

- raw export file
- `summary.md`
- `top_dirs.csv`
- `top_files.csv`
- `candidates.json`
- `deletion_candidates.csv`
- `deletion_report.md`
- `run.log`

## Installation

### Python

```bash
python -m pip install -e .
```

### Linux `ncdu`

Install `ncdu` with your distribution package manager or use the helper script in `scripts/linux/install_ncdu.sh`.

## Quick Start

### Windows

Audit a local drive:

```bash
python -m safe_delete_advisor.cli audit --path C:\ --output-dir outputs\win_c_audit --config config\defaults.json
```

Audit multiple targets in one run:

```bash
python -m safe_delete_advisor.cli audit --path C:\ --path D:\models --output-dir outputs\win_multi_audit --config config\defaults.json
```

### Linux

Audit one path with `ncdu`:

```bash
python3 -m safe_delete_advisor.cli audit --path /home --engine ncdu --output-dir outputs/linux_home_audit --config config/defaults.json
```

### Linux Helper Scripts

The repository also ships Linux-only convenience wrappers:

- `scripts/linux/prepare_linux_scripts.sh`
- `scripts/linux/verify_ncdu.sh`
- `scripts/linux/install_ncdu.sh`
- `scripts/linux/run_audit.sh`
- `scripts/linux/show_latest_audit.sh`
- `scripts/linux/find_safe_candidates.sh`

Example on DGX:

```bash
ssh dgx bash /home/jagones/Repositories/safe-delete-advisor-skill/scripts/linux/prepare_linux_scripts.sh
ssh dgx /home/jagones/Repositories/safe-delete-advisor-skill/scripts/linux/run_audit.sh
```

## Verified Runs

Real runs already verified with this repository:

- Windows host:
  - `python -m safe_delete_advisor.cli audit --path C:\Windows\Temp --path D:\ --path E:\ --path F:\ --output-dir outputs\20260919_win_multi_real --config config\defaults.json`
  - surfaced large review targets such as `docker_data.vhdx`, Steam/GamePass archives, `.safetensors`, `.gguf`, and other large assets across multiple drives
- Linux ARM64 DGX:
  - `ssh dgx bash /home/jagones/Repositories/safe-delete-advisor-skill/scripts/linux/prepare_linux_scripts.sh`
  - `ssh dgx /home/jagones/Repositories/safe-delete-advisor-skill/scripts/linux/run_audit.sh`
  - latest verified compact report: `outputs/20260919_1457_audit`
  - surfaced both `delete first` candidates like `.filepart` leftovers and `inspect before delete` model assets under user-owned paths

## Risk Buckets

- `delete first`
  - temp files
  - cache blobs
  - trash contents
  - partial downloads like `.filepart`
- `inspect before delete`
  - user-owned model folders
  - checkpoints, `.safetensors`, `.gguf`
  - large application inputs
- `do not touch`
  - system-owned paths
  - package stores
  - swap, Docker backing storage, OS directories

## Deletion Dossier

The final deletion contract is no longer just a flat leaderboard.

- `deletion_report.md`
  - human-readable dossier
  - grouped by `delete first`, `inspect before delete`, `do not touch`
  - includes full paths, reasons, and dependency-check summaries
- `deletion_candidates.csv`
  - structured flat export for spreadsheets and scripts
- `candidates.json`
  - machine-readable version for agent workflows

The selector follows a recursive 80/20 rule:

- find the children that explain about `80%` of each dominant branch
- keep descending while the branch stays dominant
- emit all relevant candidates from that walk, including many medium-size files when they dominate together

Dependency checks are cheap and local by default:

- heuristic signatures for cache/temp/trash/partial/system paths
- nearby reference scan for ambiguous user-owned assets
- optional broader scan only when an agent chooses to escalate on uncertain macrofolders

## Repository Layout

- `skills/safe-delete-advisor-skill/`: public skill entrypoint
- `config/`: thresholds, exclusions, policy settings
- `docs/`: specs and implementation plans
- `outputs/`: generated audit runs
- `scripts/linux/`: Linux helper scripts
- `src/`: engines, parsers, classifier, reporting, CLI
- `tests/`: focused automated tests
- `.agent/`: local operator memory, ignored from git
- `trash/`: disposable experiments, ignored from git

## Git Hygiene

Ignored from git:

- `.agent/`
- `outputs/`
- `trash/`
- virtualenvs, logs, editor noise

Kept in git:

- `tests/`
- `skills/`
- `AGENTS.md`
- `README.md`
- source, config, and docs

## Safety Rules

- never store secrets in the repository
- never delete automatically
- prefer compact outputs over raw dumps
- stop loudly if the requested engine is missing
- treat large user assets as review targets, not automatic junk

## Status

- cross-platform design spec written
- cross-platform implementation plan written
- shared target abstraction implemented
- Windows native scan engine implemented
- raw export bridge implemented for Windows and `ncdu`
- recursive `ncdu` directory sizing fixed for meaningful `top_dirs.csv` results
- generic CLI now supports `scan`, `summarize-export`, and `audit`
- recursive deletion dossier emitted under `outputs/` with reasons and dependency-check summaries
