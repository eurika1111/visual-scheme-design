#!/usr/bin/env python3
"""Project-level behavioral contract checks for visual-scheme-design."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "visual-scheme-design"


def read(relative: str) -> str:
    return (SKILL / relative).read_text(encoding="utf-8-sig")


SCENARIOS = {
    "first_use_stops_at_confirmation": (
        "references/home-design-workflow.md",
        [r"## Interaction Checkpoints", r"`welcome`", r"Do not cross two checkpoints", r"ask permission for the next single step"],
    ),
    "unlocked_base_blocks_residential_options": (
        "SKILL.md",
        [r"before the exact base is confirmed, locked, and at least `L2`"],
    ),
    "options_share_one_immutable_base": (
        "SKILL.md",
        [r"Bind every residential option to one locked `base_id`", r"option-specific object operations"],
    ),
    "provider_failure_is_recoverable": (
        "references/runtime-state.md",
        [r"partial_untrusted", r"do not advance the checkpoint", r"Increment `attempt`"],
    ),
    "cross_option_feedback_isolated": (
        "references/home-object-model.md",
        [r"target_scheme", r"to_scheme", r"create a new option version"],
    ),
    "viewer_frame_excludes_execution_clutter": (
        "SKILL.md",
        [r"viewer-facing frames free of cameras, lights, cables, monitor screens, UI"],
    ),
    "outline_only_request_creates_no_assets": (
        "SKILL.md",
        [r"asks only for structure, a plan, or an outline", r"do not generate images, videos, boards, or other extra assets"],
    ),
    "image_generation_preserves_geometry_authority": (
        "references/image-generation-control.md",
        [r"generated image cannot correct, unlock, or become the parent", r"camera-controlled proxy", r"generated_pending_review"],
    ),
    "web_knowledge_supports_transferable_case_logic": (
        "references/professional-knowledge-sourcing.md",
        [r"Case Strategy Extraction", r"why_it_works", r"failure_modes", r"visual_proof"],
    ),
    "computational_reasoning_prioritizes_visible_feasibility": (
        "references/residential-computational-design.md",
        [r"Feasibility First", r"Furniture Use Logic", r"Do not force a weighted total"],
    ),
    "scheme_logic_must_precede_visual_acceptance": (
        "references/scheme-logic-and-visual-plausibility.md",
        [r"Scheme Logic Manifest", r"Visual Plausibility Blockers", r"Never repair a logic failure with decorative polish alone"],
    ),
    "visual_plausibility_rejects_obvious_ai_errors": (
        "references/scheme-logic-and-visual-plausibility.md",
        [r"fake openings", r"ghost spaces", r"repeated furniture", r"multi_view_consistency"],
    ),
    "approved_option_count_overrides_fixed_abc": (
        "SKILL.md",
        [r"user-approved option count", r"three options are a comparison default, not a fixed requirement"],
    ),
    "core_proof_objects_are_validated_before_concept": (
        "references/home-geometry-validation.md",
        [r"Core-proof exception", r"real footprint", r"one named access route"],
    ),
    "accelerated_mode_keeps_critical_approvals_separate": (
        "references/home-design-workflow.md",
        [r"accelerated mode", r"Base lock and image-generation approval remain separate", r"fall back to staged mode"],
    ),
    "vertical_context_is_conditional_not_global": (
        "references/home-geometry-validation.md",
        [r"Conditional Vertical Context", r"top-down quick concept", r"perspective limitation"],
    ),
    "support_and_concurrent_use_are_project_specific": (
        "references/residential-design-knowledge.md",
        [r"support_function_inventory", r"do not turn the inventory into a universal checklist", r"concurrent use"],
    ),
    "visual_review_requires_actual_evidence": (
        "references/scheme-logic-and-visual-plausibility.md",
        [r"image_reviewed", r"structured evidence", r"self-authored list of `pass` values is not evidence"],
    ),
    "visual_evidence_is_bound_to_files_and_hashes": (
        "references/image-generation-control.md",
        [r"evidence artifact registry", r"files exist", r"SHA-256 hashes match", r"resolve to one registered artifact"],
    ),
    "external_geometry_tools_have_honest_degradation": (
        "references/geometry-tool-adapter.md",
        [r"Discovery Order", r"Required Contracts", r"Manual Degradation", r"Do not label a base or scheme tool-validated"],
    ),
    "conflicting_base_blocks_text_directions": (
        "SKILL.md",
        [r"text-only option directions as scheme work", r"current authoritative and accepted artifacts", r"disagrees on the active `base_id`", r"do not provide tentative directions"],
    ),
    "historical_and_demo_files_do_not_create_false_conflicts": (
        "references/home-design-workflow.md",
        [r"Classify demo, historical, rejected, superseded", r"cannot create a conflict in the current authoritative set"],
    ),
    "legacy_risk_tier_option_strategy_is_stale": (
        "references/home-design-workflow.md",
        [r"legacy option plans", r"fixed low/medium/high risk archetypes", r"stale strategy evidence"],
    ),
}


def main() -> int:
    failures: list[str] = []
    for scenario, (relative, patterns) in SCENARIOS.items():
        body = read(relative)
        missing = [pattern for pattern in patterns if not re.search(pattern, body, re.I | re.S)]
        if missing:
            failures.append(f"{scenario}: missing {missing} in {relative}")
        else:
            print(f"PASS {scenario}")

    if failures:
        print("Behavior contract checks failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Behavior contract checks passed: {len(SCENARIOS)} scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
