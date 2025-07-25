"""Live debug overlay for development insight."""

from __future__ import annotations

import os

try:
    import tkinter as tk
    from tkinter import ttk
except Exception:  # pragma: no cover - Tk may be unavailable
    tk = None
    ttk = None

__all__ = [
    "add_transcript",
    "add_ocr_result",
    "add_command",
    "add_memory_event",
    "DebugOverlay",
]

_MAX = 20
transcripts: list[str] = []
ocr_results: list[str] = []
commands: list[str] = []
memory_events: list[str] = []


def _trim(lst: list[str]) -> None:
    if len(lst) > _MAX:
        del lst[:-_MAX]


def add_transcript(text: str) -> None:
    """Record spoken transcript for the debug panel."""
    transcripts.append(text)
    _trim(transcripts)


def add_ocr_result(text: str) -> None:
    """Record OCR output for the debug panel."""
    ocr_results.append(text)
    _trim(ocr_results)


def add_command(text: str) -> None:
    """Record a command sent to the assistant."""
    commands.append(text)
    _trim(commands)


def add_memory_event(event: str) -> None:
    """Record memory lookup or event."""
    memory_events.append(event)
    _trim(memory_events)


if tk:

    class DebugOverlay(tk.Toplevel):
        """Collapsible live debug overlay."""

        def __init__(self, master: tk.Misc | None = None, refresh_ms: int = 1000) -> None:
            super().__init__(master)
            self.title("Debug Panel")
            self.refresh_ms = refresh_ms
            self.geometry("400x300")
            self.resizable(True, True)
            self.text = tk.Text(self, wrap=tk.WORD, state=tk.DISABLED)
            self.text.pack(fill="both", expand=True)
            self.protocol("WM_DELETE_WINDOW", self.hide)
            self._visible = True
            self.after(self.refresh_ms, self.refresh)

        def hide(self) -> None:
            self.withdraw()
            self._visible = False

        def show(self) -> None:
            self.deiconify()
            self._visible = True
            self.refresh()

        def refresh(self) -> None:
            if not self._visible:
                return
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, "=== Transcribed Speech ===\n")
            for t in transcripts[-10:]:
                self.text.insert(tk.END, f"{t}\n")
            self.text.insert(tk.END, "\n=== OCR Results ===\n")
            for t in ocr_results[-5:]:
                self.text.insert(tk.END, f"{t}\n")
            self.text.insert(tk.END, "\n=== Recent Commands ===\n")
            for t in commands[-10:]:
                self.text.insert(tk.END, f"{t}\n")
            self.text.insert(tk.END, "\n=== Memory Events ===\n")
            for t in memory_events[-10:]:
                self.text.insert(tk.END, f"{t}\n")
            self.text.config(state=tk.DISABLED)
            self.after(self.refresh_ms, self.refresh)
else:

    class DebugOverlay:
        """Fallback no-op overlay when Tkinter is unavailable."""

        def __init__(self, *_, **__) -> None:
            pass

        def hide(self) -> None:  # pragma: no cover - no GUI
            pass

        def show(self) -> None:  # pragma: no cover - no GUI
            pass

        def refresh(self) -> None:  # pragma: no cover - no GUI
            pass

def get_description() -> str:
    """Return a short summary of this module."""
    return (
        "Live debug overlay displaying transcripts, OCR results, recent commands "
        "and memory events."
    )
