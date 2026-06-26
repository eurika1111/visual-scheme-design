#!/usr/bin/env python3
"""Confirm a reviewed repair draft and promote it to an active scheme version."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run(cmd: list[str], allowed: set[int] | None = None) -> int:
    allowed = allowed or {0}
    label = Path(cmd[1]).name if len(cmd) > 1 else str(cmd[0])
    print(f"== {label}", flush=True)
    completed = subprocess.run(cmd)
    if completed.returncode not in allowed:
        raise SystemExit(completed.returncode)
    return completed.returncode


def require_review_confirmation(draft: dict[str, Any], confirmed: bool) -> None:
    if draft.get("status") != "draft_review_required":
        raise SystemExit("Repair draft status must be draft_review_required")
    operations = draft.get("operations", [])
    if not operations:
        raise SystemExit("Repair draft has no operations")
    needs_review = any(operation.get("review_required") for operation in operations)
    if needs_review and not confirmed:
        raise SystemExit("Use --confirm only after the repair draft has been reviewed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable, help="Python executable used for child scripts")
    parser.add_argument("--engine-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--current-model", required=True, type=Path)
    parser.add_argument("--repair-draft", required=True, type=Path)
    parser.add_argument("--output-model", required=True, type=Path)
    parser.add_argument("--validation-output", required=True, type=Path)
    parser.add_argument("--option-id", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--parent", default=None)
    parser.add_argument("--render-output", type=Path, default=None)
    parser.add_argument("--notes", default="confirmed repair draft")
    parser.add_argument("--confirm", action="store_true", help="Required to apply review-required repair drafts")
    args = parser.parse_args()

    draft = load_json(args.repair_draft)
    require_review_confirmation(draft, args.confirm)
    parent = args.parent or draft.get("parent_version") or "unknown"

    engine = args.engine_dir
    py = args.python
    operation_applier = engine / "operation_applier.py"
    validator = engine / "geometry_validator.py"
    renderer = engine / "simple_renderer.py"
    set_active = engine / "set_active_option.py"
    summarizer = engine / "summarize_validation.py"
    state_reader = engine / "read_project_state.py"

    run([py, str(operation_applier), str(args.current_model), str(args.repair_draft), str(args.output_model)])
    run([py, str(validator), str(args.output_model), str(args.validation_output)], allowed={0, 1})

    if args.render_output:
        run([py, str(renderer), str(args.output_model), str(args.render_output), str(args.validation_output)])

    run([
        py,
        str(set_active),
        "--state", str(args.state),
        "--option-id", args.option_id,
        "--version", args.version,
        "--model", str(args.output_model),
        "--validation", str(args.validation_output),
        "--parent", parent,
        "--last-action", "confirm_repair_draft",
        "--notes", args.notes,
    ], allowed={0, 1})
    run([py, str(summarizer), str(args.validation_output)])
    run([py, str(state_reader), str(args.state)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
