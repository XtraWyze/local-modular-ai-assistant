from __future__ import annotations

"""Speech learning tab."""

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

from modules import speech_learning
from tts_manager import speak as tts_speak


@dataclass
class SpeechLearningUI:
    notebook: ttk.Notebook

    def register(self, root: tk.Tk) -> ttk.Frame:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Speech Learning")
        ttk.Label(
            frame,
            text="Practice speaking or teach new wake/sleep phrases. Read the prompts and review the results.",
        ).pack(pady=(10, 5))

        self._make_section(frame)
        return frame

    # --------------------------------------------------------------
    def _make_section(self, frame: ttk.Frame) -> None:
        wake_frame = ttk.Frame(frame)
        wake_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(wake_frame, text="Learn Wake/Sleep", command=self.run_wake_sleep).pack(side=tk.LEFT, padx=(0, 5))
        wake_col = ttk.Frame(wake_frame)
        wake_col.pack(side=tk.LEFT, fill="both", expand=True)
        ttk.Label(wake_col, text="\n".join(speech_learning.WAKE_SLEEP_PROMPTS)).pack(anchor="w")
        self.wake_result = tk.Text(wake_col, height=len(speech_learning.WAKE_SLEEP_PROMPTS), width=60, wrap=tk.WORD)
        self.wake_result.pack(fill="x")

        sentence_frame = ttk.Frame(frame)
        sentence_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(sentence_frame, text="Sentence", command=self.run_sentence).pack(side=tk.LEFT, padx=(0, 5))
        sentence_col = ttk.Frame(sentence_frame)
        sentence_col.pack(side=tk.LEFT, fill="both", expand=True)
        ttk.Label(sentence_col, text="\n".join(speech_learning.SENTENCE_PROMPTS)).pack(anchor="w")
        self.sentence_result = tk.Text(sentence_col, height=len(speech_learning.SENTENCE_PROMPTS), width=60, wrap=tk.WORD)
        self.sentence_result.pack(fill="x")

        paragraph_frame = ttk.Frame(frame)
        paragraph_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(paragraph_frame, text="Paragraph", command=self.run_paragraph).pack(side=tk.LEFT, padx=(0, 5))
        paragraph_col = ttk.Frame(paragraph_frame)
        paragraph_col.pack(side=tk.LEFT, fill="both", expand=True)
        ttk.Label(paragraph_col, text="\n".join(speech_learning.PARAGRAPH_PROMPTS)).pack(anchor="w")
        self.paragraph_result = tk.Text(paragraph_col, height=3, width=60, wrap=tk.WORD)
        self.paragraph_result.pack(fill="x")

    def _set_ro_text(self, widget: tk.Text, text: str) -> None:
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.config(state=tk.DISABLED)

    def _run_learning(self, prompts, widget, update=False):
        self._set_ro_text(widget, "")
        results = speech_learning.read_sentences(prompts, speak_func=tts_speak)
        for heard in results:
            widget.insert(tk.END, heard + "\n")
        if update and len(results) >= 2:
            from phrase_manager import add_wake_phrase, add_sleep_phrase

            widget.insert(tk.END, add_wake_phrase(results[0]) + "\n")
            widget.insert(tk.END, add_sleep_phrase(results[1]) + "\n")

    def run_wake_sleep(self) -> None:
        self._run_learning(speech_learning.WAKE_SLEEP_PROMPTS, self.wake_result, update=True)

    def run_sentence(self) -> None:
        self._run_learning(speech_learning.SENTENCE_PROMPTS, self.sentence_result)

    def run_paragraph(self) -> None:
        self._run_learning(speech_learning.PARAGRAPH_PROMPTS, self.paragraph_result)


def register_gui_tab(notebook: ttk.Notebook, config_loader, output, root):
    return SpeechLearningUI(notebook).register(root)
