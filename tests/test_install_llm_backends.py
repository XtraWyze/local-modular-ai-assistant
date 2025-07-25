import pytest
import importlib
from pathlib import Path
import sys

import install_llm_backends


def test_clone_repo_git_missing(monkeypatch, capsys, tmp_path):
    def raise_fn(cmd):
        raise FileNotFoundError()

    monkeypatch.setattr(install_llm_backends.subprocess, "check_call", raise_fn)
    with pytest.raises(SystemExit) as excinfo:
        install_llm_backends.clone_repo("url", tmp_path / "repo")
    assert excinfo.value.code != 0
    out = capsys.readouterr().out
    assert "Git not found" in out


def test_main_ollama(monkeypatch):
    calls = []

    def mock_clone(url, dest):
        calls.append((url, dest))

    monkeypatch.setattr(install_llm_backends, "clone_repo", mock_clone)
    monkeypatch.setattr(sys, "argv", ["install_llm_backends.py", "--ollama"])
    install_llm_backends.main()
    assert calls == [(
        install_llm_backends.REPOS["ollama"],
        Path("ollama"),
    )]

