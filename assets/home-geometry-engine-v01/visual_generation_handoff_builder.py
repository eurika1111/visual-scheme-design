#!/usr/bin/env python3
"""Build a controlled visual-generation handoff from one accepted scheme version."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from scheme_option_planner import infer_room_roles
from scheme_placement_resolver import room_for_point, room_index


def load_json(path: Path | None) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig")) if path else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review_option(manifest: dict[str, Any], version: str) -> dict[str, Any] | None:
    return next((item for item in manifest.get("options", []) or [] if item.get("version") == version), None)


def history_entry(history: dict[str, Any], version: str) -> dict[str, Any] | None:
    return next((item for item in history.get("versions", []) or [] if item.get("version") == version), None)


def style_ready(style: dict[str, Any]) -> bool:
    return style.get("status") == "confirmed" and bool(style.get("direction"))


def functional_completeness(base: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
    roles = infer_room_roles(base)
    rooms = room_index(base)
    categories: dict[str, set[str]] = {room_id: set() for room_id in rooms}
    for item in (base.get("furniture", []) or []) + (intent.get("proposal_objects", []) or []):
        room_id = item.get("target_space_id")
        center = (item.get("geometry") or {}).get("center")
        if not room_id and center:
            room_id = room_for_point(center, rooms)
        if room_id in categories:
            categories[room_id].add(str(item.get("category") or item.get("type") or "unknown"))
    for key in ("fixed_fixtures", "fixtures"):
        for item in base.get(key, []) or []:
            room_id = item.get("room_id") or item.get("target_space_id")
            if room_id in categories:
                categories[room_id].add(str(item.get("category") or item.get("type") or "unknown"))

    missing = []
    for room_id in roles["bedroom"]:
        if not categories[room_id].intersection({"bed", "sofa_bed"}):
            missing.append({"room_id": room_id, "required": "sleeping_function", "allowed": ["bed", "sofa_bed"]})
    for room_id in roles["living"]:
        if "sofa" not in categories[room_id]:
            missing.append({"room_id": room_id, "required": "living_seating", "allowed": ["sofa"]})
    for room_id in roles["bathroom"]:
        for required in ("toilet", "shower", "basin"):
            if required not in categories[room_id]:
                missing.append({"room_id": room_id, "required": required, "allowed": [required]})
    for room_id in roles["kitchen"]:
        if not categories[room_id].intersection({"kitchen_counter", "countertop", "base_cabinet", "sink_cabinet"}):
            missing.append({"room_id": room_id, "required": "kitchen_worktop", "allowed": ["kitchen_counter"]})
    return {
        "status": "passed" if not missing else "incomplete",
        "room_categories": {room_id: sorted(items) for room_id, items in categories.items()},
        "missing": missing,
    }


def values(items: list[dict[str, Any]], key: str = "value") -> list[str]:
    result = []
    for item in items:
        value = item.get(key)
        if isinstance(value, list):
            result.extend(str(entry) for entry in value)
        elif value is not None:
            result.append(str(value))
    return result


def structure_lock(
    base: dict[str, Any], intent: dict[str, Any], review: dict[str, Any], base_lock: dict[str, Any]
) -> dict[str, Any]:
    return {
        "authority": "locked_base_manifest + base_object_model + isolated_scheme_intent",
        "base_id": base_lock.get("base_id"),
        "base_lock_status": base_lock.get("base_lock_status"),
        "image_is_geometry_authority": False,
        "canvas": base_lock.get("canvas"),
        "coordinate_system": base_lock.get("coordinate_system") or base.get("coordinate_system"),
        "shared_bounds_mm": base_lock.get("bounds_mm") or review.get("shared_bounds_mm"),
        "dimension_anchors": base_lock.get("dimension_anchors", []) or [],
        "wall_ids": [item.get("id") for item in base.get("walls", []) or []],
        "opening_ids": [item.get("id") for item in base.get("openings", []) or []],
        "room_ids": [item.get("id") for item in base.get("rooms", []) or []],
        "fixed_fixture_ids": [
            item.get("id") for key in ("fixed_fixtures", "fixtures") for item in base.get(key, []) or []
        ],
        "proposal_objects": [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "category": item.get("category"),
                "target_space_id": item.get("target_space_id"),
                "geometry": item.get("geometry"),
            }
            for item in intent.get("proposal_objects", []) or []
        ],
        "protected_base_objects": intent.get("protected_base_objects", []) or [],
        "authorized_base_change_operations": intent.get("base_change_operations", []) or [],
    }


def prompt_text(
    intent: dict[str, Any], style: dict[str, Any], selected: dict[str, Any], base_lock: dict[str, Any], stage: str
) -> str:
    palette = ", ".join(style.get("palette", []) or []) or "coherent restrained palette"
    materials = ", ".join(style.get("materials", []) or []) or "realistic residential materials"
    avoid = ", ".join(style.get("avoid", []) or [])
    canvas = base_lock.get("canvas", {}) or {}
    reference = selected.get("png") or (base_lock.get("confirmation_visual") or {}).get("path")
    operations = intent.get("base_change_operations", []) or []
    operations_text = json.dumps(operations, ensure_ascii=False) if operations else "none; preserve every base object"
    placement_rule = (
        "Use the supplied deterministic scheme review as the exact proposal layout."
        if stage == "deep"
        else "Use plausible concept-level furniture placement while preserving all unchanged base geometry."
    )
    return f"""Purpose: Create one client-facing top-down residential visual concept for {intent.get('scheme_id')} | {intent.get('name')}.

