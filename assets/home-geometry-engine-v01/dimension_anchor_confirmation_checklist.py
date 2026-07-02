#!/usr/bin/env python3
"""Generate a human-review checklist for unresolved dimension anchors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dimension_chain_audit import load_json, write_json


def review_status(draft: dict[str, Any]) -> str:
    if draft.get("confidence") == "high" and not draft.get("issues"):
        return "accepted_candidate"
    if draft.get("start_ref") and draft.get("end_ref"):
        return "needs_human_confirmation"
    return "needs_manual_anchor"


def issue_summary(draft: dict[str, Any]) -> list[str]:
    items: list[str] = []
    for issue in draft.get("issues", []) or []:
        value = issue.get("value") or {}
        if issue.get("type") == "anchor_span_mismatch":
            items.append(
                "anchor span mismatch: "
                f"dimension={value.get('dimension_total_mm')}mm, "
                f"anchor_span={value.get('anchor_span_mm')}mm, "
                f"residual={value.get('residual_mm')}mm"
            )
        else:
            items.append(f"{issue.get('type')}: {issue.get('message')}")
    return items


def make_item(draft: dict[str, Any]) -> dict[str, Any]:
    status = review_status(draft)
    needs_confirmation = status != "accepted_candidate"
    return {
        "id": f"CONFIRM-{draft.get('id')}",
        "dimension_chain_id": draft.get("id"),
        "axis": draft.get("axis"),
        "datum_role": draft.get("datum_role"),
        "status": status,
        "needs_confirmation": needs_confirmation,
        "dimension_total_mm": draft.get("dimension_total_mm"),
        "start_ref": draft.get("start_ref"),
        "end_ref": draft.get("end_ref"),
        "anchor_span_mm": draft.get("anchor_span_mm"),
        "residual_mm": draft.get("residual_mm"),
        "referenced_object_ids": draft.get("referenced_object_ids") or [],
        "confidence": draft.get("confidence"),
        "issue_summary": issue_summary(draft),
        "confirmation_question": confirmation_question(draft, status),
        "allowed_answers": allowed_answers(status),
    }


def confirmation_question(draft: dict[str, Any], status: str) -> str:
    chain_id = draft.get("id")
    if status == "accepted_candidate":
        return f"请确认 {chain_id} 是否可以作为主基准或兼容基准保留。"
    return (
        f"请确认 {chain_id} 是全局尺寸、局部尺寸，还是抽取/OCR 错误；"
        "确认前不能进入 L3 稳妥深化。"
    )


def allowed_answers(status: str) -> list[str]:
    if status == "accepted_candidate":
        return ["accept", "reject"]
    return ["full_extent_dimension", "local_dimension", "ocr_or_reading_error", "needs_site_measurement"]


def build_checklist(anchor_report: dict[str, Any], title: str) -> dict[str, Any]:
    items = [make_item(draft) for draft in anchor_report.get("anchor_drafts", []) or []]
    blockers = [item for item in items if item["needs_confirmation"]]
    return {
        "schema_version": "dimension_anchor_confirmation_checklist_v1",
        "title": title,
        "source_anchor_gate": anchor_report.get("anchor_gate"),
        "source_anchor_level": anchor_report.get("anchor_level"),
        "confirmation_gate": "needs_confirmation" if blockers else "ready",
        "can_quick_concept": bool(anchor_report.get("can_quick_concept")),
        "can_stable_deepening": False if blockers else bool(anchor_report.get("can_stable_deepening")),
        "summary": {
            "item_count": len(items),
            "accepted_candidate_count": sum(1 for item in items if item["status"] == "accepted_candidate"),
            "needs_confirmation_count": len(blockers),
        },
        "items": items,
    }


def render_markdown(checklist: dict[str, Any]) -> str:
    lines = [
        f"# {checklist.get('title')}",
        "",
        "## 当前结论",
        "",
        f"- confirmation_gate: `{checklist.get('confirmation_gate')}`",
        f"- can_quick_concept: `{str(checklist.get('can_quick_concept')).lower()}`",
        f"- can_stable_deepening: `{str(checklist.get('can_stable_deepening')).lower()}`",
        f"- 待确认项：{checklist.get('summary', {}).get('needs_confirmation_count')}",
        "",
        "## 确认清单",
        "",
    ]
    for item in checklist.get("items", []) or []:
        lines.extend(render_item(item))
    return "\n".join(lines).rstrip() + "\n"


def render_item(item: dict[str, Any]) -> list[str]:
    lines = [
        f"### {item.get('dimension_chain_id')}",
        "",
        f"- 状态：`{item.get('status')}`",
        f"- 方向：`{item.get('axis')}`",
        f"- 角色：`{item.get('datum_role')}`",
        f"- 尺寸总长：`{item.get('dimension_total_mm')}mm`",
        f"- 候选跨度：`{item.get('anchor_span_mm')}mm`",
        f"- residual：`{item.get('residual_mm')}mm`",
        f"- 起点：`{item.get('start_ref')}`",
        f"- 终点：`{item.get('end_ref')}`",
        f"- 关联对象：`{', '.join(item.get('referenced_object_ids') or [])}`",
        f"- 需要确认：{item.get('confirmation_question')}",
        f"- 可选判断：`{', '.join(item.get('allowed_answers') or [])}`",
    ]
    issues = item.get("issue_summary") or []
    if issues:
        lines.append("- 问题：")
        for issue in issues:
            lines.append(f"  - {issue}")
    lines.append("")
    return lines


def summarize(checklist: dict[str, Any]) -> list[str]:
    summary = checklist.get("summary", {})
    return [
        f"confirmation_gate={checklist.get('confirmation_gate')}",
        f"items={summary.get('item_count')} accepted={summary.get('accepted_candidate_count')} needs_confirmation={summary.get('needs_confirmation_count')}",
        f"can_quick_concept={str(checklist.get('can_quick_concept')).lower()} can_stable_deepening={str(checklist.get('can_stable_deepening')).lower()}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("anchor_report", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("output_md", type=Path)
    parser.add_argument("--title", default="Dimension Anchor Confirmation Checklist")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    checklist = build_checklist(load_json(args.anchor_report), args.title)
    write_json(args.output_json, checklist)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(checklist), encoding="utf-8")
    if not args.json_only:
        for line in summarize(checklist):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
