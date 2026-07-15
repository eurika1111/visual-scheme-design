#!/usr/bin/env python3
"""Create an immutable lock record for a user-confirmed residential concept base."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image

from simple_renderer import collect_points


READINESS = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}


def load_json(path: Path | None) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig")) if path else {}


def file_record(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    return {
        "path": str(resolved),
        "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(),
    }


def numeric(value: str | None) -> int | None:
    if not value:
        return None
    match = re.match(r"\s*([0-9]+(?:\.[0-9]+)?)", value)
    return round(float(match.group(1))) if match else None


def visual_size(path: Path) -> tuple[int, int]:
    if path.suffix.lower() == ".svg":
        root = ET.parse(path).getroot()
        width = numeric(root.get("width"))
        height = numeric(root.get("height"))
        if width and height:
            return width, height
        view_box = root.get("viewBox")
        if view_box:
            values = [float(value) for value in view_box.replace(",", " ").split()]
            if len(values) == 4:
                return round(values[2]), round(values[3])
        raise ValueError("SVG confirmation visual has no usable width, height, or viewBox")
    with Image.open(path) as image:
        return image.size


def model_bounds(model: dict[str, Any]) -> dict[str, float]:
    points = collect_points(model, None)
    if not points:
        raise ValueError("base model has no geometry points")
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    return {"min_x": min(xs), "min_y": min(ys), "max_x": max(xs), "max_y": max(ys)}


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    base = load_json(args.base_model)
    validation = load_json(args.validation)
    base_id = args.base_id or base.get("version")
    if not base_id:
        raise ValueError("base_id is required when the model has no version")
    readiness = validation.get("readiness") or base.get("readiness") or "L0"
    if READINESS.get(str(readiness), 0) < READINESS["L2"]:
        raise ValueError(f"cannot lock residential concept base below L2: {readiness}")
    if validation and (validation.get("errors") or []):
        raise ValueError("cannot lock a base whose validation report has errors")

    visual = args.confirmation_visual.resolve()
    if not visual.exists():
        raise ValueError(f"confirmation visual does not exist: {visual}")
    width, height = visual_size(visual)
    dimensions = base.get("dimension_chains", []) or base.get("dimensions", []) or []
    return {
        "schema_version": "residential_base_lock_v1",
        "base_id": str(base_id),
        "base_lock_status": "locked",
        "readiness": readiness,
        "locked_at": args.locked_at or date.today().isoformat(),
        "confirmed_by": args.confirmed_by,
        "confirmation_note": args.confirmation_note,
        "base_model": file_record(args.base_model),
        "confirmation_visual": file_record(visual),
        "validation_report": file_record(args.validation) if args.validation else None,
        "canvas": {"width": width, "height": height, "unit": "px"},
        "coordinate_system": base.get("coordinate_system") or {
            "origin": "lower_left", "x_axis": "right", "y_axis": "up", "unit": "mm"
        },
        "bounds_mm": model_bounds(base),
        "dimension_anchors": [item.get("id") for item in dimensions if item.get("id")],
        "immutable_fields": [
            "base_id", "base_model.sha256", "confirmation_visual.sha256", "canvas",
            "coordinate_system", "bounds_mm", "dimension_anchors"
        ],
        "image_is_geometry_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Lock a user-confirmed L2+ residential concept base.")
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--confirmation-visual", type=Path, required=True)
    parser.add_argument("--validation", type=Path)
    parser.add_argument("--base-id")
    parser.add_argument("--confirmed-by", required=True)
    parser.add_argument("--confirmation-note", default="user confirmed concept base")
    parser.add_argument("--locked-at")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true", help="Allow replacement only for controlled tests.")
    args = parser.parse_args()

    args.base_model = args.base_model.resolve()
    args.confirmation_visual = args.confirmation_visual.resolve()
    args.validation = args.validation.resolve() if args.validation else None
    args.output = args.output.resolve()
    if args.output.exists() and not args.force:
        raise SystemExit(f"locked manifest already exists; create a new base version instead: {args.output}")
    manifest = build_manifest(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"base_lock={args.output}")
    print(f"base_lock_status=locked base_id={manifest['base_id']} canvas={manifest['canvas']['width']}x{manifest['canvas']['height']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
