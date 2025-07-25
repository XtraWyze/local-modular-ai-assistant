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
