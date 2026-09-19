from pathlib import Path
import os
import subprocess
import sys

import pytest

from dirstat_skill.cli import main


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
    assert (output_dir / "review_candidates.csv").exists()
    assert (output_dir / "review_report.md").exists()


def test_python_module_cli_writes_summary_files(tmp_path: Path) -> None:
    export_path = Path("tests/fixtures/ncdu_minimal_export.json")
    output_dir = tmp_path / "module-run"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dirstat_skill.cli",
            "summarize-export",
            "--export",
            str(export_path),
            "--output-dir",
            str(output_dir),
            "--config",
            "config/defaults.json",
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert (output_dir / "summary.md").exists()


def test_cli_audit_command_writes_recursive_review_bundle(tmp_path: Path) -> None:
    target_root = tmp_path / "audit-root"
    target_root.mkdir()
    (target_root / "blob.bin").write_bytes(b"x" * 32)

    output_dir = tmp_path / "audit-run"
    exit_code = main(
        [
            "audit",
            "--path",
            str(target_root),
            "--output-dir",
            str(output_dir),
            "--engine",
            "windows-native",
            "--config",
            "config/defaults.json",
        ]
    )

    assert exit_code == 0
    assert (output_dir / "summary.md").exists()
    assert (output_dir / "top_dirs.csv").exists()
    assert (output_dir / "top_files.csv").exists()
    assert (output_dir / "candidates.json").exists()
    assert (output_dir / "review_candidates.csv").exists()
    assert (output_dir / "review_report.md").exists()
    assert (output_dir / "run.log").exists()


def test_cli_audit_command_rejects_missing_windows_target(tmp_path: Path) -> None:
    output_dir = tmp_path / "audit-run"

    with pytest.raises(FileNotFoundError):
        main(
            [
                "audit",
                "--path",
                str(tmp_path / "missing-root"),
                "--output-dir",
                str(output_dir),
                "--engine",
                "windows-native",
                "--config",
                "config/defaults.json",
            ]
        )


def test_cli_rejects_ncdu_for_windows_style_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Windows-style paths require the Windows runtime"):
        main(
            [
                "audit",
                "--path",
                "C:\\",
                "--output-dir",
                str(tmp_path / "audit-run"),
                "--engine",
                "ncdu",
                "--config",
                "config/defaults.json",
            ]
        )


def test_cli_rejects_windows_native_for_linux_style_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Linux-style paths require a Linux runtime"):
        main(
            [
                "audit",
                "--path",
                "/home",
                "--output-dir",
                str(tmp_path / "audit-run"),
                "--engine",
                "windows-native",
                "--config",
                "config/defaults.json",
            ]
        )

