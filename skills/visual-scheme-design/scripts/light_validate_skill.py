#!/usr/bin/env python3
"""Dependency-free validation for this skill.

This intentionally avoids PyYAML because the bundled Codex Python runtime in
this Windows environment may not include it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_REFERENCES = [
    "references/home-design-workflow.md",
    "references/home-object-model.md",
    "references/home-geometry-validation.md",
    "references/residential-plan-redraw.md",
    "references/scene-and-space-workflows.md",
    "references/runtime-state.md",
]

REQUIRED_TEXT = [
    "Residential Object Data Gate",
    "## Live Scene And Set-Design Rules",
    "references/home-design-workflow.md",
    "State Contract",
]


def parse_simple_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
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


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md not found"]

    text = skill_md.read_text(encoding="utf-8-sig")
    try:
        frontmatter = parse_simple_frontmatter(text)
    except ValueError as exc:
        errors.append(str(exc))
        frontmatter = {}

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if name != "visual-scheme-design":
        errors.append(f"Unexpected skill name: {name!r}")
    if not description:
        errors.append("Missing description")
    if len(description) > 1024:
        errors.append("Description is longer than 1024 characters")

    for needle in REQUIRED_TEXT:
        if needle not in text:
            errors.append(f"Missing required text in SKILL.md: {needle}")

    for rel in REQUIRED_REFERENCES:
        if not (skill_dir / rel).exists():
            errors.append(f"Missing required reference: {rel}")

    return errors


def main() -> int:
    skill_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(skill_dir)
    if errors:
        print("Skill light validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Skill light validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



