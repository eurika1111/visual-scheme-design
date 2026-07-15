# Home Geometry Validation

Use this reference when residential plan data must be judged before quick concepts, visual deepening, wall edits, curved partitions, opening placement, furniture clearance, or reference export.

## Core Principle

Geometry checks protect visual scheme reliability. They do not turn the output into construction drawings.

Target:

```text
structure-level consistency + centimeter-level key element accuracy
```

Do not require millimeter-level precision for concept work. Do flag errors that could visibly change the scheme, room relationship, opening position, fixed-service layout, or furniture fit.

## Readiness Levels

- `L0 unusable`: exterior outline, room identity, or main wall topology is broken. Do not generate schemes.
- `L1 readable draft`: spaces are recognizable, but geometry cannot yet support controlled scheme options.
- `L2 scheme-base ready`: topology, room identity, main walls, main openings, and fixed-service spaces are controlled enough for quick visual concepts.
- `L3 reference-base ready`: key dimensions, openings, door swings, fixed-service constraints, furniture footprints, and operation logs are controlled enough for visual deepening and reference export.
- `L4 reference documentation`: outputs may support review or site measurement; do not claim construction readiness.

Quick concept starts at `L2`. Visual deepening/reference export starts at `L3`.

## Two Validation Depths

For an `L2` quick concept, run only the controls needed to protect comparison:

- confirmed `base_id` is locked
- output canvas, coordinate frame, scale, framing, and dimension anchors match the lock record
- unchanged outline, walls, openings, and fixed-service anchors have not drifted
- required kitchen, bathroom, bedroom, living, and balcony functions remain recognizable
- furniture is plausibly oriented and does not visibly block access

Do not block quick concepts on exact loose-furniture coordinates, exhaustive clearance checks, construction details, or full export readiness.

For selected-scheme `L3` deepening, add exact object placement, authorized wall/opening operations, door swings, circulation, kitchen clearances, curved geometry, dimensions, and reference-export checks.

## Accuracy Policy

Use these practical tolerances as guidance, not施工图 promises:

- key individual elements should stay within centimeter-level error where possible
- visible structure drift, wrong room adjacency, wrong opening host, or major fixed-service drift is not acceptable
- non-critical decoration and loose furniture can tolerate more visual looseness
- uncertain dimensions should become confirmation items instead of blocking all quick concept work
- DWG/DXF/SVG outputs are reference files for review and site measurement

## Geometry Kernel Scope

The lightweight program should support:

- straight wall centerlines with thickness
- wall junctions: L, T, cross, endpoint touch, overlap, near-miss
- wall solids approximated from line + thickness
- rooms as closed polygons or registered spaces
- openings bound to one host wall
- doors with swing envelopes
- windows bound to exterior walls
- rectangular furniture footprints with rotation and clearance envelopes
- curved partitions after straight-wall reliability is stable

## Required Checks

Base checks:

- exterior outline is closed or explicitly marked incomplete
- wall endpoints snap within tolerance or are flagged as near-miss
- T-junctions and crosses are computed from geometry, not visual guess
- duplicate, overlapping, zero-length, and isolated walls are flagged
- room polygons do not cross wall segments unless an opening exists
- every door/window has one plausible host wall
- room labels map to one room object
- key dimensions map to controlled objects or are marked unresolved/local/reference-only

Scheme checks:

- demolished walls are alteration candidates or verified as modifiable
- new walls have explicit geometry and thickness
- curved partitions have center/radius/angle or equivalent controlled geometry
- key furniture does not collide with walls, doors, or fixed fixtures
- door swing envelopes remain usable
- circulation width meets the declared scheme threshold
- kitchen islands and cabinets preserve plausible operating clearance or are flagged

Contamination checks:

- proposal objects do not overwrite `source_facts`
- a scheme does not inherit another scheme's object without an operation record
- rejected versions are not used as parents
- generated images are not used as geometry authority

## Locked-Base Registration Check

For each comparable quick option:

1. Read the locked base manifest and scheme operation list.
2. Render or normalize the option to the exact locked canvas; do not use free scaling, stretching, or independent cropping.
3. Exclude only objects named by authorized `base_change_operations` from the unchanged set.
4. Compare stable outline corners, wall junctions, opening endpoints, fixed-service anchors, and main dimension anchors against the base.
5. Report `passed`, `needs_repair`, or `rejected`, with drift grouped by object ID or anchor.

Any unexplained translation, scale change, aspect-ratio change, wall/opening movement, or inconsistent dimension frame is a blocking quick-concept error. Repair the scheme render or generation input; do not alter the locked base to fit the output.

Add room names, coordinate references, and dimensions through deterministic layout after visual generation. Use the same positions and values across A/B/C so image-model text cannot create false size differences.

## T-Junction Logic

For two straight wall centerlines:

1. Compute line-segment intersection.
2. If no intersection, compute minimum endpoint-to-segment distance.
3. If distance is within snap tolerance, classify as `near_miss` and propose confirmation or snap.
4. If one wall endpoint lands on the interior of another segment, classify as `t_junction`.
5. If both segments cross through interiors, classify as `cross_junction`.
6. If endpoints meet, classify as `l_or_endpoint_junction` based on angle.
7. Store a `junction_id`, point, members, angle, tolerance, and validation status.

## Curved Partition Logic

Represent curved walls as controlled geometry, not prompt adjectives:

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

Validate endpoints, nearby wall connections, clearance, and whether the arc blocks openings or circulation.

## Program Role

Build and use validators as risk gates, not as full CAD engines.

Inputs:

- `base_object_model.json`
- optional `scheme_intent.json`
- optional tolerance settings

Outputs:

- `validation.json`
- normalized junction list
- object warnings
- readiness recommendation: `L0` through `L4`
- confirmation items when uncertainty is high-impact

Minimum functions:

- `segment_intersection(a, b)`
- `point_segment_distance(point, segment)`
- `classify_wall_junction(wall_a, wall_b, tolerance)`
- `find_duplicate_or_overlapping_walls(walls)`
- `bind_openings_to_host_walls(openings, walls)`
- `validate_room_closure(rooms, walls, openings)`
- `check_furniture_collisions(furniture, walls, doors, fixtures)`
- `recommend_readiness(validation_results)`

Raster-to-object extraction is a separate module. It should produce a controlled scheme-base candidate, not a construction-grade CAD model.
