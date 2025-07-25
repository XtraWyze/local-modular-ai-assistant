import re
from pathlib import Path


def test_htmlframe_messages_disabled():
    text = Path("gui_assistant.py").read_text()
    pattern = re.compile(r"HtmlFrame\(.*messages_enabled=False")
    assert pattern.search(text), "HtmlFrame should disable debug messages"
