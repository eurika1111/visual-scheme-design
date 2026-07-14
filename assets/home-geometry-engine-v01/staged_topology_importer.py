#!/usr/bin/env python3
"""Import a reviewed legacy topology master without reinterpreting its source image."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


CONFIDENCE = {"A": 0.92, "B": 0.76, "C": 0.6}
ROOM_TYPES = {
    "卫生间": "bathroom",
    "厨房": "kitchen",
    "阳台": "balcony",
    "卧室": "bedroom",
    "客厅": "living_room",
    "前室": "anteroom",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def confidence(value: Any, default: float = 0.76) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return CONFIDENCE.get(str(value).upper(), default)


def room_type(name: str) -> str:
    return next((value for key, value in ROOM_TYPES.items() if key in name), "space")


def all_wall_points(topology: dict[str, Any]) -> list[list[float]]:
    points: list[list[float]] = []
    for wall in topology.get("walls", []):
        if wall.get("render", True) is False:
            continue
        points.extend([wall["a"], wall["b"]])
    if not points:
        raise ValueError("Topology master contains no rendered wall segments.")
    return points


def dimension_register_path(topology_path: Path, topology: dict[str, Any], override: Path | None) -> Path | None:
    if override:
        return override
    value = topology.get("dimension_register")
    if not value:
        return None
    candidate = topology_path.parent / str(value)
    return candidate if candidate.exists() else None


def primary_extent(chains: list[dict[str, Any]], axis: str) -> float | None:
    direction = "horizontal" if axis == "x" else "vertical"
    candidates = [item for item in chains if item.get("direction") == direction and item.get("segments_mm")]
    if not candidates:
        return None
    preferred = [item for item in candidates if str(item.get("confidence", "")).upper() == "A"] or candidates
    return float(max(sum(item["segments_mm"]) for item in preferred))


def segment_midpoint(item: dict[str, Any]) -> list[float]:
    return [(item["from"][0] + item["to"][0]) / 2, (item["from"][1] + item["to"][1]) / 2]


def collinear_distance(opening: dict[str, Any], wall: dict[str, Any]) -> float:
    a, b = opening["from"], opening["to"]
    wa, wb = wall["a"], wall["b"]
    opening_horizontal = abs(b[0] - a[0]) >= abs(b[1] - a[1])
    wall_horizontal = abs(wb[0] - wa[0]) >= abs(wb[1] - wa[1])
    if opening_horizontal != wall_horizontal:
        return math.inf
    midpoint = segment_midpoint(opening)
    if opening_horizontal:
        span_gap = max(min(wa[0], wb[0]) - midpoint[0], midpoint[0] - max(wa[0], wb[0]), 0)
        return abs(midpoint[1] - wa[1]) + span_gap
    span_gap = max(min(wa[1], wb[1]) - midpoint[1], midpoint[1] - max(wa[1], wb[1]), 0)
    return abs(midpoint[0] - wa[0]) + span_gap


def build_package(
    topology_path: Path,
    topology: dict[str, Any],
    source_image: Path,
    dimension_register: dict[str, Any] | None,
    corrections_path: Path | None,
    corrections: dict[str, Any] | None,
    package_id: str,
    version: str,
    exterior_thickness: float,
    interior_thickness: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    corrections = corrections or {}
    opening_overrides = corrections.get("opening_overrides", {})
    room_extensions = corrections.get("room_display_extensions_px", {})
    chains_source = (dimension_register or {}).get("dimension_chains", [])
    points = all_wall_points(topology)
    min_x = min(point[0] for point in points)
    max_x = max(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    width_mm = primary_extent(chains_source, "x") or max_x - min_x
    height_mm = primary_extent(chains_source, "y") or max_y - min_y
    sx = width_mm / (max_x - min_x)
    sy = height_mm / (max_y - min_y)

    def point(value: list[float]) -> list[float]:
        return [round((value[0] - min_x) * sx, 1), round((max_y - value[1]) * sy, 1)]

    source_id = "SRC-LEGACY-TOPOLOGY-01"
    walls = []
    wall_source: dict[str, dict[str, Any]] = {}
    for item in topology.get("walls", []):
        wall_class = item.get("class", "unknown")
        rendered = item.get("render", True) is not False
        if wall_class == "do_not_alter":
            alteration = "do_not_alter"
            default_thickness = exterior_thickness
            wall_confidence = 0.9
        elif wall_class == "opening_host":
            alteration = "unknown"
            default_thickness = exterior_thickness if str(item.get("id", "")).startswith("W-E") else interior_thickness
            wall_confidence = 0.72
        else:
            alteration = "candidate" if wall_class == "non_structural" else "unknown"
            default_thickness = interior_thickness
            wall_confidence = 0.78 if wall_class == "non_structural" else 0.68
        pixel_thickness = float(item.get("th") or 0)
        thickness = pixel_thickness * (sx + sy) / 2 if pixel_thickness > 0 else default_thickness
        wall = {
            "id": item["id"],
            "type": "wall",
            "role": "opening_host_reference" if wall_class == "opening_host" else "physical_wall",
            "status": "existing",
            "alteration": alteration,
            "confidence": wall_confidence,
            "render": rendered,
            "geometry": {
                "kind": "line",
                "start": point(item["a"]),
                "end": point(item["b"]),
                "thickness": round(thickness, 1),
            },
            "source_stage": "legacy_topology_master",
            "source_trace_px": {"start": item["a"], "end": item["b"]},
            "source_note": item.get("note"),
            "version": version,
        }
        walls.append(wall)
        wall_source[item["id"]] = item

    missing_hosts: list[str] = []
    pending_swings: list[str] = []
    openings = []
    applied_opening_overrides: list[str] = []
    source_openings = list(topology.get("openings", [])) + list(topology.get("windows", []))
    for source_item in source_openings:
        item = dict(source_item)
        override = opening_overrides.get(item["id"])
        if override:
            item.update(override)
            applied_opening_overrides.append(item["id"])
        host_id = item.get("wall")
        if not host_id:
            candidates = sorted(
                ((collinear_distance(item, wall), wall["id"]) for wall in topology.get("walls", [])),
                key=lambda value: value[0],
            )
            host_id = candidates[0][1] if candidates and math.isfinite(candidates[0][0]) else None
        if host_id not in wall_source:
            missing_hosts.append(item["id"])
            continue
        a, b = point(item["from"]), point(item["to"])
        raw_type = item.get("type", "opening")
        opening_type = "door" if raw_type in {"door", "sliding_door", "glazed_door"} else "window"
        opening = {
            "id": item["id"],
            "type": opening_type,
            "host_wall_id": host_id,
            "position": [round((a[0] + b[0]) / 2, 1), round((a[1] + b[1]) / 2, 1)],
            "width": round(math.dist(a, b), 1),
            "confidence": confidence(item.get("confidence")),
            "source_stage": "legacy_topology_master",
            "source_trace_px": {"from": item["from"], "to": item["to"]},
            "source_note": item.get("note"),
            "legacy_opening_type": raw_type,
            "version": version,
        }
        if raw_type == "sliding_door":
            opening["mode"] = "sliding"
        elif raw_type in {"glazed_opening", "glazed_door"}:
            opening["mode"] = "glazed"
        if item.get("mode"):
            opening["mode"] = item["mode"]
        if item.get("group_id"):
            opening["group_id"] = item["group_id"]
        if opening_type == "door" and raw_type != "sliding_door":
            pending_swings.append(item["id"])
            if item.get("design_swing"):
                opening["legacy_design_swing"] = item["design_swing"]
        openings.append(opening)

    rooms = []
    applied_room_extensions: list[str] = []
    for item in topology.get("rooms", []):
        room = {
            "id": item["id"],
            "type": room_type(item.get("name", "")),
            "name": item.get("name", item["id"]),
            "polygon": [point(value) for value in item.get("points", [])],
            "source_area_m2": item.get("area_label"),
            "confidence": 0.82,
            "source_stage": "legacy_topology_master",
            "source_trace_px": item.get("points", []),
            "version": version,
        }
        extension_polygons = room_extensions.get(item["id"], [])
        if extension_polygons:
            room["display_extensions"] = [
                [point(value) for value in polygon]
                for polygon in extension_polygons
            ]
            applied_room_extensions.append(item["id"])
        rooms.append(room)

    dimension_chains = []
    for item in chains_source:
        axis = "x" if item.get("direction") == "horizontal" else "y" if item.get("direction") == "vertical" else "unknown"
        dimension_chains.append({
            "id": item["id"],
            "axis": axis,
            "source": source_id,
            "segments_mm": item.get("segments_mm", []),
            "confidence": confidence(item.get("confidence")),
            "location": item.get("location"),
            "notes": item.get("notes", []),
        })

    source_facts = [
        {
            "id": "SF-LEGACY-WALLS-01",
            "type": "reviewed_topology_walls",
            "object_ids": [item["id"] for item in walls],
            "source": source_id,
            "confidence": 0.82,
        },
        {
            "id": "SF-LEGACY-SPACES-01",
            "type": "reviewed_space_registration",
            "object_ids": [item["id"] for item in rooms],
            "source": source_id,
            "confidence": 0.82,
        },
        {
            "id": "SF-LEGACY-OPENINGS-01",
            "type": "reviewed_opening_registry",
            "object_ids": [item["id"] for item in openings],
            "source": source_id,
            "confidence": 0.76,
        },
    ]
    corrected_object_ids = sorted(set(applied_opening_overrides + applied_room_extensions))
    if corrected_object_ids:
        source_facts.append({
            "id": "SF-USER-CORRECTIONS-01",
            "type": "user_confirmed_object_corrections",
            "object_ids": corrected_object_ids,
            "source": source_id,
            "confidence": 0.92,
        })

    unresolved = [
        {"id": f"U-LEGACY-{index:02d}", "severity": "medium", "question": text, "source": source_id}
        for index, text in enumerate(topology.get("limitations", []), start=1)
    ]
    unresolved.extend(
        {"id": f"U-SWING-{opening_id}", "severity": "high", "question": f"Confirm normalized hinge and swing for {opening_id}.", "source": source_id}
        for opening_id in pending_swings
    )
    unresolved.extend(
        {"id": f"U-HOST-{opening_id}", "severity": "high", "question": f"Opening host could not be preserved for {opening_id}.", "source": source_id}
        for opening_id in missing_hosts
    )

    coordinate_system = {"origin": "lower_left", "x_axis": "right", "y_axis": "up", "unit": "mm", "angle_positive": "counterclockwise"}
    candidate_model = {
        "schema_version": "home_geometry_v1",
        "version": version,
        "coordinate_system": coordinate_system,
        "tolerance": {"snap_mm": 90, "duplicate_mm": 20, "opening_host_mm": 140, "door_swing_mm": 25},
        "source_images": [{"id": source_id, "path": str(source_image), "role": "primary_floor_plan"}],
        "source_facts": source_facts,
        "dimension_chains": dimension_chains,
        "extraction_notes": [
            "Imported from an existing topology master; source geometry was not reinterpreted.",
            "Legacy door swing descriptions remain unresolved until normalized and confirmed.",
            "Wall solids and construction readiness are outside this import stage.",
        ],
        "walls": walls,
        "openings": openings,
        "rooms": rooms,
        "furniture": [],
        "fixed_fixtures": [],
        "zones": [],
        "circulation_paths": [],
        "import_lineage": {
            "source_topology": str(topology_path),
            "source_schema_version": topology.get("schema_version"),
            "source_unit": topology.get("unit_geometry"),
            "pixel_frame": {"left": min_x, "right": max_x, "top": min_y, "bottom": max_y},
            "scale_x_mm_per_px": round(sx, 6),
            "scale_y_mm_per_px": round(sy, 6),
            "corrections": str(corrections_path) if corrections_path else None,
        },
    }
    package = {
        "schema_version": "source_extraction_package_v1",
        "package_id": package_id,
        "coordinate_system": coordinate_system,
        "source_images": candidate_model["source_images"],
        "dimension_chains": dimension_chains,
        "source_facts": source_facts,
        "unresolved_questions": unresolved,
        "candidate_model": candidate_model,
    }
    source_counts = {
        "walls": len(topology.get("walls", [])),
        "openings": len(source_openings),
        "rooms": len(topology.get("rooms", [])),
        "dimension_chains": len(chains_source),
        "limitations": len(topology.get("limitations", [])),
    }
    output_counts = {
        "walls": len(walls),
        "openings": len(openings),
        "rooms": len(rooms),
        "dimension_chains": len(dimension_chains),
        "unresolved_questions": len(unresolved),
    }
    dropped = {
        "walls": source_counts["walls"] - output_counts["walls"],
        "openings": source_counts["openings"] - output_counts["openings"],
        "rooms": source_counts["rooms"] - output_counts["rooms"],
        "dimension_chains": source_counts["dimension_chains"] - output_counts["dimension_chains"],
    }
    known_opening_ids = {item["id"] for item in source_openings}
    known_room_ids = {item["id"] for item in topology.get("rooms", [])}
    unknown_corrections = sorted(
        (set(opening_overrides) - known_opening_ids)
        | (set(room_extensions) - known_room_ids)
    )
    report = {
        "schema_version": "staged_topology_import_report_v1",
        "status": "passed" if not any(dropped.values()) and not unknown_corrections else "failed",
        "source_topology": str(topology_path),
        "source_counts": source_counts,
        "output_counts": output_counts,
        "dropped": dropped,
        "missing_opening_hosts": missing_hosts,
        "pending_door_swings": pending_swings,
        "corrections": {
            "source": str(corrections_path) if corrections_path else None,
            "applied_opening_overrides": applied_opening_overrides,
            "applied_room_display_extensions": applied_room_extensions,
            "unknown_object_ids": unknown_corrections,
        },
        "can_replace_confirmed_base": False,
        "next_action": "review imported topology and normalize OOM openings before base acceptance",
    }
    return package, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a reviewed legacy topology master into the current source package schema.")
    parser.add_argument("topology", type=Path)
    parser.add_argument("source_image", type=Path)
    parser.add_argument("output_package", type=Path)
    parser.add_argument("report_output", type=Path)
    parser.add_argument("--dimension-register", type=Path)
    parser.add_argument("--corrections", type=Path)
    parser.add_argument("--package-id", default="staged_topology_import_v1")
    parser.add_argument("--version", default="base_staged_import_v1")
    parser.add_argument("--exterior-thickness", type=float, default=240.0)
    parser.add_argument("--interior-thickness", type=float, default=120.0)
    args = parser.parse_args()

    topology = load_json(args.topology)
    register_path = dimension_register_path(args.topology, topology, args.dimension_register)
    register = load_json(register_path) if register_path else None
    corrections = load_json(args.corrections) if args.corrections else None
    package, report = build_package(
        args.topology,
        topology,
        args.source_image,
        register,
        args.corrections,
        corrections,
        args.package_id,
        args.version,
        args.exterior_thickness,
        args.interior_thickness,
    )
    args.output_package.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.output_package.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"import_status={report['status']} package={args.output_package}")
    print(f"preserved=walls:{report['output_counts']['walls']} openings:{report['output_counts']['openings']} rooms:{report['output_counts']['rooms']} dimensions:{report['output_counts']['dimension_chains']}")
    print(f"pending_swings={len(report['pending_door_swings'])} missing_hosts={len(report['missing_opening_hosts'])}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
