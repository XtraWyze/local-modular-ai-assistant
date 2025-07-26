"""LAN auto-discovery utilities using mDNS (zeroconf).

This module allows the assistant's remote server to advertise itself on the
local network so that other devices can find and connect without manual
configuration.

If the optional :mod:`zeroconf` package is missing the functions become
no-ops so the rest of the assistant can still run.
"""

from __future__ import annotations

__all__ = ["LanAdvertiser", "discover_services", "choose_mode_gui"]

import socket
import time
from dataclasses import dataclass
from typing import Dict, Tuple

try:
    from zeroconf import (
        Zeroconf,
        ServiceInfo,
        ServiceBrowser,
        ServiceListener,
    )
except Exception as e:  # pragma: no cover - optional dependency
    Zeroconf = None
    ServiceInfo = None
    ServiceBrowser = None
    ServiceListener = object
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

SERVICE_TYPE = "_moatassist._tcp.local."


def _local_ip() -> str:
    """Return the current machine's LAN IP or ``127.0.0.1``."""
    try:
        # This doesn't actually connect but is enough to get the outgoing IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


@dataclass
class LanAdvertiser:
    """Advertise a remote server via mDNS."""

    name: str
    port: int
    zeroconf: Zeroconf | None = None
    _info: ServiceInfo | None = None

    def start(self) -> None:
        """Start advertising the service."""
        if Zeroconf is None or ServiceInfo is None:
            return
        addr = socket.inet_aton(_local_ip())
        self.zeroconf = Zeroconf()
        self._info = ServiceInfo(
            SERVICE_TYPE,
            f"{self.name}.{SERVICE_TYPE}",
            addresses=[addr],
            port=self.port,
            properties={},
        )
        self.zeroconf.register_service(self._info)

    def stop(self) -> None:
        """Stop advertising."""
        if not self.zeroconf or not self._info:
            return
        try:
            self.zeroconf.unregister_service(self._info)
        finally:
            self.zeroconf.close()
            self.zeroconf = None
            self._info = None


class _Listener(ServiceListener):
    def __init__(self) -> None:
        self.services: Dict[str, Tuple[str, int]] = {}

    def add_service(self, zeroconf: Zeroconf, type_: str, name: str) -> None:  # type: ignore[override]
        info = zeroconf.get_service_info(type_, name)
        if not info or not info.addresses:
            return
        address = socket.inet_ntoa(info.addresses[0])
        self.services[name] = (address, info.port)


def discover_services(timeout: float = 2.0) -> Dict[str, Tuple[str, int]]:
    """Discover advertised assistant servers on the LAN."""
    if Zeroconf is None:
        return {}
    zeroconf = Zeroconf()
    listener = _Listener()
    browser = ServiceBrowser(zeroconf, SERVICE_TYPE, listener)  # noqa: F841
    time.sleep(timeout)
    zeroconf.close()
    return listener.services


def choose_mode_gui() -> str:
    """Return ``"server"`` or ``"client"`` using a tiny GUI if available."""
    # Prefer PySide6 if installed for a modern look
    if _IMPORT_ERROR:
        return "server"
    try:
        from PySide6.QtWidgets import (
            QApplication,
            QPushButton,
            QVBoxLayout,
            QWidget,
            QLabel,
        )
    except Exception:
        try:
            import tkinter as tk  # type: ignore
        except Exception:
            return "server"
        sel = {"mode": "server"}
        root = tk.Tk()
        root.title("LAN Assistant")
        tk.Label(root, text="Select mode").pack(padx=20, pady=10)

        def set_mode(m: str) -> None:
            sel["mode"] = m
            root.destroy()

        tk.Button(root, text="Server", command=lambda: set_mode("server")).pack(fill="x")
        tk.Button(root, text="Client", command=lambda: set_mode("client")).pack(fill="x")
        root.mainloop()
        return sel["mode"]
    else:
        app = QApplication([])
        sel = {"mode": "server"}
        win = QWidget()
        win.setWindowTitle("LAN Assistant")
        lay = QVBoxLayout(win)
        lay.addWidget(QLabel("Select mode"))
        btn_server = QPushButton("Server")
        btn_client = QPushButton("Client")
        lay.addWidget(btn_server)
        lay.addWidget(btn_client)

        def set_server() -> None:
            sel["mode"] = "server"
            app.quit()

        def set_client() -> None:
            sel["mode"] = "client"
            app.quit()

        btn_server.clicked.connect(set_server)
        btn_client.clicked.connect(set_client)
        win.show()
        app.exec()
        return sel["mode"]
