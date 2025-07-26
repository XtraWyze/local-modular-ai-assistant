"""Example CLI for local Stable Diffusion image generation."""
from __future__ import annotations

import argparse
import os
import webbrowser

import importlib

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Image = None  # type: ignore


def preview_image(path: str) -> None:
    """Open the generated image using Pillow or the default viewer."""
    if Image is not None:
        try:
            img = Image.open(path)
            img.show()
            return
        except Exception:
            pass
    webbrowser.open(f"file://{os.path.abspath(path)}")


def main(argv: list[str] | None = None) -> None:
    """Generate an image from ``argv`` options and show a preview."""
    parser = argparse.ArgumentParser(
        description="Generate a local image using Stable Diffusion"
    )
    parser.add_argument("--prompt", required=True, help="Text prompt for the image")
    parser.add_argument(
        "--model",
        required=True,
        help="Path to the Stable Diffusion model checkpoint",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Torch device string (default selects the best device)",
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Skip showing the image after generation",
    )
    args = parser.parse_args(argv)

    sd_generator = importlib.import_module("modules.stable_diffusion_generator")
    path = sd_generator.generate_image(args.prompt, args.model, device=args.device)
    if path.endswith(".png") and os.path.exists(path):
        print(f"Image saved to {path}")
        if not args.no_preview:
            preview_image(path)
    else:
        print(path)


if __name__ == "__main__":  # pragma: no cover - manual usage
    main()
