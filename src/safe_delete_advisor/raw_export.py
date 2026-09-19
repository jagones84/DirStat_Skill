from __future__ import annotations

import json
from pathlib import Path


def load_raw_export(export_path: Path) -> dict[str, object]:
    payload = json.loads(export_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "engine" in payload:
        return payload
    return {"engine": "ncdu", "payload": payload}
