#!/usr/bin/env python3
"""Create a deterministic scheme draft from base model plus scheme intent."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ENGINE_DIR = Path(__file__).resolve().parent


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_proposal_object(item: dict[str, Any], scheme_version: str) -> dict[str, Any] | None:
    object_type = item.get("type")
    if object_type not in {"furniture", "wall"}:
        return None
    result = copy.deepcopy(item)
    result.setdefault("source", f"scheme_intent:{scheme_version}")
    result.setdefault("status", "new")
    result.setdefault("version", scheme_version)
    result.setdefault("confidence", item.get("confidence", 0.6))
    return result


def merge_scheme(base: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
    model = copy.deepcopy(base)
    scheme_version = intent.get("version", "scheme_draft_v1")
    model["parent_base"] = intent.get("parent_base") or base.get("version") or base.get("schema_version")
    model["version"] = scheme_version
    model["scheme_id"] = intent.get("scheme_id")
    model["scheme_name"] = intent.get("name")
    model.setdefault("draft_notes", [])
    model["draft_notes"].append({
        "type": "deterministic_scheme_draft",
        "message": "Rendered from base_object_model plus scheme_intent; generated images are not geometry authority.",
    })

    for item in intent.get("proposal_objects", []) or []:
        normalized = normalize_proposal_object(item, scheme_version)
        if not normalized:
            continue
        if normalized["type"] == "furniture":
            model.setdefault("furniture", []).append(normalized)
        elif normalized["type"] == "wall":
            model.setdefault("walls", []).append(normalized)

    model.setdefault("scheme_operations", intent.get("operations", []) or [])
    return model


def run_child(args: list[str], allowed: set[int] | None = None) -> None:
    allowed = allowed or {0}
    completed = subprocess.run([sys.executable, *args], cwd=ENGINE_DIR)
    if completed.returncode not in allowed:
        raise SystemExit(completed.returncode)


def build_report(intent: dict[str, Any], model_path: Path, validation_path: Path, svg_path: Path) -> dict[str, Any]:
    return {
        "schema_version": "deterministic_scheme_draft_report_v1",
        "scheme_id": intent.get("scheme_id"),
        "scheme_version": intent.get("version"),
        "status": "draft_rendered_pending_review",
        "draft_model": str(model_path),
        "draft_svg": str(svg_path),
        "validation_report": str(validation_path),
        "image_is_geometry_authority": False,
        "next_action": "review deterministic draft before visual generation",
    }


def unresolved_placements(intent: dict[str, Any]) -> list[dict[str, Any]]:
    resolved = {"resolved", "not_required", "accepted_without_object"}
    return [item for item in intent.get("placement_requests", []) or [] if item.get("status") not in resolved]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_model", type=Path)
    parser.add_argument("scheme_intent", type=Path)
    parser.add_argument("--output-model", type=Path, required=True)
    parser.add_argument("--validation-output", type=Path, required=True)
    parser.add_argument("--svg-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    args = parser.parse_args()

    base = load_json(args.base_model)
    intent = load_json(args.scheme_intent)
    pending = unresolved_placements(intent)
    layout_gate = intent.get("layout_gate")
    if pending or layout_gate not in {None, "ready"}:
        write_json(args.report_output, {
            "schema_version": "deterministic_scheme_draft_report_v1",
            "scheme_id": intent.get("scheme_id"),
            "scheme_version": intent.get("version"),
            "status": "blocked_unresolved_placement",
            "layout_gate": layout_gate,
            "pending_request_ids": [item.get("id") for item in pending],
            "next_action": "resolve placement requests into controlled proposal_objects before rendering",
        })
        print(f"draft_blocked=pending_placements:{len(pending)}")
        print(f"report={args.report_output}")
        return 2
    draft = merge_scheme(base, intent)

    write_json(args.output_model, draft)
    run_child(["geometry_validator.py", str(args.output_model), str(args.validation_output)], allowed={0, 1})
    run_child(["simple_renderer.py", str(args.output_model), str(args.svg_output), str(args.validation_output)])
    write_json(args.report_output, build_report(intent, args.output_model, args.validation_output, args.svg_output))

    print(f"draft_model={args.output_model}")
    print(f"draft_svg={args.svg_output}")
    print(f"validation={args.validation_output}")
    print(f"report={args.report_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
