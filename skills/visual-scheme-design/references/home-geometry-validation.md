# Home Geometry Validation

Use this reference when residential plan data must be judged before quick concept generation, stable deepening, wall modification, opening placement, curved partitions, or furniture clearance checks.

## Core principle

AI extracts candidate objects. Deterministic geometry checks decide whether those objects are connected, valid, and ready for design. Do not rely on image similarity or conversational memory for topology.

## Readiness levels

- `L0 unusable`: exterior outline, room identities, or major wall topology are broken. Do not generate schemes.
- `L1 readable draft`: basic spaces are recognizable, but geometry cannot support design operations. Output only an understanding draft and uncertainty list.
- `L2 concept-design ready`: base topology, room identities, major walls, openings, and fixed service spaces are controlled enough for quick concept options.
- `L3 deepening ready`: dimensions, openings, door swings, fixed-service constraints, furniture footprints, and operation logs are controlled enough for stable layout deepening.
- `L4 construction-prep`: professional verification is still required. Treat this as documentation preparation, not construction approval.

Quick concept generation starts at `L2`, not `L1`. Stable deepening starts at `L3`.

## Geometry kernel scope

A lightweight geometry program should support these objects first:

- straight wall centerlines with thickness
- wall junctions: L, T, cross, endpoint touch, overlap, near-miss
- wall solids approximated from line + thickness
- rooms as closed polygons or registered spaces
- openings bound to one host wall
- doors with swing envelopes
- windows bound to exterior walls
- rectangular furniture footprints with rotation and clearance envelopes

Add curved partitions after the straight-wall system is reliable.

## Required checks

Base checks:

- exterior outline is closed or explicitly marked incomplete
- wall endpoints snap within tolerance or are flagged as near-miss
- T-junctions and crosses are computed from line intersection, not visual guess
- duplicate, overlapping, zero-length, and isolated walls are flagged
- room polygons do not cross wall segments unless an opening exists
- every door/window has exactly one host wall
- room labels map to one room object
- dimension endpoints map to controlled objects or are marked unresolved

Scheme checks:

- demolished walls are alteration candidates or verified as modifiable
- new walls have explicit geometry and thickness
- curved partitions have center, radius, angle range, thickness, and clearance impact
- furniture does not collide with walls, doors, or fixed fixtures
- door swing envelopes remain clear
- circulation width meets the declared concept threshold
- kitchen islands and cabinets preserve minimum operating clearance or are flagged

Contamination checks:

- proposal objects do not overwrite `source_facts`
- a scheme does not inherit another scheme's object without an operation record
- rejected versions are not used as parents
- generated images are not used as geometry authority

## T-junction logic

For two straight wall centerlines:

1. Compute line-segment intersection.
2. If no intersection, compute minimum endpoint-to-segment distance.
3. If distance is within snap tolerance, classify as `near_miss` and propose snap; do not silently snap if the tolerance is exceeded.
4. If one wall endpoint lands on the interior of another segment, classify as `t_junction`.
5. If both segments cross through interiors, classify as `cross_junction`.
6. If endpoints meet, classify as `l_or_endpoint_junction` based on angle.
7. Store a `junction_id`, point, members, angle, tolerance, and validation status.

Example:

```json
{
  "id": "J-023",
  "type": "t_junction",
  "members": ["W-A", "W-B"],
  "point": [4200, 3100],
  "angle": 90,
  "tolerance_mm": 20,
  "status": "valid"
}
```

## Curved partition logic

Represent curved walls as arcs, not prompt adjectives:

```json
{
  "id": "NW-LIVING-ARC-01",
  "type": "wall",
  "subtype": "curved_partition",
  "geometry": {
    "kind": "arc",
    "center": [6100, 4600],
    "radius": 1800,
    "start_angle": 210,
    "end_angle": 310,
    "thickness": 100
  },
  "status": "new",
  "function": "separate_entry_and_living"
}
```

Validate arc endpoints, nearby wall connections, clearance, and whether the arc blocks doors, windows, or required circulation.

## Program MVP

Build the first program as a validator, not as a full CAD engine.

Inputs:

- `base_object_model.json`
- optional `scheme_intent.json`
- optional tolerance settings

Outputs:

- `validation.json`
- normalized junction list
- object warnings
- readiness recommendation: `L0` through `L4`

Minimum functions:

- `segment_intersection(a, b)`
- `point_segment_distance(point, segment)`
- `classify_wall_junction(wall_a, wall_b, tolerance)`
- `find_duplicate_or_overlapping_walls(walls)`
- `bind_openings_to_host_walls(openings, walls)`
- `validate_room_closure(rooms, walls, openings)`
- `check_furniture_collisions(furniture, walls, doors, fixtures)`
- `recommend_readiness(validation_results)`

The first useful version can ignore raster image processing. It should validate object data produced by AI or manually corrected data. Raster-to-object extraction can be a later module.
