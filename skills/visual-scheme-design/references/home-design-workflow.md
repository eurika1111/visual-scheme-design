# Home Design Workflow

Use this reference for residential renovation, whole-home layout, source-plan reconstruction, client base confirmation, creative options, feedback, and visual deepening.

## Product Boundary

This skill creates design-scheme drawings and visual proposals, not construction drawings.

The residential chain is:

```text
source evidence -> controlled concept base -> user confirmation and base lock
-> needs brief -> isolated quick concepts -> comparison and selection
-> selected-scheme deepening -> optional UE handoff
```

Data controls structure. The confirmed visual base and its object data form one locked base package: the visual is for human confirmation; the data remains geometry authority.

## Residential Hard Boundary

- Keep the route short and reveal only the current checkpoint.
- A confirmed base is read-only. Do not modify it without a specific user request.
- Bind every option to one locked `base_id`, canvas size, lower-left origin, scale, framing, and dimension anchors.
- Store option changes as isolated operations. Images, style changes, labels, repair prompts, and UE edits cannot modify the base.

## Output Roles

| Output | Purpose | May control later geometry |
|---|---|---|
| Original source | Evidence | yes |
| Base object data | Walls, rooms, openings, dimensions, provenance | yes |
| Technical review/overlay | Internal diagnosis and source comparison | no |
| Client confirmation base | Clear, readable view bound to the active base for approval | no |
| Deterministic scheme draft | Placement and option comparison | no |
| Generated visual | Mood and client presentation | no |

Never deliver an internal diagnostic renderer as if it were the finished client base.

## Entry Routes

Choose one route after inventorying current project files.

### Route A - Reuse existing staged data

Use when accepted or reviewable topology, dimensions, wall solids, openings, SVG/DXF source data, or object JSON already exists.

1. Identify the accepted parent and rejected versions.
2. Import stable IDs, geometry, dimensions, provenance, and unresolved items.
3. Run preservation and geometry checks.
4. Repair only missing or rejected objects.
5. Render a new technical review and client confirmation base from the candidate data.

Do not restart from raster tracing merely because a newer script exists.

### Route B - Build from the source image

Use only when no usable staged data exists.

1. Register the original source, orientation, room labels, and legible dimensions.
2. Build a coarse topology with rooms, main walls, short returns, doors, windows, balconies, and fixed-service spaces.
3. Use local crops, masks, OCR, or tracing only where evidence is unclear.
4. Compare the candidate against the source before adding design content.

Avoid pretending that raw wall masks or image-to-image redraws are reliable object extraction.

## Readiness Levels

- `L0 unusable`: major structure, orientation, room identity, or openings are broken.
- `L1 readable draft`: enough to show interpretation and ask focused questions; no schemes.
- `L2 scheme-base ready`: topology, room identity, main walls, openings, and fixed-service spaces are stable enough for quick concepts.
- `L3 reference-base ready`: key dimensions, constraints, object operations, and selected-scheme placement are controlled enough for visual deepening and reference export.
- `L4 reference documentation`: package review/reference files only; still not construction-ready.

Geometry readiness and presentation readiness are separate. An `L2` model may still fail the client-base presentation gate.

## Core Workflow

1. `Project intake`
   - Collect the source plan and intended use.
   - Ask only questions that change the current checkpoint.

2. `Artifact audit`
   - Inventory current, accepted, candidate, rejected, and historical files.
   - Select Route A or Route B.

3. `Base acquisition`
   - Produce or import rooms, walls, openings, dimensions, and source facts.
   - Keep uncertainty explicit.

4. `Technical validation`
   - Check topology, continuity, opening hosts, room closure, dimensions, and object preservation.
   - Use overlays and diagnostic SVG/PNG internally.

