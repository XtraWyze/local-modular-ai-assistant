import importlib
import sys
import types
import time
import threading


def test_busy_timeout_thread_stops(monkeypatch):
    """Worker thread should stop when exceeding BUSY_TIMEOUT."""

    from pathlib import Path
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))

    # Minimal stubs for external modules
    li = types.ModuleType("llm_interface")
    li.generate_response = lambda *a, **kw: "ok"
    monkeypatch.setitem(sys.modules, "llm_interface", li)
    monkeypatch.setitem(sys.modules, "keyboard", types.ModuleType("keyboard"))
    monkeypatch.setitem(sys.modules, "pyautogui", types.ModuleType("pyautogui"))

    mm = types.ModuleType("memory_manager")
    mm.save_memory = lambda mem=None: None
    mm.load_memory = lambda: {}
    mm.store_memory = lambda *a, **kw: None
    mm.search_memory = lambda q: []
    mm.memory = {}
    monkeypatch.setitem(sys.modules, "memory_manager", mm)

    cfgval = types.ModuleType("config_validator")
    cfgval.validate_config = lambda cfg: []
    monkeypatch.setitem(sys.modules, "config_validator", cfgval)

    calls = []
    tts = types.ModuleType("modules.tts_integration")
    tts.speak = lambda text, **kw: calls.append(text)
    tts.is_speaking = lambda: False
    monkeypatch.setitem(sys.modules, "modules.tts_integration", tts)

    monkeypatch.setitem(sys.modules, "modules.window_tools", types.ModuleType("modules.window_tools"))
    monkeypatch.setitem(sys.modules, "modules.vision_tools", types.ModuleType("modules.vision_tools"))

    last = {}
    orig_thread = threading.Thread

    def rec_thread(*args, **kwargs):
        t = orig_thread(*args, **kwargs)
        last["t"] = t
        return t

    monkeypatch.setattr(threading, "Thread", rec_thread)

    assistant = importlib.import_module("assistant")
    importlib.reload(assistant)

    assistant.set_listening(True)

    assistant.BUSY_TIMEOUT = 0.05

    def slow_llm(prompt):
        time.sleep(0.3)
        return "done"

    assistant.talk_to_llm = slow_llm

    class DummyWidget:
        def insert(self, *a, **kw):
            pass

        def see(self, *a, **kw):
            pass

    assistant.process_input("hello", DummyWidget())

    last["t"].join(1.0)
    assert not last["t"].is_alive()
    assert any("lost" in msg for msg in calls)

