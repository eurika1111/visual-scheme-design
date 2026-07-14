#!/usr/bin/env python3
"""Extract thick dark wall pixels and create a source overlay for manual tracing."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a review-only thick-wall mask from a floor-plan image.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--mask-output", type=Path, required=True)
    parser.add_argument("--overlay-output", type=Path, required=True)
    parser.add_argument("--threshold", type=int, default=70)
    parser.add_argument("--minimum-thickness", type=int, default=7)
    args = parser.parse_args()

    source = Image.open(args.source).convert("RGB")
    gray = source.convert("L")
    dark = Image.fromarray(np.where(np.asarray(gray) < args.threshold, 0, 255).astype(np.uint8))
    size = max(3, args.minimum_thickness | 1)
    thick = dark.filter(ImageFilter.MaxFilter(size)).filter(ImageFilter.MinFilter(size))
    mask = np.asarray(thick) == 0

    mask_image = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8), mode="L")
    args.mask_output.parent.mkdir(parents=True, exist_ok=True)
    args.overlay_output.parent.mkdir(parents=True, exist_ok=True)
    mask_image.save(args.mask_output)

    overlay = np.asarray(source).copy()
    overlay[mask] = np.array([220, 38, 38], dtype=np.uint8)
    Image.blend(source, Image.fromarray(overlay), 0.58).save(args.overlay_output)
    print(f"wall_mask={args.mask_output}")
    print(f"wall_overlay={args.overlay_output}")
    print(f"wall_pixels={int(mask.sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
