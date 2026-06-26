#!/usr/bin/env python3
"""Update project_state.json after a scheme operation has produced a new option."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


LEVEL_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validation_status(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    if int(summary.get("error_count", 0)) > 0:
        return "failed"
    if int(summary.get("warning_count", 0)) > 0:
        return "warning"
    return "passed"


def registry_status(status: str) -> str:
    if status == "passed":
        return "保留"
    if status == "warning":
        return "待修改"
    return "淘汰"


def upsert_option(registry: list[dict[str, Any]], entry: dict[str, Any]) -> None:
    for index, item in enumerate(registry):
        if item.get("version") == entry.get("version") or item.get("id") == entry.get("id"):
            registry[index] = {**item, **entry}
            return
    registry.append(entry)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--option-id", required=True, help="User-facing option ID, e.g. 方案 B")
    parser.add_argument("--version", required=True, help="Model version ID, e.g. scheme_B_v1")
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--parent", default=None)
    parser.add_argument("--last-action", default="set_active_option")
    parser.add_argument("--notes", default=None)
    args = parser.parse_args()

    state = load_json(args.state)
    report = load_json(args.validation)
    status = validation_status(report)
    level = report.get("readiness")

    entry = {
        "id": args.option_id,
        "version": args.version,
        "status": registry_status(status),
        "parent": args.parent,
        "validation_status": status,
        "level": level,
        "files": {
            "model": str(args.model),
            "validation_report": str(args.validation),
        },
        "notes": args.notes or ("geometry validation passed" if status == "passed" else "needs review before use"),
    }

    registry = state.setdefault("option_registry", [])
    upsert_option(registry, entry)

    state["updated_at"] = date.today().isoformat()
    state["active_option"] = args.version
    state["active_option_level"] = level
    state["active_option_validation_status"] = status
    base_status = state.get("base_validation_status", state.get("validation_status"))
    state["validation_status"] = "passed" if base_status == "passed" and status == "passed" else "warning"
    state["last_action"] = args.last_action
    state.setdefault("files", {})["active_scheme_model"] = str(args.model)
    state.setdefault("files", {})["active_scheme_validation_report"] = str(args.validation)
    state.setdefault("checks", {})[args.version] = {
        "readiness": level,
        "status": status,
        "summary": report.get("summary", {}),
    }

    if status == "failed":
        blocker = f"{args.version} validation failed"
        blockers = state.setdefault("blockers", [])
        if blocker not in blockers:
            blockers.append(blocker)

    save_json(args.state, state)
    print(f"active_option={args.version} status={status} level={level}")
    return 0 if status != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
