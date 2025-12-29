import os
from pathlib import Path
import yaml

from pipboy.main import ensure_config, CONFIG_PATH


def test_config_generated(tmp_path, monkeypatch):
    # Point config path to tmp and run ensure_config
    monkeypatch.setattr("pipboy.main.CONFIG_PATH", tmp_path / "config.yaml")
    ensure_config()
    assert (tmp_path / "config.yaml").exists()
    data = yaml.safe_load((tmp_path / "config.yaml").read_text())
    assert "theme" in data
