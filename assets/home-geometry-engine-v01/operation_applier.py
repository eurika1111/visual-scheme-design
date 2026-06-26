#!/usr/bin/env python3
"""Apply object-level operations to a home geometry model.

This script creates a new model version instead of editing images. It helps turn
user requests such as "拆掉这堵墙" or "把方案 A 的岛台放到方案 B" into tracked
object changes.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


def require_keys(data: dict[str, Any], keys: list[str], context: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{context} missing required keys: {', '.join(missing)}")


def find_by_id(items: list[dict[str, Any]], object_id: str) -> dict[str, Any] | None:
    return next((item for item in items if item.get("id") == object_id), None)


def append_log(model: dict[str, Any], operation: dict[str, Any], status: str, message: str) -> None:
    model.setdefault("operation_log", []).append({
        "operation": operation.get("operation"),
        "status": status,
        "message": message,
        "raw": operation,
    })


def apply_demolish_wall(model: dict[str, Any], operation: dict[str, Any]) -> None:
    require_keys(operation, ["target_id"], "demolish_wall")
    wall = find_by_id(model.get("walls", []), operation["target_id"])
    if not wall:
        append_log(model, operation, "error", f"Wall not found: {operation['target_id']}")
        return
    if wall.get("alteration") == "do_not_alter":
        append_log(model, operation, "error", f"Wall is marked do_not_alter: {operation['target_id']}")
        return
    wall["status"] = "demolished"
    wall["version_note"] = operation.get("reason", "demolished by operation")
    append_log(model, operation, "applied", f"Wall demolished: {operation['target_id']}")


def apply_set_wall_status(model: dict[str, Any], operation: dict[str, Any]) -> None:
    require_keys(operation, ["target_id", "status"], "set_wall_status")
    wall = find_by_id(model.get("walls", []), operation["target_id"])
    if not wall:
        append_log(model, operation, "error", f"Wall not found: {operation['target_id']}")
        return
    wall["status"] = operation["status"]
    if "alteration" in operation:
        wall["alteration"] = operation["alteration"]
    append_log(model, operation, "applied", f"Wall status changed: {operation['target_id']}")


def apply_add_furniture(model: dict[str, Any], operation: dict[str, Any]) -> None:
    require_keys(operation, ["object"], "add_furniture")
    item = copy.deepcopy(operation["object"])
    require_keys(item, ["id", "type", "geometry"], "furniture object")
    if find_by_id(model.setdefault("furniture", []), item["id"]):
        append_log(model, operation, "error", f"Furniture already exists: {item['id']}")
        return
    item.setdefault("source", "operation")
    model["furniture"].append(item)
    append_log(model, operation, "applied", f"Furniture added: {item['id']}")


def apply_move_object(model: dict[str, Any], operation: dict[str, Any]) -> None:
    require_keys(operation, ["target_id", "center"], "move_object")
    object_id = operation["target_id"]
    for collection_name in ["furniture"]:
        item = find_by_id(model.get(collection_name, []), object_id)
        if item:
            geom = item.setdefault("geometry", {})
            if geom.get("kind") != "rect":
                append_log(model, operation, "error", f"Only rect furniture can be moved in V1: {object_id}")
                return
            geom["center"] = operation["center"]
            append_log(model, operation, "applied", f"Object moved: {object_id}")
            return
    append_log(model, operation, "error", f"Object not found: {object_id}")


def apply_remove_furniture(model: dict[str, Any], operation: dict[str, Any]) -> None:
    require_keys(operation, ["target_id"], "remove_furniture")
    object_id = operation["target_id"]
    furniture = model.setdefault("furniture", [])
    item = find_by_id(furniture, object_id)
    if not item:
        append_log(model, operation, "error", f"Furniture not found: {object_id}")
        return
    source = str(item.get("source", ""))
    removable = source == "operation" or source.startswith("copied_from:") or item.get("status") in {"new", "modified"}
    if not removable and not operation.get("allow_existing"):
        append_log(model, operation, "error", f"Furniture is not operation/copied/new: {object_id}")
        return
    model["furniture"] = [entry for entry in furniture if entry.get("id") != object_id]
    append_log(model, operation, "applied", f"Furniture removed: {object_id}")


def apply_copy_furniture(model: dict[str, Any], operation: dict[str, Any], source_models: dict[str, dict[str, Any]]) -> None:
    require_keys(operation, ["from_model", "from_object_id", "new_id"], "copy_furniture")
    source_name = operation["from_model"]
    source_model = source_models.get(source_name)
    if not source_model:
        append_log(model, operation, "error", f"Source model not loaded: {source_name}")
        return
    source_item = find_by_id(source_model.get("furniture", []), operation["from_object_id"])
    if not source_item:
        append_log(model, operation, "error", f"Source furniture not found: {operation['from_object_id']}")
        return
    new_item = copy.deepcopy(source_item)
    new_item["id"] = operation["new_id"]
    if "center" in operation:
        new_item.setdefault("geometry", {})["center"] = operation["center"]
    if "rotation" in operation:
        new_item.setdefault("geometry", {})["rotation"] = operation["rotation"]
    new_item["source"] = f"copied_from:{source_name}:{operation['from_object_id']}"
    if find_by_id(model.setdefault("furniture", []), new_item["id"]):
        append_log(model, operation, "error", f"Furniture already exists: {new_item['id']}")
        return
    model["furniture"].append(new_item)
    append_log(model, operation, "applied", f"Furniture copied: {new_item['id']}")


def apply_operations(base_model: dict[str, Any], operations_doc: dict[str, Any], source_models: dict[str, dict[str, Any]]) -> dict[str, Any]:
    model = copy.deepcopy(base_model)
    model["parent_version"] = operations_doc.get("parent_version", base_model.get("version", "unknown"))
    model["version"] = operations_doc.get("new_version", "derived_v1")
    model.setdefault("operation_log", [])

    handlers = {
        "demolish_wall": lambda op: apply_demolish_wall(model, op),
        "set_wall_status": lambda op: apply_set_wall_status(model, op),
        "add_furniture": lambda op: apply_add_furniture(model, op),
        "move_object": lambda op: apply_move_object(model, op),
        "remove_furniture": lambda op: apply_remove_furniture(model, op),
        "copy_furniture": lambda op: apply_copy_furniture(model, op, source_models),
    }

    for operation in operations_doc.get("operations", []):
        op_name = operation.get("operation")
        handler = handlers.get(op_name)
        if not handler:
            append_log(model, operation, "error", f"Unsupported operation: {op_name}")
            continue
        try:
            handler(operation)
        except ValueError as exc:
            append_log(model, operation, "error", str(exc))

    return model


def load_source_models(paths: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for value in paths:
        if "=" not in value:
            raise ValueError("Source model arguments must use name=path")
        name, path = value.split("=", 1)
        result[name] = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return result


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: operation_applier.py <base_model.json> <operations.json> <output_model.json> [source_name=source_model.json ...]")
        return 2
    base_model = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    operations_doc = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8-sig"))
    output_path = Path(sys.argv[3])
    source_models = load_source_models(sys.argv[4:])
    result = apply_operations(base_model, operations_doc, source_models)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    has_errors = any(item.get("status") == "error" for item in result.get("operation_log", []))
    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

