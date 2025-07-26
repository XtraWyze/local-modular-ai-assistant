"""Text-to-speech using Hugging Face models."""

from __future__ import annotations

import json
import threading
from transformers import pipeline
import sounddevice as sd
from error_logger import log_error
from . import gpu

CONFIG_PATH = "config.json"
DEFAULT_MODEL = "facebook/fastspeech2-en-ljspeech"

try:
    with open(CONFIG_PATH, "r") as f:
        _CFG = json.load(f)
except Exception:
    _CFG = {}

_tts = None


def _get_tts():
    """Lazy-load and return the HF TTS pipeline."""
    global _tts
    if _tts is None:
        model_name = _CFG.get("hf_tts_model", DEFAULT_MODEL)
        device = 0 if gpu.is_available() else -1
        _tts = pipeline("text-to-speech", model=model_name, device=device)
    return _tts


def speak(text: str, async_play: bool = True):
    """Speak ``text`` using a Hugging Face model."""
    try:
        tts = _get_tts()
        out = tts(text)
        audio = out["audio"]
        rate = out["sampling_rate"]

        def _play():
            try:
                sd.play(audio, rate)
                sd.wait()
            except Exception as e:
                log_error(f"[hf_tts] Playback error: {e}")

        if async_play:
            threading.Thread(target=_play, daemon=True).start()
        else:
            _play()
        return "spoke"
    except Exception as e:
        log_error(f"[hf_tts] Error: {e}")
        return f"[hf_tts error] {e}"
