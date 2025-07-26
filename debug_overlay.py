"""Optional GUI overlay for debugging assistant state."""

from __future__ import annotations

from typing import List

try:
    import tkinter as tk
except Exception:  # pragma: no cover - tk may be missing
    tk = None

__all__ = [
    "add_transcript",
    "add_ocr_text",
    "add_command",
    "add_memory_recall",
    "DebugOverlay",
]

_transcripts: List[str] = []
_ocr_texts: List[str] = []
_commands: List[str] = []
_memory: List[str] = []
_MAX = 20


def _trim(lst: List[str]) -> None:
    if len(lst) > _MAX:
        del lst[:-_MAX]


def add_transcript(text: str) -> None:
    _transcripts.append(text)
    _trim(_transcripts)


def add_ocr_text(text: str) -> None:
    _ocr_texts.append(text)
    _trim(_ocr_texts)


def add_command(text: str) -> None:
    _commands.append(text)
    _trim(_commands)


def add_memory_recall(text: str) -> None:
    _memory.append(text)
    _trim(_memory)


if tk:

    class DebugOverlay(tk.Toplevel):
        """Floating window showing live debug information."""

        def __init__(self, master: tk.Misc | None = None, refresh_ms: int = 1000) -> None:
            super().__init__(master)
            self.withdraw()
            self.refresh_ms = refresh_ms
            self.title("Debug Overlay")
            self.geometry("600x400")
            self.transient(master)
            self.attributes("-topmost", True)

            self.txt_trans = tk.Text(self, height=5, state=tk.DISABLED)
            self.txt_ocr = tk.Text(self, height=5, state=tk.DISABLED)
            self.txt_cmd = tk.Text(self, height=5, state=tk.DISABLED)
            self.txt_mem = tk.Text(self, height=5, state=tk.DISABLED)

            self.txt_trans.grid(row=0, column=0, sticky="nsew")
            self.txt_ocr.grid(row=0, column=1, sticky="nsew")
            self.txt_mem.grid(row=1, column=0, columnspan=2, sticky="nsew")
            self.txt_cmd.grid(row=2, column=0, columnspan=2, sticky="nsew")

            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)
            self.grid_rowconfigure(2, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

            self._visible = False
            self.after(self.refresh_ms, self.refresh)

        def toggle(self) -> None:
            if self._visible:
                self.withdraw()
                self._visible = False
            else:
                self.deiconify()
                self._visible = True
                self.refresh()

        def refresh(self) -> None:
            if not self._visible:
                self.after(self.refresh_ms, self.refresh)
                return
            self._update_text(self.txt_trans, _transcripts, "Transcription")
            self._update_text(self.txt_ocr, _ocr_texts, "OCR")
            self._update_text(self.txt_cmd, _commands, "Commands")
            self._update_text(self.txt_mem, _memory, "Memory")
            self.after(self.refresh_ms, self.refresh)

        def _update_text(self, widget: tk.Text, data: List[str], title: str) -> None:
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert(tk.END, f"=== {title} ===\n")
            for item in data[-5:]:
                widget.insert(tk.END, f"{item}\n")
            widget.config(state=tk.DISABLED)

else:

    class DebugOverlay:
        def __init__(self, *_, **__) -> None:
            self._visible = False

        def toggle(self) -> None:  # pragma: no cover - no GUI
            self._visible = not self._visible

        def refresh(self) -> None:  # pragma: no cover - no GUI
            pass
