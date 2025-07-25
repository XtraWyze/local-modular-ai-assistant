import importlib
import sys
import types


def import_assistant(monkeypatch):
    # Minimal stubs for required modules
    li = types.ModuleType('llm_interface')
    li.generate_response = lambda *a, **kw: 'ok'
    li.DEFAULT_FALLBACK = "fallback"
    monkeypatch.setitem(sys.modules, 'llm_interface', li)
    monkeypatch.setitem(sys.modules, 'keyboard', types.ModuleType('keyboard'))
    monkeypatch.setitem(sys.modules, 'pyautogui', types.ModuleType('pyautogui'))

    mm = types.ModuleType('memory_manager')
    mm.save_memory = lambda mem=None: None
    mm.load_memory = lambda: {}
    mm.store_memory = lambda *a, **kw: None
    mm.search_memory = lambda q: []
    mm.memory = {}
    monkeypatch.setitem(sys.modules, 'memory_manager', mm)

    cfgval = types.ModuleType('config_validator')
    cfgval.validate_config = lambda cfg: []
    monkeypatch.setitem(sys.modules, 'config_validator', cfgval)

    assistant = importlib.import_module('assistant')
    importlib.reload(assistant)
    return assistant, mm


def test_wake_and_sleep(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.set_listening(False)
    assert assistant.check_wake('hey assistant') is True
    assert assistant.is_listening() is True
    assert assistant.check_sleep("ok that's all") is True
    assert assistant.is_listening() is False
    assert assistant.check_wake('next question') is True
    assert assistant.is_listening() is True


def test_handle_recall(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.search_memory = lambda q: ['vector1']
    assistant.assistant_memory = {'note': 'some note'}
    result = assistant.handle_recall('note')
    assert '[Vector Memory]' in result
    assert '- vector1' in result
    assert '[Saved Memory]' in result
    assert 'note: some note' in result


def test_auto_model_selection(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.config["prefer_local_llm"] = "auto"
    monkeypatch.setattr(assistant, "_call_local_llm", lambda p, h: "local")
    monkeypatch.setattr(assistant, "_call_cloud_llm", lambda p: "cloud")
    monkeypatch.setattr(assistant, "_is_bad_response", lambda r: False)
    monkeypatch.setattr(assistant, "_is_complex_prompt", lambda p: True)
    assert assistant.talk_to_llm("hi") == "local"
    monkeypatch.setattr(assistant, "_is_complex_prompt", lambda p: False)
    assert assistant.talk_to_llm("hi") == "local"


def test_poor_local_response_triggers_cloud(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.config["prefer_local_llm"] = True
    assistant.config["min_good_response_words"] = 3
    calls = {"local": 0, "cloud": 0}

    def local(p, h):
        calls["local"] += 1
        return "bad"

    def cloud(p):
        calls["cloud"] += 1
        return "good"

    monkeypatch.setattr(assistant, "_call_local_llm", local)
    monkeypatch.setattr(assistant, "_call_cloud_llm", cloud)
    assert assistant.talk_to_llm("hi") == "bad"
    assert calls == {"local": 1, "cloud": 0}


def test_cloud_first_fallback_to_local(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.config["prefer_local_llm"] = False
    calls = {"local": 0, "cloud": 0}

    def cloud(p):
        calls["cloud"] += 1
        return "[Cloud Error] fail"

    def local(p, h):
        calls["local"] += 1
        return "local-ok"

    monkeypatch.setattr(assistant, "_call_cloud_llm", cloud)
    monkeypatch.setattr(assistant, "_call_local_llm", local)
    assert assistant.talk_to_llm("hello") == "local-ok"
    assert calls == {"local": 1, "cloud": 0}


def test_process_input_chitchat(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.set_listening(True)
    seen = {}

    def mock_llm(prompt):
        seen["text"] = prompt
        return "hi there"

    monkeypatch.setattr(assistant, "talk_to_llm", mock_llm)

    class DummyWidget:
        def insert(self, *a, **kw):
            pass

        def see(self, *a, **kw):
            pass

    assistant.process_input("how are you?", DummyWidget())
    assert seen["text"] == "how are you?"


def test_talk_to_llm_chitchat_local(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.config["prefer_local_llm"] = True
    assistant.config["min_good_response_words"] = 1
    assistant.config["min_good_response_chars"] = 1
    monkeypatch.setattr(assistant, "_call_local_llm", lambda p, h: "local-chat")
    monkeypatch.setattr(assistant, "_call_cloud_llm", lambda p: "cloud-chat")
    assert assistant.talk_to_llm("how are you?") == "local-chat"


def test_talk_to_llm_chitchat_cloud(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.config["prefer_local_llm"] = False
    assistant.config["min_good_response_words"] = 1
    assistant.config["min_good_response_chars"] = 1
    monkeypatch.setattr(assistant, "_call_local_llm", lambda p, h: "local-chat")
    monkeypatch.setattr(assistant, "_call_cloud_llm", lambda p: "cloud-chat")
    assert assistant.talk_to_llm("hello") == "local-chat"


def test_is_chitchat_word_boundary(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    # "hi" inside "this" should not trigger chit-chat detection
    assert assistant.is_chitchat("hi there") is True
    assert assistant.is_chitchat("this is bad") is False


def test_cloud_llm_provider(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    calls = {"google": 0}

    def google(p):
        calls["google"] += 1
        return "google"

    monkeypatch.setattr(assistant, "_call_google_llm", google)

    assert assistant._call_cloud_llm("hi") == "[Cloud Disabled]"
    assert calls == {"google": 0}
