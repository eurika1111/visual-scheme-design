#!/usr/bin/env python3
"""Create a conservative calibration plan from dimension-chain audit results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dimension_chain_audit import DEFAULT_TOLERANCE_MM, audit as audit_dimension_chains, load_json, write_json


def chain_residuals(audit_report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    extents = audit_report.get("summary", {}).get("model_extents", {}) or {}
    result: dict[str, list[dict[str, Any]]] = {"x": [], "y": []}
    for chain in audit_report.get("chain_summaries", []) or []:
        axis = chain.get("axis")
        if axis not in {"x", "y"}:
            continue
        span = float(extents.get(f"span_{axis}") or 0)
        total = float(chain.get("total_mm") or 0)
        residual = abs(total - span) if span > 0 else None
        result[axis].append(
            {
                "id": chain.get("id"),
                "axis": axis,
                "total_mm": total,
                "model_span_mm": span,
                "residual_mm": None if residual is None else round(residual, 3),
                "confidence": chain.get("confidence"),
                "segment_count": chain.get("segment_count"),
                "object_ids": chain.get("object_ids") or [],
                "note": chain.get("note"),
            }
        )
    return result


def confidence_value(item: dict[str, Any]) -> float:
    value = item.get("confidence")
    return float(value) if isinstance(value, (int, float)) else 0.0


def choose_primary(items: list[dict[str, Any]], tolerance_mm: float) -> dict[str, Any] | None:
    if not items:
        return None
    exactish = [item for item in items if item.get("residual_mm") is not None and float(item["residual_mm"]) <= tolerance_mm]
    candidates = exactish if exactish else items
    return sorted(candidates, key=lambda item: (float(item.get("residual_mm") or 999999), -confidence_value(item)))[0]


def classify_axis(axis: str, items: list[dict[str, Any]], tolerance_mm: float) -> dict[str, Any]:
    primary = choose_primary(items, tolerance_mm)
    chain_roles: list[dict[str, Any]] = []
    for item in items:
        residual = item.get("residual_mm")
        if primary and item.get("id") == primary.get("id") and residual is not None and float(residual) <= tolerance_mm:
            role = "primary_datum"
            action = "Use as current axis datum."
        elif residual is not None and float(residual) <= tolerance_mm:
            role = "compatible_reference"
            action = "Keep as supporting evidence."
        elif primary:
            role = "local_or_unresolved_reference"
            action = "Do not stretch the full model from this chain; add anchors before using it for L3."
        else:
            role = "unresolved_reference"
            action = "Cannot choose datum for this axis."
        chain_roles.append({**item, "role": role, "recommended_action": action})

    blockers = []
    if not primary:
        blockers.append(f"No usable {axis.upper()} dimension chain found.")
    elif any(item["role"] in {"local_or_unresolved_reference", "unresolved_reference"} for item in chain_roles):
        blockers.append(f"{axis.upper()} axis has dimension chains that do not share the selected datum.")

    return {
        "axis": axis,
        "primary_chain_id": primary.get("id") if primary else None,
        "primary_total_mm": primary.get("total_mm") if primary else None,
        "chain_roles": chain_roles,
        "blockers": blockers,
    }


def build_plan(data: dict[str, Any], tolerance_mm: float = DEFAULT_TOLERANCE_MM) -> dict[str, Any]:
    audit_report = audit_dimension_chains(data, tolerance_mm)
    grouped = chain_residuals(audit_report)
    axes = [classify_axis(axis, grouped[axis], tolerance_mm) for axis in ["x", "y"]]
    blockers = [blocker for axis in axes for blocker in axis["blockers"]]
    audit_level = audit_report.get("dimension_level", "L0")
    has_axis_datums = all(axis.get("primary_chain_id") for axis in axes)
    can_apply_to_model = audit_report.get("dimension_gate") == "passed" and not blockers
    can_quick_concept = audit_level in {"L2", "L3", "L4"} and has_axis_datums
    return {
        "schema_version": "dimension_calibration_plan_v1",
        "calibration_gate": "ready_to_apply" if can_apply_to_model else "plan_only",
        "calibration_level": "L3" if can_apply_to_model else audit_level,
        "can_quick_concept": can_quick_concept,
        "can_stable_deepening": can_apply_to_model,
        "tolerance_mm": tolerance_mm,
        "audit_gate": audit_report.get("dimension_gate"),
        "audit_level": audit_level,
        "model_extents": audit_report.get("summary", {}).get("model_extents", {}),
        "axis_plans": axes,
        "blockers": blockers,
        "recommended_next_steps": recommended_steps(blockers),
    }


def recommended_steps(blockers: list[str]) -> list[str]:
    if not blockers:
        return [
            "Apply selected datum chains to a new base model version.",
            "Run geometry validation after applying coordinates.",
            "Promote only if source extraction, dimensions, and geometry all pass L3.",
        ]
    return [
        "Keep current model at L2 for quick concept only.",
        "Add start_ref/end_ref/datum_role to each conflicting dimension chain.",
        "Confirm whether conflicting chains are full-extent dimensions or local offset dimensions.",
        "Generate a new base model version only after chain anchors are explicit.",
    ]


def summarize(plan: dict[str, Any]) -> list[str]:
    lines = [
        f"calibration_gate={plan.get('calibration_gate')} calibration_level={plan.get('calibration_level')}",
        f"can_quick_concept={str(plan.get('can_quick_concept')).lower()} can_stable_deepening={str(plan.get('can_stable_deepening')).lower()}",
    ]
    for axis in plan.get("axis_plans", []) or []:
        lines.append(f"{axis.get('axis').upper()} primary={axis.get('primary_chain_id')} total={axis.get('primary_total_mm')}")
        for blocker in axis.get("blockers", []) or []:
            lines.append(f"[blocker] {blocker}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tolerance-mm", type=float, default=DEFAULT_TOLERANCE_MM)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    plan = build_plan(load_json(args.input), args.tolerance_mm)
    write_json(args.output, plan)
    if not args.json_only:
        for line in summarize(plan):
            print(line)
    return 0 if plan["calibration_gate"] in {"ready_to_apply", "plan_only"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
