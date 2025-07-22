"""Track repeated actions and suggest creating macros."""

from collections import Counter, deque

MODULE_NAME = "macro_suggestions"

_HISTORY_LEN = 20
_actions = deque(maxlen=_HISTORY_LEN)
_suggested = set()

__all__ = ["record_action", "suggest_macros"]


def record_action(action: str) -> None:
    """Record an executed action or command."""
    _actions.append(action)


def suggest_macros(threshold: int = 3) -> list[str]:
    """Return actions occurring ``threshold`` times or more."""
    counts = Counter(_actions)
    suggestions = [act for act, cnt in counts.items() if cnt >= threshold and act not in _suggested]
    _suggested.update(suggestions)
    return suggestions


def get_description() -> str:
    return "Detects repeated actions to recommend new macros."
