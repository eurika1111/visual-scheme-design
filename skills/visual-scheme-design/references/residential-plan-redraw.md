# Residential Plan Redraw

Use this workflow when a residential source plan is a screenshot, platform image, scan, PDF, or other non-CAD artifact.

## Goal

Produce a stable concept-design base that preserves the source plan's topology, proportions, openings, circulation, and usable room relationships. It is not a substitute for site measurement or construction drawings.

Keep the workflow understandable to the user. The user must be able to see how Codex interpreted dimensions, boundaries, spaces, and uncertain structure before detailed CAD drawing begins.

## Five distinct artifacts

Never use one name for multiple artifacts.

1. `ECF — exterior control framework`
   - Contains only the closed exterior centerline skeleton and its evidence.
   - Confirm and lock it before adding internal geometry.
2. `GCF — geometric control framework`
   - Upstream reasoning and confirmation artifact.
   - Shows coordinate/dimension datums, registered spaces, and colored boundary segments.
   - This is the only artifact called “几何控制骨架/几何控制框架”.
3. `WSM — wall solid model`
   - Converts confirmed GCF boundaries into wall solids with thickness and joined corners.
4. `OOM — opening and component model`
   - Cuts door/window openings from wall solids and installs door/window components.
5. `CAD Base — clean redraw`
   - Combines confirmed WSM and OOM into a clean, editable design base.

Do not call ECF or WSM a geometric framework. Do not add internal walls, spaces, or functional zones before ECF confirmation.

## Authoritative data and contamination control

Use one machine-readable model as the sole authority. PNG, PDF, SVG, and DXF files are rendered outputs, never geometry inputs.

At the start of a redraw, create an input manifest containing only:

- the original client source
- transcribed source dimensions
- user-confirmed facts
- approved component defaults
- the accepted parent-stage object data and its validation report, when available

Accepted ECF/GCF/WSM/OOM or topology masters are reusable parent data, not historical contamination. Import them with stable IDs, provenance, unresolved items, and an object-count preservation report; keep the result as a candidate until overlay and human review pass.

Do not inherit coordinates, polygons, wall classifications, or openings from rejected, superseded, or unreviewed outputs. Historical files may be opened only for an explicitly requested comparison.

For every revision:

- create a new immutable version
- use stable IDs
- record provenance and changed objects
- apply object-level patches
- reject correction manifests that reference unknown object IDs; record every applied room-region, wall, door, or window override in the import report
- mark failed versions rejected
- never use a rejected version as a parent

## Evidence priority

Use evidence in this order:

1. Legible linear dimensions with matching endpoints.
2. Confirmed topology and adjacency.
3. Clear wall, window, door, bay-window, and shaft relationships.
4. Area labels as cross-checks.
5. Registered raster positions.
6. Explicitly labeled design assumptions.

Keep:

- `source_value`: immutable transcription
- `working_value`: solved or rounded value used by the model

Prefer a 10 mm concept grid. Record adjustments and unresolved residuals. Never distort a room silently to close a dimension chain.

## Stage 1 — Dimension register

Before drawing:

- transcribe every legible dimension
- identify its endpoints
- record whether it is total, partial, or ambiguous
- record confidence and source location
- calculate chain sums and residuals

Dimensions guide the model but may be normalized slightly for a usable concept redraw. Site-critical cabinet, appliance, and installation dimensions require later field measurement.

## Stage 2 — GCF geometric control framework

### Purpose

GCF constrains the model and exposes Codex's interpretation to the user. It is a data model rendered as a PNG for review; downstream work reads the data, not the PNG.

### Required content

The GCF must show:

- reusable horizontal and vertical coordinate datums
- important source dimensions or working coordinates
- light, translucent space registration regions with stable space IDs
- every wall-aligned boundary segment, including short returns and close parallel segments
- a simple legend

The GCF must not show:

- furniture
- door swing arcs
- detailed window frames
- hatches, wall fills, construction notes, or proposal commentary
- finished CAD graphics

### Boundary segment colors

Color applies to GCF boundary segments, not filled wall solids:

- red: exterior boundary or locked structural boundary
- blue: likely non-structural internal boundary
- orange or gray: unknown internal boundary; locked pending verification
- dashed neutral line: functional-zone annotation only, never a wall

Store classification as data. Color is only the human-readable display.

### Exterior and windows

