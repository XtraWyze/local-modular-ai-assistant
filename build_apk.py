"""Helper script to build the Android APK using Buildozer."""
from __future__ import annotations

import subprocess
from pathlib import Path


BUILD_COMMAND = ["buildozer", "android", "debug"]
SPEC_FILE = Path("buildozer.spec")


def ensure_spec() -> None:
    """Run ``buildozer init`` if ``buildozer.spec`` does not exist."""
    if not SPEC_FILE.exists():
        subprocess.check_call(["buildozer", "init"])


def build_apk() -> None:
    """Create the APK with Buildozer."""
    ensure_spec()
    subprocess.check_call(BUILD_COMMAND)


if __name__ == "__main__":  # pragma: no cover - manual usage
    build_apk()
