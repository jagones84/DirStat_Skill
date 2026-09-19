from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EngineInfo:
    binary: str
    resolved_path: Path


@dataclass(frozen=True)
class NormalizedNode:
    path: str
    name: str
    is_dir: bool
    asize: int
    dsize: int


@dataclass(frozen=True)
class ParsedExport:
    root_path: str
    nodes: list[NormalizedNode]


@dataclass(frozen=True)
class RawExportMetadata:
    engine_name: str
    root_paths: list[str]
