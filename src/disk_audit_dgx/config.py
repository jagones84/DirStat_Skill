from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    top_n: int
    min_bytes: int
    one_file_system: bool
    exclude_patterns: list[str]
    risk_do_not_touch_prefixes: list[str]
    risk_needs_inspection_prefixes: list[str]


def load_settings(
    config_path: Path,
    env_overrides: dict[str, str] | None = None,
) -> Settings:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    overrides = env_overrides or {}
    return Settings(
        top_n=int(overrides.get("TOP_N", payload["top_n"])),
        min_bytes=int(overrides.get("MIN_BYTES", payload["min_bytes"])),
        one_file_system=bool(payload["one_file_system"]),
        exclude_patterns=list(payload["exclude_patterns"]),
        risk_do_not_touch_prefixes=list(payload["risk_do_not_touch_prefixes"]),
        risk_needs_inspection_prefixes=list(payload["risk_needs_inspection_prefixes"]),
    )
