#!/usr/bin/env python3
"""Draft repair operations from a validation report without applying them.

The draft is intentionally conservative: it proposes review-required operations
and does not modify the model or project state. Temporary objects created by
operations or copied from another scheme are safer to remove than to push across
unknown room boundaries.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


MOVABLE_SOURCES = ("operation", "copied_from:")
REPAIRABLE_TYPES = {
    "furniture_furniture_collision",
    "furniture_clearance_warning",
    "kitchen_workflow_collision",
    "kitchen_workflow_clearance_warning",
    "door_swing_clearance_warning",
    "circulation_width_warning",
}
REMOVE_FIRST_TYPES = {
    "furniture_furniture_collision",
    "kitchen_workflow_collision",
    "furniture_wall_collision",
    "door_swing_furniture_collision",
    "door_swing_clearance_warning",
    "circulation_width_warning",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def furniture_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item.get("id"): item for item in model.get("furniture", []) if item.get("id")}


def rect_center(item: dict[str, Any]) -> list[float] | None:
    geom = item.get("geometry", {})
    if geom.get("kind") != "rect":
        return None
    center = geom.get("center")
    if not isinstance(center, list) or len(center) != 2:
        return None
    return [float(center[0]), float(center[1])]


def is_operation_owned(item: dict[str, Any]) -> bool:
    source = str(item.get("source", ""))
    return source == "operation" or source.startswith("copied_from:") or item.get("status") in {"new", "modified"}


def choose_operation_owned(ids: list[str], items: dict[str, dict[str, Any]]) -> str | None:
    for object_id in reversed(ids):
        item = items.get(object_id)
        if item and is_operation_owned(item):
            return object_id
    return None


def choose_move_target(ids: list[str], items: dict[str, dict[str, Any]]) -> str | None:
    return choose_operation_owned(ids, items) or (ids[-1] if ids else None)


def unit_vector(from_center: list[float], to_center: list[float]) -> tuple[float, float]:
    dx = to_center[0] - from_center[0]
    dy = to_center[1] - from_center[1]
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return (1.0, 0.0)
    return (dx / length, dy / length)


def append_reason(reasons: dict[str, list[str]], object_id: str, reason: str) -> None:
    if reason not in reasons.setdefault(object_id, []):
        reasons[object_id].append(reason)


def issue_furniture_ids(issue: dict[str, Any]) -> list[str]:
    if isinstance(issue.get("furniture_ids"), list):
        return [str(value) for value in issue["furniture_ids"]]
    if issue.get("furniture_id"):
        return [str(issue["furniture_id"])]
    if isinstance(issue.get("collides_with_furniture"), list):
        return [str(value) for value in issue["collides_with_furniture"]]
    blocked = issue.get("collides_or_too_close_furniture")
    if isinstance(blocked, list):
        ids = []
        for item in blocked:
            if isinstance(item, dict) and item.get("furniture_id"):
                ids.append(str(item["furniture_id"]))
        return ids
    return []


def draft_repairs(model: dict[str, Any], validation: dict[str, Any], padding: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items = furniture_index(model)
    remove_targets: dict[str, list[str]] = {}
    proposed_centers: dict[str, list[float]] = {}
    move_reasons: dict[str, list[str]] = {}
    skipped: list[dict[str, Any]] = []
    issues = list(validation.get("errors", [])) + list(validation.get("warnings", []))

    for issue in issues:
        issue_type = issue.get("type")
        ids = issue_furniture_ids(issue)

        if issue_type in REMOVE_FIRST_TYPES:
            target_id = issue.get("object_id") or issue.get("furniture_id") or choose_operation_owned(ids, items)
            if target_id and target_id in items and is_operation_owned(items[target_id]):
                append_reason(remove_targets, target_id, f"{issue_type}: temporary object conflicts with controlled geometry")
                continue

        if issue_type not in REPAIRABLE_TYPES or len(ids) < 2:
            skipped.append({"type": issue_type, "reason": "no safe draft operation in V1", "issue": issue})
            continue

        target_id = choose_move_target(ids, items)
        if not target_id or target_id not in items:
            skipped.append({"type": issue_type, "reason": "target furniture not found", "issue": issue})
            continue
        if target_id in remove_targets:
            continue

        other_id = next((object_id for object_id in ids if object_id != target_id and object_id in items), None)
        if not other_id:
            skipped.append({"type": issue_type, "reason": "reference furniture not found", "issue": issue})
            continue

        target_center = proposed_centers.get(target_id) or rect_center(items[target_id])
        other_center = rect_center(items[other_id])
        if not target_center or not other_center:
            skipped.append({"type": issue_type, "reason": "only rect furniture can be moved in V1", "issue": issue})
            continue

        ux, uy = unit_vector(other_center, target_center)
        distance = float(issue.get("distance_mm") or 0.0)
        required = float(issue.get("required_clearance_mm") or 0.0)
        shift = max(required - distance + padding, padding)
        proposed_centers[target_id] = [round(target_center[0] + ux * shift, 3), round(target_center[1] + uy * shift, 3)]
        append_reason(move_reasons, target_id, f"{issue_type}: move away from {other_id}")

    operations: list[dict[str, Any]] = []
    for target_id, reasons in remove_targets.items():
        operations.append({
            "operation": "remove_furniture",
            "target_id": target_id,
            "reason": "; ".join(reasons),
            "review_required": True,
        })
    for target_id, center in proposed_centers.items():
        if target_id in remove_targets:
            continue
        operations.append({
            "operation": "move_object",
            "target_id": target_id,
            "center": center,
            "reason": "; ".join(move_reasons.get(target_id, [])),
            "review_required": True,
        })
    return operations, skipped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--parent-version", default=None)
    parser.add_argument("--new-version", default=None)
    parser.add_argument("--padding", type=float, default=100.0)
    args = parser.parse_args()

    model = load_json(args.model)
    validation = load_json(args.validation)
    operations, skipped = draft_repairs(model, validation, args.padding)
    parent = args.parent_version or model.get("version", "unknown")
    output = {
        "schema_version": "home_geometry_repair_operations_draft_v1",
        "parent_version": parent,
        "new_version": args.new_version or f"{parent}_repair_draft_v1",
        "status": "draft_review_required",
        "source_model": str(args.model),
        "source_validation": str(args.validation),
        "operations": operations,
        "skipped_issues": skipped,
        "notes": [
            "Draft only: review before applying.",
            "Remove operations are limited to operation/copied/new furniture unless manually overridden.",
            "Generated draft does not update project_state.json.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"draft_operations={args.output}")
    print(f"operations={len(operations)} skipped={len(skipped)}")
    return 0 if operations else 1


if __name__ == "__main__":
    raise SystemExit(main())
