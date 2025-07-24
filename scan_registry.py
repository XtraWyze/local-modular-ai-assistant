"""Maintain system, device and network scan results."""

from __future__ import annotations

import json
import os
from typing import Any

SYSTEM_FILE = "system_registry.json"
DEVICE_FILE = "device_registry.json"
NETWORK_FILE = "network_registry.json"

system_data: dict[str, Any] = {}
device_data: list[str] = []
network_data: list[str] = []


def _load(path: str) -> Any:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def _save(path: str, data: Any) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def load() -> None:
    """Load registries from disk if available."""
    global system_data, device_data, network_data
    system_data = _load(SYSTEM_FILE) or {}
    device_data = _load(DEVICE_FILE) or []
    network_data = _load(NETWORK_FILE) or []


def refresh_system() -> dict[str, Any]:
    """Run a full system scan and store the result."""
    from modules import system_scan
    try:
        import psutil
        import socket
    except Exception:  # pragma: no cover - psutil optional
        psutil = None

    summary = None
    if system_scan:
        try:
            summary = system_scan.run({})
        except Exception:
            summary = None

    metrics: dict[str, Any] = {}
    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            vm = psutil.virtual_memory()
            disks = []
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                except Exception:
                    continue
                disks.append({
                    "mountpoint": part.mountpoint,
                    "total": usage.total,
                    "percent": usage.percent,
                })
            net = []
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        net.append({"interface": iface, "address": addr.address})
            metrics = {
                "cpu": {"percent": cpu_percent},
                "memory": {
                    "total": vm.total,
                    "available": vm.available,
                    "percent": vm.percent,
                },
                "disks": disks,
                "network": net,
            }
        except Exception:
            metrics = {}
    system_data.update({"summary": summary, "metrics": metrics})
    _save(SYSTEM_FILE, system_data)
    return system_data


def refresh_devices() -> list[str]:
    """Scan connected USB devices and store the result."""
    try:
        from modules.device_scanner import list_usb_devices

        devices = list_usb_devices()
    except Exception:
        devices = []
    device_data.clear()
    device_data.extend(devices)
    _save(DEVICE_FILE, device_data)
    return device_data


def refresh_network() -> list[str]:
    """Scan the local network and store discovered hosts."""
    try:
        from modules.device_scanner import list_network_devices

        hosts = list_network_devices()
    except Exception:
        hosts = []
    network_data.clear()
    network_data.extend(hosts)
    _save(NETWORK_FILE, network_data)
    return network_data


def refresh_all() -> None:
    """Refresh all scan registries."""
    refresh_system()
    refresh_devices()
    refresh_network()


def initialize() -> None:
    """Load registries from disk without scanning."""
    load()


