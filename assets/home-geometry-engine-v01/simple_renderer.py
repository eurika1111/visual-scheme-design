#!/usr/bin/env python3
"""Render a home object model and optional validation report to SVG.

Model coordinates stay CAD/DCC-friendly:
- origin: lower-left
- X axis: right
- Y axis: up
- unit: millimeters

SVG coordinates use top-left internally, so this script flips Y only at render
time. The source JSON remains lower-left based.
"""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path
from typing import Any

Point = tuple[float, float]


def as_point(value: list[float] | tuple[float, float]) -> Point:
    return (float(value[0]), float(value[1]))


def rect_corners(center: Point, size: Point, rotation_degrees: float) -> list[Point]:
    cx, cy = center
    w, h = size
    rad = math.radians(rotation_degrees)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    local = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    return [(cx + x * cos_r - y * sin_r, cy + x * sin_r + y * cos_r) for x, y in local]


def polygon_centroid(points: list[Point]) -> Point:
    if not points:
        return (0.0, 0.0)
    return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


def polygon_area(points: list[Point]) -> float:
    if len(points) < 3:
        return 0.0
    total = 0.0
    for a, b in zip(points, points[1:] + points[:1]):
        total += a[0] * b[1] - b[0] * a[1]
    return abs(total) / 2


def safe_text(value: Any) -> str:
    return html.escape(str(value), quote=True)


def arc_points(geom: dict[str, Any], max_degrees: float = 10.0) -> list[Point]:
    center = as_point(geom["center"])
    radius = float(geom["radius"])
    start_angle = float(geom["start_angle"])
    end_angle = float(geom["end_angle"])
    sweep = end_angle - start_angle
    steps = max(4, int(math.ceil(abs(sweep) / max_degrees)))
    points = []
    for index in range(steps + 1):
        angle = math.radians(start_angle + sweep * index / steps)
        points.append((center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)))
    return points


def collect_points(model: dict[str, Any], report: dict[str, Any] | None) -> list[Point]:
    points: list[Point] = []
    for wall in model.get("walls", []):
        geom = wall.get("geometry", {})
        if geom.get("kind") == "line":
            points.append(as_point(geom["start"]))
            points.append(as_point(geom["end"]))
        elif geom.get("kind") == "arc":
            try:
                points.extend(arc_points(geom))
            except (KeyError, TypeError, ValueError):
                pass
    for room in model.get("rooms", []):
        points.extend(as_point(p) for p in room.get("polygon", []))
    for opening in model.get("openings", []):
        points.append(as_point(opening["position"]))
    for item in model.get("furniture", []):
        geom = item.get("geometry", {})
        if geom.get("kind") == "rect":
            points.extend(rect_corners(as_point(geom["center"]), as_point(geom["size"]), float(geom.get("rotation", 0))))
    if report:
        for junction in report.get("junctions", []):
            if "point" in junction:
                points.append(as_point(junction["point"]))
    return points or [(0.0, 0.0), (1000.0, 1000.0)]


