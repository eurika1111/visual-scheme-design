#!/usr/bin/env python3
"""Behavior and fixture tests for the visual plausibility gate."""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "visual-scheme-design" / "scripts" / "evaluate_visual_plausibility.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
REVIEW_DOC = ROOT / "skills" / "visual-scheme-design" / "references" / "scheme-logic-and-visual-plausibility.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def item_by_id(items: list[dict[str, Any]], item_id: str) -> dict[str, Any]:
    return next(item for item in items if item.get("id") == item_id)


def apply_mutation(review: dict[str, Any], mutation: dict[str, Any]) -> None:
    section, item_id, field = str(mutation["path"]).split(".")
    item_by_id(review[section], item_id)[field] = mutation["value"]


def resolved_fixture(name: str) -> tuple[dict[str, Any], int, str]:
    data = load_json(FIXTURES / name)
    if "fixture_base" not in data:
        return data, 0, "displayable"
    review = load_json(FIXTURES / data["fixture_base"])
    for mutation in data.get("mutations", []):
        apply_mutation(review, mutation)
    expected = data["expected"]
    return review, int(expected["exit_code"]), str(expected["decision"])


def run_case(review: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "review.json"
        path.write_text(json.dumps(review, ensure_ascii=False), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--evidence-root", str(FIXTURES)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.returncode, json.loads(completed.stdout)


def main() -> int:
    cases: list[tuple[str, dict[str, Any], int, str]] = []
    for name in ("displayable.json", "needs_repair.json", "needs_review.json", "rejected.json"):
        review, code, decision = resolved_fixture(name)
        cases.append((name.removesuffix(".json"), review, code, decision))

    documented = re.search(
        r"Use this shape with `scripts/evaluate_visual_plausibility\.py`:\s*```json\s*(\{.*?\})\s*```",
        REVIEW_DOC.read_text(encoding="utf-8-sig"),
        re.S,
    )
    if not documented:
        print("Visual plausibility evaluator tests failed:\n- documented example not found")
        return 1
    cases.append(("documented_example", json.loads(documented.group(1)), 0, "displayable"))

    valid = resolved_fixture("displayable.json")[0]

    missing_evidence = copy.deepcopy(valid)
    item_by_id(missing_evidence["blocking_checks"], "ai_artifacts")["evidence"] = []
    cases.append(("missing_evidence_rejects", missing_evidence, 2, "rejected"))

    unknown_artifact = copy.deepcopy(valid)
    item_by_id(unknown_artifact["blocking_checks"], "ai_artifacts")["evidence"][0]["reference"] = "missing:artifact"
    cases.append(("unknown_artifact_rejects", unknown_artifact, 2, "rejected"))

    tampered_hash = copy.deepcopy(valid)
    tampered_hash["evidence_artifacts"][0]["sha256"] = "sha256:" + "0" * 64
    cases.append(("tampered_artifact_hash_rejects", tampered_hash, 2, "rejected"))

    future_review = copy.deepcopy(valid)
    future_review["reviewed_at"] = "2099-01-01T00:00:00+08:00"
    cases.append(("future_review_timestamp_rejects", future_review, 2, "rejected"))

    unvalidated_core = copy.deepcopy(valid)
    unvalidated_core["scheme_logic_manifest"]["core_proof_objects"] = [
        {"id": "ISLAND-01", "status": "unknown", "evidence": ""}
    ]
    cases.append(("unvalidated_core_proof_rejects", unvalidated_core, 2, "rejected"))

    invalid_multi = copy.deepcopy(valid)
    invalid_multi["view_ids"] = ["top", "perspective"]
    cases.append(("multi_view_requires_comparison", invalid_multi, 2, "rejected"))

    view_only = copy.deepcopy(valid)
    view_only["review_scope"] = "view"
    view_only["quality_checks"] = [
        item for item in view_only["quality_checks"]
        if item["id"] in {
            "structural_credibility", "furniture_logic", "scale_plausibility",
            "strategy_visibility", "visual_coherence",
        }
    ]
    cases.append(("view_review_is_not_delivery", view_only, 0, "view_passed"))

    failures: list[str] = []
    for name, review, expected_code, expected_decision in cases:
        code, result = run_case(review)
        if code != expected_code or result.get("decision") != expected_decision:
            failures.append(
                f"{name}: expected code={expected_code} decision={expected_decision}; "
                f"got code={code} decision={result.get('decision')} errors={result.get('errors')}"
            )
        else:
            print(f"PASS {name}")

    if failures:
        print("Visual plausibility evaluator tests failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Visual plausibility evaluator tests passed: {len(cases)} scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
