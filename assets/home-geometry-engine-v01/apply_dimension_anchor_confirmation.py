#!/usr/bin/env python3
"""Apply human dimension-anchor confirmation decisions to a new extraction package."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
from typing import Any

from dimension_chain_audit import DEFAULT_TOLERANCE_MM, load_json, write_json

GLOBAL_ANSWERS = {"accept", "full_extent_dimension"}
EXCLUDED_ANSWERS = {"local_dimension", "ocr_or_reading_error", "needs_site_measurement"}
VALID_ANSWERS = GLOBAL_ANSWERS | EXCLUDED_ANSWERS | {"reject"}


def chain_index(chains: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(chain.get("id")): chain for chain in chains if chain.get("id")}


def checklist_index(checklist: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("dimension_chain_id")): item for item in checklist.get("items", []) or [] if item.get("dimension_chain_id")}


def decision_index(response: dict[str, Any]) -> dict[str, dict[str, Any]]:
    decisions = response.get("decisions") or response.get("items") or []
    return {str(item.get("dimension_chain_id")): item for item in decisions if item.get("dimension_chain_id")}


def dimension_total(item: dict[str, Any]) -> float | None:
    value = item.get("dimension_total_mm")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def refs_from_decision_or_item(decision: dict[str, Any], item: dict[str, Any]) -> tuple[Any, Any]:
    start_ref = decision.get("start_ref") or decision.get("confirmed_start_ref") or item.get("start_ref")
    end_ref = decision.get("end_ref") or decision.get("confirmed_end_ref") or item.get("end_ref")
    return start_ref, end_ref


def refs_are_usable(start_ref: Any, end_ref: Any) -> bool:
    return isinstance(start_ref, dict) and isinstance(end_ref, dict) and start_ref.get("axis") and end_ref.get("axis")


def residual_within_tolerance(item: dict[str, Any], tolerance_mm: float) -> bool:
    residual = item.get("residual_mm")
    return isinstance(residual, (int, float)) and abs(float(residual)) <= tolerance_mm


def remove_unresolved_for_chain(package: dict[str, Any], chain_id: str) -> None:
    unresolved = package.get("unresolved_questions") or []
    package["unresolved_questions"] = [
        item for item in unresolved if chain_id not in str(item.get("id", "")) and chain_id not in [str(value) for value in item.get("object_ids", []) or []]
    ]


def append_unresolved(package: dict[str, Any], chain_id: str, answer: str, object_ids: list[Any], severity: str = "medium") -> None:
    unresolved = package.setdefault("unresolved_questions", [])
    unresolved.append(
        {
            "id": f"UQ-DIM-CONFIRM-{chain_id}",
            "severity": severity,
            "question": f"Dimension chain {chain_id} still needs confirmation result: {answer}.",
            "object_ids": object_ids,
            "blocks": ["stable_deepening"],
        }
    )


def apply_fields(chain: dict[str, Any], fields: dict[str, Any]) -> None:
    for key, value in fields.items():
        if value is None:
            continue
        chain[key] = copy.deepcopy(value)


def apply_decision_to_chain(
    chain: dict[str, Any],
    item: dict[str, Any],
    decision: dict[str, Any],
    tolerance_mm: float,
) -> tuple[str, dict[str, Any]]:
    chain_id = str(item.get("dimension_chain_id"))
    answer = str(decision.get("answer") or decision.get("decision") or "").strip()
    note = decision.get("note")
    if answer not in VALID_ANSWERS:
        return "blocked", {"reason": "invalid_answer", "answer": answer}

    start_ref, end_ref = refs_from_decision_or_item(decision, item)
    object_ids = item.get("referenced_object_ids") or []
    review = {
        "source": "dimension_anchor_confirmation_v1",
        "answer": answer,
        "confirmed_by": decision.get("confirmed_by", "human_review"),
        "note": note,
        "checklist_item_status": item.get("status"),
        "residual_mm": item.get("residual_mm"),
    }

    if answer == "accept":
        if item.get("status") != "accepted_candidate" or not refs_are_usable(start_ref, end_ref):
            return "blocked", {"reason": "accept_requires_clean_candidate", "answer": answer}
        apply_fields(
            chain,
            {
                "start_ref": start_ref,
                "end_ref": end_ref,
                "datum_role": item.get("datum_role") or "primary_datum",
                "dimension_scope": "global",
                "anchor_status": "confirmed_by_human",
                "exclude_from_global_audit": False,
                "anchor_review": {**review, "status": "applied"},
            },
        )
        return "applied", {"answer": answer, "object_ids": object_ids}

    if answer == "full_extent_dimension":
        usable_refs = refs_are_usable(start_ref, end_ref)
        if not usable_refs or (item.get("status") != "accepted_candidate" and not residual_within_tolerance(item, tolerance_mm) and not decision.get("force_apply")):
            return "blocked", {"reason": "full_extent_requires_confirmed_refs_or_matching_span", "answer": answer}
        apply_fields(
            chain,
            {
                "start_ref": start_ref,
                "end_ref": end_ref,
                "datum_role": decision.get("datum_role") or item.get("datum_role") or "compatible_reference",
                "dimension_scope": "global",
                "anchor_status": "confirmed_by_human",
                "exclude_from_global_audit": False,
                "anchor_review": {**review, "status": "applied"},
            },
        )
        return "applied", {"answer": answer, "object_ids": object_ids}

    if answer == "local_dimension":
        apply_fields(
            chain,
            {
                "datum_role": "local_reference",
                "dimension_scope": "local",
                "anchor_status": "confirmed_local_dimension",
                "exclude_from_global_audit": True,
                "anchor_review": {**review, "status": "excluded_from_global_audit"},
            },
        )
        return "excluded", {"answer": answer, "object_ids": object_ids}

    if answer == "ocr_or_reading_error":
        apply_fields(
            chain,
            {
                "datum_role": "rejected_reference",
                "dimension_scope": "ocr_error",
                "anchor_status": "rejected_ocr_or_reading_error",
                "exclude_from_global_audit": True,
                "anchor_review": {**review, "status": "excluded_from_global_audit"},
            },
        )
        return "excluded", {"answer": answer, "object_ids": object_ids}

    if answer == "needs_site_measurement":
        apply_fields(
            chain,
            {
                "datum_role": "site_measurement_required",
                "dimension_scope": "site_measurement_required",
                "anchor_status": "needs_site_measurement",
                "exclude_from_global_audit": True,
                "anchor_review": {**review, "status": "blocks_stable_deepening"},
            },
        )
        return "blocked", {"reason": "needs_site_measurement", "answer": answer, "object_ids": object_ids, "severity": "high"}

    return "blocked", {"reason": "rejected_by_human", "answer": answer, "object_ids": object_ids}


def append_note(package: dict[str, Any], message: str) -> None:
    notes = package.setdefault("extraction_notes", [])
    notes.append({"id": f"NOTE-DIM-CONFIRM-{len(notes) + 1:02d}", "type": "dimension_anchor_confirmation_apply", "message": message})


def apply_confirmation(
    package: dict[str, Any],
    checklist: dict[str, Any],
    response: dict[str, Any],
    version: str,
    tolerance_mm: float = DEFAULT_TOLERANCE_MM,
) -> tuple[dict[str, Any], dict[str, Any]]:
    result = copy.deepcopy(package)
    result["package_id"] = version
    items = checklist_index(checklist)
    decisions = decision_index(response)
    top_by_id = chain_index(result.get("dimension_chains") or [])
    model = result.get("candidate_model") if isinstance(result.get("candidate_model"), dict) else {}
    model_by_id = chain_index(model.get("dimension_chains") or [])

    applied: list[str] = []
    excluded: list[str] = []
    blocked: list[dict[str, Any]] = []
    missing: list[str] = []

    for chain_id, item in items.items():
        decision = decisions.get(chain_id)
        if not decision:
            blocked.append({"dimension_chain_id": chain_id, "reason": "missing_decision"})
            continue
        targets = [target for target in [top_by_id.get(chain_id), model_by_id.get(chain_id)] if target is not None]
        if not targets:
            missing.append(chain_id)
            continue
        statuses: list[str] = []
        detail: dict[str, Any] = {}
        for target in targets:
            status, detail = apply_decision_to_chain(target, item, decision, tolerance_mm)
            statuses.append(status)
        remove_unresolved_for_chain(result, chain_id)
        if "blocked" in statuses:
            block = {"dimension_chain_id": chain_id, **detail}
            blocked.append(block)
            append_unresolved(result, chain_id, str(decision.get("answer") or decision.get("decision")), detail.get("object_ids") or [], detail.get("severity", "medium"))
        elif "excluded" in statuses:
            excluded.append(chain_id)
        else:
            applied.append(chain_id)

    append_note(result, "Applied human dimension anchor confirmations to a new extraction package candidate.")
    if isinstance(model, dict):
        model.setdefault("extraction_notes", [])
        model["extraction_notes"].append(
            {
                "id": f"NOTE-DIM-CONFIRM-MODEL-{len(model['extraction_notes']) + 1:02d}",
                "type": "dimension_anchor_confirmation_apply",
                "message": "Dimension confirmation fields synchronized from package-level confirmation application.",
            }
        )

    report = {
        "schema_version": "dimension_anchor_confirmation_apply_report_v1",
        "output_package_id": version,
        "checklist_gate": checklist.get("confirmation_gate"),
        "applied_chain_ids": applied,
        "excluded_chain_ids": excluded,
        "blocked_items": blocked,
        "missing_chain_ids": missing,
        "can_quick_concept": bool(checklist.get("can_quick_concept")),
        "can_stable_deepening_candidate": not blocked and not missing,
    }
    return result, report


def summarize(report: dict[str, Any]) -> list[str]:
    return [
        f"output_package_id={report.get('output_package_id')}",
        f"applied={len(report.get('applied_chain_ids') or [])} excluded={len(report.get('excluded_chain_ids') or [])} blocked={len(report.get('blocked_items') or [])} missing={len(report.get('missing_chain_ids') or [])}",
        f"can_quick_concept={str(report.get('can_quick_concept')).lower()} can_stable_deepening_candidate={str(report.get('can_stable_deepening_candidate')).lower()}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("checklist", type=Path)
    parser.add_argument("response", type=Path)
    parser.add_argument("output_package", type=Path)
    parser.add_argument("output_report", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--tolerance-mm", type=float, default=DEFAULT_TOLERANCE_MM)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    result, report = apply_confirmation(
        load_json(args.package),
        load_json(args.checklist),
        load_json(args.response),
        args.version,
        args.tolerance_mm,
    )
    write_json(args.output_package, result)
    write_json(args.output_report, report)
    if not args.json_only:
        for line in summarize(report):
            print(line)
    return 0 if not report["blocked_items"] and not report["missing_chain_ids"] else 1


if __name__ == "__main__":
    raise SystemExit(main())