- Treat every exterior boundary as locked.
- In GCF only, include windows in the continuous exterior control boundary.
- Do not create gaps in the exterior skeleton for windows.
- Store window positions separately for later OOM work.

### Exterior control-line datum

Use one datum convention for the complete closed exterior skeleton:

- default to the wall centerline for every exterior segment, including window spans, returns, recesses, bay windows, and short piers
- never mix centerlines with visible inner faces or outer faces inside one closed boundary
- store the datum as `centerline`, `inner_face`, or `outer_face`; reject an exterior model with an unset or mixed datum
- detect both visible wall faces before placing a control segment; calculate the centerline from their midpoint
- where one face is hidden by a window, hatch, furniture, or low-resolution graphics, continue the centerline from adjacent collinear wall segments and record the inference
- derive L-shaped, U-shaped, stepped, and recessed corners by intersecting adjacent centerlines, not by independently clicking each visible corner
- use source dimensions to cross-check the centerline result; dimensions do not justify moving a segment away from the source without a recorded adjustment

Do not interpret a cleaner or more regular outline as an optimization. Existing exterior geometry must be faithfully registered. Any normalization requires an explicit `source_coordinate`, `working_coordinate`, reason, and residual.

For every recess or projection:

1. identify both wall faces on each leg
2. estimate local wall thickness
3. calculate each leg's centerline
4. intersect centerlines to form continuous control vertices
5. compare the clean control line with the original at enlarged scale
6. check its width and offset against the relevant dimension-chain segments

Reject the exterior framework when:

- a control line visibly hugs an inner or outer wall face
- adjacent segments use different datum conventions
- apparent wall thickness changes abruptly around a corner without source evidence
- a recess width was measured from room clear edges while neighboring geometry uses wall centerlines
- a raster overlay appears acceptable only because the red line is hidden by the thick source wall

### Space registration

Register spaces from source topology and boundaries:

- no wall and no interior door separation means one continuous space
- entrance, corridor, and living room may share one space ID with dashed functional zones
- a dressing area inside a bedroom remains part of that bedroom unless physically separated
- bay windows belong to the parent room by default
- do not split a space merely because its function changes
- do not let a translucent space region hide a boundary segment

At this stage, space polygons are control regions for checking adjacency and scale. They are not substitutes for wall geometry.

### GCF construction order

Always use this order:

1. Build, review, and lock `ECF` as an exterior-only centerline model.
2. Establish global X/Y datums from overall and chained dimensions.
3. Import the confirmed ECF data without altering its coordinates.
4. Add locked internal boundaries.
5. Add likely non-structural boundaries.
6. Add unknown boundaries.
7. Register spaces in a fixed order:
   - continuous public region
   - wet/service rooms
   - enclosed bedrooms and study
   - attached bay-window geometry
   - functional zones
8. Add space IDs, coordinate labels, and legend.
9. Render GCF and overlay it on the original source.

### GCF confirmation gate

Do not proceed until the user confirms:

- exterior form and major jogs
- all internal boundary segments, including short walls
- space extents and adjacency
- continuous versus separated regions
- structural color interpretation
- key coordinate and dimension relationships

The GCF passes only when both the overlay and the clean framework are understandable. A technical audit alone cannot approve it.

Before asking for confirmation, provide enlarged overlay checks for every exterior recess, projection, and stepped corner. Render the control line thin enough that the source wall remains visible on both sides; if both faces cannot be seen, the centerline placement has not been visually verified.

## Accuracy-preserving efficiency

Reduce repeated context and rendering work without reducing evidence or validation.

- Process one layer at a time: ECF exterior, GCF internal boundaries and spaces, WSM solids, OOM openings, then CAD Base.
- Lock every confirmed layer. Downstream stages must read its machine-readable data and must not reload or reinterpret its source geometry unless the user reopens that layer.
- Keep only the confirmed parent and current candidate active. Reject failed candidates and exclude them from discovery and geometry inheritance.
- For a local correction, crop and inspect the affected node plus enough adjacent geometry to establish continuity. Do not repeatedly analyze the full image when the unchanged layer is locked.
- Use raster wall masks and tracing only for unresolved local regions. Do not rebuild the whole plan from a wall mask when a usable staged topology master exists.
- After a local patch, run a lightweight whole-plan topology and unchanged-object check; do not regenerate unrelated diagnostic enlargements.
- Store image observations as structured evidence: face coordinates, midpoint, wall thickness, confidence, source region, and inference method. Reuse that evidence instead of repeatedly re-reading the same pixels.
- Use reusable deterministic scripts for hash checks, midpoint calculation, centerline intersection, overlap detection, local crops, overlays, and audit reports.
- Read only the current stage rules and relevant model objects during routine revisions. Load the full historical discussion only for an explicitly requested comparison.
- Do not reduce source resolution, skip dimension evidence, omit high-risk local enlargements, relax tolerances, or replace human confirmation to save tokens.
- If an efficiency shortcut conflicts with accuracy or traceability, preserve accuracy and record the extra review requirement.