5. `Client confirmation and lock`
   - Show the user the base before any scheme generation.
   - Render with solid joined walls, recognizable door/window/sliding-door symbols, room names, source areas, key dimensions when available, stable framing, and no debug IDs.
   - Compare against the original source and the best accepted visual baseline.
   - Confirm visible structure, room relationships, openings, kitchen, bathrooms, balcony, orientation, and assumptions.
   - On approval, record `base_id`, `locked_at`, canvas size, coordinate frame, scale, dimension anchors, object-data path, visual path, and confirmation note.

6. `Correction loop`
   - Convert confirmed feedback into stable-ID object corrections.
   - Branch from the accepted parent, validate, and rerender.
   - Never patch the review SVG/PNG or use a rejected candidate as parent.

7. `Needs intake`
   - Let users answer precisely or approximately.
   - Capture priorities, household, retained items, storage, kitchen/bathroom needs, style, budget, and change tolerance.

8. `Creative strategy`
   - Learn strategies from relevant cases after needs are known.
   - Create genuinely different low-, medium-, and higher-change directions when suitable.
   - Convert inspiration into object operations and risks, not image copying.

9. `Scheme production`
   - Read the locked base plus one scheme intent; do not reconstruct the base from chat or another image.
   - Keep unchanged base objects fixed. Represent only authorized demolition, additions, furniture, zones, and style as option differences.
   - Use approximate furniture placement for quick concepts when it is visually and functionally plausible; reserve exact placement for the selected scheme.
   - Keep A/B/C data isolated.

10. `Post-generation control`
   - Register each output to the locked canvas and compare it against the base.
   - Review structural drift, functional omissions, furniture logic, scale, text, and option differentiation.
   - Reject unrequested base changes; repair the smallest failed layer without unlocking the base.

11. `Selection and deepening`
   - Migrate selected ideas by object ID into a new target version.
   - Resolve exact furniture placement, authorized wall/opening changes, dimensions, clearances, and fixed-service constraints for the selected scheme.
   - Enter visual deepening/reference export at `L3`; offer UE only as a downstream option.

## Gates

Before quick concept:

- exact base version is `L2`
- technical validation has no blocking errors
- the user has seen and accepted the confirmation base or listed assumptions
- the accepted base has `base_lock_status: locked`
- needs brief and option IDs exist

Before visual generation:

- every option names the same locked `base_id`, canvas, coordinate frame, scale, and dimension anchors
- each option has an isolated intent and only explicit base-change operations
- option differentiation is meaningful
- wet areas and required bathroom/kitchen functions are present
- style direction or explicit exploratory permission exists

After visual generation:

- align output to the locked canvas without free scaling or cropping
- compare unchanged wall/opening anchors against the locked base
- reject unexplained shift, stretch, wall/opening drift, or inconsistent framing
- keep dimensions and coordinate references deterministic and identical across comparable options

Before deepening:

- selected option is fixed
- exact parent base and operation log are known
- affected objects pass validation
- output is described as visual/reference work, not construction documentation

## Tool Roles

- `staged_topology_importer.py`: import existing staged data as a candidate with preservation reporting.
- `source_wall_mask.py` and trace tools: local evidence helpers, not primary full-plan reconstruction when staged data exists.
- geometry and source validators: technical gates.
- `simple_renderer.py`: internal technical review renderer, even when labels are hidden with `--mode client`.
- project-specific or future polished base renderer: client confirmation base.
- `base_lock_manifest.py`: freeze the confirmed base ID, hashes, canvas, coordinates, bounds, and dimension anchors.
- `visual_generation_handoff_builder.py`: build quick or deep image handoffs that must inherit the lock record.
- `concept_output_review.py`: reject canvas mismatch and create same-size side-by-side, overlay, and deterministic dimension-frame review aids.
- image models: proposal appearance and concept expression only; never base reconstruction authority.

## User Experience

Show the user only meaningful checkpoints:

1. source interpretation when uncertain
2. readable client confirmation base
3. explicit base-lock confirmation
4. short, gradual needs brief
5. differentiated scheme directions
6. same-scale comparable scheme review
7. selected-scheme deepening

Do not make the user watch every internal geometry stage or debug a dense technical report.
