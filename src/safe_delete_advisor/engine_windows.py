from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path


@dataclass(frozen=True)
class WindowsExportResult:
    engine_name: str
    output_path: Path


def _scan_path(root: Path) -> list[dict[str, object]]:
    nodes: list[dict[str, object]] = []
    with os.scandir(root) as entries:
        for entry in entries:
            entry_path = Path(entry.path)
            if entry.is_dir(follow_symlinks=False):
                nodes.append(
                    {
                        "path": str(entry_path),
                        "name": entry.name,
                        "is_dir": True,
                        "size": 0,
                    }
                )
                nodes.extend(_scan_path(entry_path))
            else:
                nodes.append(
                    {
                        "path": str(entry_path),
                        "name": entry.name,
                        "is_dir": False,
                        "size": entry.stat(follow_symlinks=False).st_size,
                    }
                )
    return nodes


def build_windows_export(target: Path, output_path: Path) -> WindowsExportResult:
    payload = {
        "engine": "windows-native",
        "root": str(target),
        "nodes": _scan_path(target),
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return WindowsExportResult(engine_name="windows-native", output_path=output_path)
