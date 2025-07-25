"""Remote agent for sending and receiving commands over HTTP."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable

from urllib import request


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(data)
            cmd = payload.get("command")
            if self.server.callback and cmd:
                self.server.callback(cmd)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as exc:  # pragma: no cover - error path
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(exc).encode("utf-8"))


class RemoteServer:
    """Simple HTTP server for receiving commands.

    Parameters
    ----------
    host : str, optional
        Host interface to bind to. Defaults to ``"127.0.0.1"`` to restrict
        connections to the local machine.
    port : int, optional
        TCP port to listen on. ``0`` chooses a random free port.
    callback : Callable[[str], None] | None, optional
        Function invoked with each received command.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 0, callback: Callable[[str], None] | None = None):
        self.server = HTTPServer((host, port), _Handler)
        self.server.callback = callback
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def port(self) -> int:
        return self.server.server_port

    def start(self):
        self.thread.start()

    def shutdown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()


def send_command(host: str, port: int, command: str) -> bool:
    """Send ``command`` to the remote server at ``host:port``."""
    url = f"http://{host}:{port}/"
    data = json.dumps({"command": command}).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False
