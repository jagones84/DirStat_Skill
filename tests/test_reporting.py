from pathlib import Path

from dirstat_skill.models import NormalizedNode
from dirstat_skill.reporting import (
    build_review_candidates,
    build_top_lists,
    render_review_report,
    select_dominant_candidates,
)


def test_build_top_lists_filters_by_threshold_and_type() -> None:
    nodes = [
        NormalizedNode(path="/sample", name="sample", is_dir=True, asize=0, dsize=4096),
        NormalizedNode(path="/sample/cache", name="cache", is_dir=True, asize=0, dsize=8000),
        NormalizedNode(
            path="/sample/cache/huge.log",
            name="huge.log",
            is_dir=False,
            asize=0,
            dsize=3000,
        ),
        NormalizedNode(
            path="/sample/media.iso",
            name="media.iso",
            is_dir=False,
            asize=0,
            dsize=9000,
        ),
    ]

    report = build_top_lists(nodes=nodes, min_bytes=5000, top_n=5)

    assert [item.path for item in report.top_dirs] == ["/sample/cache"]
    assert [item.path for item in report.top_files] == ["/sample/media.iso"]


def test_select_dominant_nodes_walks_recursively_until_concrete_candidates() -> None:
    nodes = [
        NormalizedNode(path="/root", name="root", is_dir=True, asize=0, dsize=1000),
        NormalizedNode(path="/root/a", name="a", is_dir=True, asize=0, dsize=850),
        NormalizedNode(path="/root/b", name="b", is_dir=True, asize=0, dsize=150),
        NormalizedNode(path="/root/a/f1.bin", name="f1.bin", is_dir=False, asize=0, dsize=500),
        NormalizedNode(path="/root/a/f2.bin", name="f2.bin", is_dir=False, asize=0, dsize=350),
    ]

    selected = select_dominant_candidates(
        nodes=nodes,
        root_path="/root",
        dominant_percent=0.8,
        min_candidate_bytes=100,
    )

    assert [item.path for item in selected] == ["/root/a/f1.bin", "/root/a/f2.bin"]


def test_select_dominant_candidates_keeps_flat_directory_when_no_clear_winner() -> None:
    nodes = [
        NormalizedNode(path="/root", name="root", is_dir=True, asize=0, dsize=900),
        NormalizedNode(path="/root/a", name="a", is_dir=True, asize=0, dsize=300),
        NormalizedNode(path="/root/b", name="b", is_dir=True, asize=0, dsize=300),
        NormalizedNode(path="/root/c", name="c", is_dir=True, asize=0, dsize=300),
    ]

    selected = select_dominant_candidates(
        nodes=nodes,
        root_path="/root",
        dominant_percent=0.8,
        min_candidate_bytes=100,
    )

    assert [item.path for item in selected] == ["/root"]


def test_select_dominant_candidates_keeps_many_medium_files_that_dominate_together() -> None:
    nodes = [
        NormalizedNode(path="/root", name="root", is_dir=True, asize=0, dsize=1000),
        NormalizedNode(path="/root/cache", name="cache", is_dir=True, asize=0, dsize=900),
        NormalizedNode(path="/root/other", name="other", is_dir=True, asize=0, dsize=100),
        NormalizedNode(path="/root/cache/a.bin", name="a.bin", is_dir=False, asize=0, dsize=300),
        NormalizedNode(path="/root/cache/b.bin", name="b.bin", is_dir=False, asize=0, dsize=300),
        NormalizedNode(path="/root/cache/c.bin", name="c.bin", is_dir=False, asize=0, dsize=200),
        NormalizedNode(path="/root/cache/d.bin", name="d.bin", is_dir=False, asize=0, dsize=100),
    ]

    selected = select_dominant_candidates(
        nodes=nodes,
        root_path="/root",
        dominant_percent=0.8,
        min_candidate_bytes=100,
    )

    assert [item.path for item in selected] == [
        "/root/cache/a.bin",
        "/root/cache/b.bin",
        "/root/cache/c.bin",
    ]


def test_select_dominant_candidates_for_roots_preserves_single_posix_root_tree() -> None:
    nodes = [
        NormalizedNode(path="/", name="/", is_dir=True, asize=0, dsize=1000),
        NormalizedNode(path="/home", name="home", is_dir=True, asize=0, dsize=900),
        NormalizedNode(path="/var", name="var", is_dir=True, asize=0, dsize=100),
        NormalizedNode(path="/home/model.gguf", name="model.gguf", is_dir=False, asize=0, dsize=900),
    ]

    selected = select_dominant_candidates(
        nodes=nodes,
        root_path="/",
        dominant_percent=0.8,
        min_candidate_bytes=100,
    )

    assert [item.path for item in selected] == ["/home/model.gguf"]