Locked base: {base_lock.get('base_id')}.
Use {reference} as the immutable structural reference.
Output exactly {canvas.get('width')} x {canvas.get('height')} px with the same aspect ratio, framing, coordinate frame, scale, and dimension anchors.
Preserve the apartment outline, room topology, walls, doors, windows, kitchen, bathrooms, balcony, and fixed fixtures except for authorized operations.
{placement_rule}

Authorized base-change operations:
{operations_text}

Design intent:
{intent.get('intent_summary', '')}

Visual direction:
{style.get('direction')}
Palette: {palette}
Materials: {materials}
Atmosphere: {style.get('atmosphere', 'comfortable realistic residential atmosphere')}
Furniture language: {style.get('furniture_language', 'coherent and practical')}
Budget expression: {style.get('budget_expression', 'controlled and buildable')}

Hard constraints:
- keep every unchanged wall, opening, room boundary, fixed-service zone, and dimension anchor from the locked base
- do not add, remove, thicken, break, curve, or relocate walls except through the authorized operations above
- do not move doors, windows, kitchen, bathrooms, balcony, or fixed fixtures except through the authorized operations above
- do not mirror, stretch, freely crop, or independently reframe the apartment
- do not invent a second TV wall, extra island, missing shower, missing toilet, or blocked access
- no dimensions, labels, arrows, legends, captions, UI, watermark, or fake CAD text; these are added later
- render one coherent top-down plan image on the exact locked canvas

Avoid:
unreadable text, structural drift, impossible furniture orientation, overpacked decoration{', ' + avoid if avoid else ''}
"""


def style_confirmation_markdown(intent: dict[str, Any], needs: dict[str, Any]) -> str:
    current_style = values([item for item in needs.get("preferences", []) or [] if item.get("type") == "style"])
    known = " / ".join(current_style) if current_style else "尚未明确"
    return f"""# 视觉风格确认

当前选定：{intent.get('scheme_id')} `{intent.get('version')}`

已知倾向：{known}

请先选择一个接近的方向，也可以只说“更暖一点”“不要太网红”这类模糊感受：

1. 温暖克制：浅木、暖白、少量灰绿，舒适耐看。
2. 清爽现代：白灰基底、浅木或浅石材，线条简洁。
3. 自然松弛：木质、织物、低饱和自然色，居住感更强。

还可以补充：最不喜欢的颜色或材质、希望呈现的预算感、是否接受深色家具。确认前不会进入正式生图。
"""


def build_markdown(package: dict[str, Any]) -> str:
    refs = package["references"]
    return f"""# 视觉生成交接包

- 方案：{package.get('scheme_id')} `{package.get('scheme_version')}`
- 状态：`{package.get('status')}`
- 阶段：`{package.get('stage')}`
- 锁定底图：`{package.get('parent_base')}`
- 结构权威：对象数据和确定性复核图
- 图像权威：`false`
- 确定性 SVG：`{refs.get('review_svg')}`
- 结构参考 PNG：`{refs.get('review_png')}`

## 可调整

- 材质、色彩、灯光、纹理、软装氛围和非结构性小饰品。

## 禁止漂移

- 户型轮廓、墙体、门窗、房间关系、厨卫阳台、固定设施。
- 已编号家具的位置、尺寸、朝向和数量。
- 不允许用生成图反写底图或方案数据。

## 生图后

