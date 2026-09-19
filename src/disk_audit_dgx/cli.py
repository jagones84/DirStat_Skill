from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from disk_audit_dgx.config import load_settings
from disk_audit_dgx.ncdu_json import parse_ncdu_export
from disk_audit_dgx.reporting import build_top_lists
from disk_audit_dgx.risk import classify_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="disk-audit-dgx")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summarize = subparsers.add_parser("summarize-export")
    summarize.add_argument("--export", required=True)
    summarize.add_argument("--output-dir", required=True)
    summarize.add_argument("--config", required=True)

    args = parser.parse_args(argv)
    if args.command == "summarize-export":
        return _summarize_export(
            export_path=Path(args.export),
            output_dir=Path(args.output_dir),
            config_path=Path(args.config),
        )
    return 2


def _summarize_export(export_path: Path, output_dir: Path, config_path: Path) -> int:
    settings = load_settings(config_path=config_path)
    parsed = parse_ncdu_export(export_path)
    top_lists = build_top_lists(
        parsed.nodes,
        min_bytes=settings.min_bytes,
        top_n=settings.top_n,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates = []
    for node in top_lists.top_dirs + top_lists.top_files:
        candidates.append(
            {
                "path": node.path,
                "dsize": node.dsize,
                "is_dir": node.is_dir,
                "risk": classify_path(
                    node.path,
                    settings.risk_do_not_touch_prefixes,
                    settings.risk_needs_inspection_prefixes,
                ),
            }
        )

    (output_dir / "summary.md").write_text(
        "# Audit Summary\n\n"
        f"- root: `{parsed.root_path}`\n"
        f"- top_dirs: {len(top_lists.top_dirs)}\n"
        f"- top_files: {len(top_lists.top_files)}\n",
        encoding="utf-8",
    )

    with (output_dir / "top_dirs.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "dsize"])
        writer.writeheader()
        for node in top_lists.top_dirs:
            writer.writerow({"path": node.path, "dsize": node.dsize})

    with (output_dir / "top_files.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "dsize"])
        writer.writeheader()
        for node in top_lists.top_files:
            writer.writerow({"path": node.path, "dsize": node.dsize})

    (output_dir / "candidates.json").write_text(
        json.dumps(candidates, indent=2),
        encoding="utf-8",
    )
    return 0
