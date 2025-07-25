import sys
import types

mm = types.ModuleType("memory_manager")
mm.search_memory = lambda q: []
sys.modules["memory_manager"] = mm

import llm_interface


def test_generate_response(monkeypatch):
    def mock_urlopen(req, timeout=0):
        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def read(self):
                return b'{"choices": [{"message": {"content": "ok"}}]}'

        return Resp()

    monkeypatch.setattr(llm_interface.request, "urlopen", mock_urlopen)
    monkeypatch.setattr(llm_interface, "get_module_overview", lambda: {})
    llm_interface.config["llm_backend"] = "localai"
    result = llm_interface.generate_response("hi", history=[])
    assert result == "ok"


def test_generate_response_missing_fields(monkeypatch):
    def mock_urlopen(req, timeout=0):
        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def read(self):
                return b"{}"

        return Resp()

    monkeypatch.setattr(llm_interface.request, "urlopen", mock_urlopen)
    monkeypatch.setattr(llm_interface, "get_module_overview", lambda: {})
    llm_interface.config["llm_backend"] = "localai"
    result = llm_interface.generate_response("hi", history=[])
    assert result.startswith("[LLM Error]")


def test_get_url_override():
    llm_interface.config["llm_url"] = "http://remote:11434/v1/chat/completions"
    assert llm_interface._get_url() == "http://remote:11434/v1/chat/completions"
    llm_interface.config.pop("llm_url", None)
    llm_interface.config["llm_backend"] = "localai"
    assert "localhost" in llm_interface._get_url()


def test_list_models_localai(tmp_path, monkeypatch):
    models_dir = tmp_path / "LocalAI" / "models"
    models_dir.mkdir(parents=True)
    (models_dir / "m1").mkdir()
    (models_dir / "m2.gguf").touch()
    monkeypatch.chdir(tmp_path)
    llm_interface.config["llm_backend"] = "localai"
    assert sorted(llm_interface.list_models()) == ["m1", "m2"]


def test_list_models_ollama(monkeypatch):
    output = "modelA 7B\nmodelB 13B"
    monkeypatch.setattr(
        llm_interface.subprocess,
        "check_output",
        lambda cmd, text=True: output,
    )
    llm_interface.config["llm_backend"] = "ollama"
    assert llm_interface.list_models() == ["modelA", "modelB"]
