"""trigger_words.py
Lists trigger words that map to built-in modules.
"""

TRIGGERS = {
    "actions": ["enter", "tab", "click"],
    "automation_actions": ["drag", "resize", "clipboard"],
    "browser_automation": ["open browser", "search"],
    "device_scanner": ["scan devices", "list usb"],
    "voice_input": ["listen", "mute", "unmute"],
    "tts_integration": ["volume", "speed", "voice"],
}


def get_trigger_words() -> dict:
    """Return mapping of module names to trigger words."""
    return TRIGGERS


def get_description() -> str:
    """Return a short description of this module."""
    return "Defines useful trigger words for quick command detection."
