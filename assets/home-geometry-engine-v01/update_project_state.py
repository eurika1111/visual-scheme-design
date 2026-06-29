#!/usr/bin/env python3
"""Update compact project_state.json from geometry validation outputs."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validation_status(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    if int(summary.get("error_count", 0)) > 0:
        return "failed"
    if int(summary.get("warning_count", 0)) > 0:
        return "warning"
    return "passed"


def option_entry(
    label: str,
    version: str,
    report: dict[str, Any],
    model_path: Path,
    validation_path: Path,
    parent: str | None = None,
) -> dict[str, Any]:
    status = validation_status(report)
    return {
        "id": label,
        "version": version,
        "status": "保留" if status == "passed" else "待修改",
        "parent": parent,
        "validation_status": status,
        "level": report.get("readiness"),
        "files": {
            "model": str(model_path),
            "validation_report": str(validation_path),
        },
        "notes": "geometry validation passed" if status == "passed" else "needs review before use",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--base-model", required=True, type=Path)
    parser.add_argument("--base-validation", required=True, type=Path)
    parser.add_argument("--base-version", default="base_v1")
    parser.add_argument("--scheme-a-model", required=True, type=Path)
    parser.add_argument("--scheme-a-validation", required=True, type=Path)
    parser.add_argument("--scheme-a-version", default="scheme_A_v1")
    parser.add_argument("--problem-validation", required=True, type=Path)
    parser.add_argument("--base-source-quality", type=Path, help="Optional source quality gate report for the base model")
    parser.add_argument("--base-source-extraction", type=Path, help="Optional source extraction validation report for the base model")
    args = parser.parse_args()

    base_report = load_json(args.base_validation)
    scheme_a_report = load_json(args.scheme_a_validation)
    problem_report = load_json(args.problem_validation)
    source_quality_report = load_json(args.base_source_quality) if args.base_source_quality else None
    source_extraction_report = load_json(args.base_source_extraction) if args.base_source_extraction else None

    base_status = validation_status(base_report)
    scheme_a_status = validation_status(scheme_a_report)
    source_gate = source_quality_report.get("source_gate") if source_quality_report else None
    source_level = source_quality_report.get("source_level") if source_quality_report else None
    source_quality_status = source_gate or "unknown"
    extraction_gate = source_extraction_report.get("extraction_gate") if source_extraction_report else None
    extraction_level = source_extraction_report.get("extraction_level") if source_extraction_report else None
    extraction_status = extraction_gate or "unknown"

    state = {
        "schema_version": "space_scheme_state_v1",
        "updated_at": date.today().isoformat(),
        "domain": "residential",
        "mode": "execute",
        "phase": "production",
        "level": base_report.get("readiness"),
        "base_level": base_report.get("readiness"),
        "base_validation_status": base_status,
        "base_source_gate": source_gate,
        "base_source_level": source_level,
        "base_source_quality_status": source_quality_status,
        "base_source_extraction_gate": extraction_gate,
        "base_source_extraction_level": extraction_level,
        "base_source_extraction_status": extraction_status,
        "active_base": args.base_version,
        "active_option": args.scheme_a_version,
        "active_option_level": scheme_a_report.get("readiness"),
        "active_option_validation_status": scheme_a_status,
        "validation_status": "passed" if base_status == "passed" and scheme_a_status == "passed" and source_quality_status in {"passed", "unknown"} and extraction_status in {"passed", "unknown"} else "warning",
        "last_action": "run_geometry_demo",
        "option_registry": [
            option_entry("底图", args.base_version, base_report, args.base_model, args.base_validation),
            option_entry("方案 A", args.scheme_a_version, scheme_a_report, args.scheme_a_model, args.scheme_a_validation, parent=args.base_version),
        ],
        "files": {
            "base_model": str(args.base_model),
            "base_validation_report": str(args.base_validation),
            "active_scheme_model": str(args.scheme_a_model),
            "active_scheme_validation_report": str(args.scheme_a_validation),
            "problem_sample_validation_report": str(args.problem_validation),
            "base_source_quality_report": str(args.base_source_quality) if args.base_source_quality else None,
            "base_source_extraction_report": str(args.base_source_extraction) if args.base_source_extraction else None,
        },
        "checks": {
            "base": {
                "readiness": base_report.get("readiness"),
                "status": base_status,
                "summary": base_report.get("summary", {}),
            },
            "base_source_quality": source_quality_report or {},
            "base_source_extraction": source_extraction_report or {},
            "scheme_A": {
                "readiness": scheme_a_report.get("readiness"),
                "status": scheme_a_status,
                "summary": scheme_a_report.get("summary", {}),
            },
            "problem_sample": {
                "readiness": problem_report.get("readiness"),
                "status": validation_status(problem_report),
                "summary": problem_report.get("summary", {}),
            },
        },
        "blockers": [],
        "evolution_flags": [],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"project_state={args.output}")
    print(f"state_status={state['validation_status']} level={state['level']} active_option={state['active_option']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
