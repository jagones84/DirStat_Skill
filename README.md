# DirStat_Skill

> READ-ONLY ANALYSIS ONLY
>
> `DirStat_Skill` never removes files, never schedules cleanup, and never performs destructive actions.
> It only scans disk usage, builds compact reports, and suggests what a human should review.

Tired of wasting tens of GB on forgotten AI models, bloated caches, and files you have not touched since the Cold War? This is the safe read-only answer.

## Goal

`DirStat_Skill` is a public, cross-platform disk-usage analysis skill and repository.

It helps humans and agents:

- scan explicit paths on Windows or Linux
- keep raw scan data on disk instead of dumping it into an LLM
- generate compact summaries first
- follow dominant branches recursively with an 80/20 walk
- group findings into `review first`, `review carefully`, and `keep protected`
- produce a review dossier with reasons and dependency-check notes

## Identity

- public repository name: `DirStat_Skill`
- skill path: `skills/DirStat_Skill/SKILL.md`
- repository agent entrypoint: `AGENTS.md`
- Python package: `dirstat_skill`

## Runtime Matrix

- Windows filesystem on Windows host:
  - run `python -m dirstat_skill.cli audit ...`
  - engine: `windows-native`
- Linux filesystem on Linux host:
  - run `python3 -m dirstat_skill.cli audit --engine ncdu ...`
  - engine: `ncdu`
- Remote or mixed-machine workflow:
  - run the scan on the machine that owns the filesystem
  - move only the compact outputs elsewhere if you want another agent or host to review them
  - do not fake a Windows scan from Linux with a mismatched runtime

## Hard Guardrails

The CLI now fails loudly when the runtime contract is wrong:

- `windows-native` outside Windows: blocked
- `ncdu` on Windows: blocked
- Windows-style paths with Linux runtime: blocked
- Linux-style paths with Windows runtime: blocked

This is intentional. The skill is supposed to be idiot-proof, not permissive.

## Token Strategy

- raw exports stay on disk
- the first pass reads `review_report.md`, `review_candidates.csv`, `summary.md`, and `candidates.json`
- reviews start from dominant branches, not from a flat global top list
- drill-down happens path by path with a recursive 80/20 walk
- agents read raw exports only when compact outputs are missing or inconsistent

## Output Contract

Every audit run writes a bundle under `outputs/<stamp>_audit/`:

- raw export file
- `summary.md`
- `top_dirs.csv`
- `top_files.csv`
- `candidates.json`
- `review_candidates.csv`
- `review_report.md`
- `run.log`

## Installation

### Python

```bash
python -m pip install -e .
```

### Linux `ncdu`

Install `ncdu` with your distribution package manager or use `scripts/linux/install_ncdu.sh`.

## Quick Start

### Windows

```bash
python -m dirstat_skill.cli audit --path C:\ --output-dir outputs\win_c_audit --config config\defaults.json
```

Multiple targets:

```bash
python -m dirstat_skill.cli audit --path C:\ --path D:\models --output-dir outputs\win_multi_audit --config config\defaults.json
```

### Linux

```bash
python3 -m dirstat_skill.cli audit --path /home --engine ncdu --output-dir outputs/linux_home_audit --config config/defaults.json
```

### Linux Helper Scripts

```bash
bash scripts/linux/prepare_linux_scripts.sh
bash scripts/linux/run_audit.sh /home
```

### Windows Helper Script

```powershell
powershell -ExecutionPolicy Bypass -File scripts/windows/run_audit.ps1 -TargetPath C:\ -OutputDir outputs\win_c_audit
```

## Review Buckets

- `review first`
  - partial downloads
  - trash content
  - cache and temp blobs
- `review carefully`
  - user-owned models
  - checkpoints, `.safetensors`, `.gguf`
  - large application inputs
- `keep protected`
  - system-owned paths
  - package stores
  - swap, Docker backing storage, OS directories

## Review Dossier

- `review_report.md`
  - human-readable dossier
  - grouped by `review first`, `review carefully`, `keep protected`
  - includes full paths, reasons, and dependency-check summaries
- `review_candidates.csv`
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

## Safety Rules

- never store secrets in the repository
- never remove files automatically
- never issue cleanup commands from this skill
- prefer compact outputs over raw dumps
- stop loudly if the requested engine or runtime contract is wrong
- treat large user assets as review targets, not junk

## Repository Layout

- `skills/DirStat_Skill/`: public skill entrypoint
- `config/`: thresholds, exclusions, policy settings
- `docs/`: specs and implementation plans
- `outputs/`: generated audit runs
- `scripts/linux/`: Linux helper scripts
- `scripts/windows/`: Windows helper scripts
- `src/`: engines, parsers, classifier, reporting, CLI
- `tests/`: focused automated tests
- `.agent/`: local operator memory, ignored from git
- `trash/`: disposable experiments, ignored from git

