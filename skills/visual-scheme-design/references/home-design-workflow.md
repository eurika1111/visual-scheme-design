# Home Design Workflow

Use this reference for residential renovation, whole-home layout, source-plan objectization, client-visible base confirmation, creative case learning, quick visual concepts, option migration, and visual deepening.

## Core Position

This skill creates home design scheme drawings, not construction drawings.

Priority order:

```text
client-visible base confirmation
→ structure consistency
→ centimeter-level key element accuracy
→ customer needs and hard constraints
→ creative case strategy
→ object/version control
→ deterministic scheme draft
→ visual scheme output
→ review/reference export
```

Do not chase millimeter-level CAD accuracy during concept work. Allow small dimension differences when the original structure, room relationships, openings, and major fixed-service areas remain visually and spatially consistent.

Generated images are visual outputs. They must not become the authority for walls, openings, room areas, dimensions, or option geometry.

## Base Standard

Use a `scheme base`, not a construction base.

A usable scheme base must preserve:

- overall apartment outline and room adjacency
- main walls and major partitions
- doors, windows, balconies, kitchen, bathrooms, and fixed-service zones
- room labels and functional identity
- key furniture or fixture footprints when they affect layout
- object IDs for walls, rooms, openings, fixed zones, and reusable scheme elements

Accuracy target:

- key single elements should stay within centimeter-level error where possible
- suspected large errors, wrong room topology, misplaced openings, or fixed-service drift must be flagged
- DWG/DXF/SVG exports are reference outputs for review or site measurement, not construction-ready files

## Product-Facing Modes

Use two user-facing modes:

- `quick concept`: starts after `L2 scheme-base ready`; produces controlled scheme intents, deterministic scheme drafts, and visual options.
- `visual deepening`: starts after `L3 reference-base ready`; refines the selected option and may export reference DWG/DXF/SVG for review or site measurement.

At `L1`, do not generate schemes. Output only an understanding draft, uncertainty list, and the minimum confirmation needed to reach `L2`.

## Readiness Levels

- `L0 unusable`: major structure, room identity, or orientation is broken.
- `L1 readable draft`: spaces are recognizable, but the base is not controlled enough for schemes.
- `L2 scheme-base ready`: structure, room identity, main walls, main openings, and fixed-service spaces are stable enough for quick visual concepts.
- `L3 reference-base ready`: key dimensions, openings, fixed-service constraints, major furniture footprints, and operation logs are controlled enough for visual deepening and reference export.
- `L4 documentation/reference export`: prepare review materials only; do not claim construction readiness.

Mark manually anchored bases clearly when source extraction was not fully automated, for example `L3 manually anchored reference-base candidate`.

Geometry readiness and source fidelity are separate gates. A geometrically closed model is not `L2` until its source-to-base review is explicitly accepted.

## Revised Workflow

1. `Project intake`
   - Collect the original source plan and only essential needs.
   - Do not ask broad style questions before the plan is at least `L1`.

2. `Source objectization`
   - Use this order: accepted staged object data; reviewed topology import candidate; local trace patches for unresolved regions; fresh full-plan extraction only when no usable staged data exists.
   - Extract only missing candidate rooms, walls, doors, windows, balconies, fixed-service points, and key dimensions.
   - Store them as object data with uncertainty, not as a cleaned raster image.
   - Keep imported data as a candidate until preservation checks, source overlay review, and user confirmation pass; never auto-promote it over the accepted base.

3. `Client-visible base confirmation`
   - Always show a base review package before scheme generation when a project will continue beyond a quick explanation.
   - Include: base SVG/review image, coordinate origin, main dimension anchors, room/wall/opening IDs, unresolved questions, and pass/fail summary.
   - Ask the client to confirm, circle errors, or approve proceeding with listed assumptions.
   - Convert confirmed feedback into an ID-based correction manifest, then create and validate a new base candidate from the accepted parent data; never edit the review SVG/PNG as the fix.
   - Do not hide the base SVG as an internal-only artifact.
   - Compare visible room areas and major outline anchors with the source plan; record large deviations instead of explaining them away as simplification.
   - Produce a machine-readable base-fidelity report. Scheme planning remains blocked unless it matches the exact base version and has `can_plan_schemes=true`.
   - A rejected base invalidates every dependent scheme and returns the project to base reconstruction.