def test_build_review_candidates_adds_reason_and_dependency_summary(tmp_path: Path) -> None:
    cache_dir = tmp_path / ".cache"
    cache_dir.mkdir()
    blob_path = cache_dir / "blob.bin"
    blob_path.write_bytes(b"x" * 8)

    nodes = [
        NormalizedNode(path=str(blob_path), name="blob.bin", is_dir=False, asize=0, dsize=2000),
    ]

    candidates = build_review_candidates(
        selected_nodes=nodes,
        all_nodes=nodes,
        protected_prefixes=["/etc", "/usr", "/var/lib"],
        inspection_prefixes=[str(tmp_path)],
        nearby_reference_extensions=[".json", ".yaml"],
        max_nearby_reference_files=5,
    )

    assert candidates[0].review_reason
    assert "cache" in candidates[0].dependency_check_summary.lower()
    assert candidates[0].bucket == "review first"


def test_build_review_candidates_marks_system_storage_as_keep_protected() -> None:
    nodes = [
        NormalizedNode(path="/var/lib/docker-loop.xfs", name="docker-loop.xfs", is_dir=False, asize=0, dsize=2000),
    ]

    candidates = build_review_candidates(
        selected_nodes=nodes,
        all_nodes=nodes,
        protected_prefixes=["/etc", "/usr", "/var/lib"],
        inspection_prefixes=["/home"],
        nearby_reference_extensions=[".json", ".yaml"],
        max_nearby_reference_files=5,
    )

    assert candidates[0].bucket == "keep protected"
    assert "protected" in candidates[0].dependency_check_summary.lower()


def test_build_review_candidates_marks_user_model_without_nearby_refs_as_review_carefully(
    tmp_path: Path,
) -> None:
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    model_path = model_dir / "model.gguf"
    model_path.write_bytes(b"x" * 8)

    nodes = [
        NormalizedNode(path=str(model_path), name="model.gguf", is_dir=False, asize=0, dsize=2000),
    ]

    candidates = build_review_candidates(
        selected_nodes=nodes,
        all_nodes=nodes,
        protected_prefixes=["/etc", "/usr", "/var/lib"],
        inspection_prefixes=[str(tmp_path)],
        nearby_reference_extensions=[".json", ".yaml"],
        max_nearby_reference_files=5,
    )

    assert candidates[0].bucket == "review carefully"
    assert "no nearby references" in candidates[0].dependency_check_summary.lower()


def test_render_review_report_groups_candidates_by_bucket(tmp_path: Path) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"x")
    candidates = build_review_candidates(
        selected_nodes=[
            NormalizedNode(path=str(model_path), name="model.gguf", is_dir=False, asize=0, dsize=2000)
        ],
        all_nodes=[
            NormalizedNode(path=str(model_path), name="model.gguf", is_dir=False, asize=0, dsize=2000)
        ],
        protected_prefixes=["/etc", "/usr", "/var/lib"],
        inspection_prefixes=[str(tmp_path)],
        nearby_reference_extensions=[".json"],
        max_nearby_reference_files=5,
    )

    report = render_review_report(root_path=str(tmp_path), candidates=candidates)

    assert "# Review Report" in report
    assert "## Review Carefully" in report
    assert str(model_path) in report


def test_render_review_report_uses_only_review_buckets(tmp_path: Path) -> None:
    cache_path = tmp_path / ".cache" / "blob.bin"
    cache_path.parent.mkdir()
    cache_path.write_bytes(b"x")
    candidates = build_review_candidates(
        selected_nodes=[
            NormalizedNode(path=str(cache_path), name="blob.bin", is_dir=False, asize=0, dsize=2000)
        ],
        all_nodes=[
            NormalizedNode(path=str(cache_path), name="blob.bin", is_dir=False, asize=0, dsize=2000)
        ],
        protected_prefixes=["/etc", "/usr", "/var/lib"],
        inspection_prefixes=[str(tmp_path)],
        nearby_reference_extensions=[".json"],
        max_nearby_reference_files=5,
    )

    report = render_review_report(root_path=str(tmp_path), candidates=candidates)

    assert "# Review Report" in report
    assert "review first" in report.lower()
    assert "review_bucket" in report

