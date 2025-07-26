"""Entry point for the modular GUI assistant."""

from __future__ import annotations

try:
    from PIL import Image, ImageDraw  # type: ignore
except Exception:  # pragma: no cover - optional Pillow
    Image = ImageDraw = None  # type: ignore

from gui.app import main as run


def make_icon_image():
    """Return a tray icon image or ``None`` if Pillow is unavailable."""
    if Image is None:
        return None
    img = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(img)
    draw.text((18, 24), "AI", fill="white")
    return img


if __name__ == "__main__":  # pragma: no cover - manual start
    run()
