# Prompt Templates

Use these templates as starting points. Replace bracketed fields and delete irrelevant lines.

## Direction Exploration

Use when the user is still finding a creative direction. Generate one image per direction. Avoid labels and dense board layouts.

Before writing prompts for multiple options, define a differentiation map.

```text
Differentiation map:
Option A: [palette] / [material] / [lighting] / [set density] / [budget tier]
Option B: [palette] / [material] / [lighting] / [set density] / [budget tier]
Option C: [palette] / [material] / [lighting] / [set density] / [budget tier]
```

Each option should differ on at least two meaningful dimensions. Do not treat furniture swaps or small prop changes as separate directions.

```text
Purpose: Explore one visual direction for [project].

Create a single coherent concept image, not a full presentation board.
The image should show [main subject / environment / scene] with [number of people or key object].

Context:
[short project context]

Visual direction:
[one sentence: mood, palette, lighting, taste]

Hard constraints:
- [constraint 1]
- [constraint 2]
- [constraint 3]

Soft guidance:
[materials, props, atmosphere, optional elements; keep this short]

Avoid:
- text, labels, UI, captions, arrows, callouts, diagrams
- overdesigned studio look unless requested
- random extra props that are not implied
- logos or brand marks unless supplied
```

## Live Set Direction Exploration

Use for temporary live-stream set options. Generate one viewer-facing image per option.

```text
Purpose: Explore [Option ID and short name] for a temporary live-stream set.

Create a realistic viewer-facing live-stream scene, not a full room redesign and not a behind-the-scenes photo.
The base space should feel like [neutral studio / supplied venue atmosphere / simple empty set].
Show [number] Chinese guests as the visual center, seated at [table relationship].

Visual direction:
[palette, material, lighting, set density, atmosphere]

Set dressing scope:
[furniture, backdrop, movable panels, plants, lamps, plinths, small props]

Buildability:
[low / medium / high] budget, [temporary / modular / movable], no heavy construction unless specified.

Hard constraints:
- preserve the core live-stream composition
- do not redesign the whole architecture unless requested
- no cameras, lights, monitors, cables, phone UI, captions, comments, watermarks, or black border
- no generic TV studio look unless requested

Avoid:
- large custom sculptural installations for low-budget options
- dense prop packing
- copying venue references literally when they are only mood references
```

## Interior Or Space Direction Exploration

Use when the user asks for interior style, decoration direction, spatial mood, or space-planning references.

```text
Purpose: Explore [Option ID and short name] for [interior style / spatial mood / space planning].

Create one coherent realistic visual reference.
Focus on [style / material palette / spatial organization / atmosphere].

Scope:
[interior style only / space planning / decoration update / full concept]

Visual direction:
[palette, materials, furniture language, lighting, spatial mood]

Hard constraints:
- [fixed site constraints]
- [must preserve]
- [budget or buildability limit]

Avoid:
- unreadable labels or diagrams
- impossible architecture changes unless this is a concept-only exercise
- overpacked decoration
```

## Viewer-Facing Live Frame

Use for the final audience view of a live stream, talk show, interview, or product demo.

```text
Purpose: Generate the viewer-facing live-stream frame only.

Create a clean [9:16 vertical / 16:9 horizontal / square] viewer-facing live-stream frame.
Show [number] guests in [shot size], seated/standing at [table or setup].
Camera height is [eye level / slightly above face height / other].
The frame should feel like the audience's final viewing image, not a behind-the-scenes photo.

Scene atmosphere:
[venue mood, palette, lighting, background simplicity]

Staging:
[lightweight set description, keep brief]

Hard constraints:
- no cameras, lights, monitor screens, tripods, cables, phone frame, black border, livestream UI, comments, like icons, captions, or watermarks
- [budget/buildability constraint]
- [must preserve or include]

Avoid:
- technical diagrams
- split-screen layout
- unreadable text
- overcomplicated background
```

## Top View Layout

Use for a separate top-down layout image. Add exact labels later in a layout tool.

```text
Purpose: Generate a clean top-down spatial layout reference.

Create a vertical top-down view of [scene/setup].
Show the relative positions of [people], [table/furniture], [camera positions], [lighting positions], and [set pieces].
Use simple recognizable shapes and clear spacing.

Hard constraints:
- true vertical overhead view, not a tilted aerial view
- keep the layout uncluttered
- no small text labels; leave clear space for labels to be added later
- show the same approximate staging logic as the selected live frame

Avoid:
- perspective camera angle
- decorative rendering that hides the layout
- dense callouts or garbled labels
```

## 45-Degree Execution View

Use for a behind-the-scenes execution reference.

```text
Purpose: Generate a 45-degree high-angle execution view.

Create a 45-degree high-angle view of the complete temporary setup.
Show [people], [set area], [main camera], [side cameras if any], [lights], [monitor if needed], and [movable set pieces].
This is a production planning reference, not the audience-facing frame.

Scene:
[venue or simplified environment]

Hard constraints:
- show the full setup clearly
- equipment is allowed in this execution view
- keep the setup low-budget, lightweight, and buildable
- no large LED wall or permanent construction unless requested

Avoid:
- luxury studio scale
- impossible equipment placement
- crowded prop packing
```

## Board Assembly Brief

Use after the separate images exist.

```text
Assemble a visual board from these generated images:
1. Hero/viewer-facing frame
2. Top-down layout
3. 45-degree execution view
4. Optional detail/material references

Add all text, Chinese labels, arrows, titles, legends, and notes in the layout tool.
Do not ask the image model to generate small labels.

Board sections:
- title and one-sentence concept
- final audience view
- spatial layout
- execution view
- equipment and set notes
- risk/adjustment notes
```

