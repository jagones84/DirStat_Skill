from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from safe_delete_advisor.targets import ScanTarget


@dataclass(frozen=True)
class RawExportInfo:
    engine_name: str
    output_path: Path
    targets: list[ScanTarget]
