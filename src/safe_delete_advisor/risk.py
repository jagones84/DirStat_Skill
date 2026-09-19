from __future__ import annotations


def classify_path(
    path: str,
    do_not_touch_prefixes: list[str],
    needs_inspection_prefixes: list[str],
) -> str:
    normalized_path = _normalize_path(path)
    for prefix in do_not_touch_prefixes:
        normalized = _normalize_path(prefix)
        if normalized_path == normalized or normalized_path.startswith(f"{normalized}/"):
            return "do not touch"

    if _is_obvious_delete_first(normalized_path):
        return "delete first"

    for prefix in needs_inspection_prefixes:
        normalized = _normalize_path(prefix)
        if normalized_path == normalized or normalized_path.startswith(f"{normalized}/"):
            return "inspect before delete"

    return "inspect before delete"


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").rstrip("/").lower()


def _is_obvious_delete_first(normalized_path: str) -> bool:
    delete_first_exact_paths = {
        "/tmp",
        "/var/tmp",
    }
    delete_first_suffixes = (
        "/.cache",
        "/trash",
        "/.trash",
        "/appdata/local/temp",
    )
    delete_first_fragments = (
        "/.cache/",
        "/trash/",
        "/.trash/",
        "/appdata/local/temp/",
        "/tmp/",
        "/var/tmp/",
    )
    if normalized_path in delete_first_exact_paths:
        return True
    if normalized_path.endswith(delete_first_suffixes):
        return True
    if any(fragment in normalized_path for fragment in delete_first_fragments):
        return True
    return normalized_path.endswith((".filepart", ".part", ".partial", ".tmp", ".cache"))
