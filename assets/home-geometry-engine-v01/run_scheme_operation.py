#!/usr/bin/env python3
"""Run a scheme operation chain: apply operations, validate, update state, print gate."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], allowed: set[int] | None = None) -> int:
    allowed = allowed or {0}
    label = Path(cmd[1]).name if len(cmd) > 1 else str(cmd[0])
    print(f"== {label}", flush=True)
    completed = subprocess.run(cmd)
    if completed.returncode not in allowed:
        raise SystemExit(completed.returncode)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable, help="Python executable used for child scripts")
    parser.add_argument("--engine-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--base-model", required=True, type=Path)
    parser.add_argument("--operations", required=True, type=Path)
    parser.add_argument("--output-model", required=True, type=Path)
    parser.add_argument("--validation-output", required=True, type=Path)
    parser.add_argument("--option-id", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--parent", default="base_v1")
    parser.add_argument("--last-action", default="run_scheme_operation")
    parser.add_argument("--notes", default=None)
    parser.add_argument("--source-model", action="append", default=[], help="Source model in name=path format")
    parser.add_argument("--render-output", type=Path, default=None, help="Optional SVG output path")
    args = parser.parse_args()

    engine = args.engine_dir
    py = args.python
    operation_applier = engine / "operation_applier.py"
    validator = engine / "geometry_validator.py"
    renderer = engine / "simple_renderer.py"
    set_active = engine / "set_active_option.py"
    state_reader = engine / "read_project_state.py"
    summarizer = engine / "summarize_validation.py"

    run([py, str(operation_applier), str(args.base_model), str(args.operations), str(args.output_model), *args.source_model])
    run([py, str(validator), str(args.output_model), str(args.validation_output)], allowed={0, 1})

    if args.render_output:
        run([py, str(renderer), str(args.output_model), str(args.render_output), str(args.validation_output)])

    set_active_cmd = [
        py,
        str(set_active),
        "--state", str(args.state),
        "--option-id", args.option_id,
        "--version", args.version,
        "--model", str(args.output_model),
        "--validation", str(args.validation_output),
        "--parent", args.parent,
        "--last-action", args.last_action,
    ]
    if args.notes:
        set_active_cmd.extend(["--notes", args.notes])
    run(set_active_cmd, allowed={0, 1})
    run([py, str(summarizer), str(args.validation_output)])
    run([py, str(state_reader), str(args.state)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
