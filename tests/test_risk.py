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


def test_classify_path_marks_windows_system_paths_as_do_not_touch() -> None:
    assert (
        classify_path(
            "C:\\Windows\\System32",
            ["C:\\Windows", "C:\\Program Files"],
            ["C:\\Users"],
        )
        == "do not touch"
    )


def test_classify_path_marks_windows_temp_as_delete_first() -> None:
    assert (
        classify_path(
            "C:\\Users\\giova\\AppData\\Local\\Temp\\huge.tmp",
            ["C:\\Windows", "C:\\Program Files"],
            ["C:\\Users"],
        )
        == "delete first"
    )


def test_classify_path_marks_windows_temp_directory_as_delete_first() -> None:
    assert (
        classify_path(
            "C:\\Users\\giova\\AppData\\Local\\Temp",
            ["C:\\Windows", "C:\\Program Files"],
            ["C:\\Users"],
        )
        == "delete first"
    )


def test_classify_path_marks_home_assets_as_inspect_before_delete() -> None:
    assert (
        classify_path(
            "/home/jagones/ComfyUI/models/checkpoints/model.safetensors",
            ["/etc", "/usr", "/var/lib"],
            ["/home", "/var/log"],
        )
        == "inspect before delete"
    )


def test_classify_path_marks_linux_cache_directory_as_delete_first() -> None:
    assert (
        classify_path(
            "/home/jagones/.cache",
            ["/etc", "/usr", "/var/lib"],
            ["/home", "/var/log"],
        )
        == "delete first"
    )
