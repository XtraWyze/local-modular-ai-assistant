import threading
import tkinter as tk
from assistant import speak


class GuiAssistant:
    """Handle user input for the Tk GUI."""

    def __init__(
        self,
        orchestrator_module,
        chat_log: tk.Text,
        input_box: tk.Entry,
    ) -> None:
        self.orchestrator = orchestrator_module
        self.chat_log = chat_log
        self.input_box = input_box

    def on_user_input(self, text: str, via_voice: bool = False) -> None:
        """Log ``text`` and respond via orchestrator."""

        prefix = "You (voice)" if via_voice else "You"
        self.chat_log.insert(tk.END, f"{prefix}: {text}\n")
        self.chat_log.see(tk.END)
        if not via_voice:
            self.input_box.delete(0, tk.END)

        response = self.orchestrator.parse_and_execute(text, via_voice)
        if response:
            self.chat_log.insert(tk.END, f"Assistant: {response}\n")
            self.chat_log.see(tk.END)
            threading.Thread(
                target=speak,
                args=(response,),
                daemon=True,
            ).start()

    def on_enter_pressed(self, event) -> None:
        text = self.input_box.get()
        self.on_user_input(text, via_voice=False)
