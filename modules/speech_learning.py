"""Simple speech recognition practice module."""

MODULE_NAME = "speech_learning"

try:
    import speech_recognition as sr
except Exception as e:  # pragma: no cover - optional dependency
    sr = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

from typing import Iterable, List, Callable, Optional
import time
from error_logger import log_error

DEFAULT_SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "I am training my personal assistant.",
]

# Predefined prompt sets for the GUI speech learning tab
WAKE_SLEEP_PROMPTS = [
    "Wake up",
    "Go to sleep",
]

SENTENCE_PROMPTS = [
    "The quick brown fox jumps over the lazy dog.",
]

PARAGRAPH_PROMPTS = [
    (
        "This is a longer paragraph for speech training. "
        "It helps the assistant learn your voice over extended text."
    )
]

__all__ = [
    "read_sentences",
    "learn_wake_sleep",
    "WAKE_SLEEP_PROMPTS",
    "SENTENCE_PROMPTS",
    "PARAGRAPH_PROMPTS",
]

def read_sentences(
    sentences: Optional[Iterable[str]] = None,
    recognizer: Optional[object] = None,
    microphone: Optional[object] = None,
    speak_func: Optional[Callable[[str], None]] = None,
    pause_secs: float = 1.0,
    cancel_after: float = 25.0,
) -> List[str]:
    """Prompt the user to read each sentence and return transcriptions.

    Parameters
    ----------
    sentences : Iterable[str], optional
        Sentences to read. Defaults to ``DEFAULT_SENTENCES``.
    recognizer : object, optional
        ``speech_recognition.Recognizer`` or compatible instance. If ``None``,
        a new ``Recognizer`` is created.
    microphone : object, optional
        ``speech_recognition.Microphone`` or compatible context manager.
    speak_func : Callable[[str], None], optional
        Optional TTS function to announce each sentence.
    pause_secs : float, optional
        Seconds to pause between prompts. Defaults to ``1.0``.
    cancel_after : float, optional
        Abort if no speech is detected for this many seconds. Defaults to ``25``.

    Returns
    -------
    list[str]
        Recognized text for each sentence (empty string on failure).
    """
    sents = list(sentences or DEFAULT_SENTENCES)
    if recognizer is None:
        if sr is None:
            return ["" for _ in sents]
        recognizer = sr.Recognizer()
    mic_cm = microphone if microphone is not None else (sr.Microphone() if sr else None)
    results: List[str] = []

    if mic_cm is None:
        return ["" for _ in sents]

    try:
        with mic_cm as mic:
            for text in sents:
                if speak_func:
                    try:
                        speak_func(f"Please read: {text}")
                    except Exception:
                        pass

                recognized = ""
                start = time.time()

                while not recognized and time.time() - start < cancel_after:
                    try:
                        audio = recognizer.listen(mic, timeout=1, phrase_time_limit=6)
                        recognized = recognizer.recognize_google(audio)
                    except Exception as exc:  # pragma: no cover - microphone/STT errors
                        log_error(f"[{MODULE_NAME}] recognition error: {exc}")
                        recognized = ""

                if not recognized:
                    log_error(f"[{MODULE_NAME}] cancelled after inactivity")
                    results.append("")
                    break

                results.append(recognized)

                if pause_secs:
                    time.sleep(pause_secs)
    except Exception as exc:  # pragma: no cover - mic open error
        log_error(f"[{MODULE_NAME}] microphone error: {exc}")
        results.extend(["" for _ in range(len(sents) - len(results))])

    return results


def learn_wake_sleep(
    recognizer: Optional[object] = None,
    microphone: Optional[object] = None,
    speak_func: Optional[Callable[[str], None]] = None,
) -> List[str]:
    """Learn custom wake and sleep phrases.

    The first recognized phrase is added as a wake phrase and the second
    as a sleep phrase using :mod:`phrase_manager`.

    Parameters
    ----------
    recognizer, microphone, speak_func : see :func:`read_sentences`

    Returns
    -------
    list[str]
        Recognized phrases in order.
    """

    results = read_sentences(
        WAKE_SLEEP_PROMPTS,
        recognizer=recognizer,
        microphone=microphone,
        speak_func=speak_func,
    )
    if len(results) >= 2 and results[0] and results[1]:
        try:
            from phrase_manager import add_wake_phrase, add_sleep_phrase

            add_wake_phrase(results[0])
            add_sleep_phrase(results[1])
        except Exception as exc:  # pragma: no cover - optional dependency
            log_error(f"[{MODULE_NAME}] phrase update failed: {exc}")
    return results


def get_info() -> dict:
    return {
        "name": MODULE_NAME,
        "description": get_description(),
        "functions": ["read_sentences", "learn_wake_sleep"],
    }


def get_description() -> str:
    """Return a short description for discovery."""
    return "Practice speech recognition by reading sample sentences."


def register(registry=None):
    from module_manager import ModuleRegistry

    registry = registry or ModuleRegistry()
    registry.register(
        MODULE_NAME,
        {
            "read_sentences": read_sentences,
            "learn_wake_sleep": learn_wake_sleep,
            "get_info": get_info,
        },
    )

# register()
