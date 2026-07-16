#!/usr/bin/env python3
"""Resolve scheme placement requests into validated rectangular objects."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from geometry_backend import rect_corners
from geometry_validator import point_in_polygon, validate
from scheme_option_planner import infer_room_roles


TEMPLATES = {
    "sofa": {"name": "沙发", "size": [2100, 900], "clearance_mm": 600, "centered": False},
    "bed": {"name": "双人床", "size": [1800, 2000], "clearance_mm": 550, "centered": False},
    "storage": {"name": "收纳柜", "size": [1200, 450], "clearance_mm": 100, "centered": False},
    "desk": {"name": "学习办公桌", "size": [1200, 600], "clearance_mm": 450, "centered": False},
    "dining_table": {"name": "餐桌", "size": [1400, 800], "clearance_mm": 750, "centered": True},
    "kitchen_island": {"name": "厨房餐岛", "size": [1600, 800], "clearance_mm": 900, "centered": True},
    "sofa_bed": {"name": "弹性沙发床", "size": [1900, 900], "clearance_mm": 550, "centered": False},
    "flex_table": {"name": "弹性工作桌", "size": [1200, 700], "clearance_mm": 600, "centered": True},
    "shower": {"name": "淋浴区", "size": [900, 900], "clearance_mm": 60, "margin_mm": 30, "centered": False},
    "basin": {"name": "洗手盆", "size": [600, 450], "clearance_mm": 180, "margin_mm": 60, "centered": False},
}

RESOLVED_STATUSES = {"resolved", "not_required", "accepted_without_object"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def room_index(base: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {room.get("id"): room for room in base.get("rooms", []) or [] if room.get("id")}


def room_for_point(point: list[float], rooms: dict[str, dict[str, Any]]) -> str | None:
    value = (float(point[0]), float(point[1]))
    for room_id, room in rooms.items():
        polygon = [(float(p[0]), float(p[1])) for p in room.get("polygon", []) or []]
        if len(polygon) >= 3 and point_in_polygon(value, polygon):
            return room_id
    return None


def fixture_obstacles(base: dict[str, Any]) -> list[dict[str, Any]]:
    obstacles = []
    for key in ("fixed_fixtures", "fixtures"):
        for item in base.get(key, []) or []:
            if (item.get("geometry") or {}).get("kind") != "rect":
                continue
            obstacle = copy.deepcopy(item)
            obstacle["type"] = "furniture"
            obstacle.setdefault("category", "fixed_fixture")
            obstacle.setdefault("clearance_mm", 100)
            obstacles.append(obstacle)
    return obstacles


def ordered_targets(kind: str, targets: list[str], roles: dict[str, list[str]]) -> list[str]:
    priorities = {
        "kitchen_island": ["kitchen", "living"],
        "dining_layout": ["living", "kitchen"],
        "storage": ["entry", "passage", "bedroom", "living"],
        "integrated_storage": ["passage", "entry", "bedroom", "living"],
        "work_area": ["bedroom", "living"],
        "multifunction_layout": ["bedroom", "living"],
    }
    target_set = set(targets)
    ordered = []
    for role in priorities.get(kind, []):
        ordered.extend(room_id for room_id in roles.get(role, []) if room_id in target_set and room_id not in ordered)
    ordered.extend(room_id for room_id in targets if room_id not in ordered)
    return ordered


def candidate_centers(room: dict[str, Any], size: list[float], centered: bool, margin: float = 180.0) -> list[tuple[list[float], float]]:
    polygon = [(float(p[0]), float(p[1])) for p in room.get("polygon", []) or []]
    if len(polygon) < 3:
        return []
    min_x = min(p[0] for p in polygon)
    max_x = max(p[0] for p in polygon)
    min_y = min(p[1] for p in polygon)
    max_y = max(p[1] for p in polygon)
    results: list[tuple[list[float], float]] = []
    for rotation in (0.0, 90.0):
        width, depth = (size if rotation == 0 else [size[1], size[0]])
        low_x = min_x + width / 2 + margin
        high_x = max_x - width / 2 - margin
        low_y = min_y + depth / 2 + margin
        high_y = max_y - depth / 2 - margin
        if low_x > high_x or low_y > high_y:
            continue
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2
        xs = [mid_x, low_x, high_x, (low_x + mid_x) / 2, (mid_x + high_x) / 2]
        ys = [mid_y, low_y, high_y, (low_y + mid_y) / 2, (mid_y + high_y) / 2]
        pairs = [(mid_x, mid_y)] if centered else []
        pairs.extend((x, y) for y in ys for x in xs)
        if centered:
            pairs.extend((x, y) for y in ys for x in xs if (x, y) != (mid_x, mid_y))
        for x, y in pairs:
            value = ([round(x, 3), round(y, 3)], rotation)
            if value not in results:
                results.append(value)
    return results


def rectangle_inside_room(center: list[float], size: list[float], rotation: float, room: dict[str, Any]) -> bool:
    polygon = [(float(p[0]), float(p[1])) for p in room.get("polygon", []) or []]
    corners = rect_corners((float(center[0]), float(center[1])), (float(size[0]), float(size[1])), rotation)
    return len(polygon) >= 3 and all(point_in_polygon(corner, polygon) for corner in corners)


def issue_contains(report: dict[str, Any], object_id: str) -> bool:
    for item in (report.get("errors", []) or []) + (report.get("warnings", []) or []):
        if object_id in json.dumps(item, ensure_ascii=False):
            return True
    return False


def existing_in_room(
    category: str,
    room_id: str,
    items: list[dict[str, Any]],
    rooms: dict[str, dict[str, Any]],
) -> str | None:
    for item in items:
        if item.get("category") != category:
            continue
        center = (item.get("geometry") or {}).get("center")
        if center and room_for_point(center, rooms) == room_id:
            return item.get("id")
    return None


def make_object_id(intent: dict[str, Any], category: str, room_id: str, sequence: int) -> str:
    legacy = {"方案 A": "A", "方案 B": "B", "方案 C": "C"}
    raw_code = str(intent.get("option_code") or legacy.get(intent.get("scheme_id")) or "")
    scheme = re.sub(r"[^A-Za-z0-9]+", "-", raw_code).strip("-").upper()
    if not scheme:
        stable_source = str(intent.get("scheme_id") or intent.get("version") or "unknown-option")
        scheme = "OPT-" + hashlib.sha256(stable_source.encode("utf-8")).hexdigest()[:8].upper()
    category_code = re.sub(r"[^A-Za-z0-9]+", "-", category).strip("-").upper()
    room_code = re.sub(r"[^A-Za-z0-9]+", "-", room_id).strip("-").upper()
    return f"{scheme}-F-{category_code}-{room_code}-{sequence:02d}"


def try_place(
    base: dict[str, Any],
    intent: dict[str, Any],
    request_id: str,
    category: str,
    target_ids: list[str],
    rooms: dict[str, dict[str, Any]],
    proposals: list[dict[str, Any]],
    obstacles: list[dict[str, Any]],
    size_override: list[float] | None = None,
) -> tuple[str | None, int, str | None]:
    template = TEMPLATES[category]
    sizes = [[float(v) for v in (size_override or template["size"])]]
    if category == "bed" and not size_override:
        sizes.extend(([1500.0, 2000.0], [1350.0, 1900.0]))
    if category == "shower" and not size_override:
        sizes.extend(([800.0, 800.0], [700.0, 800.0]))
    if category == "basin" and not size_override:
        sizes.append([500.0, 400.0])
    attempts = 0
    all_items = (base.get("furniture", []) or []) + proposals
    for room_id in target_ids:
        room = rooms.get(room_id)
        if not room:
            continue
        existing_id = existing_in_room(category, room_id, all_items, rooms)
        if existing_id:
            return existing_id, attempts, "existing_object"
        for variant_index, size in enumerate(sizes):
            for center, rotation in candidate_centers(
                room, size, bool(template["centered"]), float(template.get("margin_mm", 180.0))
            ):
                attempts += 1
                if not rectangle_inside_room(center, size, rotation, room):
                    continue
                object_id = make_object_id(intent, category, room_id, len(proposals) + 1)
                candidate = {
                    "id": object_id,
                    "type": "furniture",
                    "name": template["name"],
                    "category": category,
                    "status": "proposed",
                    "source": f"placement_request:{request_id}",
                    "target_space_id": room_id,
                    "placement_request_id": request_id,
                    "placement_method": "validated_candidate_search",
                    "placement_variant": "standard" if variant_index == 0 else "compact_fallback",
                    "confidence": 0.65 if variant_index == 0 else 0.6,
                    "geometry": {"kind": "rect", "center": center, "size": size, "rotation": rotation},
                    "clearance_mm": float(template["clearance_mm"]),
                }
                test_model = copy.deepcopy(base)
                test_model["furniture"] = copy.deepcopy((base.get("furniture", []) or []) + obstacles + proposals + [candidate])
                if not issue_contains(validate(test_model), object_id):
                    proposals.append(candidate)
                    return object_id, attempts, candidate["placement_variant"]
    return None, attempts, None


def request_specs(request: dict[str, Any], roles: dict[str, list[str]]) -> list[tuple[str, list[str], list[float] | None]]:
    kind = request.get("kind")
    targets = request.get("target_spaces", []) or []
    if kind == "furniture_layout":
        specs = [("sofa", [room_id], None) for room_id in roles["living"] if room_id in targets]
        specs.extend(("bed", [room_id], None) for room_id in roles["bedroom"] if room_id in targets)
        return specs
    if kind in {"storage", "integrated_storage"}:
        return [("storage", ordered_targets(kind, targets, roles), None)]
    if kind == "work_area":
        return [("desk", ordered_targets(kind, targets, roles), request.get("preferred_size_mm"))]
    if kind == "dining_layout":
        return [("dining_table", ordered_targets(kind, targets, roles), None)]
    if kind == "kitchen_island":
        return [("kitchen_island", ordered_targets(kind, targets, roles), request.get("preferred_size_mm"))]
    if kind == "multifunction_layout":
        ordered = ordered_targets(kind, targets, roles)
        return [("flex_table", ordered, None)]
    if kind == "bathroom_fixtures":
        specs = []
        for room_id in roles["bathroom"]:
            if room_id in targets:
                specs.extend((("shower", [room_id], None), ("basin", [room_id], None)))
        return specs
    return []


def resolve(base: dict[str, Any], source_intent: dict[str, Any], version: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    intent = copy.deepcopy(source_intent)
    rooms = room_index(base)
    roles = infer_room_roles(base)
    obstacles = fixture_obstacles(base)
    proposals = copy.deepcopy(intent.get("proposal_objects", []) or [])
    request_reports = []
    updated_requests = []
    total_attempts = 0

    for raw in intent.get("placement_requests", []) or []:
        item = copy.deepcopy(raw)
        request_attempts = 0
        blocking = item.get("blocking", True)
        specs = request_specs(item, roles)
        if not blocking or item.get("kind") == "wall_change_candidate":
            item["blocking"] = False
            item["status"] = "deferred_confirmation"
            item["resolution_note"] = "保留为用户确认项，不自动修改墙体。"
            updated_requests.append(item)
            request_reports.append({"id": item.get("id"), "status": item["status"], "attempts": 0, "object_ids": []})
            continue

        object_ids = []
        failures = []
        if not specs:
            failures.append("unsupported_or_missing_target_semantics")
        for category, target_ids, size_override in specs:
            if not target_ids:
                failures.append(f"missing_target:{category}")
                continue
            object_id, attempts, resolution = try_place(
                base, intent, item.get("id", "PLACEMENT"), category, target_ids, rooms, proposals, obstacles, size_override
            )
            total_attempts += attempts
            request_attempts += attempts
            if object_id:
                object_ids.append(object_id)
            else:
                failures.append(f"no_valid_candidate:{category}:{','.join(target_ids)}")

        if failures:
            item["status"] = "placement_failed"
            item["failures"] = failures
        else:
            item["status"] = "resolved"
            item["resolved_object_ids"] = object_ids
        updated_requests.append(item)
        request_reports.append({
            "id": item.get("id"),
            "status": item["status"],
            "attempts": request_attempts,
            "object_ids": object_ids,
            "failures": failures,
        })

    unresolved = [item for item in updated_requests if item.get("blocking", True) and item.get("status") not in RESOLVED_STATUSES]
    source_version = intent.get("version", "scheme_v1")
    intent["parent_intent"] = source_version
    intent["version"] = version or f"{source_version}_layout_v1"
    intent["proposal_objects"] = proposals
    intent["placement_requests"] = updated_requests
    intent["layout_gate"] = "ready" if not unresolved else "placement_required"
    intent["status"] = "layout_resolved" if not unresolved else "layout_partial"
    intent["generation_report"] = {
        "status": "not_rendered",
        "geometry_authority": intent.get("parent_base"),
        "image_authority": False,
    }

    final_model = copy.deepcopy(base)
    final_model["furniture"] = copy.deepcopy((base.get("furniture", []) or []) + obstacles + proposals)
    final_validation = validate(final_model)
    report = {
        "schema_version": "scheme_placement_report_v1",
        "scheme_id": intent.get("scheme_id"),
        "source_intent": source_version,
        "resolved_intent": intent["version"],
        "layout_gate": intent["layout_gate"],
        "placed_object_count": len(proposals),
        "candidate_attempt_count": total_attempts,
        "request_reports": request_reports,
        "unresolved_request_ids": [item.get("id") for item in unresolved],
        "deferred_request_ids": [item.get("id") for item in updated_requests if item.get("status") == "deferred_confirmation"],
        "confirmation_items": [
            {
                "request_id": item.get("id"),
                "kind": item.get("kind"),
                "target_spaces": item.get("target_spaces", []),
                "failures": item.get("failures", []),
                "question": (
                    "卫浴设施与当前房间或门扇冲突，请确认是否允许调整门向、改用移门或人工指定湿区。"
                    if item.get("kind") == "bathroom_fixtures"
                    else "自动落位未找到合法位置，请确认目标房间或人工指定位置。"
                ),
            }
            for item in unresolved
        ],
        "validation_readiness": final_validation.get("readiness"),
        "validation_error_count": final_validation.get("summary", {}).get("error_count"),
        "validation_warning_count": final_validation.get("summary", {}).get("warning_count"),
        "next_action": "render deterministic draft" if not unresolved else "review failed placements or provide manual coordinates",
    }
    return intent, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve scheme placement requests using validated candidate search.")
    parser.add_argument("base_model", type=Path)
    parser.add_argument("scheme_intent", type=Path)
    parser.add_argument("--output-intent", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    parser.add_argument("--version")
    args = parser.parse_args()

    base = load_json(args.base_model)
    intent = load_json(args.scheme_intent)
    resolved, report = resolve(base, intent, args.version)
    write_json(args.output_intent, resolved)
    write_json(args.report_output, report)
    print(f"resolved_intent={args.output_intent}")
    print(f"placement_report={args.report_output}")
    print(f"layout_gate={report['layout_gate']} placed={report['placed_object_count']} attempts={report['candidate_attempt_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
