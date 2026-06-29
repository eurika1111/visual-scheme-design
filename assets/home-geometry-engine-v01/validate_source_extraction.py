#!/usr/bin/env python3
"""Validate a source extraction package before it becomes a base object model.

The package is the handoff between image understanding and deterministic geometry.
It keeps source evidence, extraction notes, unresolved questions, and the candidate
object model together so downstream steps do not rely on conversation memory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from geometry_validator import validate as validate_geometry
from source_quality_gate import assess_source_quality


REQUIRED_COORDINATE = {
    "origin": "lower_left",
    "x_axis": "right",
    "y_axis": "up",
    "unit": "mm",
}


LEVEL_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def issue(level: str, issue_type: str, message: str, target: str | None = None) -> dict[str, Any]:
    item = {"level": level, "type": issue_type, "message": message}
    if target:
        item["target"] = target
    return item


def id_set(items: list[dict[str, Any]]) -> set[str]:
    return {str(item.get("id")) for item in items if item.get("id")}


def model_object_ids(model: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for key in ["walls", "openings", "rooms", "furniture", "fixed_fixtures", "zones"]:
        ids.update(id_set(model.get(key, []) or []))
    return ids


def validate_dimension_chains(package: dict[str, Any], known_source_ids: set[str], known_object_ids: set[str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    chains = package.get("dimension_chains") or []
    if not chains:
        issues.append(issue("warning", "missing_dimension_chains", "No dimension chains were transcribed."))
        return issues
    for index, chain in enumerate(chains):
        target = chain.get("id", f"dimension_chains[{index}]")
        if chain.get("axis") not in {"x", "y", "diagonal", "unknown"}:
            issues.append(issue("error", "dimension_axis_invalid", "Dimension chain axis must be x, y, diagonal, or unknown.", target))
        segments = chain.get("segments_mm") or []
        if not segments or any(not isinstance(value, (int, float)) or value <= 0 for value in segments):
            issues.append(issue("error", "dimension_segments_invalid", "Dimension chain needs positive segments_mm values.", target))
        if chain.get("source") and str(chain.get("source")) not in known_source_ids:
            issues.append(issue("error", "dimension_source_missing", "Dimension chain source does not exist in source_images.", target))
        for object_id in chain.get("object_ids") or []:
            if str(object_id) not in known_object_ids:
                issues.append(issue("error", "dimension_object_missing", "Dimension chain references a missing object_id.", str(object_id)))
        confidence = chain.get("confidence")
        if not isinstance(confidence, (int, float)):
            issues.append(issue("warning", "dimension_confidence_missing", "Dimension chain should include confidence.", target))
    return issues


def validate_source_facts(package: dict[str, Any], known_source_ids: set[str], known_object_ids: set[str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    facts = package.get("source_facts") or []
    if not facts:
        issues.append(issue("warning", "missing_source_facts", "No source facts were recorded."))
        return issues
    for index, fact in enumerate(facts):
        target = fact.get("id", f"source_facts[{index}]")
        if fact.get("source") and str(fact.get("source")) not in known_source_ids:
            issues.append(issue("error", "source_fact_source_missing", "Source fact source does not exist in source_images.", target))
        refs = fact.get("object_ids") or []
        if not refs:
            issues.append(issue("warning", "source_fact_without_objects", "Source fact should reference affected object_ids.", target))
        for object_id in refs:
            if str(object_id) not in known_object_ids:
                issues.append(issue("error", "source_fact_object_missing", "Source fact references a missing object_id.", str(object_id)))
        confidence = fact.get("confidence")
        if not isinstance(confidence, (int, float)):
            issues.append(issue("warning", "source_fact_confidence_missing", "Source fact should include confidence.", target))
    return issues


def validate_package(package: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    if package.get("schema_version") != "source_extraction_package_v1":
        issues.append(issue("error", "schema_version_invalid", "schema_version must be source_extraction_package_v1."))

    source_images = package.get("source_images") or []
    if not source_images:
        issues.append(issue("error", "missing_source_images", "At least one source image record is required."))
    known_source_ids = id_set(source_images)

    coordinate = package.get("coordinate_system") or {}
    for key, expected in REQUIRED_COORDINATE.items():
        if coordinate.get(key) != expected:
            issues.append(issue("error", "coordinate_contract_invalid", f"coordinate_system.{key} must be {expected}.", key))

    candidate_model = package.get("candidate_model") or {}
    if not isinstance(candidate_model, dict) or not candidate_model:
        issues.append(issue("error", "missing_candidate_model", "candidate_model is required."))
        candidate_model = {}

    model = dict(candidate_model)
    model.setdefault("coordinate_system", coordinate)
    model.setdefault("source_images", source_images)
    model.setdefault("source_facts", package.get("source_facts") or [])
    model.setdefault("dimension_chains", package.get("dimension_chains") or [])
    model.setdefault("extraction_notes", package.get("extraction_notes") or [])

    known_object_ids = model_object_ids(model)
    issues.extend(validate_dimension_chains(package, known_source_ids, known_object_ids))
    issues.extend(validate_source_facts(package, known_source_ids, known_object_ids))

    unresolved = package.get("unresolved_questions") or []
    high_unresolved = [item for item in unresolved if item.get("severity") == "high"]
    if high_unresolved:
        issues.append(issue("warning", "high_unresolved_questions", "High-severity unresolved questions remain.", str(len(high_unresolved))))

    geometry_report = validate_geometry(model) if model else {"readiness": "L0", "summary": {"error_count": 1, "warning_count": 0}}
    source_quality_report = assess_source_quality(model, geometry_report) if model else {"source_gate": "failed", "source_level": "L0"}

    error_count = sum(1 for item in issues if item["level"] == "error")
    warning_count = sum(1 for item in issues if item["level"] == "warning")
    source_level = source_quality_report.get("source_level", "L0")
    if error_count:
        extraction_gate = "failed"
        extraction_level = "L0"
    elif LEVEL_ORDER.get(source_level, 0) >= LEVEL_ORDER["L3"] and not high_unresolved:
        extraction_gate = "passed"
        extraction_level = source_level
    elif LEVEL_ORDER.get(source_level, 0) >= LEVEL_ORDER["L2"]:
        extraction_gate = "warning"
        extraction_level = "L2"
    else:
        extraction_gate = "failed"
        extraction_level = source_level

    return {
        "schema_version": "source_extraction_validation_v1",
        "extraction_gate": extraction_gate,
        "extraction_level": extraction_level,
        "can_quick_concept": LEVEL_ORDER.get(extraction_level, 0) >= LEVEL_ORDER["L2"],
        "can_stable_deepening": extraction_gate == "passed" and LEVEL_ORDER.get(extraction_level, 0) >= LEVEL_ORDER["L3"],
        "summary": {
            "package_error_count": error_count,
            "package_warning_count": warning_count,
            "source_image_count": len(source_images),
            "dimension_chain_count": len(package.get("dimension_chains") or []),
            "source_fact_count": len(package.get("source_facts") or []),
            "unresolved_question_count": len(unresolved),
            "geometry_readiness": geometry_report.get("readiness"),
            "source_gate": source_quality_report.get("source_gate"),
            "source_level": source_quality_report.get("source_level"),
        },
        "issues": issues,
        "geometry_summary": geometry_report.get("summary", {}),
        "source_quality_summary": source_quality_report.get("summary", {}),
    }


def summarize(report: dict[str, Any]) -> list[str]:
    summary = report.get("summary", {})
    lines = [
        f"extraction_gate={report.get('extraction_gate')} extraction_level={report.get('extraction_level')}",
        f"can_quick_concept={str(report.get('can_quick_concept')).lower()} can_stable_deepening={str(report.get('can_stable_deepening')).lower()}",
        "counts="
        f"sources:{summary.get('source_image_count')} dimensions:{summary.get('dimension_chain_count')} "
        f"facts:{summary.get('source_fact_count')} unresolved:{summary.get('unresolved_question_count')}",
        f"geometry={summary.get('geometry_readiness')} source_quality={summary.get('source_gate')}/{summary.get('source_level')}",
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
    parser.add_argument("package", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    package = load_json(args.package)
    report = validate_package(package)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.json_only:
        for line in summarize(report):
            print(line)
    return 0 if report["extraction_gate"] in {"passed", "warning"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
