from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from safe_delete_advisor.models import DeletionCandidate, NormalizedNode
from safe_delete_advisor.risk import classify_path


@dataclass(frozen=True)
class TopLists:
    top_dirs: list[NormalizedNode]
    top_files: list[NormalizedNode]


def build_top_lists(nodes: list[NormalizedNode], min_bytes: int, top_n: int) -> TopLists:
    dirs = [node for node in nodes if node.is_dir and node.dsize >= min_bytes]
    files = [node for node in nodes if not node.is_dir and node.dsize >= min_bytes]
    top_dirs = sorted(dirs, key=lambda node: node.dsize, reverse=True)[:top_n]
    top_files = sorted(files, key=lambda node: node.dsize, reverse=True)[:top_n]
    return TopLists(top_dirs=top_dirs, top_files=top_files)


def select_dominant_candidates(
    nodes: list[NormalizedNode],
    root_path: str,
    dominant_percent: float,
    min_candidate_bytes: int,
) -> list[NormalizedNode]:
    node_by_key = {_path_key(node.path): node for node in nodes}
    children_by_parent = _build_children_index(nodes)
    root = node_by_key[_path_key(root_path)]
    selected = _select_from_node(
        node=root,
        children_by_parent=children_by_parent,
        dominant_percent=dominant_percent,
        min_candidate_bytes=min_candidate_bytes,
    )
    return _dedupe_nodes(selected)


def select_dominant_candidates_for_roots(
    nodes: list[NormalizedNode],
    dominant_percent: float,
    min_candidate_bytes: int,
) -> list[NormalizedNode]:
    children_by_parent = _build_children_index(nodes)
    roots = [node for node in nodes if _parent_key(node.path) is None]
    selected: list[NormalizedNode] = []
    for root in sorted(roots, key=lambda node: node.dsize, reverse=True):
        selected.extend(
            _select_from_node(
                node=root,
                children_by_parent=children_by_parent,
                dominant_percent=dominant_percent,
                min_candidate_bytes=min_candidate_bytes,
            )
        )
    return _dedupe_nodes(selected)


def build_deletion_candidates(
    selected_nodes: list[NormalizedNode],
    all_nodes: list[NormalizedNode],
    protected_prefixes: list[str],
    inspection_prefixes: list[str],
    nearby_reference_extensions: list[str],
    max_nearby_reference_files: int,
) -> list[DeletionCandidate]:
    candidates: list[DeletionCandidate] = []
    for node in selected_nodes:
        recommended_action = classify_path(
            node.path,
            protected_prefixes,
            inspection_prefixes,
        )
        nearby_refs = _find_nearby_references(
            node.path,
            nearby_reference_extensions=nearby_reference_extensions,
            max_nearby_reference_files=max_nearby_reference_files,
        )
        candidate_reason = _candidate_reason(node=node, recommended_action=recommended_action)
        dependency_check_summary, confidence = _dependency_summary(
            node=node,
            recommended_action=recommended_action,
            nearby_refs=nearby_refs,
        )
        candidates.append(
            DeletionCandidate(
                path=node.path,
                dsize=node.dsize,
                is_dir=node.is_dir,
                risk=recommended_action,
                candidate_reason=candidate_reason,
                dependency_check_summary=dependency_check_summary,
                dependency_check_confidence=confidence,
                recommended_action=recommended_action,
                selection_source="dominant_subtree" if node.is_dir else "dominant_leaf",
            )
        )
    return candidates


def render_deletion_report(root_path: str, candidates: list[DeletionCandidate]) -> str:
    sections = [
        ("Delete First", "delete first"),
        ("Inspect Before Delete", "inspect before delete"),
        ("Do Not Touch", "do not touch"),
    ]
    lines = [
        "# Deletion Report",
        "",
        f"- root: `{root_path}`",
        f"- total_candidates: {len(candidates)}",
        "",
    ]
    for title, action in sections:
        lines.append(f"## {title}")
        lines.append("")
        section_candidates = [item for item in candidates if item.recommended_action == action]
        if not section_candidates:
            lines.append("- none")
            lines.append("")
            continue
        for candidate in section_candidates:
            lines.append(f"### `{candidate.path}`")
            lines.append("")
            lines.append(f"- size_bytes: `{candidate.dsize}`")
            lines.append(f"- size_human: `{_human_size(candidate.dsize)}`")
            lines.append(f"- reason: {candidate.candidate_reason}")
            lines.append(f"- dependency_check: {candidate.dependency_check_summary}")
            lines.append(f"- confidence: `{candidate.dependency_check_confidence}`")
            lines.append(f"- action: `{candidate.recommended_action}`")
            lines.append("")
    return "\n".join(lines)


def write_deletion_candidates_csv(
    output_path: Path,
    candidates: list[DeletionCandidate],
) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "path",
                "dsize",
                "is_dir",
                "risk",
                "candidate_reason",
                "dependency_check_summary",
                "dependency_check_confidence",
                "recommended_action",
                "selection_source",
            ],
        )
        writer.writeheader()
        for candidate in candidates:
            writer.writerow(candidate.__dict__)


