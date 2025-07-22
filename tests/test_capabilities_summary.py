from tests.test_assistant_utils import import_assistant


def test_get_capabilities_summary(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    summary = assistant.get_capabilities_summary()
    assert isinstance(summary, str)
    assert len(summary.splitlines()) >= 3
