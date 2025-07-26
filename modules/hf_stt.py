"""Speech recognition using Hugging Face models."""

from __future__ import annotations

import io
import json
from transformers import pipeline
import soundfile as sf
from error_logger import log_error
from . import gpu

CONFIG_PATH = "config.json"
DEFAULT_MODEL = "openai/whisper-small"

try:
    with open(CONFIG_PATH, "r") as f:
        _CFG = json.load(f)
except Exception:
    _CFG = {}

_model = None


def _get_asr():
    """Lazy-load and return the HF ASR pipeline."""
    global _model
    if _model is None:
        model_name = _CFG.get("hf_stt_model", DEFAULT_MODEL)
        device = 0 if gpu.is_available() else -1
        _model = pipeline("automatic-speech-recognition", model=model_name, device=device)
    return _model


def recognize_from_audio(data: bytes) -> str:
    """Return transcribed text from ``data`` containing WAV bytes."""
    try:
        wav, rate = sf.read(io.BytesIO(data))
        asr = _get_asr()
        result = asr(wav, sampling_rate=rate)
        return result.get("text", "").strip()
    except Exception as e:
        log_error(f"[hf_stt] Recognition error: {e}")
        return ""
