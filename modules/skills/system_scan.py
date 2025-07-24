"""System scan skill for summarizing current environment."""

from __future__ import annotations

import os
from typing import Any


def _safe_import(module: str) -> Any:
    """Return imported module or ``None`` if unavailable."""
    try:
        return __import__(module, fromlist=["*"])  # type: ignore
    except Exception:
        return None


def run(params: dict) -> str:
    """Summarize open windows, browser tabs, working directory and next appointment."""
    windows = []
    window_mod = _safe_import("modules.window_tools")
    if window_mod and hasattr(window_mod, "list_open_windows"):
        try:
            windows = window_mod.list_open_windows()
        except Exception:
            windows = []

    tab_count = None
    browser_mod = _safe_import("modules.browser_automation")
    if browser_mod:
        if hasattr(browser_mod, "count_tabs"):
            try:
                tab_count = browser_mod.count_tabs()
            except Exception:
                tab_count = None
        elif hasattr(browser_mod, "_driver") and browser_mod._driver:
            try:
                tab_count = len(browser_mod._driver.window_handles)
            except Exception:
                tab_count = None

    cwd = os.getcwd()

    next_appt = "N/A"
    calendar_mod = _safe_import("modules.calendar_tools")
    if calendar_mod and hasattr(calendar_mod, "get_next_appointment"):
        try:
            next_appt = calendar_mod.get_next_appointment()
        except Exception:
            next_appt = "N/A"

    clipboard_text = None
    actions_mod = _safe_import("modules.automation_actions")
    if actions_mod and hasattr(actions_mod, "get_clipboard"):
        try:
            clipboard_text = actions_mod.get_clipboard()
        except Exception:
            clipboard_text = None

    net_devices: list[str] | None = None
    usb_devices: list[str] | None = None
    dev_mod = _safe_import("modules.device_scanner")
    if dev_mod:
        try:
            net_devices = dev_mod.list_network_devices()
        except Exception:
            net_devices = None
        try:
            usb_devices = dev_mod.list_usb_devices()
        except Exception:
            usb_devices = None

    summary_lines = [f"Open windows: {len(windows)}"]
    if windows:
        summary_lines.append("Window titles: " + ", ".join(windows[:5]))
    summary_lines.append(f"Browser tabs: {tab_count if tab_count is not None else 'N/A'}")
    summary_lines.append(f"Working directory: {cwd}")
    summary_lines.append(f"Next appointment: {next_appt}")
    if clipboard_text is not None:
        short_clip = clipboard_text[:30]
        if len(clipboard_text) > 30:
            short_clip += "..."
        summary_lines.append(f"Clipboard: {short_clip}")
    if net_devices is not None:
        summary_lines.append(f"Network devices detected: {len(net_devices)}")
    if usb_devices is not None:
        summary_lines.append(f"USB devices detected: {len(usb_devices)}")

    return "\n".join(summary_lines)
