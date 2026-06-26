# Home Design Workflow

Use this reference first for residential renovation and home-design tasks. It summarizes the working model learned from repeated failures: image generation is useful for expression, but reliable home design requires objectized source data, deterministic validation, version isolation, and controlled rendering.

## Core conclusion

The critical path is:

```text
original client plan
→ candidate source facts
→ decomposable base object model
→ geometry validation and readiness level
→ quick concept options or stable deepening
→ rendered drawings and client-facing images
```

The source plan must become sufficiently accurate object data before design options are generated. If this step is weak, later concept images, scheme migration, and deepening will inherit unstable geometry and become frustrating to correct.

## Product-facing modes

Use two user-facing modes, but gate both with data readiness:

- `quick concept`: explore several directions quickly after the base reaches `L2 concept-design ready`.
- `stable deepening`: develop a selected direction after the base reaches `L3 deepening ready`.

Do not offer quick concept generation as a workaround when the base is only `L1 readable draft`. At `L1`, the useful output is an understanding draft, object list, discrepancy report, and the minimum questions needed to improve the base.

## Readiness-controlled stages

1. `Project intake`
   - Collect the original source plan and optional area, household needs, style preference, and constraints.
   - Do not ask broad decoration questions before the source plan has a minimum readable base.

2. `Source objectization`
   - Extract candidate rooms, walls, doors, windows, dimensions, labels, balconies, fixed service points, and uncertainty.
   - Store them as object data, not only as a cleaned image.

3. `Geometry validation`
   - Run deterministic checks for wall junctions, opening hosts, room topology, duplicate or isolated walls, dimension traceability, and readiness.
   - Classify the base as `L0` through `L4`.

4. `Quick concept options`
   - Start only at `L2`.
   - Generate options from `base_object_model + scheme_intent`, not from visual guessing.
   - Each option must have independent IDs, intent data, operation logs, and generation reports.

5. `Selection and migration`
   - Convert user feedback into object operations.
   - Example: "move scheme A's island into scheme B" means copy the island object intent, validate fit in scheme B, and create `scheme_B_vNext`; it does not mean visually blend two images.

6. `Stable deepening`
   - Start only at `L3`.
   - Use the original source facts, validated base object model, selected scheme intent, and operation log.
   - Do not use a quick scheme image as geometry authority.

7. `Repair and rollback`
   - Fix the smallest affected layer: label, style, furniture, opening, wall, base geometry, or scheme operation.
   - Base changes create a new base version and mark dependent schemes affected.
   - Scheme changes create only a new scheme version.
   - Rejected versions must not become parents.


## Deterministic control checkpoints

Use these checkpoints to prevent image drift and option contamination:

1. `Before quick concept`
   - Required: `base_object_model`, readiness `L2` or higher, unresolved blockers listed, and option IDs prepared.
   - Do not proceed from a cleaned raster image alone.

2. `Before stable deepening`
   - Required: readiness `L3` or higher, selected scheme intent, active operation log, validation report, and affected-object list.
   - Do not use a quick concept image as the base for deepening.

3. `Before scheme migration`
   - Required: source scheme ID, target scheme ID, copied object IDs or design intent, target placement rule, and fit validation.
   - Example: copying an island from scheme A into scheme B must become an operation record, then a validation pass, then a render.

4. `Before rollback or revision`
   - Required: parent version, target layer to change, rejected versions list, and unaffected schemes.
   - Never repair by editing the latest visual image when the requested change belongs to an earlier object version.

5. `Before client delivery`
   - Required: generation report, validation status, option registry, and a short risk note for unresolved assumptions.

## Script and engine intervention points

Use scripts or project-local geometry tools when available instead of re-reasoning from images:

- Run object/geometry validation after source objectization and after any wall, opening, fixed fixture, or major furniture operation.
- Use an operation applier for actions such as demolish wall, add wall, move furniture, copy element from another scheme, or create a new scheme version.
- Use deterministic rendering or layout tools for SVG checks, labels, dimensions, option summaries, and client-board assembly.
- Use image generation only after the current object state and option intent are clear enough to describe.

If no script is available in the active project, still follow the same contract manually: write the object state, operation log, validation notes, and generation report before rendering.

## Failure lessons to preserve

- A visually clean CAD-like image can still contain wrong areas, moved walls, altered doors, or lost geometry.
- Image models are strong visual renderers, not reliable geometry engines.
- Repeated image-to-image transformations accumulate drift.
- Complex quick scheme images are worse geometry inputs than the original source plan because they add furniture, colors, dashed zones, and generated mistakes.
- Cross-option contamination happens when option objects are kept only in conversation memory.
- User rollback fails when the system edits the current image instead of branching from a prior object version.
- Asking users to notice and describe every visual error is unrealistic; the system must self-check object data and report uncertainty.

## Control rules

- Data controls images; images never write back into source facts.
- Every reusable design element must have an object ID, geometry, version, source, status, and confidence where relevant.
- Every user request that changes a plan must become an operation log entry before rendering.
- Every generated output must have a generation report identifying input versions, changed objects, unchanged claims, uncertainty, and validation status.
- A quick concept image may help the client choose direction; the selected direction must be migrated through object data before deepening.

## What to show the user

Keep the interface light. Show only the current state and next useful action:

```text
Base: base_v2, L2 concept-design ready
Scheme: A_v1 / B_v1 / C_v1
Current layer: furniture layout
Impact: affects scheme B only, not the base or scheme A
Next: validate island fit before rendering scheme B_v2
```

Use technical terms such as ECF, GCF, WSM, OOM, object model, or junction validation only when they help the current task. Otherwise describe the visible deliverable and the confirmation needed.

## Reference order

- Read `home-object-model.md` for IDs, versions, state isolation, scheme intents, and operation logs.
- Read `home-geometry-validation.md` for readiness levels, topology checks, wall junctions, opening hosts, curved partitions, and furniture clearance.
- Read `residential-plan-redraw.md` for rigorous source-plan redraw stages and confirmation gates.

