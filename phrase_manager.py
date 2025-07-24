import json
from typing import Any
from error_logger import log_error

CONFIG_PATH = "config.json"
MODULE_NAME = "phrase_manager"


def _load_all() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # pragma: no cover - I/O error
        log_error(f"[{MODULE_NAME}] Could not load config: {e}")
        return {}


def _save_all(cfg: dict) -> bool:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        return True
    except Exception as e:  # pragma: no cover - I/O error
        log_error(f"[{MODULE_NAME}] Could not update config: {e}")
        return False


config = _load_all()


def _add_phrase(key: str, phrase: str) -> str:
    phrase = phrase.lower().strip()
    cfg_list = config.setdefault(key, [])
    if not phrase or phrase in cfg_list:
        return "Phrase already known"
    cfg_list.append(phrase)
    all_cfg = _load_all() or {}
    all_cfg.setdefault(key, [])
    if phrase not in all_cfg[key]:
        all_cfg[key].append(phrase)
    if _save_all(all_cfg):
        config[key] = all_cfg[key]
        return f"Added {key[:-8] if key.endswith('_phrases') else key} phrase: {phrase}"
    cfg_list.pop()
    return "Failed to update config"


def add_wake_phrase(phrase: str) -> str:
    """Persist ``phrase`` to ``wake_phrases`` list in config."""
    return _add_phrase("wake_phrases", phrase)


def add_sleep_phrase(phrase: str) -> str:
    """Persist ``phrase`` to ``sleep_phrases`` list in config."""
    return _add_phrase("sleep_phrases", phrase)


def add_cancel_phrase(phrase: str) -> str:
    """Persist ``phrase`` to ``cancel_phrases`` list in config."""
    return _add_phrase("cancel_phrases", phrase)
