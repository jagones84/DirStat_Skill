from pathlib import Path

from safe_delete_advisor.config import load_settings


def test_load_settings_reads_defaults_and_overrides(tmp_path: Path) -> None:
    config_path = tmp_path / "defaults.json"
    config_path.write_text(
        """
        {
          "top_n": 20,
          "min_bytes": 1048576,
          "one_file_system": true,
          "exclude_patterns": [".cache", "node_modules"],
          "risk_do_not_touch_prefixes": ["/etc", "/usr", "/var/lib"],
          "risk_needs_inspection_prefixes": ["/opt", "/srv", "/var/log"],
          "windows_do_not_touch_prefixes": ["C:\\\\Windows", "C:\\\\Program Files"],
          "default_engine_windows": "windows-native",
          "default_engine_linux": "ncdu"
        }
        """.strip(),
        encoding="utf-8",
    )

    settings = load_settings(
        config_path=config_path,
        env_overrides={"TOP_N": "50", "MIN_BYTES": "1073741824"},
    )

    assert settings.top_n == 50
    assert settings.min_bytes == 1073741824
    assert settings.one_file_system is True
    assert settings.exclude_patterns == [".cache", "node_modules"]
    assert settings.windows_do_not_touch_prefixes == ["C:\\Windows", "C:\\Program Files"]
    assert settings.default_engine_windows == "windows-native"
    assert settings.default_engine_linux == "ncdu"
