from pathlib import Path

import pytest

from safe_delete_advisor.engine_windows import build_windows_export


def test_build_windows_export_writes_raw_json(tmp_path: Path) -> None:
    source_root = tmp_path / "scan-root"
    source_root.mkdir()
    (source_root / "cache.bin").write_bytes(b"x" * 8)
    (source_root / "nested").mkdir()
    (source_root / "nested" / "weights.gguf").write_bytes(b"y" * 16)

    export_path = tmp_path / "windows-export.json"
    result = build_windows_export(target=source_root, output_path=export_path)

    assert result.engine_name == "windows-native"
    assert export_path.exists()
    assert '"path"' in export_path.read_text(encoding="utf-8")


def test_build_windows_export_rejects_missing_root(tmp_path: Path) -> None:
    export_path = tmp_path / "windows-export.json"

    with pytest.raises(FileNotFoundError):
        build_windows_export(target=tmp_path / "missing-root", output_path=export_path)
