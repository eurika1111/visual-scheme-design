# Home Object Model

Use this reference when residential work needs controllable plan data, quick concept options, scheme migration, rollback, creative case strategies, deterministic drafts, or contamination control.

## Core principle

Data controls images. Images are rendered outputs and visual discussion aids; they must not become the authority for source geometry, wall positions, door/window locations, room areas, or dimensions.

The agent should operate on object data first, then render drawings or image prompts from the current object state.

## Data layers

Keep these layers separate:

- `source_facts`: immutable evidence from the original client plan, user-confirmed facts, and manually entered measurements.
- `base_inference`: AI-extracted candidate rooms, walls, doors, windows, dimensions, fixed fixtures, topology, and uncertainty.
- `base_object_model`: the current versioned object model accepted for design at a declared readiness level.
- `client_needs_brief`: customer residents, hard constraints, risk tolerance, desired changes, style, budget, and priorities.
- `case_strategy`: external or supplied case inspiration converted into transferable design strategies.
- `scheme_intent`: proposal-specific objects and operations such as demolition, new partitions, furniture, island, storage, function zones, style, and circulation ideas.
- `deterministic_scheme_draft`: program-rendered plan draft from base model plus scheme intent.
- `operation_log`: object-level changes created from user feedback.
- `generation_report`: what was used, what changed, what remained unchanged, what failed, and what is uncertain for each rendered output.

Never write proposal data back into `source_facts`. Never allow a generated quick-plan image to overwrite `base_object_model` geometry.

## Minimum project structure

Use a project-local state folder when files are being produced:

```text
outputs/
  project_state.json
  source_facts.json
  base_versions/
    base_v1.json
    base_v1_validation.json
    base_v1_review.svg
  client_briefs/
    needs_brief_v1.json
  case_strategies/
    case_strategy_v1.json
  schemes/
    scheme_A/
      scheme_A_v1_intent.json
      scheme_A_v1_draft.svg
      scheme_A_v1_report.json
    scheme_B/
      scheme_B_v1_intent.json
  operation_logs/
  generation_reports/
```

`project_state.json` should identify the active base version, client confirmation status, active scheme versions, rejected versions, readiness level, and unresolved blockers.

## Object types

Use stable IDs for all objects that may be referenced later:

- `Room`: room or continuous space registration.
- `Wall`: straight, polyline, or curved wall/partition with thickness and status.
- `Opening`: generic host-wall cutout.
- `Door`: opening plus swing, hinge side, leaf envelope, and host wall.
- `Window`: opening plus sill/window metadata and host wall.
- `FixedFixture`: hard-to-move service or built-in component such as flue, pipe shaft, toilet, sink, shower, drain, or exterior unit position.
- `Furniture`: movable or built-in item with footprint, rotation, clearance, and style.
- `Zone`: functional area annotation that is not a wall.
- `Dimension`: source and working dimensions with endpoints, confidence, and residuals.
- `CaseStrategy`: transferable design idea extracted from a reference case.
- `SchemeOperation`: controlled change applied to one option only.

## Object fields

Prefer this minimal shape for physical objects:

```json
{
  "id": "W-BED-A-E-01",
  "type": "wall",
  "name": "卧室A东侧墙",
  "geometry": {
    "kind": "line",
    "start": [5240, 4180],
    "end": [5240, 7280],
    "thickness": 120
  },
  "adjacent_spaces": ["BED_A", "LIVING"],
  "status": "existing",
  "alteration": "unknown",
  "source": "original_plan",
  "confidence": 0.74,
  "version": "base_v1"
}
```

Allowed wall `status` values: `existing`, `retained`, `demolished`, `new`, `modified`, `unknown`.

Allowed alteration values: `do_not_alter`, `candidate`, `unknown`, `requires_verification`.

## Client needs brief

Store customer needs before creating differentiated options when the customer has specific ideas.

Minimal shape:

```json
{
  "schema_version": "client_needs_brief_v1",
  "residents": "family of three",
  "must_keep": ["three_bedrooms", "two_bathrooms"],
  "can_consider": ["open_kitchen", "island", "more_storage"],
  "forbidden_or_sensitive": ["move_bathrooms", "major_plumbing_change"],
  "style_preference": ["warm_modern"],
  "budget_tolerance": "medium",
  "alteration_tolerance": "low|medium|high",
  "priority_order": ["storage", "living_dining_kitchen", "easy_build"]
}
```

