#!/usr/bin/env python3
"""Read compact project_state.json and print a human-friendly gate summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LEVEL_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}


def load_state(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def level_at_least(level: str | None, minimum: str) -> bool:
    return LEVEL_ORDER.get(level or "", -1) >= LEVEL_ORDER[minimum]


def state_gate(state: dict[str, Any]) -> dict[str, Any]:
    base_level = state.get("base_level", state.get("level"))
    base_status = state.get("base_validation_status", state.get("validation_status"))
    option_level = state.get("active_option_level", state.get("level"))
    option_status = state.get("active_option_validation_status", state.get("validation_status"))
    blockers = state.get("blockers") or []
    base_ok = base_status == "passed" and not blockers
    option_ok = option_status == "passed" and not blockers
    return {
        "can_quick_concept": base_ok and level_at_least(base_level, "L2"),
        "can_stable_deepening": base_ok and option_ok and level_at_least(option_level, "L3"),
        "base_level": base_level,
        "base_validation_status": base_status,
        "active_option_level": option_level,
        "active_option_validation_status": option_status,
        "reason": "ok" if base_ok and option_ok else "base_or_active_option_not_passed",
    }


def print_summary(state: dict[str, Any]) -> None:
    gate = state_gate(state)
    print(f"state: {state.get('validation_status')} / {state.get('phase')}")
    print(f"base: {gate['base_validation_status']} / {gate['base_level']}")
    print(f"active_option_state: {gate['active_option_validation_status']} / {gate['active_option_level']}")
    print(f"domain: {state.get('domain')}  mode: {state.get('mode')}")
    print(f"active_base: {state.get('active_base')}")
    print(f"active_option: {state.get('active_option')}")
    print(f"last_action: {state.get('last_action')}")
    print(f"can_quick_concept: {str(gate['can_quick_concept']).lower()}")
    print(f"can_stable_deepening: {str(gate['can_stable_deepening']).lower()}")

    registry = state.get("option_registry") or []
    if registry:
        print("options:")
        for item in registry:
            print(
                "- {id} {version}: {status}, validation={validation_status}, level={level}".format(
                    id=item.get("id"),
                    version=item.get("version"),
                    status=item.get("status"),
                    validation_status=item.get("validation_status", "unknown"),
                    level=item.get("level", "unknown"),
                )
            )

    blockers = state.get("blockers") or []
    if blockers:
        print("blockers:")
        for blocker in blockers:
            print(f"- {blocker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path, help="Path to project_state.json")
    parser.add_argument("--json", action="store_true", help="Print gate summary as JSON")
    parser.add_argument("--require", choices=["quick", "deepening"], help="Exit nonzero if the required gate is not open")
    args = parser.parse_args()

    state = load_state(args.state)
    gate = state_gate(state)

    if args.json:
        output = {
            "validation_status": state.get("validation_status"),
            "level": state.get("level"),
            "base_level": gate["base_level"],
            "base_validation_status": gate["base_validation_status"],
            "active_option_level": gate["active_option_level"],
            "active_option_validation_status": gate["active_option_validation_status"],
            "phase": state.get("phase"),
            "active_base": state.get("active_base"),
            "active_option": state.get("active_option"),
            **gate,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_summary(state)

    if args.require == "quick" and not gate["can_quick_concept"]:
        return 1
    if args.require == "deepening" and not gate["can_stable_deepening"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
