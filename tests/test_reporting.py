from safe_delete_advisor.models import NormalizedNode
from safe_delete_advisor.reporting import build_top_lists


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