This optimization changes how evidence is carried forward, not how much evidence is required.

## Stage 3 — WSM wall solid model

Create WSM only from the confirmed GCF data.

- Assign wall thickness before constructing corners.
- Convert continuous straight, L, T, U, stepped, and recessed groups into joined wall solids.
- Use wall faces or polygon unions, not thickened centerlines.
- Keep all short returns, piers, nibs, and close parallel walls.
- Resolve inside and outside corners as one continuous solid.
- Treat exterior and unknown walls as locked.
- Treat likely non-structural walls only as alteration candidates, not demolition approval.

Wall thickness is evidence, not proof of structural status.

## Stage 4 — OOM openings and components

Build complete wall solids first, then cut openings.

- Bind every opening to exactly one host wall.
- Subtract the opening from the wall solid.
- Place frames, leaves, sashes, or tracks entirely inside the opening.
- Never paint white over a wall to imitate an opening.
- Never allow a component to invade either jamb.

Concept defaults:

- ordinary room door: target 800 mm clear passage
- constrained kitchen or bathroom: 700 mm minimum, prefer 800 mm
- entrance: target 900 mm
- ordinary hinge-side wall return: prefer 100–150 mm
- internal doors open inward by default and rest against a wall
- entrance may open outward only after corridor, property, fire, and neighbor-door checks

Draw corner windows and small side windows as openings, not structural wall fragments.

## Stage 5 — CAD Base

Generate the clean redraw from confirmed WSM and OOM:

- solid walls with correct joins
- standard door and window symbols
- minimal room names and essential dimensions
- no structural color overlay in the primary clean drawing

Store structural status, uncertainty, dimensions, and provenance in companion data. Use a separate audit attachment when colored structure markup is needed.

## Validation

### GCF checks

- exterior control boundary is continuous
- the exterior boundary declares one datum convention, normally `centerline`
- the source wall is visible on both sides of the control line at sampled straight segments and every recess
- local distances from the control line to the inner and outer wall faces are approximately balanced
- no exterior segment switches from centerline to inner-face or outer-face registration
- every visible source boundary and short wall is registered
- no duplicate or overlapping boundary segments
- spaces do not cross boundary segments
- continuous regions are not incorrectly split
- bay windows are assigned to parent rooms
- colored segments match stored classifications
- coordinate labels and dimensions are traceable to the register
- original overlay and clean GCF describe the same data

### WSM/OOM checks

- no zero-thickness, disconnected, duplicate, or overlapping wall solids
- L, T, U, stepped, and recessed corners are continuous
- every opening has exactly one valid host
- frames remain inside openings
- windows meet jamb faces without gaps
- internal doors have valid spaces on both sides
- revisions change only declared objects

### Human review

Automated checks are necessary but insufficient. Before each confirmation gate, visually compare the original source, overlay, and clean output. Never present “audit passed” as equivalent to “drawing confirmed”.

## Confirmation gates

1. `ECF`: exterior centerline datum, closed outline, recesses, projections, and local enlarged overlays.
2. `GCF`: internal boundary segments, classifications, coordinate datums, spaces, adjacency, and dimensions.
3. `WSM`: wall solids, thicknesses, joins, and structural constraints.
4. `OOM`: door/window openings, sizes, hosts, and component placement.
5. `CAD Base`: clean redraw, residual report, uncertainty list, and editable output.

Lock every confirmed gate as an immutable version. A later correction creates a child version and identifies affected downstream outputs.

## Deliverables

- original source
- input manifest
- dimension register and residual report
- authoritative machine-readable model
- ECF clean exterior skeleton, full overlay, and high-risk local overlays
- GCF clean PNG and source overlay
- WSM audit drawing
- OOM opening schedule
- clean CAD Base PNG and DXF
- uncertainty/site-measurement list
- version and object-diff record
