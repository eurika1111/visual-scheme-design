#!/usr/bin/env python3
"""Apply controlled proposal-furniture feedback and create a new scheme version."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

from geometry_validator import validate
from scheme_draft_renderer import merge_scheme
from scheme_placement_resolver import fixture_obstacles, issue_contains, room_index, try_place


SUPPORTED_ACTIONS = {"copy_object", "replace_object", "move_object", "rotate_object", "remove_object"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_object(intent: dict[str, Any], object_id: str) -> dict[str, Any] | None:
    return next((item for item in intent.get("proposal_objects", []) or [] if item.get("id") == object_id), None)


def next_version(version: str) -> str:
    match = re.match(r"^(.*)_v(\d+)(?:_layout_v\d+)?$", version)
    if not match:
        return f"{version}_feedback_v1"
    return f"{match.group(1)}_v{int(match.group(2)) + 1}_layout_v1"


def block_report(feedback: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "scheme_feedback_migration_report_v1",
        "feedback_id": feedback.get("feedback_id"),
        "status": "blocked",
        "blockers": reasons,
        "next_action": "confirm the missing or conflicting feedback fields",
    }


def validate_request(
    base: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    feedback: dict[str, Any],
) -> list[str]:
    blockers = []
    if feedback.get("action") not in SUPPORTED_ACTIONS:
        blockers.append(f"unsupported action: {feedback.get('action')}")
    action = feedback.get("action")
    if action in {"copy_object", "replace_object"} and feedback.get("source_scheme") not in {source.get("scheme_id"), source.get("version")}:
        blockers.append("source_scheme does not match the loaded source intent")
    if feedback.get("target_scheme") not in {target.get("scheme_id"), target.get("version")}:
        blockers.append("target_scheme does not match the loaded target intent")
    if action in {"copy_object", "replace_object"} and source.get("parent_base") != target.get("parent_base"):
        blockers.append("source and target schemes do not share the same parent base")
    base_versions = {base.get("version"), base.get("schema_version")}
    base_versions.update(item.get("version") for key in ("walls", "rooms", "openings") for item in base.get(key, []) or [])
    if target.get("parent_base") not in base_versions:
        blockers.append("target parent_base does not match the loaded base model")
    if target.get("layout_gate") != "ready":
        blockers.append("target scheme layout is not ready")
    if action in {"copy_object", "replace_object"} and not feedback.get("source_object_id"):
        blockers.append("source_object_id is required")
    if action == "replace_object" and not feedback.get("replace_target_object_id"):
        blockers.append("replace_target_object_id is required for replace_object")
    if action in {"move_object", "rotate_object", "remove_object"} and not feedback.get("target_object_id"):
        blockers.append("target_object_id is required")
    return blockers


def finalize_target_edit(
    base: dict[str, Any],
    target: dict[str, Any],
    edited: dict[str, Any],
    feedback: dict[str, Any],
    operation: dict[str, Any],
    attempts: int = 0,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    old_version = target.get("version", "scheme_target_v1")
    edited["parent_intent"] = old_version
    edited["version"] = feedback.get("new_version") or next_version(old_version)
    edited["status"] = "feedback_applied"
    edited["layout_gate"] = "ready"
    edited.setdefault("feedback_operations", []).append(operation)
    edited["generation_report"] = {
        "status": "not_rendered",
        "geometry_authority": target.get("parent_base"),
        "image_authority": False,
    }
    validation = validate(merge_scheme(base, edited))
    errors = validation.get("errors", []) or []
    report = {
        "schema_version": "scheme_feedback_migration_report_v1",
        "feedback_id": feedback.get("feedback_id"),
        "action": feedback.get("action"),
        "status": "applied" if not errors else "blocked_validation",
        "target_parent": old_version,
        "target_version": edited.get("version"),
        "target_object_id": feedback.get("target_object_id"),
        "new_object_id": operation.get("new_object_id"),
        "candidate_attempt_count": attempts,
        "validation_readiness": validation.get("readiness"),
        "validation_error_count": len(errors),
        "validation_warning_count": len(validation.get("warnings", []) or []),
        "blockers": [item.get("type", "validation_error") for item in errors],
        "next_action": "build a new scheme review package" if not errors else "revise the feedback operation",
    }
    return (edited if not errors else None), report


def edit_target_object(
    base: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    feedback: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    blockers = validate_request(base, source, target, feedback)
    object_id = feedback.get("target_object_id", "")
    target_object = find_object(target, object_id)
    if not target_object:
        blockers.append(f"target proposal object not found: {object_id}")
    elif target_object.get("type") != "furniture":
        blockers.append("only proposal furniture can be edited in this phase")
    if blockers:
        return None, block_report(feedback, blockers)

    action = feedback["action"]
    edited = copy.deepcopy(target)
    proposals = edited.get("proposal_objects", []) or []
    current = find_object(edited, object_id)
    operation = {
        "feedback_id": feedback.get("feedback_id"),
        "action": action,
        "target_parent": target.get("version"),
        "target_object_id": object_id,
        "status": "applied",
    }

    if action == "remove_object":
        edited["proposal_objects"] = [item for item in proposals if item.get("id") != object_id]
        return finalize_target_edit(base, target, edited, feedback, operation)

    if action == "rotate_object":
        rotation = feedback.get("rotation")
        if not isinstance(rotation, (int, float)):
            return None, block_report(feedback, ["rotation must be a numeric angle in degrees"])
        previous = float((current.get("geometry") or {}).get("rotation", 0))
        new_rotation = float(rotation) % 360
        current.setdefault("geometry", {})["rotation"] = new_rotation
        current["status"] = "modified"
        current["source"] = f"feedback:{feedback.get('feedback_id')}"
        check = validate(merge_scheme(base, edited))
        if issue_contains(check, object_id):
            return None, block_report(feedback, ["rotated object fails collision, door-swing, or clearance checks"])
        operation.update({"previous_rotation": previous, "rotation": new_rotation})
        return finalize_target_edit(base, target, edited, feedback, operation)

    target_spaces = feedback.get("target_spaces") or [current.get("target_space_id")]
    target_spaces = [space for space in target_spaces if space]
    rooms = room_index(base)
    missing = [space for space in target_spaces if space not in rooms]
    if not target_spaces or missing:
        return None, block_report(feedback, [f"target spaces are missing or invalid: {missing}"])
    duplicates = [
        item.get("id") for item in proposals
        if item.get("id") != object_id
        and item.get("category") == current.get("category")
        and item.get("target_space_id") in target_spaces
    ]
    if duplicates:
        return None, block_report(feedback, [f"target already has same-category objects: {duplicates}"])

    previous_geometry = copy.deepcopy(current.get("geometry"))
    edited["proposal_objects"] = [item for item in proposals if item.get("id") != object_id]
    temporary_id, attempts, resolution = try_place(
        base,
        edited,
        feedback.get("feedback_id", "CLIENT-FEEDBACK"),
        current.get("category"),
        target_spaces,
        rooms,
        edited["proposal_objects"],
        fixture_obstacles(base),
        (current.get("geometry") or {}).get("size"),
    )
    if not temporary_id or resolution == "existing_object":
        return None, block_report(feedback, ["no valid placement found for the move request"])
    temporary = find_object(edited, temporary_id)
    moved = copy.deepcopy(current)
    moved["geometry"] = copy.deepcopy(temporary["geometry"])
    moved["target_space_id"] = temporary.get("target_space_id")
    moved["status"] = "modified"
    moved["source"] = f"feedback:{feedback.get('feedback_id')}"
    edited["proposal_objects"] = [item for item in edited["proposal_objects"] if item.get("id") != temporary_id]
    edited["proposal_objects"].append(moved)
    operation.update({
        "previous_geometry": previous_geometry,
        "target_spaces": target_spaces,
        "new_geometry": moved.get("geometry"),
        "new_object_id": object_id,
    })
    return finalize_target_edit(base, target, edited, feedback, operation, attempts)


def migrate(
    base: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    feedback: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if feedback.get("action") in {"move_object", "rotate_object", "remove_object"}:
        return edit_target_object(base, source, target, feedback)
    blockers = validate_request(base, source, target, feedback)
    source_object = find_object(source, feedback.get("source_object_id", ""))
    if not source_object:
        blockers.append(f"source object not found: {feedback.get('source_object_id')}")
    elif source_object.get("type") != "furniture":
        blockers.append("only furniture migration is supported in this phase")

    target_spaces = feedback.get("target_spaces") or ([source_object.get("target_space_id")] if source_object else [])
    target_spaces = [space for space in target_spaces if space]
    rooms = room_index(base)
    missing_rooms = [space for space in target_spaces if space not in rooms]
    if not target_spaces:
        blockers.append("target_spaces is required because no reusable source room exists")
    if missing_rooms:
        blockers.append(f"target spaces do not exist: {missing_rooms}")

    category = source_object.get("category") if source_object else None
    if category and category not in {
        "sofa", "bed", "storage", "desk", "dining_table", "kitchen_island", "sofa_bed", "flex_table"
    }:
        blockers.append(f"unsupported furniture category: {category}")

    replace_id = feedback.get("replace_target_object_id")
    target_proposals = copy.deepcopy(target.get("proposal_objects", []) or [])
    if replace_id:
        if not any(item.get("id") == replace_id for item in target_proposals):
            blockers.append(f"replace target object not found: {replace_id}")
        else:
            target_proposals = [item for item in target_proposals if item.get("id") != replace_id]
    elif source_object:
        same_category = [
            item.get("id") for item in target_proposals
            if item.get("category") == category and item.get("target_space_id") in target_spaces
        ]
        if same_category:
            blockers.append(f"target already has same-category objects: {same_category}; confirm replacement explicitly")

    if blockers:
        return None, block_report(feedback, blockers)

    migrated = copy.deepcopy(target)
    migrated["proposal_objects"] = target_proposals
    original_ids = {item.get("id") for item in target_proposals}
    size = (source_object.get("geometry") or {}).get("size")
    object_id, attempts, resolution = try_place(
        base,
        migrated,
        feedback.get("feedback_id", "CLIENT-FEEDBACK"),
        category,
        target_spaces,
        rooms,
        migrated["proposal_objects"],
        fixture_obstacles(base),
        size,
    )
    if not object_id or object_id in original_ids or resolution == "existing_object":
        return None, block_report(feedback, ["no valid new placement found in the requested target spaces"])

    new_object = find_object(migrated, object_id)
    new_object["name"] = source_object.get("name", new_object.get("name"))
    new_object["source"] = f"migrated_from:{source.get('version')}:{source_object.get('id')}"
    new_object["copied_from"] = {
        "scheme_id": source.get("scheme_id"),
        "scheme_version": source.get("version"),
        "object_id": source_object.get("id"),
    }
    new_object["feedback_id"] = feedback.get("feedback_id")
    new_object["confidence"] = min(float(source_object.get("confidence", 0.6)), 0.65)

    old_version = target.get("version", "scheme_target_v1")
    migrated["parent_intent"] = old_version
    migrated["version"] = feedback.get("new_version") or next_version(old_version)
    migrated["status"] = "feedback_applied"
    migrated["layout_gate"] = "ready"
    migrated.setdefault("feedback_operations", []).append({
        "feedback_id": feedback.get("feedback_id"),
        "action": feedback.get("action"),
        "source_scheme": source.get("version"),
        "source_object_id": source_object.get("id"),
        "target_parent": old_version,
        "new_object_id": object_id,
        "target_spaces": target_spaces,
        "replace_target_object_id": replace_id,
        "status": "applied",
    })
    migrated["generation_report"] = {
        "status": "not_rendered",
        "geometry_authority": target.get("parent_base"),
        "image_authority": False,
    }

    model = merge_scheme(base, migrated)
    validation = validate(model)
    errors = validation.get("errors", []) or []
    report = {
        "schema_version": "scheme_feedback_migration_report_v1",
        "feedback_id": feedback.get("feedback_id"),
        "status": "applied" if not errors else "blocked_validation",
        "source_scheme": source.get("version"),
        "source_object_id": source_object.get("id"),
        "target_parent": old_version,
        "target_version": migrated.get("version"),
        "new_object_id": object_id,
        "target_spaces": target_spaces,
        "candidate_attempt_count": attempts,
        "validation_readiness": validation.get("readiness"),
        "validation_error_count": len(errors),
        "validation_warning_count": len(validation.get("warnings", []) or []),
        "blockers": [item.get("type", "validation_error") for item in errors],
        "next_action": "build a new scheme review package" if not errors else "revise target placement",
    }
    return (migrated if not errors else None), report


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply controlled proposal-furniture feedback to a new scheme version.")
    parser.add_argument("base_model", type=Path)
    parser.add_argument("source_intent", type=Path)
    parser.add_argument("target_intent", type=Path)
    parser.add_argument("feedback", type=Path)
    parser.add_argument("--output-intent", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    args = parser.parse_args()

    feedback = load_json(args.feedback)
    migrated, report = migrate(
        load_json(args.base_model), load_json(args.source_intent), load_json(args.target_intent), feedback
    )
    if migrated:
        write_json(args.output_intent, migrated)
    write_json(args.report_output, report)
    print(f"feedback_report={args.report_output}")
    print(f"feedback_status={report['status']} new_object={report.get('new_object_id')}")
    return 0 if report["status"] == "applied" else 2


if __name__ == "__main__":
    raise SystemExit(main())
