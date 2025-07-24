import importlib
import json
import os
from pathlib import Path


def setup_api(monkeypatch, tmp_path: Path):
    cfg = {"api_keys": {"openai": "abc", "anthropic": "def"}}
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(cfg))
    api = importlib.import_module("modules.api_keys")
    importlib.reload(api)
    monkeypatch.setattr(api, "_config_loader", api.ConfigLoader(str(cfg_path)), raising=False)
    api._config = api._config_loader.config
    return api, cfg_path


def test_apply_keys(monkeypatch, tmp_path):
    api, _ = setup_api(monkeypatch, tmp_path)
    api.apply_keys_from_config()
    assert os.environ.get("OPENAI_API_KEY") == "abc"
    assert os.environ.get("ANTHROPIC_API_KEY") == "def"


def test_save_keys(monkeypatch, tmp_path):
    api, cfg_path = setup_api(monkeypatch, tmp_path)
    api.save_api_keys({"google": "ghi"})
    saved = json.loads(cfg_path.read_text())
    assert saved["api_keys"]["google"] == "ghi"
    assert os.environ.get("GOOGLE_API_KEY") == "ghi"