If no needs are known, mark the brief as `exploratory` and keep options clearly separated by risk level.

## Case strategy

Creative cases must be converted into strategy records before entering a scheme.

```json
{
  "id": "CASE-ARC-WALL-01",
  "source": "reference_case_url_or_user_image",
  "inspiration": "curved partition softens living-dining boundary",
  "transferable_strategy": "use a controlled curved partition to separate zones without fully closing the space",
  "target_spaces": ["R-LIVING", "R-DINING"],
  "risk_level": "medium|high",
  "required_validation": ["arc_geometry", "door_clearance", "circulation_width"],
  "allowed_in_options": ["方案 C"],
  "copy_image_geometry": false
}
```

Case strategy rules:

- Learn principles, not layouts.
- Do not copy reference wall positions, furniture, or style literally unless the user explicitly asks and the base allows it.
- High-risk strategies must become explicit operations with validation.
- Case images are not geometry authority.

## Scheme risk levels

Default residential option structure:

- `方案 A / low_risk`: retain structure, optimize furniture, storage, circulation, and style.
- `方案 B / medium_risk`: partial functional upgrade such as open kitchen, island, dining relation, local partition changes.
- `方案 C / high_creativity`: bold exploration such as curved partitions, multifunction rooms, larger spatial reorganization, or demolition candidates.

A/B/C must differ by more than furniture swaps. At least two meaningful dimensions should differ: alteration scope, function, circulation, storage strategy, kitchen relationship, style/material direction, or risk level.

## Scheme operations

Convert user feedback and creative ideas into operation records before rendering.

For client feedback, retain both the original sentence and its controlled interpretation. Minimum fields are `feedback_id`, `action`, `source_scheme`, `source_object_id`, `target_scheme`, `target_spaces`, and optional `replace_target_object_id`. Missing source or target identity is a confirmation request, not permission to infer from images.

Example: copying an island from scheme A into scheme B:

```json
{
  "operation": "copy_object_intent",
  "from_scheme": "scheme_A_v1",
  "from_object_id": "A-KIT-ISLAND-01",
  "to_scheme": "scheme_B_v2",
  "target_space": "KITCHEN",
  "fit_rule": "preserve_size_if_clearance_allows_else_scale_down",
  "validation": ["check_clearance", "check_door_swing", "check_kitchen_workflow"]
}
```

Do not satisfy this request by visually mixing two generated images. Copy the source object's size, footprint, style intent, and functional role, then re-place it in the target scheme using geometry validation.

## Deterministic scheme draft

Before generating a plan-like visual, produce or request a deterministic draft when practical.

The draft should include:

- base walls, openings, room boundaries, and fixed-service spaces
- proposal walls, curved partitions, islands, storage, and key furniture footprints
- option ID and version
- coordinate/grid reference or major dimension anchors when available
- labels added by deterministic layout, not by the image model

If the deterministic draft fails, repair object data or scheme operations before visual generation.

## Generation review states

Use explicit states for generated outputs:

- `not_rendered`
- `generated_pending_review`
- `reviewed_passed`
- `needs_repair`
- `rejected`

Each generation report should record:

- image path
- prompt file
- base model path
- scheme intent path
- deterministic draft path when available
- observed issues
- whether the image may be shown to client
- whether it can be used for deepening

Generated images cannot upgrade a scheme's geometry level. Only validated object data and deterministic drafts can do that.

## Version rules

- Changing base geometry creates `base_vNext` and marks dependent schemes as affected.
- Changing one scheme creates `scheme_X_vNext` only.
- Changing style does not alter source facts or base geometry.
- Changing labels does not alter source facts, base geometry, or scheme operations.
- Failed renderings or failed validations are marked `rejected` and must not become parents.
- Migration between schemes must be explicit in `operation_log`.

## Rendering contract

Rendering tools read object data and generation reports. They should not infer hidden geometry from images or prior conversation when object data exists.

For quick concept images, render visual style and proposal intent from `base_object_model + scheme_intent + deterministic_scheme_draft`. For deepening drawings, render from `base_object_model` that has reached the required readiness level plus validated operation logs.
