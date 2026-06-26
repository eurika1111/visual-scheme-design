# Home Object Model

Use this reference when residential work needs controllable plan data, quick concept options, scheme migration, rollback, or contamination control.

## Core principle

Data controls images. Images are rendered outputs and visual discussion aids; they must not become the authority for source geometry, wall positions, door/window locations, room areas, or dimensions.

The agent should operate on object data first, then render drawings or image prompts from the current object state.

## Data layers

Keep these layers separate:

- `source_facts`: immutable evidence from the original client plan, user-confirmed facts, and manually entered measurements.
- `base_inference`: AI-extracted candidate rooms, walls, doors, windows, dimensions, fixed fixtures, topology, and uncertainty.
- `base_object_model`: the current versioned object model accepted for design at a declared readiness level.
- `scheme_intent`: proposal-specific objects and operations such as demolition, new partitions, furniture, island, storage, function zones, style, and circulation ideas.
- `operation_log`: object-level changes created from user feedback.
- `generation_report`: what was used, what changed, what remained unchanged, and what is uncertain for each rendered output.

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
  schemes/
    scheme_A/
      scheme_A_v1_intent.json
      scheme_A_v1_report.json
    scheme_B/
      scheme_B_v1_intent.json
  operation_logs/
  generation_reports/
```

`project_state.json` should identify the active base version, active scheme versions, rejected versions, readiness level, and unresolved blockers.

## Object types

Use stable IDs for all objects that may be referenced later:

- `Room`: room or continuous space registration.
- `Wall`: straight, polyline, or curved wall/partition with thickness and status.
- `Opening`: generic host-wall cutout.
- `Door`: opening plus swing, hinge side, leaf envelope, and host wall.
- `Window`: opening plus sill/window metadata and host wall.
- `FixedFixture`: hard-to-move service or built-in component such as flue, pipe shaft, toilet, sink, or exterior unit position.
- `Furniture`: movable or built-in item with footprint, rotation, clearance, and style.
- `Zone`: functional area annotation that is not a wall.
- `Dimension`: source and working dimensions with endpoints, confidence, and residuals.

## Object fields

Prefer this minimal shape:

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

## Scheme operations

Convert user feedback into operation records before rendering.

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

## Version rules

- Changing base geometry creates `base_vNext` and marks dependent schemes as affected.
- Changing one scheme creates `scheme_X_vNext` only.
- Changing style does not alter source facts or base geometry.
- Changing labels does not alter source facts, base geometry, or scheme operations.
- Failed renderings or failed validations are marked `rejected` and must not become parents.
- Migration between schemes must be explicit in `operation_log`.

## Rendering contract

Rendering tools read object data and generation reports. They should not infer hidden geometry from images or prior conversation when object data exists.

For quick concept images, render visual style and proposal intent from `base_object_model + scheme_intent`. For deepening drawings, render from `base_object_model` that has reached the required readiness level plus validated operation logs.
