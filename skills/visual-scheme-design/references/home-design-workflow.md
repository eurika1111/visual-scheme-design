# Home Design Workflow

## Contents

- Product boundary, base authority, and checkpoints
- Source routes and readiness levels
- Residential workflow and gates
- Provider recovery, tool roles, and user experience

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

## Interaction Checkpoints

Use `staged` mode by default. In `accelerated` mode, the user must have supplied complete evidence, explicitly requested a faster route, and have no unresolved high-impact ambiguity. Base lock and image-generation approval remain separate hard stops in both modes.

1. `welcome`: for first use, new project, or clean test, briefly explain that the workflow confirms the floor-plan base before needs and concepts. State that outputs are design proposals, not construction drawings. Ask permission for the next single step.
2. `source_understanding`: summarize recognized rooms, orientation, obvious openings, uncertainties, and intended base accuracy. Ask the user to correct the understanding before producing a confirmation base.
3. `base_confirmation`: show the candidate base and ask for visible corrections. Lock only after explicit approval; corrections create a new candidate and return to this checkpoint.
4. `needs_rounds`: collect needs over short rounds, not one long questionnaire.
5. `option_direction_confirmation`: present the approved number of short text directions with meaningful differences, alteration risk, and unresolved assumptions. Three is a useful comparison default, not a fixed requirement. Generate no images until the user approves or edits these directions.
6. `generated_option_review`: review and show comparable outputs, then ask which option to retain, repair, combine, or reject.
7. `deepening_confirmation`: state what exact placement, dimensions, export, or optional UE work will start; proceed only after approval.

In staged mode, do not cross two checkpoints in one assistant turn. `继续`, `下一步`, or silence about later phases confirms only the next action already declared. A user may revise an earlier checkpoint at any time; branch or return without carrying later data backward.

In accelerated mode, combine only `welcome + source_understanding` or `needs_rounds + option_direction_confirmation` into one clearly labeled confirmation package. List every bundled decision and unresolved assumption. Do not combine base lock with needs/options, and do not combine option approval with image generation. If evidence conflicts or the user gives a partial answer, fall back to staged mode.

If the user explicitly requests a first-time test, ignore previous conversational preferences and old generated options. Existing project files may be reused only as hidden evidence after checking their accepted/rejected status; present the experience as a fresh project and ask each required confirmation again.

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

1. `Welcome and scope`
   - Apply the first-use introduction when required.
   - Establish only the requested outcome and the next checkpoint.

2. `Project intake`
   - Collect the source plan and intended use.
   - Ask only questions that change the current checkpoint.

3. `Artifact audit`
   - Inventory current, accepted, candidate, rejected, and historical files.
   - Classify demo, historical, rejected, superseded, and unrelated files before conflict detection. They may provide trace evidence but cannot create a conflict in the current authoritative set.
   - Resolve conflicts among current authoritative and accepted artifacts in active `base_id`, version, lock manifest, room identity, and fixed-function mapping before treating any option artifact as current.
   - Mark legacy option plans that assign fixed low/medium/high risk archetypes to A/B/C as stale strategy evidence; do not reuse their directions without user confirmation.
   - Select Route A or Route B.

4. `Source understanding confirmation`
   - Describe recognized spaces, orientation, openings, uncertainties, and accuracy target without rendering a new base.
   - Stop for correction or approval.

5. `Base acquisition`
   - Produce or import rooms, walls, openings, dimensions, and source facts.
   - Keep uncertainty explicit.

6. `Technical validation`
   - Check topology, continuity, opening hosts, room closure, dimensions, and object preservation.
   - Use overlays and diagnostic SVG/PNG internally.

7. `Client confirmation and lock`
   - Show the user the base before any scheme generation.
   - Render with solid joined walls, recognizable door/window/sliding-door symbols, room names, source areas, key dimensions when available, stable framing, and no debug IDs.
   - Compare against the original source and the best accepted visual baseline.
   - Confirm visible structure, room relationships, openings, kitchen, bathrooms, balcony, orientation, and assumptions.
   - On approval, record `base_id`, `locked_at`, canvas size, coordinate frame, scale, dimension anchors, object-data path, visual path, and confirmation note.

8. `Correction loop`
   - Convert confirmed feedback into stable-ID object corrections.
   - Branch from the accepted parent, validate, and rerender.
   - Never patch the review SVG/PNG or use a rejected candidate as parent.

9. `Needs intake`
   - Let users answer precisely or approximately.
   - Round 1: residents, daily routines, must-keep rooms, and hard restrictions.
   - Round 2: pain points, storage, kitchen/bathroom use, room priorities, and alteration tolerance.
   - Round 3: style feeling, disliked directions, budget expression, and willingness to compare uncertain options.
   - Ask 1-3 focused questions per round. Accept `不确定` and offer examples without treating them as final choices.

10. `Creative strategy`
   - Learn strategies from relevant cases after needs are known. Extract the move, problem solved, why it works, conditions, failure modes, current-plan mapping, and required visual proof according to `professional-knowledge-sourcing.md`.
   - Derive genuinely different directions from the user's conflict variables. Assess alteration risk after each core move is defined; do not use risk tiers as the direction generator.
   - Convert inspiration into object operations and risks, not image copying.
   - Use `residential-computational-design.md` when relationship, access, furniture-use, placement, or option-diversity checks would prevent an obvious contradiction.
   - Create one `scheme_logic_manifest_v1` per option according to `scheme-logic-and-visual-plausibility.md`.

