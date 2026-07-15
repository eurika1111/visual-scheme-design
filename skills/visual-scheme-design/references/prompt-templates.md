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

## Residential First-Use Welcome

Use for a new customer, new project, or explicit clean test. Do not inspect and render the base in the same user-facing turn.

```text
阶段：开始

当前判断：
我会先确认户型理解和概念底图，再分几轮了解居住需求，之后先用文字给出 A/B/C 方向；你确认方向后才生成方案图。输出用于方案讨论，不是施工图。

请确认/补充：
1. 这次希望解决的主要问题是什么？不确定也可以说“先帮我看看”。
2. 是否先开始户型图理解？这一步不会生成设计方案。

下一步：
只整理户型结构理解和不确定项，等待你确认后再制作底图候选。
```

## Residential Source Understanding

Use after the welcome and source audit, before rendering a confirmation base.

```text
阶段：户型理解

我识别到：
- rooms and relationships: [short list]
- orientation and entry: [short statement]
- doors/windows/fixed zones: [short statement]
- uncertainties: [only high-impact items]

请确认/补充：
1. 房间名称和相邻关系是否正确？
2. 哪些墙、门窗或区域最容易看错，需要重点保留？
3. 是否按“结构一致、关键尺寸厘米级、非施工图”的标准制作概念底图？

下一步：
确认后只生成概念底图候选，不生成装修方案。
```

## Residential Base Review Handoff

Use after source objectization and before any residential scheme generation.

```text
Base review package for [project]

Show:
- original source plan
- clean base SVG / confirmation drawing
- coordinate origin and orientation
- main dimension anchors
- unresolved questions and assumptions

Keep room, wall, opening, and fixed-service IDs in the backend lock package; do not clutter the client view with debug IDs.

Ask the client to confirm:
1. Does the outline match the original plan?
2. Are room names and adjacency correct?
3. Are doors, windows, kitchen, bathrooms, and balcony in the right places?
4. Are any walls, door openings, or service zones visibly wrong?
5. May we proceed to needs intake and concept options with these assumptions?
```

## Residential Needs Intake

Use before generating home-design options when the user has not provided enough constraints.

Ask in three short rounds and stop after each round:

```text
Round 1 - people and hard limits
- Who lives here and what daily routines matter?
- Which room count or functions must remain?
- Which spaces or objects must not change?

Round 2 - problems and alteration
- Which 1-3 current problems matter most?
- What storage, kitchen, bathroom, work, child, elder, or guest needs matter?
- Alteration attitude: conservative / moderate / exploratory / not sure, show comparisons.

Round 3 - feeling and budget
- Desired feeling or disliked styles; fuzzy descriptions are welcome.
- Budget expression: controlled / balanced / willing to invest in key areas / not sure.
- Which uncertain ideas should A/B/C compare rather than decide now?

Ask 1-3 questions at a time. Separate hard constraints from preferences. Do not turn examples into requirements without confirmation.
```

## Residential Option Direction Approval

Use after needs rounds and before any scheme image generation.

```text
阶段：方案方向确认

方案 A：[core idea] | 改动程度：[low] | 主要解决：[problem]
方案 B：[core idea] | 改动程度：[medium] | 主要解决：[problem]
方案 C：[core idea] | 改动程度：[exploratory] | 主要解决：[problem]

请确认/补充：
1. 哪些方向保留、替换或合并？
2. 哪个方向可以更大胆，哪个必须稳妥？
3. 是否批准按这三个方向生成同底图、同尺寸的概念图？

下一步：
仅生成获批方向，并在展示前完成结构漂移和基本功能检查。
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

Use before image generation when controlled proposal geometry, authorized wall changes, or exact comparison needs a deterministic draft. Do not make this a mandatory delay for every low-risk quick concept.

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

Use only after the base is confirmed and locked, the needs brief exists, and the current option has an isolated scheme intent. Add a deterministic draft when proposal geometry requires it.

Prefer a generated `visual_generation_handoff` over reconstructing the prompt from chat history. The handoff's structure lock and active accepted version are authoritative; style fields control only visual treatment.
Do not generate a full-home image when `functional_completeness` is incomplete. Resolve or explicitly confirm missing sleeping, living, kitchen, or bathroom functions first.

```text
Purpose: Generate one client-facing top-down residential visual concept for [Option ID and short name].

Locked base: [base_id and lock manifest]
Output canvas: [exact width x height]
Coordinate frame and scale: [inherit exactly]
Dimension anchors: [inherit exactly]

Use the locked base plan, and deterministic draft when supplied, as the structural reference.
Preserve every base object except the objects explicitly named in authorized base-change operations.

Design intent:
[scheme-specific intent]

Controlled proposal objects:
[island / storage / curved partition / new furniture / local wall change]

Authorized base-change operations:
[empty by default; stable object IDs and operations only]

Visual direction:
[style, palette, material, furniture language]

Hard constraints:
- preserve the exact canvas, aspect ratio, framing, coordinate frame, scale, and unchanged dimension anchors
- do not change the base outline or fixed-service zones unless explicitly authorized above
- do not thicken, break, invent, remove, or move walls unless explicitly authorized above
- do not move, reverse, remove, or invent doors/windows unless explicitly authorized above
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
- output uses the exact locked base canvas, framing, scale, and dimension frame
- outline and room topology still match base
- walls are continuous and not randomly thickened
- doors and windows remain in plausible host walls
- kitchen and bathrooms are complete and not moved
- furniture orientation is usable
- island/storage/partition does not block circulation
- A/B/C are meaningfully different
- no garbled labels, watermarks, UI, or dense fake dimensions

Register the output against the locked base and compare unchanged outline corners, wall junctions, opening endpoints, fixed-service anchors, and main dimension anchors. Any unexplained shift, stretch, crop, or object drift is blocking.

Set result:
- reviewed_passed
- needs_repair
- rejected

Repair only the smallest failed layer: prompt, scheme intent, deterministic draft, or generated visual. Do not repair or unlock the confirmed base unless the user requested a specific base correction.
```
