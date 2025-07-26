"""Simple launcher enabling LAN discovery for the assistant."""
from __future__ import annotations

import argparse
import time

from lan_discovery import LanAdvertiser, discover_services, choose_mode_gui
from remote_agent import RemoteServer, send_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch assistant with LAN discovery")
    parser.add_argument("--mode", choices=["server", "client"], help="Run as server or client")
    parser.add_argument("--command", default="hello", help="Command to send in client mode")
    parser.add_argument("--timeout", type=float, default=3.0, help="Discovery timeout seconds")
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
            print("No assistant found on LAN")
            return
        # Pick first discovered service
        _name, (host, port) = next(iter(services.items()))
        if send_command(host, port, args.command):
            print(f"Sent '{args.command}' to {host}:{port}")
        else:
            print("Failed to send command")


if __name__ == "__main__":
    main()
