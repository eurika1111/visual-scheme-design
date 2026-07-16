# Scheme Logic And Visual Plausibility

Use this reference before generating or accepting a residential visual scheme. The target is not construction-level numerical proof. The target is a visually credible proposal whose spatial logic can be explained, seen, and reviewed without obvious errors.

## Contents

- Product objective
- Scheme logic manifest
- Logic gate
- Visual plausibility blockers
- Quality review
- Review decisions
- Repair routing

## Product Objective

Optimize for this sequence:

```text
preserve the accepted space
-> solve one named user problem
-> make daily use understandable
-> express the logic visibly
-> reject obvious contradictions and AI artifacts
```

Use dimensions and geometry as guardrails where they prevent visible or functional mistakes. Do not imply that more measurements, parameters, or scores automatically make a visual proposal more reasonable.

## Scheme Logic Manifest

Create one manifest for every option before image generation:

```yaml
schema_version: scheme_logic_manifest_v1
base_id: base_v1
option_id: 方案 A
option_version: scheme_A_v1
primary_problem: the one main problem this option addresses
core_move: the main spatial decision
linked_obligations:
  - one to three related duties that must not be sacrificed
user_routines:
  - routine this decision supports
functional_relationships:
  - functions that should be near, connected, separated, or protected
circulation_story:
  - how entry, daily movement, doors, and major destinations work
furniture_logic:
  - orientation, use side, seating, viewing, storage, and access logic
core_proof_objects:
  - furniture, island, cabinet, door, or partition whose fit proves the core move
support_function_inventory:
  - project-specific laundry, drying, cleaning, food, waste, linen, entry, child, elder, pet, or maintenance need
concurrent_use_scenarios:
  - one to three relevant simultaneous activities in a core space
environmental_comfort:
  - affected daylight, glare, ventilation, exhaust, privacy, noise, or odor relationship
fixed_elements:
  - base objects and relationships that must remain
tradeoff: what this option gives up or makes less convenient
visual_proof:
  - what the final view must visibly show for the logic to be believable
blocking_unknowns: []
```

Keep this compact. It is a design argument and review contract, not a second object model.

Only include the four conditional lists when they affect this project. Keep one `primary_problem`, but use `linked_obligations` so a whole-home scheme does not erase related family duties. If a `core_proof_object` carries the option's main promise, validate its real footprint, use side, opening envelope, and one named access route before concept generation. In the visual review record, its `evidence` value must name a verified `validation` artifact from `evidence_artifacts`.

## Logic Gate

Before generation, confirm:

- the primary problem comes from the needs brief
- the core move addresses that problem rather than creating novelty for its own sake
- required rooms and daily functions remain understandable
- main access and furniture use do not contain an obvious contradiction
- core proof objects have passed their minimum pre-generation fit check
- project-specific support functions, concurrent use, and environmental comfort effects are addressed when relevant
- fixed elements and authorized changes match the option operations
- the tradeoff is stated honestly
- the requested view can show the listed `visual_proof`
- no `blocking_unknowns` remain unless the user explicitly accepts an exploratory result

If the logic cannot be explained in a few sentences, do not hide the weakness with style prompts or extra imagery.

## Visual Plausibility Blockers

Review these blocker IDs after generation:

- `base_fidelity`: major outline, room, opening, fixed-zone, or view relationship drifted
- `functional_completeness`: a required living, sleeping, kitchen, bathroom, access, or project-specific function disappeared
- `access_logic`: a door, route, balcony, work zone, or main destination is visibly blocked or contradictory
- `furniture_usability`: furniture crosses structure, floats, duplicates, faces the wrong use relationship, or lacks a believable use side
- `scheme_logic_alignment`: the image does not show the manifest's core move or contradicts its fixed elements and visual proof
- `ai_artifacts`: fake openings, broken walls, ghost spaces, repeated furniture, impossible joins, unreadable pseudo-diagrams, or other obvious generation errors appear
- `multi_view_consistency`: when multiple views are claimed as one scheme, persistent openings, major furniture, orientation, or spatial relationships conflict

