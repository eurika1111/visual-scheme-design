#!/usr/bin/env python3
"""Build a client-visible base handoff markdown package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rel(path: Path | None, base: Path) -> str:
    if not path:
        return "not provided"
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- none\n"
    return "".join(f"- {item}\n" for item in items)


def issue_lines(report: dict[str, Any], limit: int = 8) -> list[str]:
    issues = report.get("issues") or report.get("warnings") or []
    lines = []
    for item in issues[:limit]:
        kind = item.get("type", "issue")
        target = item.get("target") or item.get("object_id") or item.get("room_id")
        level = item.get("level") or item.get("status") or "note"
        message = item.get("message", "")
        suffix = f" ({target})" if target else ""
        lines.append(f"`{level}` {kind}{suffix}: {message}".strip())
    omitted = max(0, len(issues) - limit)
    if omitted:
        lines.append(f"... {omitted} more issues omitted")
    return lines


def confirmation_lines(checklist: dict[str, Any], limit: int = 8) -> list[str]:
    items = checklist.get("items") or checklist.get("confirmation_items") or []
    lines = []
    for item in items[:limit]:
        item_id = item.get("id") or item.get("dimension_chain_id") or item.get("dimension_id") or item.get("chain_id", "item")
        status = item.get("status", "needs_review")
        prompt = item.get("confirmation_question") or item.get("prompt") or item.get("question") or ""
        residual = item.get("residual_mm")
        residual_note = f" residual={residual}mm." if residual is not None else ""
        lines.append(f"`{item_id}` - {status}.{residual_note} {prompt}".strip())
    omitted = max(0, len(items) - limit)
    if omitted:
        lines.append(f"... {omitted} more items omitted")
    return lines


def build_markdown(args: argparse.Namespace) -> str:
    project_root = args.project_root
    validation = load_json(args.validation)
    dimension = load_json(args.dimension_audit)
    checklist = load_json(args.checklist)

    summary = validation.get("summary", {})
    geometry_summary = validation.get("geometry_summary", {})
    dimension_summary = dimension.get("summary", {})
    base_level = validation.get("extraction_level") or validation.get("readiness") or "unknown"
    base_gate = validation.get("extraction_gate") or validation.get("validation_status") or "unknown"

    confirmation = confirmation_lines(checklist)
    validation_issues = issue_lines(validation)
    dimension_issues = issue_lines(dimension)

    title = args.title or "Residential Base Review Package"
    return f"""# {title}

## Current Decision

- Base level: `{base_level}`
- Base gate: `{base_gate}`
- Can quick concept: `{str(validation.get("can_quick_concept", "unknown")).lower()}`
- Can visual deepening/reference: `{str(validation.get("can_stable_deepening", "unknown")).lower()}`
- Construction status: `not construction-ready`

## Files To Review

- Original source image: `{rel(args.source_image, project_root)}`
- Base model: `{rel(args.base_model, project_root)}`
- Base review SVG: `{rel(args.review_svg, project_root)}`
- Source validation: `{rel(args.validation, project_root)}`
- Dimension audit: `{rel(args.dimension_audit, project_root)}`
- Dimension checklist: `{rel(args.checklist_md, project_root)}`

## Validation Summary

- Sources: `{summary.get("source_image_count", "unknown")}`
- Rooms: `{geometry_summary.get("room_count", summary.get("room_count", "unknown"))}`
- Openings: `{geometry_summary.get("opening_count", "unknown")}`
- Geometry readiness: `{summary.get("geometry_readiness", validation.get("readiness", "unknown"))}`
- Dimension gate: `{summary.get("dimension_gate", dimension.get("dimension_gate", "unknown"))}`
- Dimension level: `{summary.get("dimension_level", dimension.get("dimension_level", "unknown"))}`
- Model span: `{dimension_summary.get("model_extents", {}).get("span_x", "unknown")} x {dimension_summary.get("model_extents", {}).get("span_y", "unknown")} mm`

## Client Confirmation

Please confirm before scheme generation:

1. The apartment outline matches the original source plan.
2. Room names and adjacencies are correct.
3. Doors, windows, kitchen, bathrooms, balcony, and entry are in the right places.
4. No visible wall, opening, or fixed-service zone is obviously wrong.
5. The listed assumptions are acceptable for visual scheme design.

## Confirmation Items

{bullet_list(confirmation)}
## Validation Notes

{bullet_list(validation_issues)}
## Dimension Notes

{bullet_list(dimension_issues)}
## Next Step After Confirmation

Collect customer needs: residents, must-keep rooms, demolition tolerance, open-kitchen attitude, island attitude, storage priorities, budget/risk level, style direction, and no-change areas.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--title", default=None)
    parser.add_argument("--source-image", type=Path, default=None)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--review-svg", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--dimension-audit", type=Path, default=None)
    parser.add_argument("--checklist", type=Path, default=None)
    parser.add_argument("--checklist-md", type=Path, default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_markdown(args), encoding="utf-8")
    print(f"handoff={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
