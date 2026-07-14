#!/usr/bin/env python3
"""Gate scheme planning on source-to-base fidelity and explicit human review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def polygon_area_m2(points: list[list[float]]) -> float | None:
    if len(points) < 3:
        return None
    area = 0.0
    for left, right in zip(points, points[1:] + points[:1]):
        area += float(left[0]) * float(right[1]) - float(right[0]) * float(left[1])
    return abs(area) / 2_000_000.0


def base_version(base: dict[str, Any]) -> str:
    return str(base.get("version") or (base.get("base_inference") or {}).get("version") or "base_v1")


def assess(base: dict[str, Any], evidence: dict[str, Any], max_area_deviation: float) -> dict[str, Any]:
    rooms = {item.get("id"): item for item in base.get("rooms", []) or [] if item.get("id")}
    comparisons = []
    blockers = []
    for anchor in evidence.get("room_area_anchors", []) or []:
        room_id = anchor.get("room_id")
        room = rooms.get(room_id)
        source_area = float(anchor.get("source_area_m2", 0) or 0)
        model_area = polygon_area_m2((room or {}).get("polygon", []) or [])
        if not room or model_area is None or source_area <= 0:
            blockers.append(f"invalid_room_area_anchor:{room_id}")
            continue
        deviation = abs(model_area - source_area) / source_area
        comparisons.append({
            "room_id": room_id,
            "source_area_m2": source_area,
            "model_area_m2": round(model_area, 2),
            "deviation_ratio": round(deviation, 3),
            "status": "passed" if deviation <= max_area_deviation else "failed",
        })
        if deviation > max_area_deviation:
            blockers.append(f"room_area_deviation:{room_id}:{deviation:.3f}")

    review_status = evidence.get("review_status", "pending")
    if review_status != "accepted":
        blockers.append(f"human_review:{review_status}")
    version = base_version(base)
    if evidence.get("base_version") != version:
        blockers.append("base_version_mismatch")
    if not evidence.get("source_image") or not evidence.get("review_image"):
        blockers.append("missing_source_or_review_image")

    return {
        "schema_version": "base_fidelity_report_v1",
        "base_version": version,
        "fidelity_gate": "open" if not blockers else "closed",
        "can_plan_schemes": not blockers,
        "review_status": review_status,
        "confirmed_by": evidence.get("confirmed_by"),
        "max_area_deviation_ratio": max_area_deviation,
        "area_comparisons": comparisons,
        "blockers": blockers,
        "next_action": "plan schemes" if not blockers else "rebuild or review the scheme base",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check source-to-base fidelity before scheme planning.")
    parser.add_argument("base_model", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-area-deviation", type=float, default=0.25)
    args = parser.parse_args()
    report = assess(load_json(args.base_model), load_json(args.evidence), args.max_area_deviation)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"fidelity_gate={report['fidelity_gate']} can_plan_schemes={str(report['can_plan_schemes']).lower()}")
    for blocker in report["blockers"]:
        print(f"[blocker] {blocker}")
    return 0 if report["can_plan_schemes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
