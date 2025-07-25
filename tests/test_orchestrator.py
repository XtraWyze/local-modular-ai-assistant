import sys
import types
import importlib


def test_parse_and_execute_multiple_args(monkeypatch):
    # Create stub tools module with a function requiring two args
    calls = []
    stub_tools = types.ModuleType("modules.tools")

    def stub_click_at(x, y):
        calls.append((x, y))
        return f"clicked {x},{y}"

    stub_tools.click_at = stub_click_at
    stub_tools.__all__ = ["click_at"]
    monkeypatch.setitem(sys.modules, "modules.tools", stub_tools)

    # Stub assistant module providing talk_to_llm
    stub_assistant = types.ModuleType("assistant")
    stub_assistant.talk_to_llm = lambda prompt: "click_at(1, 2)"
    monkeypatch.setitem(sys.modules, "assistant", stub_assistant)

    orch = importlib.reload(importlib.import_module("orchestrator"))

    result = orch.parse_and_execute("please click")
    assert result == "clicked 1,2"
    assert calls == [(1, 2)]


def test_parse_and_execute_invalid_function(monkeypatch):
    stub_tools = types.ModuleType("modules.tools")
    stub_tools.__all__ = ["click_at"]
    stub_tools.click_at = lambda x, y: None
    monkeypatch.setitem(sys.modules, "modules.tools", stub_tools)

    calls = []
    def mock_llm(prompt):
        calls.append(prompt)
        if "Translate" in prompt:
            return "os.system('rm -rf /')"
        return "fallback"

    stub_assistant = types.ModuleType("assistant")
    stub_assistant.talk_to_llm = mock_llm
    monkeypatch.setitem(sys.modules, "assistant", stub_assistant)

    orch = importlib.reload(importlib.import_module("orchestrator"))

    result = orch.parse_and_execute("run bad")
    assert "I don\u2019t know a skill" in result


def test_parse_and_execute_type_validation(monkeypatch):
    stub_tools = types.ModuleType("modules.tools")

    def stub_click_at(x: int, y: int):
        return "done"

    stub_tools.click_at = stub_click_at
    stub_tools.__all__ = ["click_at"]
    monkeypatch.setitem(sys.modules, "modules.tools", stub_tools)

    calls = []

    def mock_llm(prompt):
        calls.append(prompt)
        if "Translate" in prompt:
            return "click_at('a', 'b')"
        return "fallback"

    stub_assistant = types.ModuleType("assistant")
    stub_assistant.talk_to_llm = mock_llm
    monkeypatch.setitem(sys.modules, "assistant", stub_assistant)

    orch = importlib.reload(importlib.import_module("orchestrator"))

    result = orch.parse_and_execute("bad args")
    assert result == "fallback"
    # Ensure fallback was triggered with the original user text
    assert calls[-1] == "bad args"


def test_parse_and_execute_high_risk_denied_when_disabled(monkeypatch):
    """High-risk functions should be blocked when ALLOW_HIGH_RISK=0."""
    stub_tools = types.ModuleType("modules.tools")
    stub_tools.__all__ = ["run_python"]
    stub_tools.run_python = lambda code: "executed"
    monkeypatch.setitem(sys.modules, "modules.tools", stub_tools)

    stub_assistant = types.ModuleType("assistant")
    stub_assistant.talk_to_llm = lambda prompt: "run_python('print(1)')"
    monkeypatch.setitem(sys.modules, "assistant", stub_assistant)
    monkeypatch.setenv("ALLOW_HIGH_RISK", "0")

    orch = importlib.reload(importlib.import_module("orchestrator"))

    result = orch.parse_and_execute("execute code")
    assert "requires elevated privileges" in result


def test_parse_and_execute_high_risk_allowed_by_default(monkeypatch):
    """High-risk functions run when ALLOW_HIGH_RISK is unset."""
    stub_tools = types.ModuleType("modules.tools")
    stub_tools.__all__ = ["run_python"]
    stub_tools.run_python = lambda code: "executed"
    monkeypatch.setitem(sys.modules, "modules.tools", stub_tools)

    stub_assistant = types.ModuleType("assistant")
    stub_assistant.talk_to_llm = lambda prompt: "run_python('print(1)')"
    monkeypatch.setitem(sys.modules, "assistant", stub_assistant)
    monkeypatch.delenv("ALLOW_HIGH_RISK", raising=False)

    orch = importlib.reload(importlib.import_module("orchestrator"))

    result = orch.parse_and_execute("execute code")
    assert result == "executed"


def test_parse_and_execute_create_module(monkeypatch):
    dummy_mod = types.ModuleType("modules.module_generator")
    calls = []

    def dummy_interactive(desc, name=None):
        calls.append((desc, name))
        return "modules/demo_mod.py"

    dummy_mod.generate_module_interactive = dummy_interactive
    dummy_mod.__all__ = ["generate_module_interactive"]
    monkeypatch.setitem(sys.modules, "modules.module_generator", dummy_mod)

    stub_tools = types.ModuleType("modules.tools")
    stub_tools.__all__ = []
    monkeypatch.setitem(sys.modules, "modules.tools", stub_tools)

    stub_assistant = types.ModuleType("assistant")
    stub_assistant.talk_to_llm = lambda prompt: ""
    monkeypatch.setitem(sys.modules, "assistant", stub_assistant)

    orch = importlib.reload(importlib.import_module("orchestrator"))

    result = orch.parse_and_execute("create module demo_mod does things")
    assert result == "modules/demo_mod.py"
    assert calls == [("does things", "demo_mod")]

