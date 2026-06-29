#!/usr/bin/env python3
"""Source object quality gate for residential plan objectization.

This script does not extract objects from raster images. It checks whether an
already extracted object model is reliable enough to become the base for quick
concept or stable deepening work.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from geometry_validator import validate


LEVEL_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def clamp_level(level: str, ceiling: str) -> str:
    if LEVEL_ORDER.get(level, 0) > LEVEL_ORDER.get(ceiling, 0):
        return ceiling
    return level


def confidence_values(items: list[dict[str, Any]]) -> list[float]:
    values = []
    for item in items:
        value = item.get("confidence")
        if isinstance(value, (int, float)):
            values.append(float(value))
    return values


def avg(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def object_ids(items: list[dict[str, Any]]) -> list[str]:
    return [str(item.get("id", "<missing>")) for item in items]


def count_missing_confidence(groups: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    findings = []
    for group_name, items in groups.items():
        missing = [str(item.get("id", "<missing>")) for item in items if "confidence" not in item]
        if missing:
            findings.append({
                "type": "missing_confidence",
                "severity": "low",
                "group": group_name,
                "object_ids": missing[:12],
                "omitted": max(0, len(missing) - 12),
            })
    return findings


def source_trace_count(model: dict[str, Any]) -> int:
    keys = ["source_facts", "dimensions", "dimension_chains", "source_images", "extraction_notes"]
    return sum(1 for key in keys if model.get(key))


def source_reference_findings(model: dict[str, Any], known_ids: set[str]) -> list[dict[str, Any]]:
    findings = []
    for group_name in ["source_facts", "dimensions", "dimension_chains"]:
        for item in model.get(group_name, []) or []:
            refs = item.get("object_ids") or []
            if isinstance(refs, str):
                refs = [refs]
            missing = [str(ref) for ref in refs if str(ref) not in known_ids]
            if missing:
                findings.append({
                    "type": "source_reference_missing_object",
                    "severity": "high",
                    "group": group_name,
                    "source_id": item.get("id", "<missing>"),
                    "object_ids": missing,
                })
    return findings


def assess_source_quality(model: dict[str, Any], validation: dict[str, Any] | None = None) -> dict[str, Any]:
    validation_report = validation or validate(model)
    findings: list[dict[str, Any]] = []
    groups = {
        "walls": model.get("walls", []),
        "openings": model.get("openings", []),
        "rooms": model.get("rooms", []),
        "furniture": model.get("furniture", []),
    }
    walls = groups["walls"]
    active_walls = [wall for wall in walls if wall.get("status") != "demolished"]
    rooms = groups["rooms"]
    openings = groups["openings"]

    coordinate = model.get("coordinate_system", {})
    if coordinate.get("origin") != "lower_left" or coordinate.get("unit") != "mm":
        findings.append({
            "type": "coordinate_contract_weak",
            "severity": "high",
            "message": "coordinate_system should use lower_left origin and mm unit",
        })

    if len(active_walls) < 4:
        findings.append({
            "type": "too_few_active_walls",
            "severity": "high",
            "count": len(active_walls),
        })
    if not rooms:
        findings.append({"type": "missing_rooms", "severity": "high"})
    if not openings:
        findings.append({"type": "missing_openings", "severity": "medium"})

    all_ids = []
    for items in groups.values():
        all_ids.extend(object_ids(items))
    known_ids = set(all_ids)
    duplicates = sorted([item_id for item_id, count in Counter(all_ids).items() if count > 1])
    if duplicates:
        findings.append({"type": "duplicate_object_id", "severity": "high", "object_ids": duplicates})
    findings.extend(source_reference_findings(model, known_ids))

    findings.extend(count_missing_confidence({"walls": walls, "rooms": rooms}))

    confidences = confidence_values(walls + rooms)
    average_confidence = avg(confidences)
    low_confidence = [
        str(item.get("id", "<missing>"))
        for item in walls + rooms
        if isinstance(item.get("confidence"), (int, float)) and float(item["confidence"]) < 0.7
    ]
    if average_confidence is None:
        findings.append({"type": "source_confidence_absent", "severity": "medium"})
    elif average_confidence < 0.72:
        findings.append({
            "type": "source_confidence_low",
            "severity": "medium",
            "average_confidence": round(average_confidence, 3),
        })
    if low_confidence:
        findings.append({
            "type": "low_confidence_objects",
            "severity": "medium",
            "object_ids": low_confidence[:12],
            "omitted": max(0, len(low_confidence) - 12),
        })

    if source_trace_count(model) == 0:
        findings.append({
            "type": "source_traceability_weak",
            "severity": "medium",
            "message": "No source_facts, dimensions, dimension_chains, source_images, or extraction_notes found",
        })

    validation_errors = validation_report.get("summary", {}).get("error_count", len(validation_report.get("errors", [])))
    validation_warnings = validation_report.get("summary", {}).get("warning_count", len(validation_report.get("warnings", [])))
    validation_level = validation_report.get("readiness", "L0")

    high_count = sum(1 for item in findings if item.get("severity") == "high")
    medium_count = sum(1 for item in findings if item.get("severity") == "medium")

    source_level = validation_level
    if validation_errors:
        source_level = clamp_level(source_level, "L1")
    if high_count:
        source_level = clamp_level(source_level, "L1")
    elif medium_count:
        source_level = clamp_level(source_level, "L2")
    if validation_warnings and LEVEL_ORDER.get(source_level, 0) > LEVEL_ORDER["L2"]:
        source_level = "L2"

    if LEVEL_ORDER.get(source_level, 0) >= LEVEL_ORDER["L3"]:
        gate = "passed"
    elif LEVEL_ORDER.get(source_level, 0) >= LEVEL_ORDER["L2"]:
        gate = "warning"
    else:
        gate = "failed"

    return {
        "schema_version": "source_quality_gate_v1",
        "source_gate": gate,
        "source_level": source_level,
        "validation_readiness": validation_level,
        "can_quick_concept": LEVEL_ORDER.get(source_level, 0) >= LEVEL_ORDER["L2"],
        "can_stable_deepening": LEVEL_ORDER.get(source_level, 0) >= LEVEL_ORDER["L3"],
        "summary": {
            "active_wall_count": len(active_walls),
            "room_count": len(rooms),
            "opening_count": len(openings),
            "average_wall_room_confidence": None if average_confidence is None else round(average_confidence, 3),
            "validation_error_count": validation_errors,
            "validation_warning_count": validation_warnings,
            "source_finding_count": len(findings),
            "source_trace_count": source_trace_count(model),
        },
        "findings": findings,
    }


def summarize(report: dict[str, Any]) -> list[str]:
    summary = report.get("summary", {})
    lines = [
        f"source_gate={report.get('source_gate')} source_level={report.get('source_level')} validation={report.get('validation_readiness')}",
        f"can_quick_concept={str(report.get('can_quick_concept')).lower()} can_stable_deepening={str(report.get('can_stable_deepening')).lower()}",
        "objects="
        f"walls:{summary.get('active_wall_count')} rooms:{summary.get('room_count')} openings:{summary.get('opening_count')} "
        f"avg_conf:{summary.get('average_wall_room_confidence')}",
    ]
    findings = report.get("findings", [])
    if findings:
        counts = Counter(item.get("type", "unknown") for item in findings)
        lines.append("finding_counts=" + ", ".join(f"{name}:{count}" for name, count in sorted(counts.items())))
        for item in findings[:8]:
            target = item.get("object_ids") or item.get("group") or item.get("message")
            if target is None and "count" in item:
                target = f"count={item['count']}"
            if target is None:
                target = ""
            lines.append(f"[{item.get('severity', 'info')}] {item.get('type')}: {target}")
        if len(findings) > 8:
            lines.append(f"... {len(findings) - 8} more findings omitted")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--validation", type=Path, help="Optional existing validation report")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    model = load_json(args.model)
    validation = load_json(args.validation) if args.validation else None
    report = assess_source_quality(model, validation)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.json_only:
        for line in summarize(report):
            print(line)
    return 0 if report["source_gate"] in {"passed", "warning"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
