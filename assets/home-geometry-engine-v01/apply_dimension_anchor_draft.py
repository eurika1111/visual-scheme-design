#!/usr/bin/env python3
"""Apply reviewed dimension anchor drafts to a new source extraction package."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from dimension_chain_anchor_drafter import build_anchor_draft
from dimension_chain_audit import load_json, write_json


def chain_index(chains: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(chain.get("id")): chain for chain in chains if chain.get("id")}


def apply_to_chain(chain: dict[str, Any], draft: dict[str, Any]) -> str:
    clean = draft.get("confidence") == "high" and not draft.get("issues")
    review = {
        "datum_role": draft.get("datum_role"),
        "confidence": draft.get("confidence"),
        "anchor_span_mm": draft.get("anchor_span_mm"),
        "residual_mm": draft.get("residual_mm"),
        "status": "applied" if clean else "needs_confirmation",
        "source": "dimension_chain_anchor_draft_v1",
    }
    chain["anchor_review"] = review
    if clean:
        chain["start_ref"] = draft.get("start_ref")
        chain["end_ref"] = draft.get("end_ref")
        chain["datum_role"] = draft.get("datum_role")
        chain["anchor_status"] = "confirmed_by_draft"
        return "applied"
    chain["datum_role"] = draft.get("datum_role")
    chain["anchor_status"] = "needs_confirmation"
    return "needs_confirmation"


def append_note(package: dict[str, Any], message: str) -> None:
    notes = package.setdefault("extraction_notes", [])
    notes.append(
        {
            "id": f"NOTE-DIM-ANCHOR-{len(notes) + 1:02d}",
            "type": "dimension_anchor_draft_apply",
            "message": message,
        }
    )


def append_unresolved(package: dict[str, Any], draft: dict[str, Any]) -> None:
    unresolved = package.setdefault("unresolved_questions", [])
    unresolved.append(
        {
            "id": f"UQ-DIM-ANCHOR-{draft.get('id')}",
            "severity": "medium",
            "question": f"Confirm dimension chain anchors for {draft.get('id')} before L3 deepening.",
            "object_ids": draft.get("referenced_object_ids") or [],
            "blocks": ["stable_deepening"],
        }
    )


def apply_anchor_draft(package: dict[str, Any], anchor_report: dict[str, Any] | None, version: str) -> tuple[dict[str, Any], dict[str, Any]]:
    result = copy.deepcopy(package)
    result["package_id"] = version

    if anchor_report is None:
        anchor_report = build_anchor_draft(result)

    top_chains = result.get("dimension_chains") or []
    model = result.get("candidate_model") or {}
    model_chains = model.get("dimension_chains") or []
    top_by_id = chain_index(top_chains)
    model_by_id = chain_index(model_chains)

    applied: list[str] = []
    needs_confirmation: list[str] = []
    missing: list[str] = []

    for draft in anchor_report.get("anchor_drafts", []) or []:
        chain_id = str(draft.get("id"))
        status = None
        for target in [top_by_id.get(chain_id), model_by_id.get(chain_id)]:
            if target is None:
                continue
            status = apply_to_chain(target, draft)
        if status == "applied":
            applied.append(chain_id)
        elif status == "needs_confirmation":
            needs_confirmation.append(chain_id)
            append_unresolved(result, draft)
        else:
            missing.append(chain_id)

    append_note(
        result,
        "Applied high-confidence dimension anchors as draft-confirmed fields; conflicting chains remain marked for confirmation.",
    )
    if isinstance(model, dict):
        model.setdefault("extraction_notes", [])
        model["extraction_notes"].append(
            {
                "id": f"NOTE-DIM-ANCHOR-MODEL-{len(model['extraction_notes']) + 1:02d}",
                "type": "dimension_anchor_draft_apply",
                "message": "Dimension chain anchor fields synchronized from package-level draft application.",
            }
        )

    report = {
        "schema_version": "dimension_anchor_apply_report_v1",
        "output_package_id": version,
        "anchor_gate": anchor_report.get("anchor_gate"),
        "anchor_level": anchor_report.get("anchor_level"),
        "applied_chain_ids": applied,
        "needs_confirmation_chain_ids": needs_confirmation,
        "missing_chain_ids": missing,
        "can_quick_concept": anchor_report.get("can_quick_concept"),
        "can_stable_deepening": False if needs_confirmation or missing else bool(anchor_report.get("can_stable_deepening")),
    }
    return result, report


def summarize(report: dict[str, Any]) -> list[str]:
    return [
        f"output_package_id={report.get('output_package_id')}",
        f"applied={len(report.get('applied_chain_ids') or [])} needs_confirmation={len(report.get('needs_confirmation_chain_ids') or [])} missing={len(report.get('missing_chain_ids') or [])}",
        f"can_quick_concept={str(report.get('can_quick_concept')).lower()} can_stable_deepening={str(report.get('can_stable_deepening')).lower()}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("anchor_report", type=Path)
    parser.add_argument("output_package", type=Path)
    parser.add_argument("output_report", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    package = load_json(args.package)
    anchor_report = load_json(args.anchor_report)
    result, report = apply_anchor_draft(package, anchor_report, args.version)
    write_json(args.output_package, result)
    write_json(args.output_report, report)
    if not args.json_only:
        for line in summarize(report):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
