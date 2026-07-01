#!/usr/bin/env python3
"""Draft start/end anchors for dimension chains from referenced model objects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dimension_chain_audit import DEFAULT_TOLERANCE_MM, load_json, write_json
from dimension_chain_calibrator import build_plan


def candidate_model(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("candidate_model") if isinstance(data.get("candidate_model"), dict) else data


def source_chains(data: dict[str, Any], model: dict[str, Any]) -> list[dict[str, Any]]:
    chains = data.get("dimension_chains")
    if isinstance(chains, list) and chains:
        return chains
    model_chains = model.get("dimension_chains")
    return model_chains if isinstance(model_chains, list) else []


def object_points(item: dict[str, Any]) -> list[tuple[float, float]]:
    geometry = item.get("geometry") or {}
    points: list[tuple[float, float]] = []
    if geometry.get("kind") == "line":
        for key in ["start", "end"]:
            value = geometry.get(key)
            if isinstance(value, list) and len(value) >= 2:
                points.append((float(value[0]), float(value[1])))
    elif geometry.get("kind") == "rect":
        center = geometry.get("center") or []
        size = geometry.get("size") or []
        if len(center) >= 2 and len(size) >= 2:
            half_x = float(size[0]) / 2
            half_y = float(size[1]) / 2
            cx = float(center[0])
            cy = float(center[1])
            points.extend([(cx - half_x, cy - half_y), (cx + half_x, cy + half_y)])
    elif geometry.get("kind") == "arc":
        center = geometry.get("center") or []
        radius = float(geometry.get("radius") or 0)
        if len(center) >= 2:
            points.extend(
                [
                    (float(center[0]) - radius, float(center[1]) - radius),
                    (float(center[0]) + radius, float(center[1]) + radius),
                ]
            )
    for value in item.get("polygon", []) or []:
        if isinstance(value, list) and len(value) >= 2:
            points.append((float(value[0]), float(value[1])))
    position = item.get("position")
    if isinstance(position, list) and len(position) >= 2:
        points.append((float(position[0]), float(position[1])))
    return points


def object_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for key in ["walls", "openings", "rooms", "furniture", "fixed_fixtures", "zones"]:
        for item in model.get(key, []) or []:
            object_id = item.get("id")
            if object_id:
                result[str(object_id)] = item
    return result


def role_lookup(calibration_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    roles: dict[str, dict[str, Any]] = {}
    for axis_plan in calibration_plan.get("axis_plans", []) or []:
        for item in axis_plan.get("chain_roles", []) or []:
            chain_id = item.get("id")
            if chain_id:
                roles[str(chain_id)] = item
    return roles


def coordinate_extent(points: list[tuple[float, float]], axis: str) -> tuple[float, float] | None:
    if not points:
        return None
    index = 0 if axis == "x" else 1
    values = [point[index] for point in points]
    return min(values), max(values)


def draft_anchor(
    chain: dict[str, Any],
    objects: dict[str, dict[str, Any]],
    role: dict[str, Any] | None,
    model_extents: dict[str, Any],
) -> dict[str, Any]:
    axis = chain.get("axis")
    chain_id = chain.get("id")
    object_ids = [str(item) for item in chain.get("object_ids") or []]
    referenced = [objects[object_id] for object_id in object_ids if object_id in objects]
    missing = [object_id for object_id in object_ids if object_id not in objects]
    points = [point for item in referenced for point in object_points(item)]
    extent = coordinate_extent(points, axis) if axis in {"x", "y"} else None
    role_name = role.get("role") if role else "unclassified"
    if role_name == "primary_datum" and axis in {"x", "y"} and model_extents.get("available"):
        extent = (float(model_extents[f"min_{axis}"]), float(model_extents[f"max_{axis}"]))
    total = sum(float(value) for value in chain.get("segments_mm") or [] if isinstance(value, (int, float)))

    issues: list[dict[str, Any]] = []
    if axis not in {"x", "y"}:
        issues.append({"level": "warning", "type": "axis_not_anchorable", "message": "Only x/y chains can receive geometric anchors."})
    if missing:
        issues.append({"level": "error", "type": "missing_referenced_objects", "message": "Some referenced objects are missing.", "object_ids": missing})
    if not referenced:
        issues.append({"level": "error", "type": "no_referenced_objects", "message": "No referenced objects were found for this chain."})
    if extent is None:
        issues.append({"level": "warning", "type": "extent_unavailable", "message": "Could not infer coordinate extent from referenced objects."})

    start_ref = None
    end_ref = None
    span = None
    residual = None
    if extent is not None:
        span = extent[1] - extent[0]
        residual = abs(total - span)
        anchor_source = "model_extent_primary_datum" if role_name == "primary_datum" else "referenced_object_extent"
        start_ref = {"axis": axis, "coordinate_mm": round(extent[0], 3), "source": anchor_source}
        end_ref = {"axis": axis, "coordinate_mm": round(extent[1], 3), "source": anchor_source}
        if residual > DEFAULT_TOLERANCE_MM:
            issues.append(
                {
                    "level": "warning",
                    "type": "anchor_span_mismatch",
                    "message": "Referenced object span does not match dimension total.",
                    "value": {"dimension_total_mm": round(total, 3), "anchor_span_mm": round(span, 3), "residual_mm": round(residual, 3)},
                }
            )

    datum_role = role_name
    confidence = "high" if not issues and datum_role in {"primary_datum", "compatible_reference"} else "medium" if start_ref and end_ref else "low"
    return {
        "id": chain_id,
        "axis": axis,
        "datum_role": datum_role,
        "dimension_total_mm": round(total, 3),
        "start_ref": start_ref,
        "end_ref": end_ref,
        "anchor_span_mm": None if span is None else round(span, 3),
        "residual_mm": None if residual is None else round(residual, 3),
        "referenced_object_ids": object_ids,
        "missing_object_ids": missing,
        "confidence": confidence,
        "issues": issues,
    }


def build_anchor_draft(data: dict[str, Any], tolerance_mm: float = DEFAULT_TOLERANCE_MM) -> dict[str, Any]:
    model = candidate_model(data)
    chains = source_chains(data, model)
    calibration_plan = build_plan(data, tolerance_mm)
    objects = object_index(model)
    roles = role_lookup(calibration_plan)
    model_extents = calibration_plan.get("model_extents", {}) or {}
    drafts = [draft_anchor(chain, objects, roles.get(str(chain.get("id"))), model_extents) for chain in chains]
    error_count = sum(1 for draft in drafts for item in draft["issues"] if item["level"] == "error")
    warning_count = sum(1 for draft in drafts for item in draft["issues"] if item["level"] == "warning")
    anchored_count = sum(1 for draft in drafts if draft.get("start_ref") and draft.get("end_ref"))
    all_primary_clear = all(
        not draft["issues"] for draft in drafts if draft.get("datum_role") in {"primary_datum", "compatible_reference"}
    )
    gate = "ready_for_review" if anchored_count and not error_count else "needs_manual_anchor"
    level = "L3" if gate == "ready_for_review" and not warning_count and all_primary_clear else "L2" if anchored_count else "L1"
    return {
        "schema_version": "dimension_chain_anchor_draft_v1",
        "anchor_gate": gate,
        "anchor_level": level,
        "can_quick_concept": level in {"L2", "L3", "L4"},
        "can_stable_deepening": gate == "ready_for_review" and level == "L3",
        "summary": {
            "dimension_chain_count": len(chains),
            "anchored_chain_count": anchored_count,
            "error_count": error_count,
            "warning_count": warning_count,
        },
        "calibration_gate": calibration_plan.get("calibration_gate"),
        "calibration_level": calibration_plan.get("calibration_level"),
        "anchor_drafts": drafts,
        "recommended_next_steps": recommended_steps(gate, level),
    }


def recommended_steps(gate: str, level: str) -> list[str]:
    if gate == "ready_for_review" and level == "L3":
        return [
            "Review anchor refs before applying them to source_extraction_package.",
            "Create a new source extraction package version with explicit start_ref/end_ref/datum_role.",
            "Run source extraction validation and geometry validation again.",
        ]
    return [
        "Keep this as an anchor draft, not source truth.",
        "Manually confirm chains with span mismatch or missing references.",
        "Only promote anchors after start/end objects are visually confirmed against the source plan.",
    ]


def summarize(report: dict[str, Any]) -> list[str]:
    summary = report.get("summary", {})
    lines = [
        f"anchor_gate={report.get('anchor_gate')} anchor_level={report.get('anchor_level')}",
        f"can_quick_concept={str(report.get('can_quick_concept')).lower()} can_stable_deepening={str(report.get('can_stable_deepening')).lower()}",
        f"counts=chains:{summary.get('dimension_chain_count')} anchored:{summary.get('anchored_chain_count')} warnings:{summary.get('warning_count')} errors:{summary.get('error_count')}",
    ]
    for draft in report.get("anchor_drafts", []) or []:
        lines.append(
            f"{draft.get('id')}: role={draft.get('datum_role')} confidence={draft.get('confidence')} residual={draft.get('residual_mm')}"
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tolerance-mm", type=float, default=DEFAULT_TOLERANCE_MM)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    report = build_anchor_draft(load_json(args.input), args.tolerance_mm)
    write_json(args.output, report)
    if not args.json_only:
        for line in summarize(report):
            print(line)
    return 0 if report["anchor_gate"] in {"ready_for_review", "needs_manual_anchor"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
