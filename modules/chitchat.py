"""Helper functions for small talk and LLM interaction."""

import re

from modules.long_term_storage import save_entry

# Config will be resolved lazily from the assistant module
config = None

# Simple list of greetings and small-talk phrases
CHITCHAT_PHRASES = [
    "hello",
    "hi",
    "hey",
    "how are you",
    "how's it going",
    "how is your day",
    "what's up",
]

# Precompiled regex patterns for chit-chat detection
_CHITCHAT_PATTERNS = [re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE) for p in CHITCHAT_PHRASES]

# Persistent memory for last prompt/response (lazy loaded)
assistant_memory = None
conversation_history = None


def is_chitchat(text: str) -> bool:
    """Return True if ``text`` looks like casual conversation."""
    return any(p.search(text) for p in _CHITCHAT_PATTERNS)


def talk_to_llm(prompt: str) -> str:
    """Send ``prompt`` to the local LLM."""

    from assistant import _call_local_llm, _is_complex_prompt
    from memory_manager import save_memory, load_memory, store_memory
    from state_manager import update_state, save_state, state as state_dict

    try:
        global assistant_memory, conversation_history, config
        from assistant import config as cfg
        config = cfg
        if assistant_memory is None:
            assistant_memory = load_memory()
        conversation_history = state_dict.setdefault("conversation_history", [])
        save_state()
        max_hist = config.get("conversation_history_limit", 6)
        conversation_history.append({"role": "user", "content": prompt})
        state_dict["conversation_history"] = conversation_history
        save_state()
        history = conversation_history[-max_hist:]

        prefer = config.get("prefer_local_llm", True)
        response = None

        def record(resp: str) -> str:
            conversation_history.append({"role": "assistant", "content": resp})
            state_dict["conversation_history"] = conversation_history
            save_state()
            store_memory(prompt, resp)
            save_entry(f"Q: {prompt}\nA: {resp}")
            assistant_memory["last_prompt"] = prompt
            assistant_memory["last_response"] = resp
            save_memory(assistant_memory)
            update_state(last_prompt=prompt, last_response=resp)
            return resp

        if prefer == "auto":
            prefer = True

        response = _call_local_llm(prompt, history)

        return record(response)
    except Exception as e:  # pragma: no cover - unexpected failures
        return f"Error with local model: {e}"


def get_description() -> str:
    """Return a short summary of this module."""
    return "Chit-chat detection helpers and LLM conversation wrapper."


def get_info() -> dict:
    return {
        "name": "chitchat",
        "description": "Identify casual chat and route prompts to an LLM.",
        "functions": ["is_chitchat", "talk_to_llm"],
    }