class SvgCanvas:
    def __init__(
        self,
        points: list[Point],
        margin: float = 130.0,
        target_width: float = 1200.0,
        bounds: tuple[float, float, float, float] | None = None,
    ) -> None:
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        self.min_x, self.min_y, self.max_x, self.max_y = bounds or (min(xs), min(ys), max(xs), max(ys))
        model_w = max(1.0, self.max_x - self.min_x)
        model_h = max(1.0, self.max_y - self.min_y)
        self.scale = target_width / model_w
        self.margin = margin
        self.width = model_w * self.scale + margin * 2
        self.height = model_h * self.scale + margin * 2
        self.items: list[str] = []

    def xy(self, p: Point) -> Point:
        x = self.margin + (p[0] - self.min_x) * self.scale
        y = self.margin + (self.max_y - p[1]) * self.scale
        return (x, y)

    def add(self, raw: str) -> None:
        self.items.append(raw)

    def line(self, a: Point, b: Point, color: str, width: float, dash: str | None = None, opacity: float = 1.0, cap: str = "round") -> None:
        x1, y1 = self.xy(a)
        x2, y2 = self.xy(b)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{width:.2f}" stroke-linecap="{cap}" opacity="{opacity}"{dash_attr}/>'
        )

    def polygon(self, points: list[Point], fill: str, stroke: str, width: float, opacity: float = 1.0) -> None:
        rendered = " ".join(f"{x:.2f},{y:.2f}" for x, y in [self.xy(p) for p in points])
        self.add(f'<polygon points="{rendered}" fill="{fill}" stroke="{stroke}" stroke-width="{width:.2f}" opacity="{opacity}"/>')

    def circle(self, center: Point, radius: float, fill: str, stroke: str = "none", width: float = 1.0) -> None:
        x, y = self.xy(center)
        self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{width:.2f}"/>')

    def text(self, pos: Point, text: str, size: float = 18.0, fill: str = "#111827") -> None:
        x, y = self.xy(pos)
        self.add(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size:.2f}" fill="{fill}" '
            f'font-family="Arial, Microsoft YaHei">{safe_text(text)}</text>'
        )

    def centered_text(self, pos: Point, text: str, size: float = 18.0, fill: str = "#111827") -> None:
        x, y = self.xy(pos)
        self.add(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size:.2f}" fill="{fill}" '
            f'font-family="Arial, Microsoft YaHei" text-anchor="middle" dominant-baseline="middle">{safe_text(text)}</text>'
        )

    def screen_text(self, x: float, y: float, text: str, size: float = 18.0, fill: str = "#111827") -> None:
        self.add(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size:.2f}" fill="{fill}" '
            f'font-family="Arial, Microsoft YaHei">{safe_text(text)}</text>'
        )

    def render(self) -> str:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width:.0f}" height="{self.height:.0f}" '
            f'viewBox="0 0 {self.width:.2f} {self.height:.2f}">\n'
            '<rect width="100%" height="100%" fill="#fbfaf7"/>\n'
            + "\n".join(self.items)
            + "\n</svg>\n"
        )


def room_label(room: dict[str, Any], points: list[Point], mode: str) -> str:
    if mode == "debug":
        return room.get("id", "room")
    name = room.get("name") or room.get("label") or room.get("id", "room")
    area_sqm = polygon_area(points) / 1_000_000
    if area_sqm > 0:
        return f"{name}\n{area_sqm:.1f}m2"
    return str(name)


def opening_label(opening: dict[str, Any], mode: str) -> str:
    if mode == "debug":
        return opening.get("id", "opening")
    if opening.get("type") == "door":
        return "D"
    if opening.get("type") == "window":
        return "W"
    return "O"


def wall_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(wall.get("id")): wall for wall in model.get("walls", []) if wall.get("id")}


def line_wall_frame(wall: dict[str, Any]) -> tuple[Point, Point, Point, Point, float, float] | None:
    geom = wall.get("geometry", {})
    if geom.get("kind") != "line":
        return None
    start = as_point(geom["start"])
    end = as_point(geom["end"])
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    if length <= 0:
        return None
    unit = (dx / length, dy / length)
    normal = (-unit[1], unit[0])
    thickness = float(geom.get("thickness", 120))
    return start, end, unit, normal, length, thickness


def opening_frame(opening: dict[str, Any], walls: dict[str, dict[str, Any]]) -> tuple[Point, Point, Point, float, float] | None:
    wall = walls.get(str(opening.get("host_wall_id")))
    if not wall:
        return None
    frame = line_wall_frame(wall)
    if not frame:
        return None
    _, _, unit, normal, _, thickness = frame
    pos = as_point(opening["position"])
    width = float(opening.get("width") or 800)
    return pos, unit, normal, width, thickness


def offset(point: Point, direction: Point, distance: float) -> Point:
    return (point[0] + direction[0] * distance, point[1] + direction[1] * distance)


