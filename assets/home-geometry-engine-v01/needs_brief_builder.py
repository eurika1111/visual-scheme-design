#!/usr/bin/env python3
"""Build a structured residential needs brief from a lightweight client response.

The input is intentionally tolerant. Answers may be precise, vague, or still
undecided. The output separates hard constraints, preferences, exploration
items, and follow-up questions so early scheme options can stay controlled
without forcing the client to over-decide too soon.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

FUZZY_VALUES = {
    "unsure",
    "not_sure",
    "open_to_suggestions",
    "depends",
    "maybe",
    "to_be_discussed",
    "no_clear_preference",
}

LOW_RISK_DEMOLITION = {"none", "avoid", "light_only", "minor"}
MEDIUM_RISK_DEMOLITION = {"partial", "moderate", "some"}
HIGH_RISK_DEMOLITION = {"major", "bold", "open_to_big_change"}


QUESTION_LABELS = {
    "household": "常住人口与家庭结构",
    "must_keep_rooms": "必须保留的房间",
    "demolition_attitude": "拆改接受度",
    "kitchen_attitude": "厨房开放程度",
    "island_attitude": "岛台态度",
    "storage_priority": "收纳优先级",
    "life_focus": "生活重点",
    "style_preference": "风格倾向",
    "budget_risk": "预算与施工风险",
    "no_change_areas": "不可动区域",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def answer_payload(data: dict[str, Any]) -> dict[str, Any]:
    answers = data.get("answers")
    return answers if isinstance(answers, dict) else data


def choice_of(raw: Any) -> Any:
    if isinstance(raw, dict):
        return raw.get("choice", raw.get("value"))
    return raw


def notes_of(raw: Any) -> str:
    if isinstance(raw, dict):
        return str(raw.get("notes") or raw.get("note") or "").strip()
    return ""


def confidence_of(raw: Any) -> str:
    if isinstance(raw, dict):
        return str(raw.get("confidence") or "normal")
    return "normal"


def value_tokens(value: Any) -> set[str]:
    tokens: set[str] = set()
    for item in as_list(value):
        if isinstance(item, str):
            tokens.add(item)
        elif isinstance(item, dict):
            choice = choice_of(item)
            tokens.update(str(v) for v in as_list(choice))
    return tokens


def add_if(target: list[dict[str, Any]], item: dict[str, Any]) -> None:
    if item not in target:
        target.append(item)


def classify_unknowns(answers: dict[str, Any]) -> list[dict[str, Any]]:
    unknowns: list[dict[str, Any]] = []
    for key, label in QUESTION_LABELS.items():
        raw = answers.get(key)
        tokens = value_tokens(choice_of(raw))
        note = notes_of(raw)
        confidence = confidence_of(raw)
        if not raw or tokens & FUZZY_VALUES or confidence == "low":
            unknowns.append(
                {
                    "field": key,
                    "label": label,
                    "status": "needs_follow_up",
                    "note": note or "客户暂未明确，可先作为探索项处理。",
                }
            )
    return unknowns


def build_brief(data: dict[str, Any]) -> dict[str, Any]:
    answers = answer_payload(data)
    hard_constraints: list[dict[str, Any]] = []
    preferences: list[dict[str, Any]] = []
    exploration_items: list[dict[str, Any]] = []

    household = answers.get("household", {})
    if household:
        preferences.append({"type": "household", "value": household, "source": "client_answer"})

    must_keep_rooms = value_tokens(choice_of(answers.get("must_keep_rooms")))
    for room in sorted(must_keep_rooms - FUZZY_VALUES):
        add_if(hard_constraints, {"type": "must_keep_room", "value": room, "source": "client_answer"})

    no_change = value_tokens(choice_of(answers.get("no_change_areas")))
    for area in sorted(no_change - FUZZY_VALUES):
        add_if(hard_constraints, {"type": "no_change_area", "value": area, "source": "client_answer"})

    demolition = value_tokens(choice_of(answers.get("demolition_attitude")))
    kitchen = value_tokens(choice_of(answers.get("kitchen_attitude")))
    island = value_tokens(choice_of(answers.get("island_attitude")))
    storage = value_tokens(choice_of(answers.get("storage_priority")))
    life_focus = value_tokens(choice_of(answers.get("life_focus")))
    style = value_tokens(choice_of(answers.get("style_preference")))
    budget = value_tokens(choice_of(answers.get("budget_risk")))

    if demolition & LOW_RISK_DEMOLITION:
        hard_constraints.append({"type": "demolition_limit", "value": "avoid_major_demolition", "source": "client_answer"})
    elif demolition & MEDIUM_RISK_DEMOLITION:
        preferences.append({"type": "demolition", "value": "partial_changes_allowed", "source": "client_answer"})
    elif demolition & HIGH_RISK_DEMOLITION:
        exploration_items.append({"type": "demolition", "value": "bold_layout_change_candidate", "source": "client_answer"})

    if "closed" in kitchen:
        hard_constraints.append({"type": "kitchen", "value": "keep_closed_kitchen", "source": "client_answer"})
    elif kitchen & {"semi_open", "open", "more_open"}:
        preferences.append({"type": "kitchen", "value": "improve_kitchen_openness", "source": "client_answer"})
    elif kitchen & FUZZY_VALUES:
        exploration_items.append({"type": "kitchen", "value": "test_open_vs_closed", "source": "client_answer"})

    if "avoid" in island or "no" in island:
        hard_constraints.append({"type": "island", "value": "avoid_island", "source": "client_answer"})
    elif island & {"preferred", "want", "nice_to_have"}:
        preferences.append({"type": "island", "value": "include_if_fits", "source": "client_answer"})
    elif island & FUZZY_VALUES or "depends" in island:
        exploration_items.append({"type": "island", "value": "test_island_feasibility", "source": "client_answer"})

    if storage & {"high", "very_high", "strong"}:
        preferences.append({"type": "storage", "value": "strong_storage", "source": "client_answer"})
    elif storage & FUZZY_VALUES:
        exploration_items.append({"type": "storage", "value": "compare_storage_levels", "source": "client_answer"})

    for focus in sorted(life_focus - FUZZY_VALUES):
        preferences.append({"type": "life_focus", "value": focus, "source": "client_answer"})
    for style_item in sorted(style - FUZZY_VALUES):
        preferences.append({"type": "style", "value": style_item, "source": "client_answer"})

    risk_profile = {
        "demolition": "low",
        "open_kitchen": "unclear",
        "island": "unclear",
        "budget": "normal",
    }
    if demolition & MEDIUM_RISK_DEMOLITION:
        risk_profile["demolition"] = "medium"
    if demolition & HIGH_RISK_DEMOLITION:
        risk_profile["demolition"] = "high"
    if kitchen & {"open", "semi_open", "more_open"}:
        risk_profile["open_kitchen"] = "accepted"
    if "closed" in kitchen:
        risk_profile["open_kitchen"] = "avoid"
    if island & {"preferred", "want", "nice_to_have"}:
        risk_profile["island"] = "preferred"
    if island & {"avoid", "no"}:
        risk_profile["island"] = "avoid"
    if budget & {"low", "controlled"}:
        risk_profile["budget"] = "controlled"
    if budget & {"high", "effect_first", "flexible"}:
        risk_profile["budget"] = "flexible"

    unknowns = classify_unknowns(answers)
    comparison_variables = []
    seen_variables: set[str] = set()
    for item in [*preferences, *exploration_items]:
        variable_id = str(item.get("type") or "unknown")
        if variable_id in seen_variables:
            continue
        seen_variables.add(variable_id)
        comparison_variables.append({
            "id": variable_id,
            "source": item.get("source"),
            "status": "compare_or_resolve_before_option_approval",
        })

    return {
        "schema_version": "needs_brief_v1",
        "project_id": data.get("project_id", "unknown_project"),
        "intake_status": "ready_with_unknowns" if unknowns else "ready",
        "household": household,
        "hard_constraints": hard_constraints,
        "preferences": preferences,
        "exploration_items": exploration_items,
        "unknowns": unknowns,
        "risk_profile": risk_profile,
        "option_direction_status": "pending_user_confirmation",
        "comparison_variables": comparison_variables,
        "source_answers": answers,
    }


def bullet(items: list[Any]) -> str:
    if not items:
        return "- none\n"
    lines = []
    for item in items:
        if isinstance(item, dict):
            value = item.get("value", item.get("note", item))
            label = item.get("type") or item.get("label") or item.get("field") or "item"
            lines.append(f"- `{label}`: {value}")
        else:
            lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def build_markdown(brief: dict[str, Any]) -> str:
    return f"""# Needs Brief - {brief.get('project_id', 'unknown_project')}

## Intake Status

- Status: `{brief.get('intake_status')}`
- Demolition risk: `{brief.get('risk_profile', {}).get('demolition')}`
- Open kitchen: `{brief.get('risk_profile', {}).get('open_kitchen')}`
- Island: `{brief.get('risk_profile', {}).get('island')}`
- Budget: `{brief.get('risk_profile', {}).get('budget')}`

## Hard Constraints

{bullet(brief.get('hard_constraints', []))}
## Preferences

{bullet(brief.get('preferences', []))}
## Exploration Items

{bullet(brief.get('exploration_items', []))}
## Needs Follow-Up

{bullet(brief.get('unknowns', []))}
## Comparison Variables

{bullet(brief.get('comparison_variables', []))}

Option directions remain pending user confirmation. Do not assign low/medium/high risk archetypes to option letters.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("response", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    data = load_json(args.response)
    brief = build_brief(data)
    write_json(args.output_json, brief)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(build_markdown(brief), encoding="utf-8")
    print(f"needs_brief_json={args.output_json}")
    print(f"needs_brief_md={args.output_md}")
    print(f"intake_status={brief['intake_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
