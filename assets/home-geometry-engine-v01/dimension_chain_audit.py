#!/usr/bin/env python3
"""Audit transcribed dimension chains against each other and the model extents."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_TOLERANCE_MM = 80.0
LEVEL_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def issue(level: str, issue_type: str, message: str, target: str | None = None, value: Any = None) -> dict[str, Any]:
    item: dict[str, Any] = {"level": level, "type": issue_type, "message": message}
    if target:
        item["target"] = target
    if value is not None:
        item["value"] = value
    return item


def candidate_model(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("candidate_model") if isinstance(data.get("candidate_model"), dict) else data


def dimension_chains(data: dict[str, Any], model: dict[str, Any]) -> list[dict[str, Any]]:
    chains = data.get("dimension_chains")
    if isinstance(chains, list) and chains:
        return chains
    model_chains = model.get("dimension_chains")
    return model_chains if isinstance(model_chains, list) else []


def is_global_chain(chain: dict[str, Any]) -> bool:
    if chain.get("exclude_from_global_audit") is True:
        return False
    if chain.get("dimension_scope") in {"local", "ocr_error", "site_measurement_required"}:
        return False
    if chain.get("anchor_status") in {"confirmed_local_dimension", "rejected_ocr_or_reading_error", "needs_site_measurement"}:
        return False
    return True


def collect_points(model: dict[str, Any]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for wall in model.get("walls", []) or []:
        geometry = wall.get("geometry") or {}
        if geometry.get("kind") == "line":
            for key in ["start", "end"]:
                value = geometry.get(key)
                if isinstance(value, list) and len(value) >= 2:
                    points.append((float(value[0]), float(value[1])))
        elif geometry.get("kind") == "arc":
            center = geometry.get("center") or [0, 0]
            radius = float(geometry.get("radius") or 0)
            points.extend(
                [
                    (float(center[0]) - radius, float(center[1]) - radius),
                    (float(center[0]) + radius, float(center[1]) + radius),
                ]
            )
    for room in model.get("rooms", []) or []:
        for value in room.get("polygon", []) or []:
            if isinstance(value, list) and len(value) >= 2:
                points.append((float(value[0]), float(value[1])))
    return points


def model_extents(model: dict[str, Any]) -> dict[str, Any]:
    points = collect_points(model)
    if not points:
        return {"available": False}
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return {
        "available": True,
        "min_x": min(xs),
        "max_x": max(xs),
        "span_x": max(xs) - min(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "span_y": max(ys) - min(ys),
    }


def summarize_chains(chains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for index, chain in enumerate(chains):
        segments = chain.get("segments_mm") or []
        numeric_segments = [float(value) for value in segments if isinstance(value, (int, float))]
        results.append(
            {
                "id": chain.get("id", f"dimension_chain_{index + 1}"),
                "axis": chain.get("axis", "unknown"),
                "segment_count": len(segments),
                "total_mm": round(sum(numeric_segments), 3),
                "confidence": chain.get("confidence"),
                "object_ids": chain.get("object_ids") or [],
                "dimension_scope": chain.get("dimension_scope", "global_or_unknown"),
                "datum_role": chain.get("datum_role"),
                "anchor_status": chain.get("anchor_status"),
                "global_audit": is_global_chain(chain),
                "note": chain.get("note"),
            }
        )
    return results


def classify_gate(issues: list[dict[str, Any]]) -> tuple[str, str]:
    if any(item["level"] == "error" for item in issues):
        return "failed", "L1"
    if any(item["level"] == "warning" for item in issues):
        return "warning", "L2"
    return "passed", "L3"


def audit(data: dict[str, Any], tolerance_mm: float = DEFAULT_TOLERANCE_MM) -> dict[str, Any]:
    model = candidate_model(data)
    chains = dimension_chains(data, model)
    global_chains = [chain for chain in chains if is_global_chain(chain)]
    issues: list[dict[str, Any]] = []
    summaries = summarize_chains(chains)
    global_summaries = [item for item in summaries if item.get("global_audit")]
    extents = model_extents(model)

    if not chains:
        issues.append(issue("error", "missing_dimension_chains", "No dimension chains are available."))
    elif not global_chains:
        issues.append(issue("warning", "missing_global_dimension_chains", "No global dimension chains remain after confirmation filtering."))

    for item in global_summaries:
        if item["axis"] not in {"x", "y"}:
            issues.append(issue("warning", "dimension_axis_not_audited", "Only x/y chains can be compared to model extents.", item["id"]))
        if item["segment_count"] <= 0 or item["total_mm"] <= 0:
            issues.append(issue("error", "dimension_total_invalid", "Dimension chain total must be positive.", item["id"]))

    for axis in ["x", "y"]:
        axis_items = [item for item in global_summaries if item["axis"] == axis]
        if len(axis_items) < 2:
            continue
        totals = [float(item["total_mm"]) for item in axis_items]
        spread = max(totals) - min(totals)
        if spread > tolerance_mm:
            issues.append(
                issue(
                    "warning",
                    "axis_chain_total_conflict",
                    f"{axis.upper()} dimension chains differ by more than tolerance.",
                    axis,
                    {"spread_mm": round(spread, 3), "tolerance_mm": tolerance_mm},
                )
            )

    if extents.get("available"):
        for axis in ["x", "y"]:
            span = float(extents[f"span_{axis}"])
            for item in [entry for entry in global_summaries if entry["axis"] == axis]:
                residual = abs(float(item["total_mm"]) - span)
                if residual > tolerance_mm:
                    issues.append(
                        issue(
                            "warning",
                            "chain_model_span_mismatch",
                            f"{item['id']} total does not match current model {axis.upper()} span.",
                            item["id"],
                            {"chain_total_mm": item["total_mm"], "model_span_mm": round(span, 3), "residual_mm": round(residual, 3)},
                        )
                    )
    else:
        issues.append(issue("warning", "model_extents_unavailable", "Model extents could not be computed."))

    gate, level = classify_gate(issues)
    return {
        "schema_version": "dimension_chain_audit_v1",
        "dimension_gate": gate,
        "dimension_level": level,
        "can_quick_concept": LEVEL_ORDER[level] >= LEVEL_ORDER["L2"],
        "can_stable_deepening": gate == "passed" and LEVEL_ORDER[level] >= LEVEL_ORDER["L3"],
        "tolerance_mm": tolerance_mm,
        "summary": {
            "dimension_chain_count": len(chains),
            "global_dimension_chain_count": len(global_chains),
            "excluded_dimension_chain_count": len(chains) - len(global_chains),
            "error_count": sum(1 for item in issues if item["level"] == "error"),
            "warning_count": sum(1 for item in issues if item["level"] == "warning"),
            "model_extents": extents,
        },
        "chain_summaries": summaries,
        "issues": issues,
    }


def summarize(report: dict[str, Any]) -> list[str]:
    lines = [
        f"dimension_gate={report.get('dimension_gate')} dimension_level={report.get('dimension_level')}",
        f"can_quick_concept={str(report.get('can_quick_concept')).lower()} can_stable_deepening={str(report.get('can_stable_deepening')).lower()}",
        f"counts=dimensions:{report.get('summary', {}).get('dimension_chain_count')} warnings:{report.get('summary', {}).get('warning_count')} errors:{report.get('summary', {}).get('error_count')}",
    ]
    for item in report.get("issues", [])[:10]:
        target = f" ({item['target']})" if item.get("target") else ""
        lines.append(f"[{item.get('level')}] {item.get('type')}{target}: {item.get('message')}")
    omitted = max(0, len(report.get("issues", [])) - 10)
    if omitted:
        lines.append(f"... {omitted} more issues omitted")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tolerance-mm", type=float, default=DEFAULT_TOLERANCE_MM)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    report = audit(load_json(args.input), args.tolerance_mm)
    write_json(args.output, report)
    if not args.json_only:
        for line in summarize(report):
            print(line)
    return 0 if report["dimension_gate"] in {"passed", "warning"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
