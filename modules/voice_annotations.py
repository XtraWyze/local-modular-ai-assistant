"""Capture voice notes during macro recording and save transcriptions."""

import os

try:
    import speech_recognition as sr
except Exception as e:  # pragma: no cover - optional dependency
    sr = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

from error_logger import log_error

MACRO_DIR = "macros"
MODULE_NAME = "voice_annotations"

__all__ = ["record_annotation"]


def record_annotation(name: str, duration: int = 5) -> str:
    """Record a short voice annotation and save it to ``macros/<name>_annotation.txt``."""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as mic:
            audio = recognizer.listen(mic, phrase_time_limit=duration)
            text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        text = ""
    except Exception as e:  # pragma: no cover - microphone errors
        log_error(f"[{MODULE_NAME}] record_annotation failed: {e}")
        return f"Error recording annotation: {e}"
    os.makedirs(MACRO_DIR, exist_ok=True)
    path = os.path.join(MACRO_DIR, f"{name}_annotation.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path
    except Exception as e:  # pragma: no cover - disk errors
        log_error(f"[{MODULE_NAME}] save failed: {e}")
        return f"Error saving annotation: {e}"


def get_description() -> str:
    return "Record spoken notes and attach them to automation macros."
