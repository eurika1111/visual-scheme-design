#!/usr/bin/env python3
"""Convert an auditable pixel trace specification into a millimeter object model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a home object model from a source-image trace specification.")
    parser.add_argument("trace_spec", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    spec = load_json(args.trace_spec)
    frame = spec["pixel_frame"]
    sx = float(frame["width_mm"]) / (float(frame["right_px"]) - float(frame["left_px"]))
    sy = float(frame["height_mm"]) / (float(frame["bottom_px"]) - float(frame["top_px"]))

    def point(value: list[float]) -> list[float]:
        return [
            round((float(value[0]) - float(frame["left_px"])) * sx, 1),
            round((float(frame["bottom_px"]) - float(value[1])) * sy, 1),
        ]

    def convert_wall(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": item["id"], "type": "wall", "status": "existing",
            "alteration": item.get("alteration", "unknown"), "confidence": item.get("confidence", 0.76),
            "geometry": {
                "kind": "line", "start": point(item["start_px"]), "end": point(item["end_px"]),
                "thickness": round(float(item.get("thickness_px", 10)) * (sx + sy) / 2, 1),
            },
            "source_trace_px": {"start": item["start_px"], "end": item["end_px"]},
            "version": spec["version"],
        }

    walls = [convert_wall(item) for item in spec.get("walls", [])]
    wall_by_id = {item["id"]: item for item in walls}
    openings = []
    for item in spec.get("openings", []):
        host = wall_by_id[item["host_wall_id"]]
        start, end = host["geometry"]["start"], host["geometry"]["end"]
        horizontal = abs(end[0] - start[0]) >= abs(end[1] - start[1])
        opening = {
            "id": item["id"], "type": item["type"], "host_wall_id": item["host_wall_id"],
            "position": point(item["position_px"]),
            "width": round(float(item["width_px"]) * (sx if horizontal else sy), 1),
            "confidence": item.get("confidence", 0.72), "source_trace_px": item["position_px"],
            "version": spec["version"],
        }
        if item.get("swing"):
            opening["swing"] = item["swing"]
        openings.append(opening)

    rooms = []
    for item in spec.get("rooms", []):
        rooms.append({
            "id": item["id"], "name": item["name"], "type": item["type"],
            "confidence": item.get("confidence", 0.76),
            "polygon": [point(value) for value in item["polygon_px"]],
            "source_area_m2": item.get("source_area_m2"),
            "source_trace_px": item["polygon_px"], "version": spec["version"],
        })

    fixtures = []
    for item in spec.get("fixed_fixtures", []):
        center = point(item["center_px"])
        fixtures.append({
            "id": item["id"], "type": item["type"], "name": item.get("name", item["type"]), "room_id": item["room_id"],
            "confidence": item.get("confidence", 0.72),
            "geometry": {
                "kind": "rect", "center": center,
                "size": [round(item["size_px"][0] * sx, 1), round(item["size_px"][1] * sy, 1)],
                "rotation": item.get("rotation", 0),
            },
            "source_trace_px": {"center": item["center_px"], "size": item["size_px"]},
            "version": spec["version"],
        })

    model = {
        "schema_version": "home_geometry_v1", "version": spec["version"],
        "coordinate_system": {"origin": "lower_left", "x_axis": "right", "y_axis": "up", "unit": "mm", "angle_positive": "counterclockwise"},
        "tolerance": {"snap_mm": 90, "duplicate_mm": 20, "opening_host_mm": 140, "door_swing_mm": 25},
        "walls": walls, "openings": openings, "rooms": rooms, "furniture": [], "fixed_fixtures": fixtures,
        "zones": spec.get("zones", []), "circulation_paths": [],
        "source_images": [{"id": "SRC-130-PLAN-01", "path": spec["source_image"], "role": "primary_floor_plan"}],
        "source_facts": spec.get("source_facts", []),
        "dimension_chains": spec.get("dimension_chains", []),
        "extraction_notes": spec.get("extraction_notes", []),
        "trace_calibration": {"pixel_frame": frame, "scale_x_mm_per_px": round(sx, 6), "scale_y_mm_per_px": round(sy, 6)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"trace_model={args.output}")
    print(f"objects=walls:{len(walls)} rooms:{len(rooms)} openings:{len(openings)} fixtures:{len(fixtures)}")
    print(f"scale={sx:.4f}x{sy:.4f} mm_per_px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
