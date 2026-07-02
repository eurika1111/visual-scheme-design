#!/usr/bin/env python3
"""Render dimension anchor review overlays from a source extraction package."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

Point = tuple[float, float]


COLORS = {
    "global": "#16a34a",
    "local": "#f59e0b",
    "ocr_error": "#dc2626",
    "site_measurement_required": "#dc2626",
    "unknown": "#64748b",
}


STATUS_LABELS = {
    "confirmed_by_human": "confirmed global",
    "confirmed_by_draft": "draft global",
    "confirmed_local_dimension": "local dimension",
    "rejected_ocr_or_reading_error": "OCR/read error",
    "needs_site_measurement": "site measure",
    "needs_confirmation": "needs confirmation",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def candidate_model(package: dict[str, Any]) -> dict[str, Any]:
    return package.get("candidate_model") if isinstance(package.get("candidate_model"), dict) else package


def source_chains(package: dict[str, Any], model: dict[str, Any]) -> list[dict[str, Any]]:
    chains = package.get("dimension_chains")
    if isinstance(chains, list) and chains:
        return chains
    model_chains = model.get("dimension_chains")
    return model_chains if isinstance(model_chains, list) else []


def as_point(value: Any) -> Point | None:
    if isinstance(value, list) and len(value) >= 2:
        return (float(value[0]), float(value[1]))
    return None


def object_points(item: dict[str, Any]) -> list[Point]:
    geom = item.get("geometry") or {}
    points: list[Point] = []
    if geom.get("kind") == "line":
        for key in ["start", "end"]:
            point = as_point(geom.get(key))
            if point:
                points.append(point)
    elif geom.get("kind") == "rect":
        center = as_point(geom.get("center"))
        size = as_point(geom.get("size"))
        if center and size:
            points.extend([(center[0] - size[0] / 2, center[1] - size[1] / 2), (center[0] + size[0] / 2, center[1] + size[1] / 2)])
    elif geom.get("kind") == "arc":
        center = as_point(geom.get("center"))
        radius = float(geom.get("radius") or 0)
        if center:
            points.extend([(center[0] - radius, center[1] - radius), (center[0] + radius, center[1] + radius)])
    for raw in item.get("polygon", []) or []:
        point = as_point(raw)
        if point:
            points.append(point)
    pos = as_point(item.get("position"))
    if pos:
        points.append(pos)
    return points


def object_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for key in ["walls", "openings", "rooms", "furniture", "fixed_fixtures", "zones"]:
        for item in model.get(key, []) or []:
            if item.get("id"):
                result[str(item["id"])] = item
    return result


def collect_points(model: dict[str, Any]) -> list[Point]:
    objects = object_index(model)
    points = [point for item in objects.values() for point in object_points(item)]
    return points or [(0.0, 0.0), (1000.0, 1000.0)]


class Canvas:
    def __init__(self, points: list[Point], margin: float = 170.0, target_width: float = 1200.0) -> None:
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        self.min_x = min(xs)
        self.max_x = max(xs)
        self.min_y = min(ys)
        self.max_y = max(ys)
        self.model_w = max(1.0, self.max_x - self.min_x)
        self.model_h = max(1.0, self.max_y - self.min_y)
        self.scale = target_width / self.model_w
        self.margin = margin
        self.width = self.model_w * self.scale + margin * 2
        self.height = self.model_h * self.scale + margin * 2
        self.items: list[str] = []

    def xy(self, point: Point) -> Point:
        x = self.margin + (point[0] - self.min_x) * self.scale
        y = self.margin + (self.max_y - point[1]) * self.scale
        return x, y

    def add(self, raw: str) -> None:
        self.items.append(raw)

    def line(self, a: Point, b: Point, color: str, width: float = 2.0, dash: str | None = None, opacity: float = 1.0) -> None:
        x1, y1 = self.xy(a)
        x2, y2 = self.xy(b)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width:.2f}" opacity="{opacity}" stroke-linecap="round"{dash_attr}/>' )

    def polygon(self, points: list[Point], fill: str, stroke: str, width: float, opacity: float = 1.0) -> None:
        rendered = " ".join(f"{x:.2f},{y:.2f}" for x, y in [self.xy(point) for point in points])
        self.add(f'<polygon points="{rendered}" fill="{fill}" stroke="{stroke}" stroke-width="{width:.2f}" opacity="{opacity}"/>')

    def circle(self, point: Point, radius: float, fill: str, stroke: str = "white", width: float = 2.0) -> None:
        x, y = self.xy(point)
        self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{width:.2f}"/>')

    def text(self, point: Point, text: str, size: float = 15.0, fill: str = "#111827", anchor: str = "start") -> None:
        x, y = self.xy(point)
        safe = html.escape(str(text), quote=True)
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size:.2f}" fill="{fill}" font-family="Arial" text-anchor="{anchor}">{safe}</text>')

    def screen_text(self, x: float, y: float, text: str, size: float = 16.0, fill: str = "#111827") -> None:
        safe = html.escape(str(text), quote=True)
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size:.2f}" fill="{fill}" font-family="Arial">{safe}</text>')

    def render(self) -> str:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width:.0f}" height="{self.height:.0f}" viewBox="0 0 {self.width:.2f} {self.height:.2f}">\n<rect width="100%" height="100%" fill="#fbfaf7"/>\n' + "\n".join(self.items) + "\n</svg>\n"


def chain_color(chain: dict[str, Any]) -> str:
    scope = chain.get("dimension_scope")
    if scope in COLORS:
        return COLORS[scope]
    status = chain.get("anchor_status")
    if status in {"confirmed_by_human", "confirmed_by_draft"}:
        return COLORS["global"]
    if status in {"confirmed_local_dimension"}:
        return COLORS["local"]
    if status in {"rejected_ocr_or_reading_error", "needs_site_measurement"}:
        return COLORS["ocr_error"]
    return COLORS["unknown"]


def chain_label(chain: dict[str, Any]) -> str:
    total = sum(float(value) for value in chain.get("segments_mm") or [] if isinstance(value, (int, float)))
    status = STATUS_LABELS.get(str(chain.get("anchor_status")), str(chain.get("anchor_status") or "unconfirmed"))
    return f"{chain.get('id')}  {total:.0f}mm  {status}"


def ref_coord(ref: Any) -> float | None:
    if isinstance(ref, dict) and isinstance(ref.get("coordinate_mm"), (int, float)):
        return float(ref["coordinate_mm"])
    return None


def object_extent_for_chain(chain: dict[str, Any], objects: dict[str, dict[str, Any]], axis: str) -> tuple[float, float] | None:
    index = 0 if axis == "x" else 1
    values: list[float] = []
    for object_id in chain.get("object_ids") or []:
        item = objects.get(str(object_id))
        if not item:
            continue
        values.extend(point[index] for point in object_points(item))
    if not values:
        return None
    return min(values), max(values)


def render_base(canvas: Canvas, model: dict[str, Any]) -> None:
    for room in model.get("rooms", []) or []:
        points = [point for raw in room.get("polygon", []) or [] if (point := as_point(raw))]
        if len(points) >= 3:
            canvas.polygon(points, "#e2e8f0", "#94a3b8", 1.2, 0.35)
    for wall in model.get("walls", []) or []:
        geom = wall.get("geometry") or {}
        if geom.get("kind") == "line":
            start = as_point(geom.get("start"))
            end = as_point(geom.get("end"))
            if start and end:
                width = max(5.0, float(geom.get("thickness") or 120) * canvas.scale)
                canvas.line(start, end, "#171717", width, opacity=0.9)
                canvas.text(((start[0] + end[0]) / 2, (start[1] + end[1]) / 2), wall.get("id", "wall"), 12, "#475569")
    for opening in model.get("openings", []) or []:
        point = as_point(opening.get("position"))
        if point:
            canvas.circle(point, 6, "#2563eb")


def render_dimension_chains(canvas: Canvas, chains: list[dict[str, Any]], objects: dict[str, dict[str, Any]]) -> None:
    x_count = 0
    y_count = 0
    for chain in chains:
        axis = chain.get("axis")
        if axis not in {"x", "y"}:
            continue
        color = chain_color(chain)
        dash = "10 7" if chain.get("exclude_from_global_audit") or chain.get("dimension_scope") in {"local", "ocr_error", "site_measurement_required"} else None
        start_value = ref_coord(chain.get("start_ref"))
        end_value = ref_coord(chain.get("end_ref"))
        extent = object_extent_for_chain(chain, objects, axis)
        if (start_value is None or end_value is None) and extent:
            start_value, end_value = extent
        if start_value is None or end_value is None:
            continue
        if axis == "x":
            y = canvas.max_y + 260 + x_count * 170
            a = (start_value, y)
            b = (end_value, y)
            label_point = ((start_value + end_value) / 2, y + 80)
            x_count += 1
        else:
            x = canvas.max_x + 260 + y_count * 170
            a = (x, start_value)
            b = (x, end_value)
            label_point = (x + 80, (start_value + end_value) / 2)
            y_count += 1
        canvas.line(a, b, color, 4.0, dash=dash, opacity=0.92)
        canvas.circle(a, 7, color)
        canvas.circle(b, 7, color)
        canvas.text(label_point, chain_label(chain), 15, color)


def render_legend(canvas: Canvas, package: dict[str, Any], chains: list[dict[str, Any]]) -> None:
    canvas.screen_text(24, 36, f"Dimension Anchor Review - {package.get('package_id', 'package')}", 22, "#111827")
    rows = [
        (COLORS["global"], "solid: confirmed global datum/reference"),
        (COLORS["local"], "dashed: local dimension excluded from global audit"),
        (COLORS["ocr_error"], "red: OCR/read error or site measurement required"),
        (COLORS["unknown"], "gray: unconfirmed or draft-only"),
    ]
    y = 66
    for color, label in rows:
        canvas.add(f'<line x1="28" y1="{y}" x2="78" y2="{y}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
        canvas.screen_text(88, y + 5, label, 14, "#334155")
        y += 24
    global_count = sum(1 for chain in chains if not chain.get("exclude_from_global_audit"))
    excluded_count = len(chains) - global_count
    canvas.screen_text(28, y + 10, f"chains: {len(chains)} / global audit: {global_count} / excluded: {excluded_count}", 14, "#334155")


def render_review_svg(package: dict[str, Any]) -> str:
    model = candidate_model(package)
    chains = source_chains(package, model)
    objects = object_index(model)
    canvas = Canvas(collect_points(model))
    render_base(canvas, model)
    render_dimension_chains(canvas, chains, objects)
    render_legend(canvas, package, chains)
    return canvas.render()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("output_svg", type=Path)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    package = load_json(args.package)
    args.output_svg.parent.mkdir(parents=True, exist_ok=True)
    args.output_svg.write_text(render_review_svg(package), encoding="utf-8")
    if not args.json_only:
        chains = source_chains(package, candidate_model(package))
        global_count = sum(1 for chain in chains if not chain.get("exclude_from_global_audit"))
        print(f"dimension_anchor_review_svg={args.output_svg}")
        print(f"chains={len(chains)} global={global_count} excluded={len(chains) - global_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())