# actions.py

import re

__all__ = ["detect_action", "trigger_action"]

# 1. normalize user text
def normalize(text: str) -> str:
    """Lowercase ``text`` and remove punctuation."""
    text = text.lower()
    # strip punctuation
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# 2. map each “canonical” action to the phrases you want to catch
ACTION_SYNONYMS = {
    "ENTER": [
        "enter", "return", "submit", "confirm",
        "press enter", "hit enter", "press return"
    ],
    "TAB": [
        "tab", "next", "press tab", "hit tab", "move forward"
    ],
    "CLICK": [
        "click", "press click", "hit click", "tap"
    ],
    # …add more: PAGE_DOWN, SCROLL_UP, F5, etc.
}

# 3. scan for a match
def detect_action(user_text: str) -> str | None:
    """Return matching action keyword from ``user_text`` if found."""
    text = normalize(user_text)
    # first try full-phrase
    for action, phrases in ACTION_SYNONYMS.items():
        for phrase in phrases:
            if phrase in text:
                return action
    # then single-word fall‑back
    words = text.split()
    for action, phrases in ACTION_SYNONYMS.items():
        for word in phrases:
            if word in words:
                return action
    return None

def trigger_action(action: str) -> str:
    """Perform a basic keyboard or mouse action."""
    import keyboard
    import pyautogui

    act = action.upper()
    if act == "ENTER":
        keyboard.press_and_release("enter")
        return "Pressed Enter"
    if act == "TAB":
        keyboard.press_and_release("tab")
        return "Pressed Tab"
    if act == "CLICK":
        pyautogui.click()
        return "Clicked Mouse"
    return f"Unknown action: {action}"

def get_info():
    return {
        "name": "actions",
        "description": "Action detection and automation utilities.",
        "functions": ["detect_action", "trigger_action"]
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Utilities to parse user text and trigger basic keyboard or mouse actions."