结果先标记为 `generated_pending_review`，检查结构漂移、墙体连续性、门窗、厨卫完整性、家具朝向、通行和水印文字；通过后才能进入客户展示。
"""


def build_package(args: argparse.Namespace) -> dict[str, Any]:
    base = load_json(args.base_model)
    base_lock = load_json(args.base_lock)
    intent = load_json(args.scheme_intent)
    manifest = load_json(args.review_manifest)
    history = load_json(args.history)
    needs = load_json(args.needs_brief)
    style = load_json(args.style_brief)
    version = intent.get("version")
    selected = review_option(manifest, version)
    entry = history_entry(history, version)
    blockers = []

    if base_lock.get("base_lock_status") != "locked":
        blockers.append("base lock status is not locked")
    if base_lock.get("base_id") != intent.get("parent_base"):
        blockers.append("scheme parent_base does not match locked base_id")
    locked_model = base_lock.get("base_model") or {}
    if locked_model.get("sha256") != file_sha256(args.base_model):
        blockers.append("base model content differs from the locked base hash")
    canvas = base_lock.get("canvas") or {}
    if not canvas.get("width") or not canvas.get("height"):
        blockers.append("locked base has no usable canvas")

    if args.stage == "deep":
        if intent.get("layout_gate") != "ready":
            blockers.append("selected scheme layout is not ready")
        if manifest.get("status") != "ready" or not manifest.get("same_scale") or not selected:
            blockers.append("selected version is missing from a ready deterministic review package")
        if not entry or entry.get("status") != "accepted":
            blockers.append("selected version is not accepted in scheme history")
        if history.get("active_versions", {}).get(intent.get("scheme_id")) != version:
            blockers.append("selected version is not the active version in scheme history")
        preview_size = manifest.get("shared_preview_size_px") or []
        locked_size = [canvas.get("width"), canvas.get("height")]
        if preview_size and list(preview_size) != locked_size:
            blockers.append("deterministic review canvas differs from the locked base canvas")

    selected = selected or {}
    validation = load_json(Path(selected["validation"])) if selected.get("validation") else {}
    if len(validation.get("errors", []) or []) > 0:
        blockers.append("selected deterministic draft has geometry errors")
    completeness = functional_completeness(base, intent)
    if completeness["status"] != "passed":
        blockers.append("selected scheme is missing essential room functions")

    unresolved = selected.get("deferred_request_ids", []) or []
    status = "blocked" if blockers else ("ready" if style_ready(style) else "needs_style_confirmation")
    package = {
        "schema_version": "visual_generation_handoff_v1",
        "stage": args.stage,
        "status": status,
        "generation_gate": "open" if status == "ready" else "closed",
        "scheme_id": intent.get("scheme_id"),
        "scheme_version": version,
        "parent_base": intent.get("parent_base"),
        "intent_summary": intent.get("intent_summary"),
        "risk_level": intent.get("risk_level"),
        "hard_constraints": intent.get("hard_constraints", []) or [],
        "deferred_request_ids": unresolved,
        "deferred_visual_rule": "keep current confirmed geometry; do not visualize unconfirmed structural changes",
        "style_status": style.get("status", "not_provided"),
        "style_brief": style,
        "structure_lock": structure_lock(base, intent, manifest, base_lock),
        "functional_completeness": completeness,
        "visual_freedom": ["materials", "palette", "lighting", "textures", "soft_furnishing_mood", "small_nonstructural_decor"],
        "blockers": blockers,
        "references": {
            "base_model": str(args.base_model.resolve()),
            "base_lock": str(args.base_lock.resolve()),
            "confirmation_visual": (base_lock.get("confirmation_visual") or {}).get("path"),
            "scheme_intent": str(args.scheme_intent.resolve()),
            "review_manifest": str(args.review_manifest.resolve()) if args.review_manifest else None,
            "review_svg": selected.get("svg"),
            "review_png": selected.get("png"),
            "validation": selected.get("validation"),
            "needs_brief": str(args.needs_brief.resolve()),
            "history": str(args.history.resolve()) if args.history else None,
        },
        "prompt": prompt_text(intent, style, selected, base_lock, args.stage) if status == "ready" else None,
        "post_generation_status": "generated_pending_review",
        "post_generation_checks": [
            "outline_and_room_topology",
            "wall_continuity_and_thickness",
            "door_window_positions",
            "kitchen_bathroom_completeness",
            "furniture_position_orientation_count",
            "circulation",
            "labels_watermarks_ui",
            "locked_canvas_and_dimension_frame",
        ],
    }
    return package


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a gated handoff for residential visual generation.")
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--base-lock", type=Path, required=True)
    parser.add_argument("--scheme-intent", type=Path, required=True)
    parser.add_argument("--stage", choices=("quick", "deep"), default="quick")
    parser.add_argument("--review-manifest", type=Path)
    parser.add_argument("--history", type=Path)
    parser.add_argument("--needs-brief", type=Path, required=True)
    parser.add_argument("--style-brief", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    package = build_package(args)
    write_json(args.output_dir / "visual_generation_handoff.json", package)
    (args.output_dir / "visual_generation_handoff.md").write_text(build_markdown(package), encoding="utf-8")
    if package["status"] == "ready":
        (args.output_dir / "generation_prompt.txt").write_text(package["prompt"], encoding="utf-8")
    elif package["status"] == "needs_style_confirmation":
        intent = load_json(args.scheme_intent)
        needs = load_json(args.needs_brief)
        (args.output_dir / "style_confirmation.md").write_text(
            style_confirmation_markdown(intent, needs), encoding="utf-8"
        )
    print(f"handoff={args.output_dir / 'visual_generation_handoff.json'}")
    print(f"handoff_status={package['status']} generation_gate={package['generation_gate']}")
    return 2 if package["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
