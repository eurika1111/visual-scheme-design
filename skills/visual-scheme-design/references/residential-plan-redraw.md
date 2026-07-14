# Residential Plan Redraw

Use this reference when the residential source is a screenshot, platform image, scan, PDF, or an existing staged redraw that needs to become a reliable scheme-design base.

## Goal

Preserve topology, proportions, rooms, openings, circulation, and recognizable source dimensions closely enough for visual scheme design. Target centimeter-level working geometry where evidence supports it; require site measurement for installation or construction use.

## First Decision: Reuse Or Rebuild

Before reading pixels, inventory existing artifacts.

Prefer the newest accepted or reviewable machine-readable parent in this order:

1. base object model with validation report
2. wall/opening/room topology master
3. wall solids or editable SVG/DXF with stable IDs
4. dimension register plus reviewed control framework
5. original raster source

Accepted staged artifacts may skip earlier reconstruction layers. Do not force every project through ECF, GCF, WSM, and OOM as separate user-facing stages.

Reject or isolate historical candidates that were visually or geometrically rejected.

## Authority And Contamination

Use one active machine-readable base candidate as geometry authority.

Every candidate must record:

- parent version
- source files
- stable object IDs
- changed objects
- uncertainty and confidence
- validation report
- status: candidate, accepted, or rejected

SVG, PNG, PDF, generated images, and technical overlays are outputs. They do not write geometry back into the base.

Client feedback becomes an ID-based correction manifest. Unknown IDs block the correction. Applied changes appear in the import or operation report.

## Minimum Base Data

Record only what the current design stage needs:

- coordinate system: lower-left origin, X right, Y up, millimeters
- rooms and continuous/open relationships
- wall centerlines or solids with thickness and alteration status
- short returns, recesses, projections, and junctions that affect topology
- doors, windows, sliding doors, bay windows, balconies, shafts, and hosts
- legible source dimensions and residuals
- source area labels as cross-checks
- fixed-service spaces and unresolved assumptions

Do not smooth irregular source geometry merely to make the redraw cleaner.

## Incremental Reconstruction

When a usable parent exists:

1. import it without changing coordinates
2. compare object counts and IDs
3. validate walls, rooms, openings, and dimensions
4. inspect only failed or uncertain local regions
5. patch objects and create a new candidate

When only a raster exists:

1. register orientation, outline, room names, and dimensions
2. establish main exterior and interior boundaries
3. add short walls and stepped corners
4. register rooms and adjacency
5. add openings and fixed-service elements
6. overlay the candidate on the source

Use OCR, masks, edge detection, and tracing as evidence aids. None of them may silently replace human/source review.

## Technical Review Output

The technical review may show:

- object IDs
- confidence or warning colors
- centerlines
- opening hosts
- room polygons
- source overlay
- geometry errors and near misses

Its job is diagnosis. It may be visually plain or dense. Do not present it as the finished client base.

## Client Confirmation Base Contract

The client base is a separate deterministic render from the same candidate data. It must provide:

- continuous solid wall faces with clean joins
- consistent wall hierarchy without accidental bumps
- clear openings cut from the correct host walls
- recognizable swing doors, sliding doors, windows, and bay windows
- room names and source area labels without overlap
- main dimensions arranged outside the plan
- one stable scale, orientation, and framing
- no debug IDs, warning clutter, code labels, or accidental blank ownership regions

Unknown door swing must not vanish. Use source evidence or a clearly marked candidate swing; if neither is defensible, show the opening location and one focused confirmation callout.

Window-adjacent and bay-window regions must carry explicit room ownership in data or presentation regions. Do not leave unexplained white gaps that appear outside every room.

Use the best accepted prior redraw as a visual regression baseline. A new renderer must not replace it merely because the new data model is cleaner.

## Presentation Gate

The client base passes only when all are true:

- outline and room relationships match the source
- every required door/window is visible and correctly typed
- wall joins and thickness transitions are visually coherent
- room labels and areas are readable
- dimensions and symbols are consistent
- no element hides another required element
- side-by-side review is not visibly worse than the accepted baseline

Geometry validation alone cannot open this gate.

## Correction Loop

1. Record client feedback against stable object IDs.
2. Separate geometry changes from presentation-only changes.
3. Apply geometry changes to a new data candidate.
4. Apply presentation changes to renderer rules or explicit non-authoritative presentation regions.
5. Run preservation, geometry, and presentation checks.
6. Rerender from data.

Never fix a base by painting over its SVG/PNG. Never generalize one project's coordinate patch into the engine without a reusable rule and regression test.

## Validation Priorities

Check in this order:

1. source and version isolation
2. object preservation
3. outline and room topology
4. wall continuity and junctions
5. door/window hosts, types, sizes, and directions
6. room ownership near windows and openings
7. dimensions and residuals
8. client-base readability

## Deliverables

Keep deliverables proportional to the project:

- base object data and validation report
- source overlay or diagnostic review when needed
- client confirmation base PNG/SVG
- short unresolved-item list
- optional reference DXF/DWG/SVG for site measurement or later redraw

Do not generate every intermediate layer unless it resolves a real uncertainty or the user asks to inspect it.