4. `Needs and constraints intake`
   - Before options, collect high-impact needs unless the user explicitly asks for blind inspiration.
   - Minimum questions: residents, must-keep rooms, openness to demolition, open-kitchen attitude, island attitude, storage needs, budget/risk tolerance, style preference, fixed no-change areas.
   - Separate hard constraints from taste, ideas, and optional wishes.

5. `Creative case learning`
   - Search or use supplied references only after needs are known.
   - Learn from cases by extracting strategies, not copying images.
   - Store each case idea as: inspiration, transferable strategy, current-home placement, risk level, required validation.
   - Do not let reference images override source geometry.

6. `Differentiated scheme strategy`
   - Create A/B/C using different risk and creativity levels, not minor furniture swaps.
   - Recommended default:
     - `方案 A`: low-risk optimization; little or no demolition, furniture/storage/circulation improvement.
     - `方案 B`: medium-risk functional upgrade; open kitchen, island, partial partition changes, stronger living-dining-kitchen relationship.
     - `方案 C`: high-creativity exploration; curved partition, multifunction room, spatial reorganization, bolder alteration candidates.
   - Each option needs independent IDs, intent data, operation records, risk level, and generation report.

7. `Object operations and validation`
   - Convert every creative idea into object operations before rendering.
   - Validate walls, openings, door swings, furniture footprints, fixed-service zones, circulation, and proposal-specific risks.
   - High-risk changes such as demolition, moving wet zones, curved walls, or major spatial reconfiguration must be marked `requires_verification` unless confirmed.

8. `Controlled placement resolution`
   - Convert placement requests into proposal objects with stable IDs, room targets, dimensions, coordinates, rotation, and source request IDs.
   - Search a finite set of candidates and reuse geometry checks for room containment, wall/furniture collision, door swing, fixed fixtures, and circulation.
   - Allow recorded compact furniture fallbacks when standard sizes do not fit; do not silently shrink objects.
   - Keep demolition and other high-risk structure changes as confirmation items instead of applying them automatically.
   - Keep `layout_gate=placement_required` when a blocking request has no valid candidate.

9. `Deterministic scheme draft`
   - Before AI visual generation, create a deterministic plan draft when the output is a floor-plan scheme.
   - The draft should include controlled walls, openings, room names, key furniture, proposal objects, rough dimensions or coordinate grid, and option ID.
   - Build a client-visible review package with the same base bounds, scale, lower-left origin, dimensions, and annotation rules for every option.
   - Show every option draft, object list, compact-size fallback, validation summary, and deferred high-risk item before visual rendering.
   - The client or operator should be able to compare each draft against the base SVG and compare A/B/C directly.

10. `Visual scheme generation`
   - Build a visual-generation handoff only from the active `accepted` scheme version and its matching deterministic review package.
   - If style remains vague, keep the generation gate closed and offer a few broad directions plus free-form room for partial preferences.
   - The handoff must separate immutable geometry from allowed visual freedom and list every deferred structural idea as "do not visualize until confirmed".
   - Use visual generation for material, color, atmosphere, and client-friendly polish.
   - Do not ask the image model to create authoritative dimensions, small Chinese labels, dense annotations, or construction-grade walls.
   - Add labels, dimensions, coordinates, legends, and notes later in deterministic layout tools.

11. `Post-generation review`
   - Every generated image starts as `generated_pending_review`.
   - Check structure drift, wall continuity/thickness, door/window drift, bathroom/kitchen completeness, furniture logic, circulation, option differentiation, labels/text failures, and watermark/UI artifacts.
   - Mark the result `reviewed_passed`, `needs_repair`, or `rejected`.
   - Repair the smallest layer: prompt, scheme intent, deterministic draft, base model, or source extraction.

