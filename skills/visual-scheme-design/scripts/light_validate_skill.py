#!/usr/bin/env python3
"""Dependency-free structural and contract validation for this skill."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path


REQUIRED_REFERENCES = [
    "references/home-design-workflow.md",
    "references/residential-design-knowledge.md",
    "references/scheme-logic-and-visual-plausibility.md",
    "references/professional-knowledge-sourcing.md",
    "references/residential-computational-design.md",
    "references/geometry-tool-adapter.md",
    "references/home-object-model.md",
    "references/home-geometry-validation.md",
    "references/residential-plan-redraw.md",
    "references/scene-and-space-workflows.md",
    "references/repair-and-iteration.md",
    "references/client-board-output.md",
    "references/prompt-templates.md",
    "references/image-generation-control.md",
    "references/ue-visualization-workflow.md",
    "references/runtime-state.md",
    "references/usage-guide.md",
]

REQUIRED_CONTRACTS = {
    "SKILL.md": [
        "## Non-Negotiable Contracts",
        "## Interaction Contract",
        "## Residential Object Data Gate",
        "## Failure And Recovery Rule",
        "Do not use generated images as geometry or version authority",
        "do not generate images, videos, boards, or other extra assets",
    ],
    "references/home-design-workflow.md": [
        "## Readiness Levels",
        "On provider failure:",
        "do not create a generated option, accepted version, or completed checkpoint",
    ],
    "references/residential-design-knowledge.md": [
        "## Evidence Levels",
        "## Adjacency And Conflict Mapping",
        "## Evaluation Rubric",
    ],
    "references/professional-knowledge-sourcing.md": [
        "## Case Strategy Extraction",
        "failure_modes",
        "## Safety Boundary",
    ],
    "references/residential-computational-design.md": [
        "## Feasibility First",
        "## Furniture Use Logic",
        "## Option Distinctness",
    ],
    "references/scheme-logic-and-visual-plausibility.md": [
        "## Scheme Logic Manifest",
        "## Visual Plausibility Blockers",
        "## Review Decisions",
        "Never repair a logic failure with decorative polish alone",
        '"image_reviewed": true',
        '"review_scope": "scheme_package"',
    ],
    "references/geometry-tool-adapter.md": [
        "## Discovery Order",
        "## Required Contracts",
        "## Manual Degradation",
        "Do not label a base or scheme tool-validated",
    ],
    "references/image-generation-control.md": [
        "## Authority Boundary",
        "## Handoff Contract",
        "## Drift Acceptance",
    ],
    "references/runtime-state.md": [
        '"prompt_package_hash"',
        "partial_untrusted",
        "do not advance the checkpoint",
    ],
    "references/repair-and-iteration.md": [
        "## Provider Failure Recovery",
        "Treat provider failures as delivery failures, not design revisions",
    ],
    "references/prompt-templates.md": [
        "## Contents",
        "## Provider Failure Recovery",
        "valid_generated_version_created: false",
    ],
}


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_text(path: Path) -> str:
    return normalize(path.read_text(encoding="utf-8-sig"))


def parse_simple_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        raise ValueError("Invalid or missing YAML frontmatter delimiters")

    data: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Unsupported frontmatter line: {raw_line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def parse_interface_value(text: str, key: str) -> str | None:
    match = re.search(rf'^\s{{2}}{re.escape(key)}:\s*"([^"]*)"\s*$', text, re.M)
    return match.group(1) if match else None


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md not found"]

    text = read_text(skill_md)
    try:
        frontmatter = parse_simple_frontmatter(text)
    except ValueError as exc:
        errors.append(str(exc))
        frontmatter = {}

    if set(frontmatter) != {"name", "description"}:
        errors.append("Frontmatter must contain only name and description")
    if frontmatter.get("name") != skill_dir.name:
        errors.append(
            f"Skill name {frontmatter.get('name')!r} does not match folder {skill_dir.name!r}"
        )
    description = frontmatter.get("description", "")
    if not description:
        errors.append("Missing description")
    if len(description) > 1024:
        errors.append("Description is longer than 1024 characters")
    if len(text.splitlines()) >= 500:
        errors.append("SKILL.md must stay below 500 lines")

    for rel in REQUIRED_REFERENCES:
        path = skill_dir / rel
        if not path.exists():
            errors.append(f"Missing required reference: {rel}")
        if rel not in text:
            errors.append(f"SKILL.md does not route directly to: {rel}")

    linked_refs = set(re.findall(r"references/[A-Za-z0-9._/-]+\.md", text))
    for rel in sorted(linked_refs):
        if not (skill_dir / rel).exists():
            errors.append(f"Broken reference route in SKILL.md: {rel}")

    for rel, needles in REQUIRED_CONTRACTS.items():
        path = skill_dir / rel
        if not path.exists():
            continue
        body = read_text(path)
        for needle in needles:
            if needle not in body:
                errors.append(f"Missing contract in {rel}: {needle}")

    readiness_owners: list[str] = []
    for path in [skill_md, *sorted((skill_dir / "references").glob("*.md"))]:
        if re.search(r"^## Readiness Levels\s*$", read_text(path), re.M):
            readiness_owners.append(path.relative_to(skill_dir).as_posix())
    if readiness_owners != ["references/home-design-workflow.md"]:
        errors.append(
            "Readiness level definitions must exist only in "
            f"references/home-design-workflow.md; found {readiness_owners}"
        )

    interface_path = skill_dir / "agents" / "openai.yaml"
    if not interface_path.exists():
        errors.append("Missing agents/openai.yaml")
    else:
        interface_text = read_text(interface_path)
        for key in ("display_name", "short_description", "default_prompt"):
            if not parse_interface_value(interface_text, key):
                errors.append(f"Missing interface field: {key}")
        default_prompt = parse_interface_value(interface_text, "default_prompt") or ""
        short_description = parse_interface_value(interface_text, "short_description") or ""
        if short_description and not 25 <= len(short_description) <= 64:
            errors.append("short_description must be 25-64 characters")
        if "$visual-scheme-design" not in default_prompt:
            errors.append("default_prompt must invoke $visual-scheme-design")

    plausibility_script = skill_dir / "scripts" / "evaluate_visual_plausibility.py"
    if not plausibility_script.exists():
        errors.append("Missing scripts/evaluate_visual_plausibility.py")
    else:
        review_doc = read_text(skill_dir / "references" / "scheme-logic-and-visual-plausibility.md")
        documented = re.search(
            r"Use this shape with `scripts/evaluate_visual_plausibility\.py`:\s*```json\s*(\{.*?\})\s*```",
            review_doc,
            re.S,
        )
        if not documented:
            errors.append("Documented visual plausibility example not found")
        else:
            try:
                example = json.loads(documented.group(1))
                spec = importlib.util.spec_from_file_location("visual_plausibility_gate", plausibility_script)
                if spec is None or spec.loader is None:
                    raise RuntimeError("unable to load evaluator module")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                with tempfile.TemporaryDirectory() as temp:
                    evidence_root = Path(temp)
                    materialized_hashes: dict[str, str] = {}
                    for artifact in example.get("evidence_artifacts", []):
                        relative_path = str(artifact.get("path") or "missing")
                        artifact_path = evidence_root / relative_path
                        artifact_path.parent.mkdir(parents=True, exist_ok=True)
                        if relative_path not in materialized_hashes:
                            payload = f"evidence-file:{relative_path}\n".encode("utf-8")
                            artifact_path.write_bytes(payload)
                            materialized_hashes[relative_path] = "sha256:" + hashlib.sha256(payload).hexdigest()
                        artifact["sha256"] = materialized_hashes[relative_path]
                    result, exit_code = module.evaluate(example, evidence_root)
                    if exit_code != 0 or result.get("decision") != "displayable":
                        errors.append(
                            "Materialized documented visual plausibility example must evaluate to displayable; "
                            f"got {result.get('decision')} errors={result.get('errors')}"
                        )
                    missing_evidence = copy.deepcopy(example)
                    next(
                        item for item in missing_evidence["blocking_checks"] if item.get("id") == "ai_artifacts"
                    )["evidence"] = []
                    negative, negative_code = module.evaluate(missing_evidence, evidence_root)
                    if negative_code != 2 or negative.get("decision") != "rejected":
                        errors.append("Evaluator smoke test must reject a passing check with missing evidence")
                    tampered = copy.deepcopy(example)
                    tampered["evidence_artifacts"][0]["sha256"] = "sha256:" + "0" * 64
                    tampered_result, tampered_code = module.evaluate(tampered, evidence_root)
                    if tampered_code != 2 or tampered_result.get("decision") != "rejected":
                        errors.append("Evaluator smoke test must reject a tampered evidence hash")
            except (json.JSONDecodeError, KeyError, StopIteration, RuntimeError) as exc:
                errors.append(f"Visual plausibility smoke test failed: {exc}")

    return errors


def main() -> int:
    skill_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(skill_dir.resolve())
    if errors:
        print("Skill light validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Skill light validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