def render_opening_symbol(canvas: SvgCanvas, opening: dict[str, Any], walls: dict[str, dict[str, Any]], mode: str) -> None:
    frame = opening_frame(opening, walls)
    if not frame:
        pos = as_point(opening["position"])
        color = "#2563eb" if opening.get("type") == "door" else "#0891b2"
        canvas.circle(pos, 9 if mode == "client" else 8, color, "white", 2)
        canvas.text((pos[0] + 95, pos[1] + 95), opening_label(opening, mode), size=15, fill=color)
        return

    pos, unit, normal, width, thickness = frame
    half = width / 2
    gap_start = offset(pos, unit, -half)
    gap_end = offset(pos, unit, half)
    canvas.line(gap_start, gap_end, "#fbfaf7", max(10.0, (thickness + 90) * canvas.scale), cap="butt")

    if opening.get("type") == "window":
        for shift in (-thickness * 0.22, thickness * 0.22):
            a = offset(gap_start, normal, shift)
            b = offset(gap_end, normal, shift)
            canvas.line(a, b, "#0f172a", 1.6, cap="butt")
        canvas.line(gap_start, gap_end, "#0891b2", 2.0, cap="butt")
    else:
        hinge_side = -1 if opening.get("swing", {}).get("hinge") == "left" else 1
        hinge = gap_start if hinge_side < 0 else gap_end
        leaf_end = offset(hinge, normal, width)
        canvas.line(hinge, leaf_end, "#111827", 2.0, cap="butt")
        start_angle = math.degrees(math.atan2(unit[1] * hinge_side, unit[0] * hinge_side))
        end_angle = math.degrees(math.atan2(normal[1], normal[0]))
        points = []
        sweep = end_angle - start_angle
        while sweep > 180:
            sweep -= 360
        while sweep < -180:
            sweep += 360
        for index in range(9):
            angle = math.radians(start_angle + sweep * index / 8)
            points.append((hinge[0] + width * math.cos(angle), hinge[1] + width * math.sin(angle)))
        for a, b in zip(points, points[1:]):
            canvas.line(a, b, "#64748b", 1.5, dash="5 4", opacity=0.85, cap="butt")

    if mode == "debug":
        canvas.text((pos[0] + 95, pos[1] + 95), opening_label(opening, mode), size=15, fill="#2563eb")


def render_header(canvas: SvgCanvas, model: dict[str, Any], report: dict[str, Any] | None, mode: str, title: str | None) -> None:
    readiness = report.get("readiness") if report else "no validation"
    warnings = len(report.get("warnings", [])) if report else 0
    errors = len(report.get("errors", [])) if report else 0
    heading = title or ("Client Base Confirmation" if mode == "client" else "Home Geometry Check")
    canvas.screen_text(26, 38, heading, 24, "#111827")
    canvas.screen_text(26, 66, f"readiness: {readiness}  rooms: {len(model.get('rooms', []))}  openings: {len(model.get('openings', []))}", 15, "#475569")
    canvas.screen_text(26, 88, f"warnings: {warnings}  errors: {errors}  coordinate origin: lower-left, unit: mm", 15, "#475569")


def render_scale_and_origin(canvas: SvgCanvas) -> None:
    base_y = canvas.height - 42
    base_x = 26
    scale_mm = 2000
    scale_px = scale_mm * canvas.scale
    canvas.add(f'<line x1="{base_x}" y1="{base_y}" x2="{base_x + scale_px:.2f}" y2="{base_y}" stroke="#111827" stroke-width="3"/>')
    canvas.add(f'<line x1="{base_x}" y1="{base_y - 8}" x2="{base_x}" y2="{base_y + 8}" stroke="#111827" stroke-width="2"/>')
    canvas.add(f'<line x1="{base_x + scale_px:.2f}" y1="{base_y - 8}" x2="{base_x + scale_px:.2f}" y2="{base_y + 8}" stroke="#111827" stroke-width="2"/>')
    canvas.screen_text(base_x, base_y + 24, "2000 mm", 13, "#334155")
    ox, oy = canvas.xy((canvas.min_x, canvas.min_y))
    canvas.circle((canvas.min_x, canvas.min_y), 7, "#111827", "white", 1.5)
    canvas.screen_text(ox + 12, oy - 10, "(0,0) lower-left", 13, "#334155")


