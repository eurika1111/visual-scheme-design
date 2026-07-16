#!/usr/bin/env python3
"""Build isolated residential scheme intents from user-approved directions.

The planner decides strategy, targets, risk, and placement requirements. It does
not invent final coordinates. Unresolved placement requests intentionally keep
the deterministic-draft gate closed until a later layout step resolves them.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOM_KEYWORDS = {
    "kitchen": ("kitchen", "厨房"),
    "living": ("living", "客厅", "餐厅", "dining", "public"),
    "bedroom": ("bed", "卧室", "study", "书房"),
    "bathroom": ("bath", "卫生间", "卫浴"),
    "entry": ("entry", "foyer", "入户", "玄关"),
    "passage": ("passage", "corridor", "hall", "过道", "过厅"),
    "balcony": ("balcony", "阳台"),
}

KITCHEN_CATEGORIES = {"kitchen_island", "base_cabinet", "cabinet", "countertop", "sink_cabinet", "stove", "fridge"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalized_text(*values: Any) -> str:
    return " ".join(str(value or "").lower() for value in values)


def point_in_polygon(point: list[float], polygon: list[list[float]]) -> bool:
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, current in enumerate(polygon):
        xi, yi = current
        xj, yj = polygon[j]
        crosses = (yi > y) != (yj > y)
        if crosses and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def infer_room_roles(base: dict[str, Any]) -> dict[str, list[str]]:
    rooms = base.get("rooms", []) or []
    roles = {role: [] for role in ROOM_KEYWORDS}
    room_by_id = {room.get("id"): room for room in rooms if room.get("id")}

    for room in rooms:
        room_id = room.get("id")
        text = normalized_text(room_id, room.get("name"), room.get("function"), room.get("category"))
        for role, keywords in ROOM_KEYWORDS.items():
            if room_id and any(keyword in text for keyword in keywords):
                roles[role].append(room_id)

    for item in base.get("furniture", []) or []:
        center = (item.get("geometry") or {}).get("center")
        category = str(item.get("category") or "")
        if not center:
            continue
        role = "kitchen" if category in KITCHEN_CATEGORIES else "living" if category == "sofa" else None
        if not role or roles[role]:
            continue
        for room_id, room in room_by_id.items():
            polygon = room.get("polygon") or []
            if len(polygon) >= 3 and point_in_polygon(center, polygon):
                roles[role].append(room_id)
                break

    return {role: sorted(set(ids)) for role, ids in roles.items()}


def values_of(brief: dict[str, Any], collection: str, item_type: str | None = None) -> list[Any]:
    values = []
    for item in brief.get(collection, []) or []:
        if not isinstance(item, dict):
            continue
        if item_type is None or item.get("type") == item_type:
            values.append(item.get("value"))
    return values


def has_text(values: list[Any], *needles: str) -> bool:
    text = normalized_text(*values)
    return any(needle.lower() in text for needle in needles)


def protected_objects(base: dict[str, Any], brief: dict[str, Any], roles: dict[str, list[str]]) -> list[str]:
    protected = {
        wall.get("id")
        for wall in base.get("walls", []) or []
        if wall.get("id") and wall.get("alteration") == "do_not_alter"
    }
    for key in ("fixed_fixtures", "fixtures"):
        protected.update(item.get("id") for item in base.get(key, []) or [] if item.get("id"))

    no_change = values_of(brief, "hard_constraints", "no_change_area")
    if has_text(no_change, "卫生间", "bath"):
        protected.update(roles["bathroom"])
    if has_text(no_change, "厨房", "kitchen"):
        protected.update(roles["kitchen"])
    if has_text(no_change, "阳台", "balcony"):
        protected.update(roles["balcony"])
    return sorted(item for item in protected if item)


def case_strategies(case_data: dict[str, Any] | None, option_id: str) -> list[dict[str, Any]]:
    if not case_data:
        return []
    raw = case_data.get("strategies", case_data.get("case_strategies", []))
    selected = []
    for item in raw or []:
        allowed = item.get("allowed_in_options") or []
        if not allowed or option_id in allowed:
            selected.append({
                "id": item.get("id"),
                "transferable_strategy": item.get("transferable_strategy"),
                "risk_level": item.get("risk_level", "unknown"),
                "required_validation": item.get("required_validation", []),
                "copy_image_geometry": False,
            })
    return selected


def request(request_id: str, kind: str, target_spaces: list[str], purpose: str, **extra: Any) -> dict[str, Any]:
    result = {
        "id": request_id,
        "kind": kind,
        "target_spaces": sorted(set(target_spaces)),
        "purpose": purpose,
        "status": "placement_required",
    }
    result.update(extra)
    return result


def build_option(
    direction: dict[str, Any],
    base_version: str,
    brief: dict[str, Any],
    roles: dict[str, list[str]],
    protected: list[str],
    case_data: dict[str, Any] | None,
) -> dict[str, Any]:
    option_id = str(direction["option_id"])
    version = str(direction["version"])
    name = str(direction["name"])
    risk = str(direction.get("alteration_risk") or "unassessed")
    strategy_kind = str(direction.get("strategy_kind") or "custom")
    storage_high = has_text(values_of(brief, "preferences", "storage"), "strong_storage")
    work_focus = has_text(values_of(brief, "preferences", "life_focus"), "居家办公", "home office", "work")
    kitchen_interest = has_text(values_of(brief, "preferences", "kitchen"), "improve_kitchen_openness")
    island_avoid = has_text(values_of(brief, "hard_constraints", "island"), "avoid_island")
    island_interest = not island_avoid and (
        has_text(values_of(brief, "preferences", "island"), "include_if_fits")
        or has_text(values_of(brief, "exploration_items", "island"), "test_island_feasibility")
    )
    demolition_risk = (brief.get("risk_profile") or {}).get("demolition", "low")

    requests: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    blockers: list[str] = []
    option_code = str(direction.get("code") or option_id).strip().replace(" ", "_")
    essential_targets = roles["living"] + roles["bedroom"]
    requests.append(request(
        f"{option_code}-PLACE-ESSENTIAL-FURNITURE-01",
        "furniture_layout",
        essential_targets,
        "补齐每套方案共有的客厅坐席和卧室睡眠功能。",
    ))
    requests.append(request(
        f"{option_code}-PLACE-BATHROOM-FIXTURES-01",
        "bathroom_fixtures",
        roles["bathroom"],
        "补齐卫生间淋浴和洗手盆，保留底图已有马桶。",
    ))

    if strategy_kind == "daily_efficiency":
        targets = roles["living"] + roles["bedroom"] + roles["passage"]
        operations.append({"id": f"{option_code}-OP-01", "type": "layout_refine", "target_spaces": targets, "description": "保留主要结构，优化家具、收纳和通行。"})
        if storage_high:
            requests.append(request(f"{option_code}-PLACE-STORAGE-01", "storage", roles["entry"] + roles["passage"] + roles["bedroom"], "增加收纳但不压缩主通道。", depth_range_mm=[350, 600]))
        if work_focus:
            requests.append(request(f"{option_code}-PLACE-WORK-01", "work_area", roles["bedroom"] + roles["living"], "安排可持续使用的学习或办公位置。", preferred_size_mm=[1200, 600]))
        summary = "保留主要结构和固定服务区，优先解决家具尺度、收纳和日常动线。"
        differentiation = {"alteration_scope": "none_or_light", "primary_goal": "daily_efficiency", "spatial_character": "stable"}
        validation = ["check_furniture_footprints", "check_door_swing_clearance", "check_circulation_width"]
    elif strategy_kind == "kitchen_living_relation":
        targets = roles["kitchen"] + roles["living"]
        operations.append({"id": f"{option_code}-OP-01", "type": "relationship_upgrade", "target_spaces": targets, "description": "测试厨房、餐区和客厅之间更紧密的关系。"})
        if not roles["kitchen"]:
            blockers.append("missing_kitchen_room_mapping")
        if island_interest:
            requests.append(request(f"{option_code}-PLACE-ISLAND-01", "kitchen_island", targets, "验证岛台或餐岛是否适配。", preferred_size_mm=[1600, 800], required_clearance_mm=900))
        else:
            requests.append(request(f"{option_code}-PLACE-DINING-01", "dining_layout", targets, "即使保持封闭厨房，也要明确餐区与客厅的家具关系。"))
        if kitchen_interest or (brief.get("risk_profile") or {}).get("open_kitchen") == "unclear":
            requests.append(request(f"{option_code}-SELECT-KITCHEN-WALL-01", "wall_change_candidate", targets, "选择可讨论的局部隔墙，不自动拆墙。", status="wall_selection_required", requires_verification=True, blocking=False))
        summary = "在不触碰硬约束的前提下，重点比较客餐厨关系、局部开放和岛台可行性。"
        differentiation = {"alteration_scope": "local_candidate", "primary_goal": "kitchen_living_relation", "spatial_character": "connected"}
        validation = ["check_kitchen_workflow", "check_island_clearance", "check_fixed_service_zones", "check_circulation_width"]
    elif strategy_kind == "flexible_use":
        targets = roles["bedroom"] + roles["passage"] + roles["entry"] + roles["living"]
        operations.append({"id": f"{option_code}-OP-01", "type": "flexible_space_strategy", "target_spaces": targets, "description": "探索弹性房间、复合功能和更鲜明的空间组织。"})
        requests.append(request(f"{option_code}-PLACE-FLEX-01", "multifunction_layout", targets, "建立与其他获批方向不同的弹性功能组合。"))
        if storage_high:
            requests.append(request(f"{option_code}-PLACE-STORAGE-01", "integrated_storage", roles["passage"] + roles["entry"] + roles["bedroom"], "形成连续但不阻断动线的收纳策略。", depth_range_mm=[350, 600]))
        if demolition_risk == "high":
            requests.append(request(f"{option_code}-PLACE-PARTITION-01", "curved_or_new_partition", roles["living"] + roles["entry"], "探索受控曲线或新隔断。", requires_verification=True))
        summary = "以弹性功能和空间重组形成高差异方案；拆改未确认时只登记候选，不自动执行。"
        differentiation = {"alteration_scope": "exploratory", "primary_goal": "flexibility", "spatial_character": "distinctive"}
        validation = ["check_room_function", "check_circulation_width", "check_door_swing_clearance", "check_proposal_geometry"]
    else:
        operations.extend(direction.get("operations", []) or [])
        requests.extend(direction.get("placement_requests", []) or [])
        summary = str(direction.get("intent_summary") or direction.get("core_move") or "用户批准的自定义空间方向。")
        differentiation = direction.get("differentiation") or {}
        validation = direction.get("validation_plan", []) or []
        if not operations and not requests:
            blockers.append("custom_direction_has_no_operations_or_placement_requests")

    summary = str(direction.get("intent_summary") or summary)
    differentiation = direction.get("differentiation") or differentiation
    validation = direction.get("validation_plan") or validation

    if not any(roles.values()):
        blockers.append("missing_room_semantics")

    return {
        "schema_version": "scheme_intent_v1",
        "scheme_id": option_id,
        "option_code": option_code,
        "version": version,
        "name": name,
        "parent_base": base_version,
        "status": "strategy_ready_with_blockers" if blockers else "strategy_ready",
        "risk_level": risk,
        "intent_summary": summary,
        "primary_problem": direction.get("primary_problem"),
        "core_move": direction.get("core_move"),
        "tradeoff": direction.get("tradeoff"),
        "direction_approval": "user_approved",
        "differentiation": differentiation,
        "protected_base_objects": protected,
        "hard_constraints": brief.get("hard_constraints", []),
        "preferences_used": brief.get("preferences", []),
        "case_strategies": case_strategies(case_data, option_id),
        "proposal_objects": [],
        "placement_requests": requests,
        "operations": operations,
        "validation_plan": validation,
        "risk_flags": brief.get("unknowns", []),
        "blockers": blockers,
        "layout_gate": "placement_required" if requests else "ready",
        "generation_report": {
            "status": "not_rendered",
            "geometry_authority": base_version,
            "image_authority": False,
        },
    }


def build_markdown(plan: dict[str, Any]) -> str:
    lines = [
        f"# 方案策略规划 - {plan.get('project_id')}",
        "",
        f"- 当前底图：`{plan.get('base_version')}`",
        f"- 规划状态：`{plan.get('status')}`",
        "- 当前只确定方案策略和目标空间，具体坐标将在下一步受控落位后写入。",
        "",
    ]
    for option in plan["options"]:
        lines.extend([
            f"## {option['scheme_id']} - {option['name']}",
            "",
            option["intent_summary"],
            "",
            f"- 风险级别：`{option['risk_level']}`",
            f"- 落位状态：`{option['layout_gate']}`",
            f"- 目标空间：{', '.join(sorted({space for request_item in option['placement_requests'] for space in request_item['target_spaces']})) or '需要补充房间映射'}",
            f"- 待落位事项：{len(option['placement_requests'])}",
            f"- 阻断项：{', '.join(option['blockers']) or '无'}",
            "",
        ])
    lines.extend(["## 下一步", "", "把待落位事项转换成受控坐标和对象，校验通过后再生成确定性方案草图。", ""])
    return "\n".join(lines)


def differentiation_report(options: list[dict[str, Any]]) -> dict[str, Any]:
    comparisons = []
    for index, left in enumerate(options):
        for right in options[index + 1:]:
            left_axes = left["differentiation"]
            right_axes = right["differentiation"]
            changed = sorted(key for key in set(left_axes) | set(right_axes) if left_axes.get(key) != right_axes.get(key))
            comparisons.append({
                "left": left["scheme_id"],
                "right": right["scheme_id"],
                "changed_axes": changed,
                "status": "passed" if len(changed) >= 2 else "failed",
            })
    return {
        "status": "passed" if all(item["status"] == "passed" for item in comparisons) else "failed",
        "comparisons": comparisons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan isolated approved scheme intents without inventing coordinates.")
    parser.add_argument("base_model", type=Path)
    parser.add_argument("needs_brief", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--case-strategy", type=Path)
    parser.add_argument("--base-fidelity-report", type=Path, required=True)
    parser.add_argument("--directions", type=Path, required=True)
    args = parser.parse_args()

    base = load_json(args.base_model)
    brief = load_json(args.needs_brief)
    direction_package = load_json(args.directions)
    fidelity = load_json(args.base_fidelity_report)
    effective_base_version = base.get("version") or (base.get("base_inference") or {}).get("version") or "base_v1"
    if fidelity.get("base_version") != effective_base_version or not fidelity.get("can_plan_schemes"):
        raise SystemExit("base fidelity gate must be open for this exact base version")
    if (base.get("coordinate_system") or {}).get("origin") != "lower_left":
        raise SystemExit("base model must use lower_left origin")
    if (base.get("coordinate_system") or {}).get("unit") != "mm":
        raise SystemExit("base model must use millimeters")
    if brief.get("schema_version") != "needs_brief_v1":
        raise SystemExit("needs brief must use needs_brief_v1")
    if direction_package.get("schema_version") != "approved_option_directions_v1":
        raise SystemExit("directions must use approved_option_directions_v1")
    if direction_package.get("status") != "approved":
        raise SystemExit("option directions must be explicitly approved")
    directions = direction_package.get("directions") or []
    if not isinstance(directions, list) or not directions:
        raise SystemExit("at least one approved option direction is required")
    required_direction_fields = {"option_id", "version", "name", "code", "strategy_kind", "primary_problem", "core_move", "tradeoff", "alteration_risk", "differentiation"}
    for index, direction in enumerate(directions):
        if not isinstance(direction, dict):
            raise SystemExit(f"approved direction {index} must be an object")
        missing = sorted(field for field in required_direction_fields if not direction.get(field))
        if missing:
            raise SystemExit(f"approved direction {index} is missing: {', '.join(missing)}")
    for unique_field in ("option_id", "version", "code"):
        values = [item.get(unique_field) for item in directions]
        if len(values) != len(directions) or len(set(values)) != len(values):
            raise SystemExit(f"approved option directions require unique {unique_field} values")

    case_data = load_json(args.case_strategy) if args.case_strategy else None
    base_version = base.get("version") or (base.get("base_inference") or {}).get("version") or "base_v1"
    roles = infer_room_roles(base)
    protected = protected_objects(base, brief, roles)
    options = [build_option(direction, base_version, brief, roles, protected, case_data) for direction in directions]
    plan = {
        "schema_version": "scheme_option_plan_v1",
        "project_id": brief.get("project_id", "unknown_project"),
        "base_version": base_version,
        "needs_brief_version": brief.get("schema_version"),
        "approved_direction_package": str(args.directions.resolve()),
        "approved_option_count": len(directions),
        "status": "strategy_ready_with_blockers" if any(option["blockers"] for option in options) else "strategy_ready",
        "room_roles": roles,
        "protected_base_objects": protected,
        "options": options,
        "differentiation_check": differentiation_report(options),
        "next_action": "resolve placement requests before deterministic draft rendering",
    }
    if plan["differentiation_check"]["status"] != "passed":
        raise SystemExit("scheme options must differ on at least two controlled axes")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "scheme_option_plan.json", plan)
    (args.output_dir / "scheme_option_plan.md").write_text(build_markdown(plan), encoding="utf-8")
    for option in options:
        filename = option["version"] + "_intent.json"
        write_json(args.output_dir / filename, option)

    print(f"option_plan={args.output_dir / 'scheme_option_plan.json'}")
    print(f"option_plan_md={args.output_dir / 'scheme_option_plan.md'}")
    for option in options:
        print(f"{option['version']}={args.output_dir / (option['version'] + '_intent.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