Any confirmed blocker prevents delivery as a valid scheme. Use `unknown` when the supplied evidence cannot decide; do not convert uncertainty into a pass. In a scheme-package review, use `not_applicable` only for `multi_view_consistency` when one view is being reviewed.

For a single-view review, another blocker may be `not_applicable` only when `covered_by` names the scheme-package view or deterministic file that carries the evidence. A scheme-package review cannot skip those blockers.

## Quality Review

After blockers pass, rate these as `weak`, `acceptable`, or `strong`:

- `structural_credibility`: the space reads as one coherent buildable environment
- `routine_readability`: the user can understand how daily activities happen
- `circulation_intuition`: primary movement is visually legible without technical explanation
- `furniture_logic`: furniture forms believable use relationships
- `scale_plausibility`: proportions feel credible even when exact measurements are not claimed
- `strategy_visibility`: the option's main design move is easy to see
- `option_distinctness`: the view remains recognizably different from the other approved directions
- `visual_coherence`: style, material, lighting, and spatial intent support one another

Do not total these into a pseudo-precise score. A weak quality item requires a targeted repair; it cannot override or compensate for a blocker.

Use `review_scope: view` for one image and require only structural credibility, furniture logic, scale plausibility, strategy visibility, and visual coherence. It may return `view_passed`, which is not a delivery decision. Use `review_scope: scheme_package` for final delivery and review all eight quality items. `not_applicable` requires `covered_by`; do not use it to hide missing evidence.

## Review Record

Use this shape with `scripts/evaluate_visual_plausibility.py`:

