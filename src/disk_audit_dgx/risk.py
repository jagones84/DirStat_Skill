from __future__ import annotations


def classify_path(
    path: str,
    do_not_touch_prefixes: list[str],
    needs_inspection_prefixes: list[str],
) -> str:
    for prefix in do_not_touch_prefixes:
        normalized = prefix.rstrip("/")
        if path == normalized or path.startswith(f"{normalized}/"):
            return "do not touch"

    for prefix in needs_inspection_prefixes:
        normalized = prefix.rstrip("/")
        if path == normalized or path.startswith(f"{normalized}/"):
            return "needs inspection"

    return "safe to review"
