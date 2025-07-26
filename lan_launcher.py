"""Simple launcher enabling LAN discovery for the assistant."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from lan_discovery import LanAdvertiser, discover_services, choose_mode_gui
from remote_agent import RemoteServer, send_command
from error_logger import log_error


def _show_error(msg: str) -> None:
    """Display an error via Tkinter messagebox if available, else print."""
    log_error(msg)
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("LAN Launcher", msg)
        root.destroy()
    except Exception:
        print(msg)


def _find_client_script(path: str | None = None) -> str | None:
    """Return path to the client GUI script if it exists."""
    if path:
        return path if os.path.isfile(path) else None
    base = Path(__file__).resolve().parent
    for name in ("gui_client.py", "remote_gui_client.py"):
        cand = base / name
        if cand.is_file():
            return str(cand)
    return None


def launch_client_gui(host: str, port: int, client_path: str | None = None) -> bool:
    """Launch the LAN client GUI as a subprocess."""
    script = _find_client_script(client_path)
    if not script:
        _show_error("Client GUI script not found. Please specify --client-path.")
        return False
    cmd = [sys.executable, script, "--host", host, "--port", str(port)]
    try:
        subprocess.Popen(cmd)
    except Exception as exc:  # pragma: no cover - subprocess errors
        _show_error(f"Failed to start client GUI: {exc}")
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch assistant with LAN discovery")
    parser.add_argument("--mode", choices=["server", "client"], help="Run as server or client")
    parser.add_argument("--command", help="Command to send instead of launching GUI")
    parser.add_argument("--timeout", type=float, default=3.0, help="Discovery timeout seconds")
    parser.add_argument("--client-path", help="Path to client GUI script")
    args = parser.parse_args()

    mode = args.mode or choose_mode_gui()

    if mode == "server":
        srv = RemoteServer(host="0.0.0.0", port=0, callback=print)
        srv.start()
        advertiser = LanAdvertiser("AI-Assistant", srv.port)
        advertiser.start()
        print(f"Server running on port {srv.port}. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            advertiser.stop()
            srv.shutdown()
    else:
        services = discover_services(timeout=args.timeout)
        if not services:
            _show_error("No assistant found on LAN")
            return
        _name, (host, port) = next(iter(services.items()))
        if args.command:
            if send_command(host, port, args.command):
                print(f"Sent '{args.command}' to {host}:{port}")
            else:
                _show_error("Failed to send command")
        else:
            launch_client_gui(host, port, args.client_path)


if __name__ == "__main__":
    main()
