import sys
import threading
import traceback

from error_logger import log_error

_speak = lambda *_args, **_kwargs: None
_ready_cb = None


def _handle_exception(exc_type, exc, tb):
    """Handle uncaught exceptions by logging and announcing."""
    stack = "".join(traceback.format_exception(exc_type, exc, tb))
    log_error(f"Unhandled exception: {exc}", context=stack)
    try:
        _speak("Crash prevented. I'm ready again.")
    except Exception:
        pass
    if _ready_cb:
        try:
            _ready_cb()
        except Exception as ready_exc:  # pragma: no cover - callback failure
            log_error(f"Crash handler callback failed: {ready_exc}")


def setup_crash_handler(speak_func, ready_callback=None):
    """Install global hooks to prevent crashes."""
    global _speak, _ready_cb
    _speak = speak_func
    _ready_cb = ready_callback
    sys.excepthook = _handle_exception
    if hasattr(threading, "excepthook"):
        def _thread_hook(args):
            _handle_exception(args.exc_type, args.exc_value, args.exc_traceback)
        threading.excepthook = _thread_hook


def get_description() -> str:
    return "Global exception hook that logs errors and announces recovery."
