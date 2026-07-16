#!/usr/bin/env python3
"""Regression checks for user-approved option counts and identities."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "assets" / "home-geometry-engine-v01"
PLANNER = ENGINE / "scheme_option_planner.py"
BASE = ENGINE / "examples" / "base_object_model.sample.json"
PLACEMENT_TEMPLATE = ENGINE / "examples" / "scheme_intent.placement-sample.json"
REVIEW_BUILDER = ENGINE / "scheme_review_package_builder.py"
STATE_UPDATER = ENGINE / "update_project_state.py"


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def direction(option_id: str, code: str, version: str, goal: str, character: str) -> dict:
    return {
        "option_id": option_id,
        "code": code,
        "version": version,
        "name": f"Direction {code}",
        "strategy_kind": "custom",
        "primary_problem": f"Problem {code}",
        "core_move": f"Core move {code}",
        "tradeoff": f"Tradeoff {code}",
        "alteration_risk": "unassessed",
        "differentiation": {"primary_goal": goal, "spatial_character": character},
        "operations": [{"id": f"{code}-OP-01", "type": "test_move", "target_spaces": []}],
    }


def run_planner(status: str, directions: list[dict], root: Path) -> subprocess.CompletedProcess[str]:
    brief = root / "needs.json"
    fidelity = root / "fidelity.json"
    direction_file = root / "directions.json"
    output = root / "out"
    write_json(brief, {"schema_version": "needs_brief_v1", "project_id": "planner_test"})
    write_json(fidelity, {"base_version": "base_sample_v1", "can_plan_schemes": True})
    write_json(direction_file, {
        "schema_version": "approved_option_directions_v1",
        "status": status,
        "directions": directions,
    })
    return subprocess.run(
        [
            sys.executable,
            str(PLANNER),
            str(BASE),
            str(brief),
            "--output-dir", str(output),
            "--base-fidelity-report", str(fidelity),
            "--directions", str(direction_file),
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        two = [
            direction("方案 稳态", "S", "scheme_stable_v1", "daily_efficiency", "stable"),
            direction("方案 共享", "H", "scheme_shared_v1", "shared_use", "connected"),
        ]
        result = run_planner("approved", two, root)
        if result.returncode != 0:
            print(result.stdout + result.stderr)
            return 1
        plan = json.loads((root / "out" / "scheme_option_plan.json").read_text(encoding="utf-8"))
        assert plan["approved_option_count"] == 2
        assert len(plan["options"]) == 2
        assert [item["option_code"] for item in plan["options"]] == ["S", "H"]
        assert (root / "out" / "scheme_stable_v1_intent.json").exists()
        assert (root / "out" / "scheme_shared_v1_intent.json").exists()
        print("PASS approved_two_direction_set")

    with tempfile.TemporaryDirectory() as temp:
        result = run_planner("pending", [direction("方案 一", "1", "scheme_one_v1", "one", "quiet")], Path(temp))
        assert result.returncode != 0
        assert "explicitly approved" in result.stderr
        print("PASS pending_directions_are_blocked")

    with tempfile.TemporaryDirectory() as temp:
        duplicate_versions = [
            direction("方案 一", "1", "scheme_same_v1", "one", "quiet"),
            direction("方案 二", "2", "scheme_same_v1", "two", "active"),
        ]
        result = run_planner("approved", duplicate_versions, Path(temp))
        assert result.returncode != 0
        assert "unique version" in result.stderr
        print("PASS duplicate_versions_are_blocked")

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        sys.path.insert(0, str(ENGINE))
        from scheme_placement_resolver import resolve  # noqa: PLC0415

        base = json.loads(BASE.read_text(encoding="utf-8-sig"))
        template = json.loads(PLACEMENT_TEMPLATE.read_text(encoding="utf-8-sig"))
        resolved_paths: list[Path] = []
        object_ids: set[str] = set()
        for index, code in enumerate(("NORTH", "SOUTH", "EAST", "WEST"), start=1):
            intent = copy.deepcopy(template)
            intent["scheme_id"] = f"方案 {code}"
            intent["option_code"] = code
            intent["version"] = f"scheme_{code.lower()}_v1"
            resolved, report = resolve(base, intent)
            assert report["layout_gate"] == "ready"
            ids = {item["id"] for item in resolved.get("proposal_objects", [])}
            assert not object_ids.intersection(ids)
            object_ids.update(ids)
            path = root / f"{code.lower()}.json"
            write_json(path, resolved)
            resolved_paths.append(path)
        review_dir = root / "review"
        completed = subprocess.run(
            [sys.executable, str(REVIEW_BUILDER), str(BASE), *(str(path) for path in resolved_paths), "--output-dir", str(review_dir)],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            print(completed.stdout + completed.stderr)
            return 1
        manifest = json.loads((review_dir / "scheme_review_manifest.json").read_text(encoding="utf-8"))
        assert manifest["status"] == "ready"
        assert len(manifest["options"]) == 4
        assert "A/B/C" not in (review_dir / "scheme_review.md").read_text(encoding="utf-8")
        print("PASS four_custom_options_reach_review_package")

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        validation = root / "validation.json"
        problem = root / "problem.json"
        state = root / "state.json"
        write_json(validation, {"readiness": "L3", "summary": {"error_count": 0, "warning_count": 0}})
        write_json(problem, {"readiness": "L0", "summary": {"error_count": 1, "warning_count": 0}})
        completed = subprocess.run(
            [
                sys.executable, str(STATE_UPDATER),
                "--output", str(state),
                "--base-model", str(BASE),
                "--base-validation", str(validation),
                "--base-version", "base_sample_v1",
                "--active-option-id", "方案 NORTH",
                "--active-option-code", "NORTH",
                "--active-option-model", str(BASE),
                "--active-option-validation", str(validation),
                "--active-option-version", "scheme_north_v1",
                "--problem-validation", str(problem),
            ],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            print(completed.stdout + completed.stderr)
            return 1
        project_state = json.loads(state.read_text(encoding="utf-8"))
        assert project_state["active_option"] == "scheme_north_v1"
        assert project_state["option_registry"][1]["id"] == "方案 NORTH"
        assert project_state["option_registry"][1]["option_code"] == "NORTH"
        assert project_state["checks"]["active_option"]["id"] == "方案 NORTH"
        print("PASS custom_active_option_reaches_project_state")

    print("Option direction planner tests passed: 5 scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
