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
    level = state.get("level")
    status = state.get("validation_status")
    blockers = state.get("blockers") or []
    base_ok = status == "passed" and not blockers
    return {
        "can_quick_concept": base_ok and level_at_least(level, "L2"),
        "can_stable_deepening": base_ok and level_at_least(level, "L3"),
        "reason": "ok" if base_ok else "validation_not_passed_or_blocked",
    }


def print_summary(state: dict[str, Any]) -> None:
    gate = state_gate(state)
    print(f"state: {state.get('validation_status')} / {state.get('level')} / {state.get('phase')}")
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
