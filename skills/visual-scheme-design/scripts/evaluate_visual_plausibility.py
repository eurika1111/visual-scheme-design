#!/usr/bin/env python3
"""Enforce the visual plausibility review gate without external dependencies."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_BLOCKERS = {
    "base_fidelity",
    "functional_completeness",
    "access_logic",
    "furniture_usability",
    "scheme_logic_alignment",
    "ai_artifacts",
    "multi_view_consistency",
}
REQUIRED_LOGIC_FIELDS = {
    "primary_problem",
    "core_move",
    "user_routines",
    "functional_relationships",
    "circulation_story",
    "furniture_logic",
    "fixed_elements",
    "tradeoff",
    "visual_proof",
    "blocking_unknowns",
}
VIEW_QUALITY = {
    "structural_credibility",
    "furniture_logic",
    "scale_plausibility",
    "strategy_visibility",
    "visual_coherence",
}
PACKAGE_QUALITY = VIEW_QUALITY | {
    "routine_readability",
    "circulation_intuition",
    "option_distinctness",
}
VALID_BLOCKER_STATUS = {"pass", "fail", "unknown", "not_applicable"}
VALID_QUALITY_RATING = {"weak", "acceptable", "strong", "unknown", "not_applicable"}
VALID_REVIEW_SCOPE = {"view", "scheme_package"}
VALID_REVIEW_METHOD = {
    "manual_visual_review",
    "multimodal_image_inspection",
    "deterministic_and_visual_review",
    "cross_view_visual_review",
}
VALID_EVIDENCE_KINDS = {
    "overlay",
    "anchor_comparison",
    "deterministic_validation",
    "full_image_review",
    "region_review",
    "cross_view_comparison",
    "scheme_document",
    "source_reference",
}
VALID_ARTIFACT_KINDS = {"image", "overlay", "validation", "document", "comparison", "source"}
EVIDENCE_ARTIFACT_KINDS = {
    "overlay": {"overlay"},
    "anchor_comparison": {"overlay", "validation"},
    "deterministic_validation": {"validation"},
    "full_image_review": {"image", "overlay"},
    "region_review": {"image", "overlay"},
    "cross_view_comparison": {"image", "overlay", "comparison"},
    "scheme_document": {"document", "comparison"},
    "source_reference": {"source", "image", "document"},
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    return value is not None


def valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    if parsed.tzinfo is None:
        return False
    return parsed <= datetime.now(parsed.tzinfo) + timedelta(minutes=5)


def validate_artifacts(
    review: dict[str, Any], evidence_root: Path | None, errors: list[str]
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    artifacts = review.get("evidence_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("evidence_artifacts must be a non-empty list")
        return {}, set()
    if evidence_root is None:
        errors.append("evidence_root is required to verify evidence artifacts")
    artifact_map: dict[str, dict[str, Any]] = {}
    verified: set[str] = set()
    for index, artifact in enumerate(artifacts):
        label = f"evidence_artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{label} must be an object")
            continue
        artifact_id = str(artifact.get("id") or "")
        if not artifact_id:
            errors.append(f"{label} requires id")
            continue
        if artifact_id in artifact_map:
            errors.append(f"duplicate evidence artifact id: {artifact_id}")
            continue
        artifact_map[artifact_id] = artifact
        kind = artifact.get("kind")
        if kind not in VALID_ARTIFACT_KINDS:
            errors.append(f"{label} has invalid kind: {kind}")
        path_value = artifact.get("path")
        expected_hash = str(artifact.get("sha256") or "")
        if not nonempty(path_value):
            errors.append(f"{label} requires path")
        if not expected_hash.startswith("sha256:") or len(expected_hash) != 71:
            errors.append(f"{label} requires sha256:<64 lowercase hex>")
        else:
            try:
                int(expected_hash[7:], 16)
            except ValueError:
                errors.append(f"{label} has invalid sha256")
        if evidence_root is None or not nonempty(path_value):
            continue
        path = Path(str(path_value))
        resolved = path if path.is_absolute() else evidence_root / path
        if not resolved.is_file():
            errors.append(f"{label} evidence file does not exist: {resolved}")
            continue
        actual_hash = "sha256:" + hashlib.sha256(resolved.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            errors.append(f"{label} sha256 mismatch")
            continue
        verified.add(artifact_id)
    return artifact_map, verified


def validate_evidence(
    item: dict[str, Any],
    label: str,
    errors: list[str],
    artifact_map: dict[str, dict[str, Any]],
    verified_artifacts: set[str],
) -> set[str]:
    evidence = item.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{label} requires structured evidence")
        return set()
    kinds: set[str] = set()
    for index, record in enumerate(evidence):
        if not isinstance(record, dict):
            errors.append(f"{label} evidence[{index}] must be an object")
            continue
        kind = record.get("kind")
        if kind not in VALID_EVIDENCE_KINDS:
            errors.append(f"{label} evidence[{index}] has invalid kind: {kind}")
        else:
            kinds.add(kind)
        for field in ("reference", "finding"):
            if not nonempty(record.get(field)):
                errors.append(f"{label} evidence[{index}] missing {field}")
        artifact_id = str(record.get("reference") or "")
        artifact = artifact_map.get(artifact_id)
        if artifact is None:
            errors.append(f"{label} evidence[{index}] references unknown artifact: {artifact_id}")
        elif artifact_id not in verified_artifacts:
            errors.append(f"{label} evidence[{index}] artifact is not verified: {artifact_id}")
        elif kind in EVIDENCE_ARTIFACT_KINDS and artifact.get("kind") not in EVIDENCE_ARTIFACT_KINDS[kind]:
            errors.append(
                f"{label} evidence[{index}] kind {kind} is incompatible with artifact kind {artifact.get('kind')}"
            )
    return kinds


def evaluate(review: dict[str, Any], evidence_root: Path | None = None) -> tuple[dict[str, Any], int]:
    errors: list[str] = []
    if review.get("schema_version") != "visual_plausibility_review_v1":
        errors.append("schema_version must be visual_plausibility_review_v1")
    for field in ("base_id", "option_id", "view_ids", "reviewer"):
        if not nonempty(review.get(field)):
            errors.append(f"missing required field: {field}")
    scope = review.get("review_scope")
    if scope not in VALID_REVIEW_SCOPE:
        errors.append(f"review_scope must be one of: {', '.join(sorted(VALID_REVIEW_SCOPE))}")
    if review.get("image_reviewed") is not True:
        errors.append("image_reviewed must be true after an actual visual inspection")
    if review.get("review_method") not in VALID_REVIEW_METHOD:
        errors.append("review_method is missing or unsupported")
    if not valid_timestamp(review.get("reviewed_at")):
        errors.append("reviewed_at must be a non-future ISO 8601 timestamp with timezone")
    artifact_map, verified_artifacts = validate_artifacts(review, evidence_root, errors)

    manifest = review.get("scheme_logic_manifest")
    if not isinstance(manifest, dict):
        errors.append("scheme_logic_manifest must be an object")
        manifest = {}
    missing_logic = sorted(
        field for field in REQUIRED_LOGIC_FIELDS if not nonempty(manifest.get(field))
        and field != "blocking_unknowns"
    )
    if "blocking_unknowns" not in manifest or not isinstance(manifest.get("blocking_unknowns"), list):
        missing_logic.append("blocking_unknowns")
    if missing_logic:
        errors.append("missing scheme logic fields: " + ", ".join(sorted(set(missing_logic))))
    for field in (
        "linked_obligations",
        "core_proof_objects",
        "support_function_inventory",
        "concurrent_use_scenarios",
        "environmental_comfort",
    ):
        if field in manifest and not isinstance(manifest.get(field), list):
            errors.append(f"scheme logic field must be a list when present: {field}")
    for index, item in enumerate(manifest.get("core_proof_objects", []) or []):
        if not isinstance(item, dict) or not nonempty(item.get("id")):
            errors.append(f"core_proof_objects[{index}] requires an object id")
            continue
        if item.get("status") != "passed":
            errors.append(f"core proof object is not validated: {item.get('id')}")
        evidence_id = str(item.get("evidence") or "")
        if not evidence_id:
            errors.append(f"core proof object has no validation evidence: {item.get('id')}")
        elif evidence_id not in artifact_map:
            errors.append(f"core proof object references unknown evidence artifact: {evidence_id}")
        elif evidence_id not in verified_artifacts:
            errors.append(f"core proof object evidence is not verified: {evidence_id}")
        elif artifact_map[evidence_id].get("kind") != "validation":
            errors.append(f"core proof object evidence must be a validation artifact: {evidence_id}")

    blocker_items = review.get("blocking_checks")
    if not isinstance(blocker_items, list):
        errors.append("blocking_checks must be a list")
        blocker_items = []
    blocker_map: dict[str, str] = {}
    for item in blocker_items:
        if not isinstance(item, dict):
            errors.append("each blocking check must be an object")
            continue
        check_id = item.get("id")
        status = item.get("status")
        if check_id in blocker_map:
            errors.append(f"duplicate blocking check: {check_id}")
        if check_id not in REQUIRED_BLOCKERS:
            errors.append(f"unknown blocking check: {check_id}")
        if status not in VALID_BLOCKER_STATUS:
            errors.append(f"invalid blocker status for {check_id}: {status}")
        if check_id in REQUIRED_BLOCKERS and status in VALID_BLOCKER_STATUS:
            blocker_map[check_id] = status
        label = f"blocker {check_id}"
        if status in {"pass", "fail"}:
            kinds = validate_evidence(item, label, errors, artifact_map, verified_artifacts)
            if check_id == "base_fidelity" and not kinds.intersection(
                {"overlay", "anchor_comparison", "deterministic_validation", "source_reference"}
            ):
                errors.append("base_fidelity evidence must include a geometry or source comparison")
            if check_id == "ai_artifacts" and not kinds.intersection({"full_image_review", "region_review"}):
                errors.append("ai_artifacts evidence must include an actual image review")
            if check_id == "multi_view_consistency" and len(review.get("view_ids") or []) > 1 \
                    and "cross_view_comparison" not in kinds:
                errors.append("multi_view_consistency requires cross_view_comparison evidence")
        elif status == "unknown" and not nonempty(item.get("notes")):
            errors.append(f"{label} unknown status requires notes")
        elif status == "not_applicable" and not nonempty(item.get("covered_by")):
            errors.append(f"{label} not_applicable status requires covered_by")

    missing_blockers = sorted(REQUIRED_BLOCKERS - set(blocker_map))
    if missing_blockers:
        errors.append("missing blocking checks: " + ", ".join(missing_blockers))
    if blocker_map.get("multi_view_consistency") == "not_applicable" and len(review.get("view_ids") or []) > 1:
        errors.append("multi_view_consistency cannot be not_applicable for multiple views")
    for check_id, status in blocker_map.items():
        if scope == "scheme_package" and check_id != "multi_view_consistency" and status == "not_applicable":
            errors.append(f"{check_id} cannot be not_applicable in a scheme_package review")

    quality_items = review.get("quality_checks")
    if not isinstance(quality_items, list):
        errors.append("quality_checks must be a list")
        quality_items = []
    weak_quality: list[str] = []
    unknown_quality: list[str] = []
    quality_seen: set[str] = set()
    not_applicable_quality: list[str] = []
    for item in quality_items:
        if not isinstance(item, dict):
            errors.append("each quality check must be an object")
            continue
        check_id = str(item.get("id") or "")
        rating = item.get("rating")
        if not check_id:
            errors.append("quality check id is required")
        elif check_id not in PACKAGE_QUALITY:
            errors.append(f"unknown quality check: {check_id}")
        elif check_id in quality_seen:
            errors.append(f"duplicate quality check: {check_id}")
        else:
            quality_seen.add(check_id)
        if rating not in VALID_QUALITY_RATING:
            errors.append(f"invalid quality rating for {check_id}: {rating}")
        elif rating == "weak":
            weak_quality.append(check_id)
        elif rating == "unknown":
            unknown_quality.append(check_id)
        elif rating == "not_applicable":
            not_applicable_quality.append(check_id)
        if rating in {"weak", "acceptable", "strong"}:
            validate_evidence(item, f"quality {check_id}", errors, artifact_map, verified_artifacts)
        elif rating == "unknown" and not nonempty(item.get("notes")):
            errors.append(f"quality {check_id} unknown rating requires notes")
        elif rating == "not_applicable" and not nonempty(item.get("covered_by")):
            errors.append(f"quality {check_id} not_applicable rating requires covered_by")
    required_quality = PACKAGE_QUALITY if scope == "scheme_package" else VIEW_QUALITY
    missing_quality = sorted(required_quality - quality_seen)
    if missing_quality:
        errors.append("missing quality checks: " + ", ".join(missing_quality))

    failed_blockers = sorted(key for key, value in blocker_map.items() if value == "fail")
    unknown_blockers = sorted(key for key, value in blocker_map.items() if value == "unknown")
    logic_unknowns = manifest.get("blocking_unknowns") if isinstance(manifest.get("blocking_unknowns"), list) else []

    if errors or failed_blockers:
        decision, exit_code = "rejected", 2
    elif unknown_blockers or logic_unknowns or unknown_quality:
        decision, exit_code = "needs_review", 1
    elif weak_quality:
        decision, exit_code = "needs_repair", 1
    elif scope == "view":
        decision, exit_code = "view_passed", 0
    else:
        decision, exit_code = "displayable", 0

    result = {
        "schema_version": "visual_plausibility_gate_result_v1",
        "decision": decision,
        "base_id": review.get("base_id"),
        "option_id": review.get("option_id"),
        "review_scope": scope,
        "errors": errors,
        "failed_blockers": failed_blockers,
        "unknown_blockers": unknown_blockers,
        "logic_unknowns": logic_unknowns,
        "weak_quality": sorted(weak_quality),
        "unknown_quality": sorted(unknown_quality),
        "not_applicable_quality": sorted(not_applicable_quality),
        "delivery_decision_allowed": scope == "scheme_package",
        "evidence_integrity_status": "verified" if artifact_map and len(verified_artifacts) == len(artifact_map) else "failed",
        "image_is_geometry_authority": False,
    }
    return result, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a visual plausibility review package.")
    parser.add_argument("review", type=Path)
    parser.add_argument("--evidence-root", type=Path, help="Root for relative evidence artifact paths; defaults to review directory")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    review_path = args.review.resolve()
    evidence_root = args.evidence_root.resolve() if args.evidence_root else review_path.parent
    result, exit_code = evaluate(load_json(review_path), evidence_root)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
