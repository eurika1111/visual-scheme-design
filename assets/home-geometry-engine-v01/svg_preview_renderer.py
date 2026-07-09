#!/usr/bin/env python3
"""Rasterize project-generated SVG files to PNG previews without a browser.

This is intentionally small and conservative. It supports the SVG subset emitted
by simple_renderer.py and dimension_anchor_review_svg.py: rect, line, polygon,
circle, and text. It avoids browser/GUI calls so Windows permission popups do not
block routine visual checks.
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

Point = tuple[float, float]


def parse_float(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    cleaned = str(value).strip().replace("px", "")
    try:
        return float(cleaned)
    except ValueError:
        return default


def parse_color(value: str | None, opacity: float = 1.0) -> tuple[int, int, int, int] | None:
    if not value or value == "none":
        return None
    value = value.strip()
    if value.startswith("#") and len(value) == 7:
        return (int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16), int(max(0.0, min(1.0, opacity)) * 255))
    if value.lower() == "white":
        return (255, 255, 255, int(opacity * 255))
    if value.lower() == "black":
        return (0, 0, 0, int(opacity * 255))
    return None


def parse_points(raw: str | None) -> list[Point]:
    if not raw:
        return []
    nums = [float(item) for item in re.findall(r"-?\d+(?:\.\d+)?", raw)]
    return list(zip(nums[0::2], nums[1::2]))


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def canvas_size(root: ET.Element, max_width: int | None) -> tuple[int, int, float]:
    view_box = root.get("viewBox")
    if view_box:
        values = [float(v) for v in view_box.replace(",", " ").split()]
        width = values[2]
        height = values[3]
    else:
        width = parse_float(root.get("width"), 1200)
        height = parse_float(root.get("height"), 900)
    scale = 1.0
    if max_width and width > max_width:
        scale = max_width / width
    return max(1, int(round(width * scale))), max(1, int(round(height * scale))), scale


def scaled_point(point: Point, scale: float) -> Point:
    return (point[0] * scale, point[1] * scale)


def scaled_points(points: list[Point], scale: float) -> list[Point]:
    return [scaled_point(point, scale) for point in points]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_line(draw: ImageDraw.ImageDraw, elem: ET.Element, scale: float) -> None:
    opacity = parse_float(elem.get("opacity"), 1.0)
    fill = parse_color(elem.get("stroke"), opacity)
    if fill is None:
        return
    width = max(1, int(round(parse_float(elem.get("stroke-width"), 1.0) * scale)))
    p1 = scaled_point((parse_float(elem.get("x1")), parse_float(elem.get("y1"))), scale)
    p2 = scaled_point((parse_float(elem.get("x2")), parse_float(elem.get("y2"))), scale)
    draw.line([p1, p2], fill=fill, width=width)


def draw_rect(draw: ImageDraw.ImageDraw, elem: ET.Element, scale: float) -> None:
    opacity = parse_float(elem.get("opacity"), 1.0)
    fill = parse_color(elem.get("fill"), opacity)
    stroke = parse_color(elem.get("stroke"), opacity)
    width = max(1, int(round(parse_float(elem.get("stroke-width"), 1.0) * scale)))
    x = parse_float(elem.get("x")) * scale
    y = parse_float(elem.get("y")) * scale
    w = parse_float(elem.get("width"), 0) * scale
    h = parse_float(elem.get("height"), 0) * scale
    draw.rectangle([x, y, x + w, y + h], fill=fill, outline=stroke, width=width)


def draw_polygon(draw: ImageDraw.ImageDraw, elem: ET.Element, scale: float) -> None:
    points = scaled_points(parse_points(elem.get("points")), scale)
    if len(points) < 2:
        return
    opacity = parse_float(elem.get("opacity"), 1.0)
    fill = parse_color(elem.get("fill"), opacity)
    stroke = parse_color(elem.get("stroke"), opacity)
    width = max(1, int(round(parse_float(elem.get("stroke-width"), 1.0) * scale)))
    draw.polygon(points, fill=fill)
    if stroke:
        draw.line(points + [points[0]], fill=stroke, width=width)


def draw_circle(draw: ImageDraw.ImageDraw, elem: ET.Element, scale: float) -> None:
    opacity = parse_float(elem.get("opacity"), 1.0)
    fill = parse_color(elem.get("fill"), opacity)
    stroke = parse_color(elem.get("stroke"), opacity)
    width = max(1, int(round(parse_float(elem.get("stroke-width"), 1.0) * scale)))
    cx = parse_float(elem.get("cx")) * scale
    cy = parse_float(elem.get("cy")) * scale
    radius = parse_float(elem.get("r")) * scale
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=fill, outline=stroke, width=width)


def draw_text(draw: ImageDraw.ImageDraw, elem: ET.Element, scale: float) -> None:
    text = "".join(elem.itertext()).strip()
    if not text:
        return
    opacity = parse_float(elem.get("opacity"), 1.0)
    fill = parse_color(elem.get("fill"), opacity) or (17, 24, 39, 255)
    size = max(8, int(round(parse_float(elem.get("font-size"), 16) * scale)))
    font = load_font(size)
    x = parse_float(elem.get("x")) * scale
    y = parse_float(elem.get("y")) * scale
    anchor = elem.get("text-anchor")
    baseline = elem.get("dominant-baseline")
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    if anchor == "middle":
        x -= text_w / 2
    if baseline == "middle":
        y -= text_h / 2
    draw.text((x, y), text, font=font, fill=fill)


def render_svg(svg_path: Path, output_png: Path, max_width: int | None) -> None:
    root = ET.fromstring(svg_path.read_text(encoding="utf-8-sig"))
    width, height, scale = canvas_size(root, max_width)
    image = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    for elem in root.iter():
        tag = local_name(elem.tag)
        if tag == "svg":
            continue
        if tag == "rect":
            draw_rect(draw, elem, scale)
        elif tag == "line":
            draw_line(draw, elem, scale)
        elif tag == "polygon":
            draw_polygon(draw, elem, scale)
        elif tag == "circle":
            draw_circle(draw, elem, scale)
        elif tag == "text":
            draw_text(draw, elem, scale)

    output_png.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_png)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_svg", type=Path)
    parser.add_argument("output_png", type=Path)
    parser.add_argument("--max-width", type=int, default=1600)
    args = parser.parse_args()

    render_svg(args.input_svg, args.output_png, args.max_width)
    print(f"preview_png={args.output_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
