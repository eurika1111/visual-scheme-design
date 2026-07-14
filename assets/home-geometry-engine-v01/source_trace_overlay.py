#!/usr/bin/env python3
"""Draw traced wall centerlines and room polygons directly over the source plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


COLORS = [(14, 165, 233, 48), (34, 197, 94, 42), (249, 115, 22, 42), (168, 85, 247, 38)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a source-image trace overlay.")
    parser.add_argument("trace_spec", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.trace_spec.read_text(encoding="utf-8-sig"))
    source = Image.open(args.source).convert("RGBA")
    layer = Image.new("RGBA", source.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    for index, room in enumerate(spec.get("rooms", [])):
        points = [tuple(value) for value in room["polygon_px"]]
        color = COLORS[index % len(COLORS)]
        draw.polygon(points, fill=color, outline=(color[0], color[1], color[2], 180), width=2)
    for wall in spec.get("walls", []):
        draw.line(
            [tuple(wall["start_px"]), tuple(wall["end_px"])],
            fill=(0, 190, 255, 235), width=3,
        )
    for opening in spec.get("openings", []):
        x, y = opening["position_px"]
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 235, 59, 245), outline=(120, 80, 0, 255), width=1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(source, layer).convert("RGB").save(args.output)
    print(f"trace_overlay={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
