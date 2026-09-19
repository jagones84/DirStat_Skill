from safe_delete_advisor.risk import classify_path


def test_classify_path_marks_system_prefix_as_do_not_touch() -> None:
    assert (
        classify_path(
            "/var/lib/docker",
            ["/etc", "/usr", "/var/lib"],
            ["/home", "/var/log"],
        )
        == "do not touch"
    )
