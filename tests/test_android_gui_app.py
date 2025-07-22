import pytest

import android_gui_app as aga

if not aga.KIVY_AVAILABLE:
    pytest.skip("kivy not installed", allow_module_level=True)


def test_layout_has_memory(monkeypatch):
    import android_cli_assistant as aca

    monkeypatch.setattr(aca, "load_memory", lambda: {})
    layout = aga.AssistantLayout()
    assert hasattr(layout, "memory")
