# Source Object Extraction Prompt Template

Use this prompt when turning an original residential floor-plan image into object data for the home geometry engine.

## Goal

Extract a `source_extraction_package_v1` JSON package. Do not create design proposals. Do not redraw or beautify the plan. The output is data for validation, not a client-facing image.

## Non-Negotiable Rules

- Coordinate origin is the lower-left corner of the plan.
- X axis goes right, Y axis goes up, unit is millimeters.
- Preserve the source plan's topology. Do not regularize walls silently.
- Every reusable item needs a stable ID, geometry, source evidence, and confidence.
- If a value is unclear, mark it as uncertainty instead of guessing confidently.
- Generated images, concept方案图, or previous failed outputs cannot become source evidence.
- Keep source facts separate from candidate model and proposal ideas.

## Required Output Shape

Return one JSON object:

```json
{
  "schema_version": "source_extraction_package_v1",
  "package_id": "source_extraction_<project>_v1",
  "coordinate_system": {
    "origin": "lower_left",
    "x_axis": "right",
    "y_axis": "up",
    "unit": "mm",
    "angle_positive": "counterclockwise"
  },
  "source_images": [],
  "dimension_chains": [],
  "source_facts": [],
  "candidate_model": {},
  "unresolved_questions": [],
  "extraction_notes": []
}
```

## Extraction Order

1. Register `source_images`.
2. Transcribe legible dimensions into `dimension_chains`.
3. Register exterior and major internal walls in `candidate_model.walls`.
4. Register rooms/spaces in `candidate_model.rooms`.
5. Register doors/windows in `candidate_model.openings`.
6. Add fixed fixtures only when visible or labeled.
7. Create `source_facts` that link source evidence to object IDs.
8. Add unresolved questions for ambiguous walls, openings, dimensions, and room boundaries.

## ID Style

Use readable stable IDs:

- Walls: `W-EXT-S-01`, `W-BED-A-E-01`, `W-KIT-N-01`
- Rooms: `ROOM-LIVING`, `ROOM-BED-A`, `ROOM-KITCHEN`
- Openings: `D-ENTRY`, `D-BED-A-01`, `WIN-LIVING-S-01`
- Dimensions: `DIM-X-TOP-01`, `DIM-Y-LEFT-01`
- Source facts: `SF-WALL-EXT-01`, `SF-ROOM-LABEL-01`
- Questions: `UQ-WALL-01`, `UQ-DIM-01`

## Wall Geometry

Straight wall:

```json
{
  "id": "W-BED-A-E-01",
  "type": "wall",
  "name": "bedroom A east wall",
  "geometry": {"kind": "line", "start": [5240, 4180], "end": [5240, 7280], "thickness": 120},
  "status": "existing",
  "alteration": "unknown",
  "source": "SRC-PLAN-01",
  "confidence": 0.74
}
```

Curved partition only when the source clearly shows or the user explicitly asks for it:

```json
{
  "id": "NW-LIVING-ARC-01",
  "type": "wall",
  "subtype": "curved_partition",
  "geometry": {"kind": "arc", "center": [6100, 3300], "radius": 1600, "start_angle": 210, "end_angle": 330, "thickness": 100},
  "status": "new",
  "alteration": "candidate",
  "source": "user_brief",
  "confidence": 0.72
}
```

## Dimension Chain Shape

```json
{
  "id": "DIM-X-TOP-01",
  "axis": "x",
  "source": "SRC-PLAN-01",
  "segments_mm": [1224, 2169, 622, 612, 1126, 4007, 530, 1320],
  "object_ids": ["W-EXT-W-01", "W-EXT-E-01"],
  "confidence": 0.88,
  "note": "Top dimension chain transcribed from source image."
}
```

## Source Fact Shape

```json
{
  "id": "SF-ROOM-LABEL-01",
  "type": "room_label_and_area",
  "source": "SRC-PLAN-01",
  "object_ids": ["ROOM-LIVING"],
  "source_value": "客厅 29.2㎡",
  "working_value": "living room registered as ROOM-LIVING",
  "confidence": 0.9
}
```

## Unresolved Question Shape

```json
{
  "id": "UQ-WALL-01",
  "severity": "high",
  "question": "This short wall return is visible but its endpoint is unclear; confirm whether it connects to W-HALL-N-01.",
  "object_ids": ["W-HALL-RETURN-01"],
  "blocks": ["stable_deepening"]
}
```

## Before Returning

Self-check the package:

- Are all referenced `object_ids` present in `candidate_model`?
- Are all dimensions linked to a source image?
- Are low-confidence or ambiguous areas listed in `unresolved_questions`?
- Does `candidate_model.coordinate_system` match the package coordinate system?
- Is every source-derived claim in `source_facts`, not hidden in prose?

If exact geometry is not reliable, output the best candidate package with explicit low confidence and unresolved questions. Do not invent precision.
