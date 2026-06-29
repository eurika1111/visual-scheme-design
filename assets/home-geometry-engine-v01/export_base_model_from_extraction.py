#!/usr/bin/env python3
"""Export a validated source extraction package into a base object model."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from validate_source_extraction import LEVEL_ORDER, load_json, validate_package


MODEL_KEYS = [
    "schema_version",
    "coordinate_system",
    "tolerance",
    "source_images",
    "source_facts",
    "dimension_chains",
    "extraction_notes",
    "walls",
    "openings",
    "rooms",
    "furniture",
    "fixed_fixtures",
    "zones",
    "circulation_paths",
]


def level_at_least(level: str | None, minimum: str) -> bool:
    return LEVEL_ORDER.get(level or "", -1) >= LEVEL_ORDER[minimum]


def normalized_candidate_model(package: dict[str, Any], version: str) -> dict[str, Any]:
    candidate = dict(package.get("candidate_model") or {})
    model: dict[str, Any] = {}
    for key in MODEL_KEYS:
        if key in candidate:
            model[key] = candidate[key]

    model["schema_version"] = candidate.get("schema_version", "home_geometry_v1")
    model["coordinate_system"] = candidate.get("coordinate_system") or package.get("coordinate_system")
    model["source_images"] = candidate.get("source_images") or package.get("source_images") or []
    model["source_facts"] = candidate.get("source_facts") or package.get("source_facts") or []
    model["dimension_chains"] = candidate.get("dimension_chains") or package.get("dimension_chains") or []
    model["extraction_notes"] = candidate.get("extraction_notes") or package.get("extraction_notes") or []
    model["base_inference"] = {
        "source_package_id": package.get("package_id"),
        "exported_at": date.today().isoformat(),
        "version": version,
        "unresolved_questions": package.get("unresolved_questions") or [],
    }

    for key in ["walls", "openings", "rooms", "furniture", "fixed_fixtures", "zones"]:
        for item in model.get(key, []) or []:
            item.setdefault("version", version)
    return model


def export_base_model(package: dict[str, Any], minimum_level: str, allow_warning: bool, version: str) -> tuple[dict[str, Any], dict[str, Any]]:
    report = validate_package(package)
    gate = report.get("extraction_gate")
    level = report.get("extraction_level")
    gate_ok = gate == "passed" or (allow_warning and gate == "warning")
    if not gate_ok or not level_at_least(level, minimum_level):
        raise ValueError(
            f"Extraction package blocked: gate={gate}, level={level}, required={minimum_level}, allow_warning={allow_warning}"
        )
    model = normalized_candidate_model(package, version)
    model["export_report"] = {
        "schema_version": "base_model_export_report_v1",
        "source_package_id": package.get("package_id"),
        "extraction_gate": gate,
        "extraction_level": level,
        "minimum_level": minimum_level,
        "allow_warning": allow_warning,
        "exported_at": date.today().isoformat(),
    }
    return model, report


def summarize(model: dict[str, Any], report: dict[str, Any], output: Path) -> list[str]:
    return [
        f"exported_base_model={output}",
        f"extraction_gate={report.get('extraction_gate')} extraction_level={report.get('extraction_level')}",
        "objects="
        f"walls:{len(model.get('walls', []) or [])} rooms:{len(model.get('rooms', []) or [])} "
        f"openings:{len(model.get('openings', []) or [])} furniture:{len(model.get('furniture', []) or [])}",
        f"source_trace=sources:{len(model.get('source_images', []) or [])} facts:{len(model.get('source_facts', []) or [])} dimensions:{len(model.get('dimension_chains', []) or [])}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--validation-output", type=Path, help="Optional source extraction validation report output")
    parser.add_argument("--minimum-level", choices=["L2", "L3"], default="L2")
    parser.add_argument("--allow-warning", action="store_true", help="Allow warning/L2 packages to export for quick concept work")
    parser.add_argument("--version", default="base_v1")
    args = parser.parse_args()

    package = load_json(args.package)
    try:
        model, report = export_base_model(package, args.minimum_level, args.allow_warning, args.version)
    except ValueError as exc:
        report = validate_package(package)
        if args.validation_output:
            args.validation_output.parent.mkdir(parents=True, exist_ok=True)
            args.validation_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(str(exc))
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.validation_output:
        args.validation_output.parent.mkdir(parents=True, exist_ok=True)
        args.validation_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for line in summarize(model, report, args.output):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
