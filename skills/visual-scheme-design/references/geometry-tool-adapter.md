# Geometry Tool Adapter

Use this reference before claiming that a residential base, option, lock, or generated image passed a deterministic geometry workflow. The skill is globally installed, while geometry engines are project resources; make that dependency explicit.

## Discovery Order

1. Use an explicit tool path recorded in project state or supplied by the user.
2. Check the current project for `assets/home-geometry-engine-v01` or a compatible `geometry_toolchain.json` manifest.
3. Use a project-local adapter only after confirming its input/output contracts below.
4. Do not search unrelated workspaces, copy an engine silently, or assume the current machine has the demo engine.

Record the resolved engine root, tool version or content hash, validation method, and output paths in the project state or validation report.

## Required Contracts

| capability | compatible tool example | minimum result |
|---|---|---|
| source import | `staged_topology_importer.py` | candidate object package plus preservation report |
| source/base validation | `validate_source_extraction.py`, `geometry_validator.py` | errors, warnings, readiness evidence, and affected object IDs |
| deterministic review | `simple_renderer.py` | same-coordinate review view derived from object data |
| base lock | `base_lock_manifest.py` | base ID, model hash, canvas, coordinate frame, bounds, anchors, confirmation record |
| option placement | `scheme_placement_resolver.py` | isolated option version, resolved object geometry, and placement report |
| option comparison | `scheme_review_package_builder.py` | same-scale review package tied to one locked base |
| image handoff | `visual_generation_handoff_builder.py` | structure and logic references, hashes, blockers, and closed/open generation gate |
| output review | `concept_output_review.py` | canvas comparison and visual review aids without modifying the base |

Before invoking a compatible tool, inspect its `--help` or parser and confirm required files. Do not infer a CLI from the filename alone.

## Failure Behavior

- A missing, incompatible, or failed tool does not become a passing validation result.
- Preserve the current base, option version, and checkpoint.
- Report which deterministic claim is unavailable and whether a manual review can answer the immediate question.
- Do not label a base or scheme tool-validated when only a qualitative inspection occurred.
- Do not create a lock manifest unless the base identity, content hash, canvas, and confirmation evidence can be recorded.

## Manual Degradation

When no compatible engine exists, use the workflow's normal evidence requirements and record `validation_method: manual_visual_review` with explicit checked facts, unknowns, and reviewer. Manual review may support a workflow readiness decision only when the required base facts are actually visible and the user confirms the candidate base. Unknown structure, room identity, opening, fixed-service, or scale relationships remain blockers; do not invent precision.

For a quick visual exploration that the workflow permits, label approximate placement and unverified vertical conditions honestly. For selected-scheme deepening, exact placement, controlled operations, and required fixed-service checks still need deterministic data or qualified project verification.

## Project Adapter Rule

Keep project engines in the project, not duplicated inside this skill. If the same discovery and invocation code is repeatedly needed across projects, add a small stable wrapper under `scripts/`; keep the full geometry engine external and versioned with its project or dedicated package.
