import importlib
import sys
from pathlib import Path


def _run_script(name, tmp_path, monkeypatch):
    mod = importlib.import_module(name)
    calls = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mod.subprocess, "check_call", lambda c: calls.append(c))
    monkeypatch.setattr(mod, "VENV_DIR", Path("env"))
    monkeypatch.setattr(sys, "executable", "python")
    mod.main()
    return calls


def test_setup_ollama(monkeypatch, tmp_path):
    calls = _run_script("setup_ollama_env", tmp_path, monkeypatch)
    assert ["python", "-m", "venv", "env"] in calls
    assert any("pip" in cmd for cmd in calls[-2])


def test_setup_opendream(monkeypatch, tmp_path):
    calls = _run_script("setup_opendream_env", tmp_path, monkeypatch)
    assert ["python", "-m", "venv", "env"] in calls
    assert any("diffusers" in " ".join(c) for c in calls)


def test_setup_fastapi(monkeypatch, tmp_path):
    calls = _run_script("setup_fastapi_env", tmp_path, monkeypatch)
    assert ["python", "-m", "venv", "env"] in calls
    assert any("fastapi" in " ".join(c) for c in calls)
