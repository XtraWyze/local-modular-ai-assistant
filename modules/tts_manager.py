"""Switchable TTS backend helper."""

import json
import importlib

def _coqui():
    return importlib.import_module('modules.tts_integration')

def _gtts():
    return importlib.import_module('modules.gtts_tts')

CONFIG_PATH = "config.json"
try:
    with open(CONFIG_PATH, "r") as f:
        _CFG = json.load(f)
except Exception:
    _CFG = {}

BACKEND = _CFG.get("tts_backend", "coqui")  # "coqui" or "gtts"

__all__ = ["speak", "is_speaking", "stop_speech"]


def speak(text: str, **kwargs):
    if BACKEND == "gtts":
        return _gtts().speak(text, **kwargs)
    return _coqui().speak(text, **kwargs)


def is_speaking() -> bool:
    return _coqui().is_speaking()


def stop_speech():
    return _coqui().stop_speech()


def get_description() -> str:
    return "Routes speak() calls to gTTS or Coqui based on config.tts_backend."
