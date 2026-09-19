# Changelog

## [0.1.0] - 2026-09-19
### Added
- Public cross-platform `DirStat_Skill` repository layout for Windows and Linux hosts.
- Native Windows scan engine and generic CLI commands: `scan`, `summarize-export`, and `audit`.
- Recursive review dossier outputs with `review_report.md`, `review_candidates.csv`, and `candidates.json`.
- Public skill packaging with `SKILL.md` and `AGENTS.md` for agent-driven usage.

### Changed
- Renamed the public identity from `safe-delete-advisor-skill` to `DirStat_Skill`.
- Renamed the Python package from `safe_delete_advisor` to `dirstat_skill`.
- Reframed all public docs and outputs around review-only language instead of cleanup automation.

### Fixed
- Added hard-fail CLI guardrails for invalid engine/platform/path combinations.
- Aligned OpenClaw skill symlinks to the canonical repository path.

### Safety
- The tool is read-only and never removes files automatically.
