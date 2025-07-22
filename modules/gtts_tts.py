"""Google TTS based speaker used when online."""

try:
    from gtts import gTTS
    import playsound
except Exception as e:  # pragma: no cover - optional dependency
    gTTS = None
    playsound = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

import os
import tempfile
from error_logger import log_error

MODULE_NAME = "gtts_tts"

__all__ = ["speak"]

def speak(text: str, lang: str = 'en') -> str:
    """Speak ``text`` using Google TTS online service."""
    if gTTS is None:
        return f"gTTS not available: {_IMPORT_ERROR}"
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp = tmp_file.name
    tmp_file.close()
    try:
        gTTS(text, lang=lang).save(tmp)
        playsound.playsound(tmp)
    except Exception as e:
        log_error(f"[gtts_tts] TTS error: {e}")
        return f"TTS error: {e}"
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return "spoke"


def get_description() -> str:
    return "Online gTTS speech synthesis for fallback when offline TTS is missing."