## Client Option Summary

Use after options are selected and need to be shown to a client.

```text
[Option ID] [Short name]
Positioning: [one sentence]
Keywords: [keyword 1] / [keyword 2] / [keyword 3]
Best for: [use case]
Buildability: [low / medium / high]
Risk or adjustment: [one concise note]
```

## Repair Prompt Pattern

Use when a generated result failed.

```text
Previous result failed because: [one failure class]

Keep:
- [what worked]

Change only:
- [one targeted change]

New prompt:
[revised prompt]

Negative constraints:
- [repeat the specific failure to avoid]
```

## Residential Base Review Handoff

Use after source objectization and before any residential scheme generation.

```text
Base review package for [project]

Show:
- original source plan
- base SVG / deterministic review drawing
- coordinate origin and orientation
- main dimension anchors
- room, wall, opening, and fixed-service IDs
- unresolved questions and assumptions

Ask the client to confirm:
1. Does the outline match the original plan?
2. Are room names and adjacency correct?
3. Are doors, windows, kitchen, bathrooms, and balcony in the right places?
4. Are any walls, door openings, or service zones visibly wrong?
5. May we proceed to needs intake and concept options with these assumptions?
```

## Residential Needs Intake

Use before generating home-design options when the user has not provided enough constraints.

```text
Before creating options, collect only high-impact needs:

- Who will live here?
- Must we keep the current number of bedrooms?
- Can the kitchen become open or semi-open?
- Is an island or dining island desired?
- Can any non-structural wall be considered for removal?
- What storage problems matter most?
- What budget/risk level is acceptable: conservative, medium, or exploratory?
- What style direction should options explore?
- Which spaces must not be changed?

Separate hard constraints from preferences.
```

## Residential Case Strategy Extraction

Use after needs are known and before A/B/C scheme intents.

```text
For each reference case, extract strategy only:

Case: [name/source]
Observed idea: [what is interesting]
Transferable strategy: [principle that could apply]
Possible placement in current plan: [room/zone/object]
Risk level: [low / medium / high]
Required validation: [clearance / demolition feasibility / wet-zone risk / curved geometry / door swing]
Use in option: [A / B / C / none]

Do not copy reference geometry directly.
Do not let case images override the source plan.
```

## Residential Differentiated Options

Use to create A/B/C before visual rendering.

```text
Option A - Low-risk optimization
Scope: retain structure; improve furniture, storage, circulation, and style.
Risk: low.
Must validate: door swings, furniture fit, storage not blocking circulation.

Option B - Medium-risk functional upgrade
Scope: open or semi-open kitchen, island/dining island, local partition or dining-living relation changes.
Risk: medium.
Must validate: kitchen workflow, island clearance, fixed-service zones, door/window access.

Option C - High-creativity exploration
Scope: curved partition, multifunction room, stronger spatial reorganization, demolition candidates, bold storage/function strategy.
Risk: medium-high or high.
Must validate: alteration feasibility, wall status, circulation, fixed-service zones, curved geometry, furniture fit.
```

## Residential Deterministic Draft Brief

Use before image generation for plan-like home options.

```text
Create a deterministic scheme draft from object data, not from visual guessing.

Include:
- base walls, room boundaries, doors, windows, kitchen, bathrooms, balcony
- proposal objects: new walls, demolished candidates, island, storage, key furniture
- option ID and version
- coordinate/grid or main dimension anchors
- clear room labels and object IDs added by layout tool

Do not use AI-generated concept images as the geometry source.
```

## Residential Top-Down Visual Prompt

Use only after base confirmation, needs brief, scheme intent, and preferably deterministic draft exist.

Prefer a generated `visual_generation_handoff` over reconstructing the prompt from chat history. The handoff's structure lock and active accepted version are authoritative; style fields control only visual treatment.

```text
Purpose: Generate one client-facing top-down residential visual concept for [Option ID and short name].

Use the deterministic draft and base plan as the structural reference.
Preserve the apartment outline, main walls, doors, windows, kitchen, bathrooms, balcony, and fixed-service zones.

Design intent:
[scheme-specific intent]

Controlled proposal objects:
[island / storage / curved partition / new furniture / local wall change]

Visual direction:
[style, palette, material, furniture language]

Hard constraints:
- do not change the base outline or fixed-service zones
- do not thicken, break, or invent walls
- do not move doors or windows
- do not block bathroom, kitchen, balcony, or bedroom access
- no dense dimensions, small labels, arrows, legends, UI, watermarks, or unreadable text
- labels and dimensions will be added later by deterministic layout tools

Avoid:
- copying another option
- treating reference cases as direct floor plans
- impossible furniture orientation
- missing shower/toilet fixtures in bathrooms
- duplicate TV walls unless requested
```

## Residential Post-Generation Review

Use immediately after each generated residential plan image.

```text
Review status: generated_pending_review

Check:
- outline and room topology still match base
- walls are continuous and not randomly thickened
- doors and windows remain in plausible host walls
- kitchen and bathrooms are complete and not moved
- furniture orientation is usable
- island/storage/partition does not block circulation
- A/B/C are meaningfully different
- no garbled labels, watermarks, UI, or dense fake dimensions

Set result:
- reviewed_passed
- needs_repair
- rejected

Repair only the smallest failed layer: prompt, scheme intent, deterministic draft, or base model.
```
