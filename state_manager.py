import json
import os

STATE_FILE = "assistant_state.json"
ACTIONS_FILE = "learned_actions.json"

_DEFAULT_STATE = {"history": [], "conversation_history": [], "resume_phrases": []}
_default_actions = {}

state = _DEFAULT_STATE.copy()
actions = _default_actions.copy()

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
        return f"Learned resume phrase: {phrase}"
    return "Phrase already known"

# Auto-load on import
load_state()
load_actions()
