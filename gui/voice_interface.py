"""Abstraction for microphone control and events."""

from __future__ import annotations

import threading
from typing import Callable, List

from modules import voice_input


class VoiceInterface:
    """Wrap ``modules.voice_input`` with a simple event system."""

    def __init__(self, vosk_model_path: str) -> None:
        self.vosk_model_path = vosk_model_path
        self._callbacks: List[Callable[[str], None]] = []

    def on_event(self, callback: Callable[[str], None]) -> None:
        """Register a callback for mic events (``listening_started``/``stopped``)."""
        self._callbacks.append(callback)

    def start_listening(self, output_widget, muted_callback=lambda: False) -> None:
        """Start the hotword listener in a background thread."""
        result = voice_input.start_hotword(
            output_widget, self.vosk_model_path, muted_callback
        )
        if "started" in result:
            for cb in self._callbacks:
                cb("listening_started")

    def stop_listening(self) -> None:
        """Stop the hotword listener."""
        result = voice_input.stop_hotword()
        if "stopped" in result:
            for cb in self._callbacks:
                cb("listening_stopped")