def _build_children_index(nodes: list[NormalizedNode]) -> dict[str | None, list[NormalizedNode]]:
    children_by_parent: dict[str | None, list[NormalizedNode]] = {}
    for node in nodes:
        children_by_parent.setdefault(_parent_key(node.path), []).append(node)
    return children_by_parent


def _select_from_node(
    node: NormalizedNode,
    children_by_parent: dict[str | None, list[NormalizedNode]],
    dominant_percent: float,
    min_candidate_bytes: int,
) -> list[NormalizedNode]:
    if not node.is_dir or node.dsize < min_candidate_bytes:
        return [node]
    children = [
        child
        for child in sorted(
            children_by_parent.get(_path_key(node.path), []),
            key=lambda item: item.dsize,
            reverse=True,
        )
        if child.dsize >= min_candidate_bytes
    ]
    if not children:
        return [node]
    total_child_size = sum(child.dsize for child in children)
    if total_child_size <= 0:
        return [node]
    selected_children: list[NormalizedNode] = []
    cumulative = 0
    for child in children:
        selected_children.append(child)
        cumulative += child.dsize
        if cumulative / total_child_size >= dominant_percent:
            break
    if (
        len(selected_children) == len(children)
        and len(children) > 1
        and all(child.is_dir for child in children)
    ):
        return [node]
    selected: list[NormalizedNode] = []
    for child in selected_children:
        if child.is_dir:
            selected.extend(
                _select_from_node(
                    node=child,
                    children_by_parent=children_by_parent,
                    dominant_percent=dominant_percent,
                    min_candidate_bytes=min_candidate_bytes,
                )
            )
        else:
            selected.append(child)
    return selected or [node]


def _candidate_reason(node: NormalizedNode, recommended_action: str) -> str:
    normalized = _path_key(node.path)
    if normalized.endswith((".filepart", ".part", ".partial")):
        return "partial download file selected by recursive 80/20 walk"
    if any(fragment in normalized for fragment in ("/.cache", "/trash", "/.trash", "/appdata/local/temp", "/tmp", "/var/tmp")):
        return "cache/temp/trash path selected by recursive 80/20 walk"
    if recommended_action == "do not touch":
        return "protected system or runtime-owned path"
    if normalized.endswith((".gguf", ".safetensors", ".ckpt", ".bin", ".pth")):
        return "user-owned model asset selected by recursive 80/20 walk"
    if node.is_dir:
        return "directory dominates parent space under recursive 80/20 walk"
    return "file selected by recursive 80/20 walk"


def _dependency_summary(
    node: NormalizedNode,
    recommended_action: str,
    nearby_refs: list[str],
) -> tuple[str, str]:
    normalized = _path_key(node.path)
    if recommended_action == "do not touch":
        return "protected path matched system/runtime policy prefixes", "high"
    if any(fragment in normalized for fragment in ("/.cache", "/trash", "/.trash", "/appdata/local/temp", "/tmp", "/var/tmp")):
        return "matched cache/temp/trash signature; no nearby manifests or workflow refs required", "high"
    if normalized.endswith((".filepart", ".part", ".partial")):
        return "matched partial-download signature; safe to remove if incomplete", "high"
    if nearby_refs:
        return f"nearby references found in {', '.join(nearby_refs)}", "medium"
    return "no nearby references found in candidate directory or checked ancestors", "low"


def _find_nearby_references(
    path: str,
    nearby_reference_extensions: list[str],
    max_nearby_reference_files: int,
) -> list[str]:
    candidate_path = Path(path)
    if not candidate_path.exists():
        return []
    search_dirs: list[Path] = []
    current = candidate_path if candidate_path.is_dir() else candidate_path.parent
    for _ in range(3):
        if current in search_dirs:
            break
        search_dirs.append(current)
        if current.parent == current:
            break
        current = current.parent
    basename = candidate_path.name.lower()
    matches: list[str] = []
    for directory in search_dirs:
        try:
            entries = sorted(directory.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            continue
        for entry in entries:
            if not entry.is_file():
                continue
            if entry.suffix.lower() not in nearby_reference_extensions:
                continue
            try:
                content = entry.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if basename in content.lower():
                matches.append(entry.name)
            if len(matches) >= max_nearby_reference_files:
                return matches
    return matches


def _path_key(path: str) -> str:
    normalized = path.replace("\\", "/").rstrip("/").lower()
    if not normalized and path.startswith("/"):
        return "/"
    return normalized


def _parent_key(path: str) -> str | None:
    normalized = _path_key(path)
    if not normalized:
        return None
    if normalized == "/":
        return None
    if len(normalized) == 2 and normalized[1] == ":":
        return None
    if normalized.startswith("/") and normalized.count("/") == 1:
        return "/"
    parent = normalized.rsplit("/", 1)[0] if "/" in normalized else ""
    if not parent:
        return None
    return parent


def _dedupe_nodes(nodes: list[NormalizedNode]) -> list[NormalizedNode]:
    deduped: list[NormalizedNode] = []
    seen: set[str] = set()
    for node in nodes:
        key = _path_key(node.path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(node)
    return deduped


def _human_size(size_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size_bytes} B"