12. `Selection and migration`
   - First convert natural-language feedback into a short record containing feedback ID, action, source scheme, source object ID, target scheme, target spaces, and optional replacement object ID.
   - Example: "move scheme A's island into scheme B" means copy the island object intent, validate fit in scheme B, and create `scheme_B_vNext`; do not visually blend two images.
   - Re-place the copied object against the target option's objects and constraints; do not reuse the source coordinates blindly.
   - If the target room is unclear or already contains the same object category, ask for confirmation instead of guessing.
   - Preserve the source option and target parent unchanged; only the new target version receives the feedback operation.
   - Low-risk automated feedback may copy, replace, move, rotate, or remove proposal furniture. Structural walls, openings, fixed fixtures, and wet zones remain outside this automatic path.

13. `Visual deepening / reference export`
   - Start only at `L3` plus selected scheme intent, operation log, validation report, and affected-object list.
   - Use original source facts, controlled base, selected scheme intent, deterministic draft, and operation log.
   - Reference DWG/DXF/SVG outputs are for review/site measurement and must not be described as施工图.

14. `Repair and rollback`
   - Fix the smallest affected layer: base geometry, scheme operation, deterministic draft, visual prompt, labels, style, furniture, or output board.
   - Base changes create a new base version and mark dependent schemes affected.
   - Scheme changes create only a new scheme version.
   - Rejected versions must not become parents.

## Control Checkpoints

Before quick concept:

- Required: `L2`, client-visible base review, an explicitly accepted base-fidelity report for the exact base version, base object model, unresolved blockers listed, needs/constraints brief, and option IDs prepared.
- If the user has no needs yet, ask whether to proceed with three exploratory directions.
- Do not proceed from a cleaned raster image alone.

Before creative case learning:

- Required: customer needs or an explicit exploration goal.
- Output strategy notes, not copied case layouts.
- Mark ideas as low/medium/high risk before mapping them to the current plan.

Before visual generation:

- Required: active accepted scheme version, scheme intent, operation list, risk level, resolved blocking placement requests, matching deterministic review package, confirmed or explicitly exploratory style brief, and visual-generation handoff.
- Every bedroom needs a controlled sleeping function, the living room needs seating, the kitchen needs a worktop, and every bathroom needs a toilet, basin, and bathing function before a full-home visual can proceed.
- If fixture completion conflicts with a door swing or room boundary, return a visible confirmation item; do not ask the image model to invent a solution.
- For plan images, do not rely on prompt-only control when dimensions, wall continuity, or furniture orientation matter.

Before visual deepening/reference export:

- Required: `L3`, selected scheme intent, operation log, deterministic draft, validation report, generation review status, and affected-object list.
- Do not use a quick concept image as geometry authority.

Before scheme migration:

- Required: source scheme ID, target scheme ID, copied object IDs or design intent, target placement rule, and fit validation.

Before client delivery:

- Required: generation report, validation status, option registry, review notes, and short risk note for unresolved assumptions.

## Script Role

Scripts are backend risk controls. Use them to:

- prevent obvious structural drift
- keep option data isolated
- detect wrong or uncertain dimensions
- generate confirmation lists and review diagrams
- create deterministic scheme drafts
- support reference SVG/DWG/DXF export

Do not let script checks turn the workflow into施工图 production. If a check is too strict for visual scheme design, report it as a risk or confirmation item instead of blocking all concept work.

## Failure Lessons

- A clean CAD-like image can still contain wrong areas, moved walls, altered doors, or lost geometry.
- Image models are strong visual renderers, not reliable geometry engines.
- Repeated image-to-image transformations accumulate drift.
- Complex quick scheme images are worse geometry inputs than the original source plan.
- Cross-option contamination happens when option objects are kept only in conversation memory.
- Asking users to find every visual error is unrealistic; the system must self-check and ask only high-impact questions.
- Creative references increase option quality only when converted into object operations and validations.
- Prompt-only control is not enough for wall thickness, door continuity, bathroom fixtures, furniture orientation, or consistent scale.

## What To Show The User

Keep output light but visible:

```text
Base: L3 manually anchored reference-base candidate
Shown: base SVG, dimension anchors, unresolved assumptions
Need confirmation: bathroom door position and top local dimension
Needs brief: open kitchen? island? demolition tolerance? storage priority?
Next: learn 3-5 relevant cases and create differentiated A/B/C scheme intents
```

Use technical terms only when they help the current task.