11. `Option direction confirmation`
   - Enter this checkpoint only when the current authoritative and accepted artifacts name the same exact locked base and the required room and fixed-function mappings are consistent. Ignore demo, historical, rejected, superseded, and unrelated files after recording their status.
   - Text-only directions are scheme work, not harmless brainstorming. On a base or mapping conflict, report the conflict and stop before proposing any tentative direction.
   - Present the user-approved option set in text before image generation.
   - State each option's primary problem, core move, meaningful differences, use consequence, tradeoff, and key risk.
   - Stop for approval or revision.

12. `Scheme production`
   - Read the locked base plus one scheme intent; do not reconstruct the base from chat or another image.
   - Keep unchanged base objects fixed. Represent only authorized demolition, additions, furniture, zones, and style as option differences.
   - Use approximate furniture placement for quick concepts when it is visually and functionally plausible; reserve exact placement for the selected scheme.
   - Exception: when furniture, an island, cabinetry, an operable partition, or a door is a `core_proof_object`, validate its footprint, use side, opening envelope, and one named access route before concept generation.
   - Keep every approved option's data isolated regardless of option count.
   - Keep the logic manifest bound to the same base and option version; mark it stale when operations change.

13. `Post-generation control`
   - Register each output to the locked canvas and compare it against the base.
   - Review structural drift, functional omissions, furniture logic, scale, text, and option differentiation.
   - Reject unrequested base changes; repair the smallest failed layer without unlocking the base.
   - If the provider fails, times out, or returns an incomplete artifact, keep the checkpoint open and record a failed attempt; do not register an option version.
   - Retry from the same immutable generation package unless the user changes an output parameter.
   - Use `image-generation-control.md` for reference roles, camera/proxy requirements, drift acceptance, and multi-view consistency claims.
   - Review the output against `scheme-logic-and-visual-plausibility.md`; run `scripts/evaluate_visual_plausibility.py` when a structured review package exists.

14. `Selection and deepening`
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
- each layout-sensitive request has one deterministic structural reference; perspective views that require fidelity have a camera-controlled proxy or are labeled approximate
- each option has a current scheme logic manifest with no unaccepted blocking unknowns
- the requested view can visibly demonstrate the manifest's `visual_proof`
- every `core_proof_object` has a minimum fit/use/access validation record
- a perspective or 45-degree view carries known vertical/building facts or is explicitly labeled concept-height/approximate

After visual generation:

- align output to the locked canvas without free scaling or cropping
- compare unchanged wall/opening anchors against the locked base
- reject unexplained shift, stretch, wall/opening drift, or inconsistent framing
- keep dimensions and coordinate references deterministic and identical across comparable options
- keep the output in `generated_pending_review` until canvas, structural anchors, authorized operations, required functions, and option identity pass review
- reject confirmed base-fidelity, functional, access, furniture-use, scheme-logic, AI-artifact, or claimed multi-view consistency failures
- do not call a result displayable until its structured plausibility decision is `displayable`

On provider failure:

- preserve the current checkpoint, confirmed base, needs brief, approved option direction, and isolated scheme intent
- record request ID, option ID, `base_id`, prompt-package hash, failure class, and attempt number
- do not create a generated option, accepted version, or completed checkpoint
- treat partial artifacts as untrusted until normal post-generation review passes
- retry idempotently from the same package; branch only when the user changes an output parameter

Before deepening:

- selected option is fixed
- exact parent base and operation log are known
- affected objects pass validation
- output is described as visual/reference work, not construction documentation

## Tool Roles

Resolve project tools and degradation behavior through `geometry-tool-adapter.md`; filenames below are compatible examples, not globally installed commands.

- `staged_topology_importer.py`: import existing staged data as a candidate with preservation reporting.
- `source_wall_mask.py` and trace tools: local evidence helpers, not primary full-plan reconstruction when staged data exists.
- geometry and source validators: technical gates.
- `simple_renderer.py`: internal technical review renderer, even when labels are hidden with `--mode client`.
- project-specific or future polished base renderer: client confirmation base.
- `base_lock_manifest.py`: freeze the confirmed base ID, hashes, canvas, coordinates, bounds, and dimension anchors.
- `visual_generation_handoff_builder.py`: build quick or deep image handoffs that must inherit the lock record.
- `concept_output_review.py`: reject canvas mismatch and create same-size side-by-side, overlay, and deterministic dimension-frame review aids.
- current web research: close named professional-knowledge gaps and create versioned evidence records; never replace site or qualified verification.
- adjacency, circulation, placement, and option evaluation tools: produce reports tied to the same base and option hashes; if unavailable, keep the assessment explicit and qualitative instead of inventing computed precision.
- `evaluate_visual_plausibility.py`: validate structured evidence, referenced file existence, and hashes, then return `view_passed`, `displayable`, `needs_repair`, `needs_review`, or `rejected`; it does not inspect pixels by itself.
- image models: proposal appearance and concept expression only; never base reconstruction authority.

## User Experience

Show the user only meaningful checkpoints, but never hide a required decision:

1. short first-use introduction and next action
2. source understanding before base creation
3. readable client confirmation base and explicit lock
4. short, gradual needs rounds or one accelerated needs package when eligible
5. text-only differentiated option directions using the approved option count
6. same-scale comparable generated-option review
7. selected-scheme deepening approval

Do not make the user watch every internal geometry stage or debug a dense technical report.
