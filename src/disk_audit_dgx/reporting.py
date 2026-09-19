from __future__ import annotations

from dataclasses import dataclass

from disk_audit_dgx.models import NormalizedNode


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
