import json
import os
import yaml
from config_loader import ConfigLoader
from error_logger import log_error

STATE_FILE = "assistant_state.json"
ACTIONS_FILE = "learned_actions.json"
MACRO_MAP_FILE = "learned_macros.yaml"

_DEFAULT_STATE = {"history": [], "conversation_history": [], "resume_phrases": []}
_default_actions = {}

state = _DEFAULT_STATE.copy()
actions = _default_actions.copy()
macro_map: dict[str, str] = {}

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

def load_actions():
    global actions
    if os.path.isfile(ACTIONS_FILE):
        with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
            actions = json.load(f)
    else:
        actions = _default_actions.copy()
    return actions


def load_macro_map() -> dict:
    """Load command-to-action mappings from :data:`MACRO_MAP_FILE`."""
    global macro_map
    if os.path.isfile(MACRO_MAP_FILE):
        with open(MACRO_MAP_FILE, "r", encoding="utf-8") as f:
            macro_map = yaml.safe_load(f) or {}
    else:
        macro_map = {}
    return macro_map

def save_actions(act=None):
    if act is None:
        act = actions
    with open(ACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(act, f, indent=2)


def save_macro_map(data: dict | None = None) -> None:
    """Persist ``data`` or current map to :data:`MACRO_MAP_FILE`."""
    if data is None:
        data = macro_map
    with open(MACRO_MAP_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

def register_action(name, path):
    actions[name] = path
    save_actions()


def register_macro_command(command: str, action: str) -> str:
    """Map a spoken ``command`` to an ``action`` (macro name)."""
    cmd = command.strip().lower()
    macro_map[cmd] = action.strip()
    save_macro_map()
    return f"Learned macro: '{cmd}' -> {action.strip()}"

def get_action(name):
    return actions.get(name)


def get_macro_action(command: str) -> str | None:
    """Return the macro mapped to ``command`` if any."""
    return macro_map.get(command.strip().lower())


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


def remove_macro_command(command: str) -> bool:
    """Remove stored mapping for ``command`` if present."""
    cmd = command.strip().lower()
    if cmd in macro_map:
        try:
            del macro_map[cmd]
            save_macro_map()
            return True
        except Exception as e:  # pragma: no cover - unexpected error
            log_error(f"[state_manager] remove_macro_command error: {e}")
    return False


def clear_actions() -> None:
    """Delete all registered actions and persist the empty list."""
    actions.clear()
    try:
        save_actions()
    except Exception as e:  # pragma: no cover - file I/O error
        log_error(f"[state_manager] clear_actions error: {e}")


def clear_macro_commands() -> None:
    """Delete all command mappings and persist the empty file."""
    macro_map.clear()
    try:
        save_macro_map()
    except Exception as e:  # pragma: no cover - file I/O error
        log_error(f"[state_manager] clear_macro_commands error: {e}")


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
load_macro_map()