```json
{
  "schema_version": "visual_plausibility_review_v1",
  "review_scope": "scheme_package",
  "base_id": "base_v1",
  "option_id": "方案 A",
  "view_ids": ["top"],
  "image_reviewed": true,
  "review_method": "deterministic_and_visual_review",
  "reviewed_at": "2026-07-15T10:00:00+08:00",
  "reviewer": "reviewer-id",
  "evidence_artifacts": [
    {"id": "overlay:top", "kind": "overlay", "path": "evidence/base_overlay.svg", "sha256": "sha256:7c34af8c8c00ca9ee4facbe6e0621d68813d0c0dde8e36284043f3c787abc9b8", "view_id": "top"},
    {"id": "anchors:main", "kind": "overlay", "path": "evidence/base_overlay.svg", "sha256": "sha256:7c34af8c8c00ca9ee4facbe6e0621d68813d0c0dde8e36284043f3c787abc9b8", "view_id": "top"},
    {"id": "validation:functions", "kind": "validation", "path": "evidence/validation.json", "sha256": "sha256:9921dbb9ff0133fae2d2f9604a0422ecad5c02957ce2b1614f046780cac2a994"},
    {"id": "view:top", "kind": "image", "path": "evidence/top_view.svg", "sha256": "sha256:4b7bd53e1a5d295839d8ee5b03e74568148dda57ccbb0ba7288e98f4e8b0a4d2", "view_id": "top"},
    {"id": "region:dining", "kind": "image", "path": "evidence/top_view.svg", "sha256": "sha256:4b7bd53e1a5d295839d8ee5b03e74568148dda57ccbb0ba7288e98f4e8b0a4d2", "view_id": "top"},
    {"id": "logic:visual_proof", "kind": "document", "path": "evidence/scheme_logic.json", "sha256": "sha256:948a10c23d69b172bc39fbcf73453c6fad344afc4569a7c4000d916f89b594a7"},
    {"id": "logic:user_routines", "kind": "document", "path": "evidence/scheme_logic.json", "sha256": "sha256:948a10c23d69b172bc39fbcf73453c6fad344afc4569a7c4000d916f89b594a7"},
    {"id": "comparison:approved-set", "kind": "comparison", "path": "evidence/comparison.json", "sha256": "sha256:4cbb37a67124324372ea06cfe341057837d849830fe2df6649b85117be551f63"}
  ],
  "scheme_logic_manifest": {
    "primary_problem": "improve shared dining",
    "core_move": "connect dining to kitchen while preserving access",
    "user_routines": ["daily shared meals"],
    "functional_relationships": ["kitchen preferred_near dining"],
    "circulation_story": ["entry and bedroom routes remain clear"],
    "furniture_logic": ["seats have believable use and passage sides"],
    "fixed_elements": ["base walls and openings"],
    "tradeoff": "less enclosed storage",
    "visual_proof": ["continuous kitchen-dining relationship"],
    "blocking_unknowns": []
  },
  "blocking_checks": [
    {"id": "base_fidelity", "status": "pass", "evidence": [{"kind": "overlay", "reference": "overlay:top", "finding": "locked outline and openings align"}]},
    {"id": "functional_completeness", "status": "pass", "evidence": [{"kind": "deterministic_validation", "reference": "validation:functions", "finding": "required functions remain present"}]},
    {"id": "access_logic", "status": "pass", "evidence": [{"kind": "full_image_review", "reference": "view:top", "finding": "named routes remain open"}]},
    {"id": "furniture_usability", "status": "pass", "evidence": [{"kind": "region_review", "reference": "region:dining", "finding": "seating retains use and passage sides"}]},
    {"id": "scheme_logic_alignment", "status": "pass", "evidence": [{"kind": "scheme_document", "reference": "logic:visual_proof", "finding": "core move is visible"}]},
    {"id": "ai_artifacts", "status": "pass", "evidence": [{"kind": "full_image_review", "reference": "view:top", "finding": "full image and high-risk joins contain no obvious artifacts"}]},
    {"id": "multi_view_consistency", "status": "not_applicable", "covered_by": "single-view package"}
  ],
  "quality_checks": [
    {"id": "structural_credibility", "rating": "strong", "evidence": [{"kind": "full_image_review", "reference": "view:top", "finding": "space reads coherently"}]},
    {"id": "routine_readability", "rating": "acceptable", "evidence": [{"kind": "scheme_document", "reference": "logic:user_routines", "finding": "shared dining is understandable"}]},
    {"id": "circulation_intuition", "rating": "acceptable", "evidence": [{"kind": "full_image_review", "reference": "view:top", "finding": "primary routes are legible"}]},
    {"id": "furniture_logic", "rating": "strong", "evidence": [{"kind": "region_review", "reference": "region:dining", "finding": "furniture supports use"}]},
    {"id": "scale_plausibility", "rating": "acceptable", "evidence": [{"kind": "anchor_comparison", "reference": "anchors:main", "finding": "major proportions remain plausible"}]},
    {"id": "strategy_visibility", "rating": "strong", "evidence": [{"kind": "full_image_review", "reference": "view:top", "finding": "core move is immediately visible"}]},
    {"id": "option_distinctness", "rating": "acceptable", "evidence": [{"kind": "scheme_document", "reference": "comparison:approved-set", "finding": "core move differs from other options"}]},
    {"id": "visual_coherence", "rating": "acceptable", "evidence": [{"kind": "full_image_review", "reference": "view:top", "finding": "appearance supports intent"}]}
  ]
}
```

## Review Decisions

- `view_passed`: one reviewed view passes its required checks; it is not a delivery decision
- `displayable`: a scheme-package review passes every required blocker and quality item
- `needs_repair`: blockers pass, but one or more quality items are weak
- `needs_review`: no blocker has failed, but evidence, required checks, or logic fields remain unknown or incomplete
- `rejected`: a blocker failed or the review package is invalid

Map these to client-facing language as `单视图通过，待方案包复核`, `可展示`, `需要局部修复`, `需要补充复核`, and `不能作为有效方案`.

The script validates structured evidence records, referenced file existence, content hashes, review time, and decision logic; it does not inspect pixels itself. Resolve relative artifact paths from the review package directory or pass `--evidence-root`. Do not create the review record until a human or multimodal agent has actually inspected the image. A provider success, fabricated artifact registry, or self-authored list of `pass` values is not evidence.

## Repair Routing

- Fix the scheme logic when the core move, routine, tradeoff, or visual proof is incoherent.
- Fix object operations or deterministic placement when access or furniture use is wrong before generation.
- Fix the reference package, prompt, mask, camera proxy, or generated image when the logic is sound but the visual drifts.
- Fix board assembly when the scheme is valid but comparison, labels, hierarchy, or explanation is unclear.

Never repair a logic failure with decorative polish alone.
