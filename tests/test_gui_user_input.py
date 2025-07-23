



from types import SimpleNamespace

from gui_assistant_core import GuiAssistant


class DummyOrchestrator:
    def __init__(self):
        self.calls = []


    def parse_and_execute(self, text, via_voice=False):
        self.calls.append((text, via_voice))
        return "ok"




class DummyText:
    def __init__(self):
        self.data = ""
    def insert(self, _pos, text):
        self.data += text
    def see(self, _pos):
        pass
    def get(self, *_):
        return self.data


class DummyEntry(DummyText):
    def delete(self, *_):
        self.data = ""

    def insert(self, _pos, text):
        self.data = text + self.data


def test_on_user_input_typing():
    log = DummyText()
    entry = DummyEntry()
    entry.insert(0, "hi")
    orch = DummyOrchestrator()
    gui = GuiAssistant(orch, log, entry)
    gui.on_user_input("hello", via_voice=False)
    assert "You: hello" in log.get()
    assert "Assistant: ok" in log.get()
    assert entry.get() == ""
    assert orch.calls == [("hello", False)]


def test_on_user_input_voice():
    log = DummyText()
    entry = DummyEntry()
    entry.insert(0, "keep")
    orch = DummyOrchestrator()
    gui = GuiAssistant(orch, log, entry)
    gui.on_user_input("hello", via_voice=True)
    assert "You (voice): hello" in log.get()

    assert "Assistant: ok" in log.get()
    assert entry.get() == "keep"
    assert orch.calls == [("hello", True)]

    assert entry.get() == "keep"
    assert orch.calls == [("hello", True)]



