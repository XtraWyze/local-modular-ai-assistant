import json
import os
from config_loader import ConfigLoader
from error_logger import log_error

STATE_FILE = "assistant_state.json"
ACTIONS_FILE = "learned_actions.json"

_DEFAULT_STATE = {"history": [], "conversation_history": [], "resume_phrases": []}
_default_actions = {}

state = _DEFAULT_STATE.copy()
actions = _default_actions.copy()

# Load configuration for phrase persistence
_config_loader = ConfigLoader()

def load_state():
    global state
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = _DEFAULT_STATE.copy()
    # Ensure new keys exist in older state files
    for key, value in _DEFAULT_STATE.items():
        state.setdefault(key, value.copy() if isinstance(value, list) else value)
    return state

def save_state(st=None):
    if st is None:
        st = state
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2)

def update_state(**kwargs):
    state.update(kwargs)
    state.setdefault("history", []).append(kwargs)
    save_state()
    try:
        from modules import debug_panel
        debug_panel.add_memory_event(f"state update: {kwargs}")
    except Exception:
        pass

def load_actions():
    global actions
    if os.path.isfile(ACTIONS_FILE):
        with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
            actions = json.load(f)
    else:
        actions = _default_actions.copy()
    return actions

def save_actions(act=None):
    if act is None:
        act = actions
    with open(ACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(act, f, indent=2)

def register_action(name, path):
    actions[name] = path
    save_actions()

def get_action(name):
    return actions.get(name)


def remove_action(name: str) -> bool:
    """Remove ``name`` from stored actions if present.

    Returns ``True`` if removed, ``False`` otherwise."""
    try:
        if name in actions:
            del actions[name]
            save_actions()
            return True
    except Exception as e:  # pragma: no cover - unexpected error
        log_error(f"[state_manager] remove_action error: {e}")
    return False


def clear_actions() -> None:
    """Delete all registered actions and persist the empty list."""
    actions.clear()
    try:
        save_actions()
    except Exception as e:  # pragma: no cover - file I/O error
        log_error(f"[state_manager] clear_actions error: {e}")


def _update_config_phrase(key: str, phrase: str) -> None:
    """Ensure ``phrase`` is stored under ``key`` in the config file."""
    cfg = _config_loader.config
    phrases = cfg.setdefault(key, [])
    phrase = phrase.lower().strip()
    if phrase and phrase not in phrases:
        phrases.append(phrase)
        try:
            with open(_config_loader.path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            _config_loader.last_modified = os.path.getmtime(_config_loader.path)
        except Exception as e:  # pragma: no cover - file I/O error
            log_error(f"[state_manager] Could not update config: {e}")


def get_resume_phrases() -> list:
    """Return learned resume trigger phrases."""
    return state.setdefault("resume_phrases", [])


def add_resume_phrase(phrase: str) -> str:
    """Add ``phrase`` to ``resume_phrases`` if new and persist state."""
    phrase = phrase.lower().strip()
    phrases = get_resume_phrases()
    if phrase and phrase not in phrases:
        phrases.append(phrase)
        save_state()
        _update_config_phrase("resume_phrases", phrase)
        return f"Learned resume phrase: {phrase}"
    return "Phrase already known"

# Auto-load on import
load_state()
load_actions()