def render_main_dimensions(canvas: SvgCanvas) -> None:
    width_mm = canvas.max_x - canvas.min_x
    height_mm = canvas.max_y - canvas.min_y
    left, top = canvas.xy((canvas.min_x, canvas.max_y))
    right, bottom = canvas.xy((canvas.max_x, canvas.min_y))
    dim_top = max(106.0, top - 26.0)
    dim_right = min(canvas.width - 32.0, right + 34.0)
    canvas.add(f'<line x1="{left:.2f}" y1="{dim_top:.2f}" x2="{right:.2f}" y2="{dim_top:.2f}" stroke="#475569" stroke-width="2"/>')
    canvas.screen_text((left + right) / 2 - 38, dim_top - 8, f"{width_mm:.0f} mm", 15, "#334155")
    canvas.add(f'<line x1="{dim_right:.2f}" y1="{top:.2f}" x2="{dim_right:.2f}" y2="{bottom:.2f}" stroke="#475569" stroke-width="2"/>')
    canvas.screen_text(dim_right + 8, (top + bottom) / 2, f"{height_mm:.0f} mm", 15, "#334155")


def render_model(
    model: dict[str, Any],
    report: dict[str, Any] | None = None,
    mode: str = "debug",
    title: str | None = None,
    bounds: tuple[float, float, float, float] | None = None,
) -> str:
    canvas = SvgCanvas(collect_points(model, report), bounds=bounds)
    render_header(canvas, model, report, mode, title)

    room_colors = ["#eef2ff", "#ecfdf5", "#fffbeb", "#fdf2f8", "#f0f9ff"]
    for index, room in enumerate(model.get("rooms", [])):
        points = [as_point(p) for p in room.get("polygon", [])]
        if len(points) < 3:
            continue
        fill = room_colors[index % len(room_colors)]
        canvas.polygon(points, fill, "#cbd5e1", 1.2, opacity=0.5 if mode == "client" else 0.35)
        cx, cy = polygon_centroid(points)
        for offset, line in enumerate(room_label(room, points, mode).splitlines()):
            canvas.centered_text((cx, cy - offset * 150 / canvas.scale), line, size=17 if mode == "client" else 18, fill="#334155")

    for wall in model.get("walls", []):
        geom = wall.get("geometry", {})
        thickness = float(geom.get("thickness", 120))
        stroke = max(6.0, thickness * canvas.scale)
        color = "#111111" if wall.get("alteration") == "do_not_alter" else "#2b2b2b"
        if geom.get("kind") == "line":
            canvas.line(as_point(geom["start"]), as_point(geom["end"]), color, stroke, cap="butt")
            if mode == "debug":
                mid = ((geom["start"][0] + geom["end"][0]) / 2, (geom["start"][1] + geom["end"][1]) / 2)
                canvas.text(mid, wall.get("id", "wall"), size=14, fill="#374151")
        elif geom.get("kind") == "arc":
            try:
                points = arc_points(geom)
            except (KeyError, TypeError, ValueError):
                continue
            for start, end in zip(points, points[1:]):
                canvas.line(start, end, color, stroke)
            if mode == "debug":
                canvas.text(points[len(points) // 2], wall.get("id", "arc"), size=14, fill="#374151")

    walls = wall_index(model)
    for opening in model.get("openings", []):
        render_opening_symbol(canvas, opening, walls, mode)

    for item in model.get("furniture", []):
        geom = item.get("geometry", {})
        if geom.get("kind") != "rect":
            continue
        corners = rect_corners(as_point(geom["center"]), as_point(geom["size"]), float(geom.get("rotation", 0)))
        canvas.polygon(corners, "#f9d38c", "#b45309", 2.0, opacity=0.75)
        label = item.get("id", "furniture") if mode == "debug" else item.get("name", item.get("type", "furniture"))
        canvas.text(as_point(geom["center"]), label, size=15, fill="#7c2d12")

    if report and mode == "debug":
        for junction in report.get("junctions", []):
            point = as_point(junction["point"])
            if junction.get("type") == "near_miss":
                canvas.circle(point, 10, "#ef4444", "white", 2)
                canvas.text((point[0] + 80, point[1] + 80), f'{junction["id"]} near-miss', size=16, fill="#dc2626")
            else:
                canvas.circle(point, 6, "#22c55e", "white", 1.5)

        furniture_by_id = {item.get("id"): item for item in model.get("furniture", [])}
        for swing in report.get("door_swing_checks", []):
            if "hinge" in swing and "open_end_90" in swing:
                color = "#f97316" if swing.get("status") == "warning" else "#64748b"
                canvas.line(as_point(swing["hinge"]), as_point(swing["open_end_90"]), color, 3.0, dash="8 6", opacity=0.8)

        for path in report.get("circulation_checks", []):
            if "start" in path and "end" in path:
                color = "#f97316" if path.get("status") == "warning" else "#16a34a"
                canvas.line(as_point(path["start"]), as_point(path["end"]), color, 4.0, dash="12 8", opacity=0.75)
                canvas.text(as_point(path["start"]), path.get("path_id", "path"), size=14, fill=color)

        for warning in report.get("warnings", []):
            marked_ids = list(warning.get("furniture_ids", []))
            if warning.get("furniture_id"):
                marked_ids.append(warning.get("furniture_id"))
            if warning.get("object_id") and str(warning.get("object_id", "")).startswith("F-"):
                marked_ids.append(warning.get("object_id"))
            for furniture_id in sorted(set(marked_ids)):
                item = furniture_by_id.get(furniture_id)
                if not item:
                    continue
                geom = item.get("geometry", {})
                if geom.get("kind") != "rect":
                    continue
                center = as_point(geom["center"])
                canvas.circle(center, 18, "none", "#dc2626", 3)
                canvas.text((center[0] + 100, center[1] + 100), warning.get("type", "warning"), size=14, fill="#dc2626")

        for warning in report.get("warnings", []):
            if warning.get("type") in ["room_edge_off_wall", "room_edge_under_supported", "room_area_mismatch"]:
                room = next((r for r in model.get("rooms", []) if r.get("id") == warning.get("room_id")), None)
                if room:
                    points = [as_point(p) for p in room.get("polygon", [])]
                    canvas.text(polygon_centroid(points), warning.get("type", "room warning"), size=16, fill="#dc2626")

        for error in report.get("errors", []):
            if error.get("type") == "opening_binding_error":
                opening = next((o for o in model.get("openings", []) if o.get("id") == error.get("opening_id")), None)
                if opening:
                    pos = as_point(opening["position"])
                    canvas.circle(pos, 14, "none", "#dc2626", 3)
                    canvas.text((pos[0] + 120, pos[1] - 120), "bad host", size=18, fill="#dc2626")

    render_main_dimensions(canvas)
    render_scale_and_origin(canvas)
    return canvas.render()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_object_model", type=Path)
    parser.add_argument("output_svg", type=Path)
    parser.add_argument("validation", type=Path, nargs="?")
    parser.add_argument("--mode", choices=["debug", "client"], default="debug")
    parser.add_argument("--title")
    args = parser.parse_args()

    model = json.loads(args.base_object_model.read_text(encoding="utf-8-sig"))
    report = json.loads(args.validation.read_text(encoding="utf-8-sig")) if args.validation else None
    args.output_svg.parent.mkdir(parents=True, exist_ok=True)
    args.output_svg.write_text(render_model(model, report, args.mode, args.title), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
