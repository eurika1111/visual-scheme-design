#!/usr/bin/env python3
"""Summarize validation errors and warnings into short actionable lines."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


SEVERITY = {
    "opening_binding_error": "error",
    "coordinate_system_error": "error",
    "duplicate_id": "error",
    "zero_length_wall": "error",
    "overlapping_or_duplicate_wall": "error",
    "furniture_furniture_collision": "high",
    "kitchen_workflow_collision": "high",
    "door_swing_furniture_collision": "high",
    "door_swing_wall_collision": "high",
    "furniture_wall_collision": "high",
    "circulation_width_warning": "medium",
    "furniture_clearance_warning": "medium",
    "kitchen_workflow_clearance_warning": "medium",
    "door_swing_clearance_warning": "medium",
    "room_edge_off_wall": "medium",
    "room_edge_under_supported": "medium",
    "room_area_mismatch": "low",
    "wall_near_miss": "medium",
    "isolated_wall": "low",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fmt_ids(value: Any) -> str:
    if isinstance(value, list):
        return " + ".join(str(v) for v in value)
    return str(value)


def describe_issue(item: dict[str, Any]) -> str:
    t = item.get("type", "unknown")
    severity = SEVERITY.get(t, "info")

    if "furniture_ids" in item:
        ids = fmt_ids(item["furniture_ids"])
        dist = item.get("distance_mm")
        required = item.get("required_clearance_mm")
        if "collision" in t:
            return f"[{severity}] {t}: {ids} overlap/collide; distance={dist}mm, required={required}mm"
        return f"[{severity}] {t}: {ids} too close; distance={dist}mm, required={required}mm"

    if "object_id" in item:
        target = item.get("object_id")
        wall_ids = item.get("wall_ids")
        extra = f", walls={fmt_ids(wall_ids)}" if wall_ids else ""
        return f"[{severity}] {t}: {target}{extra}"

    if "members" in item:
        return f"[{severity}] {t}: {fmt_ids(item['members'])}"

    if "door_id" in item:
        return f"[{severity}] {t}: door={item.get('door_id')}"

    if "room_id" in item:
        return f"[{severity}] {t}: room={item.get('room_id')}, edge={item.get('edge_index')}"

    if "path_id" in item:
        return f"[{severity}] {t}: path={item.get('path_id')}"

    if "opening_id" in item:
        return f"[{severity}] {t}: opening={item.get('opening_id')}"

    return f"[{severity}] {t}: {item.get('message', 'see validation report')}"


def summarize(report: dict[str, Any], limit: int) -> list[str]:
    issues = list(report.get("errors", [])) + list(report.get("warnings", []))
    counter = Counter(item.get("type", "unknown") for item in issues)
    lines = [
        f"readiness={report.get('readiness')} errors={report.get('summary', {}).get('error_count', 0)} warnings={report.get('summary', {}).get('warning_count', 0)}",
    ]
    if counter:
        counts = ", ".join(f"{name}:{count}" for name, count in sorted(counter.items()))
        lines.append(f"issue_counts={counts}")
    for item in issues[:limit]:
        lines.append(describe_issue(item))
    if len(issues) > limit:
        lines.append(f"... {len(issues) - limit} more issues omitted")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("validation", type=Path)
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = load_json(args.validation)
    if args.json:
        issues = list(report.get("errors", [])) + list(report.get("warnings", []))
        output = {
            "readiness": report.get("readiness"),
            "summary": report.get("summary", {}),
            "issue_counts": dict(Counter(item.get("type", "unknown") for item in issues)),
            "issues": [describe_issue(item) for item in issues[: args.limit]],
            "omitted": max(0, len(issues) - args.limit),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for line in summarize(report, args.limit):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
