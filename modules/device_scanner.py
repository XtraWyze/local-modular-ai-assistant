"""device_scanner.py
Utilities for discovering network hosts and connected devices.
"""

__all__ = ["list_network_devices", "list_usb_devices"]

import subprocess
import re

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psutil = None

def list_network_devices() -> list[str]:
    """Return IP addresses found in ``arp -a`` output."""
    try:
        output = subprocess.check_output("arp -a", shell=True, text=True)
    except Exception:
        return []
    ips = []
    for line in output.splitlines():
        m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if m:
            ips.append(m.group(1))
    return ips

def list_usb_devices() -> list[str]:
    """Return connected removable drives or USB device names."""
    devices = []
    if psutil is not None:
        try:
            for part in psutil.disk_partitions(all=False):
                opts = getattr(part, "opts", "")
                if "removable" in opts or part.device.lower().startswith("/dev"):
                    devices.append(part.device)
        except Exception:
            pass
        if devices:
            return devices
    try:
        output = subprocess.check_output("lsusb", shell=True, text=True)
        devices = [line.strip() for line in output.splitlines() if line.strip()]
    except Exception:
        devices = []
    return devices


def get_info():
    return {
        "name": "device_scanner",
        "description": "Discover network hosts and connected devices.",
        "functions": ["list_network_devices", "list_usb_devices"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Scan for hosts on the local network and list plugged-in devices."
