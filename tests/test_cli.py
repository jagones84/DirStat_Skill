from pathlib import Path

from disk_audit_dgx.cli import main


def test_cli_summarize_export_writes_summary_files(tmp_path: Path) -> None:
    export_path = Path("tests/fixtures/ncdu_minimal_export.json")
    output_dir = tmp_path / "run"

    exit_code = main(
        [
            "summarize-export",
            "--export",
            str(export_path),
            "--output-dir",
            str(output_dir),
            "--config",
            "config/defaults.json",
        ]
    )

    assert exit_code == 0
    assert (output_dir / "summary.md").exists()
    assert (output_dir / "top_dirs.csv").exists()
    assert (output_dir / "top_files.csv").exists()
    assert (output_dir / "candidates.json").exists()
