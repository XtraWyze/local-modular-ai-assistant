"""Simple client GUI for controlling a remote assistant over LAN.

This mirrors the main GUI layout with an output panel, text entry,
'Pro Mode' toggle and 'Model Selection' tab but sends commands to a
remote :class:`~remote_agent.RemoteServer` instead of running them
locally.
"""

from __future__ import annotations

import argparse
import os
import tkinter as tk
from tkinter import ttk

from lan_discovery import discover_services
from remote_agent import send_command


def send_remote_command(host: str, port: int, text: str) -> bool:
    """Wrapper around :func:`remote_agent.send_command` for tests."""
    return send_command(host, port, text)


class DummyTk:
    """Minimal stand-in used when running tests without a display."""

    def __init__(self) -> None:
        self.tk = self
        self._last_child_ids = {}
        self._w = "."
        self.children = {}

    def __getattr__(self, _name):  # pragma: no cover - used only in tests
        return lambda *a, **k: None


def _create_root() -> tk.Tk:
    if os.environ.get("PYTEST_CURRENT_TEST"):
        root = DummyTk()  # type: ignore[assignment]
        # Mimic tk.Tk behaviour so tk variables work without a real window
        tk._default_root = root  # type: ignore[attr-defined]
        tk._support_default_root = True  # type: ignore[attr-defined]
    else:
        root = tk.Tk()
        root.title("LAN Assistant Client")
        root.geometry("900x650")
    return root


class LanClientGUI:
    """Tkinter GUI that forwards commands to a remote assistant."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.root = _create_root()
        self._build_ui()

    # ---- UI construction -------------------------------------------------
    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both")
        main_tab = ttk.Frame(notebook)
        model_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="Assistant")
        notebook.add(model_tab, text="Model Selection")

        frame = ttk.Frame(main_tab)
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.output = tk.Text(frame, height=20, wrap=tk.WORD, state=tk.DISABLED)
        self.output.pack(fill="both", expand=True)

        entry_frame = ttk.Frame(main_tab)
        entry_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.entry = ttk.Entry(entry_frame)
        self.entry.pack(side=tk.LEFT, fill="x", expand=True)
        self.entry.bind("<Return>", lambda _e: self.send())
        ttk.Button(entry_frame, text="Send", command=self.send).pack(side=tk.LEFT)

        self.pro_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            model_tab,
            text="Pro Mode (use Hugging Face models)",
            variable=self.pro_var,
            command=self._toggle_pro_mode,
        ).pack(anchor="w", padx=10, pady=10)

    # ---- Helper methods --------------------------------------------------
    def _append_output(self, text: str) -> None:
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see("end")
        self.output.config(state=tk.DISABLED)

    def send(self) -> None:
        text = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        if not text:
            return
        self._append_output(f"You: {text}")
        ok = send_remote_command(self.host, self.port, text)
        resp = "sent" if ok else "failed"
        self._append_output(f"Assistant: {resp}")

    def _toggle_pro_mode(self) -> None:
        cmd = "enable pro mode" if self.pro_var.get() else "disable pro mode"
        send_remote_command(self.host, self.port, cmd)
        self._append_output(f"[SYSTEM] {cmd}")

    # ---- Public API ------------------------------------------------------
    def start(self) -> None:  # pragma: no cover - just runs mainloop
        self.root.mainloop()


def _discover_server(timeout: float = 3.0) -> tuple[str, int] | None:
    services = discover_services(timeout=timeout)
    if services:
        _name, (host, port) = next(iter(services.items()))
        return host, port
    return None


def main() -> None:  # pragma: no cover - CLI helper
    parser = argparse.ArgumentParser(description="LAN Assistant Client")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--discover", action="store_true", help="auto-discover server")
    args = parser.parse_args()

    host = args.host
    port = args.port
    if args.discover and (host is None or port is None):
        found = _discover_server()
        if found:
            host, port = found
            print(f"Discovered server at {host}:{port}")

    if host is None or port is None:
        parser.error("host and port required if discovery fails")

    gui = LanClientGUI(host, port)
    gui.start()


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
