# Prompt Templates

## Contents

- General image and scene prompts
- Residential intake, base, needs, and option prompts
- Residential logic, deterministic draft, and image handoff prompts
- Review, repair, and provider-failure recovery

Use these templates as starting points. Replace bracketed fields and delete irrelevant lines.

## Direction Exploration

Use when the user is still finding a creative direction. Generate one image per direction. Avoid labels and dense board layouts.

Before writing prompts for multiple options, define a differentiation map.

```text
Differentiation map:
Repeat for each approved direction:
Option [ID]: [palette] / [material] / [lighting] / [set density] / [budget tier]
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
我会先确认户型理解和概念底图，再了解居住需求，之后按你确认的数量给出文字方案方向；你确认方向后才生成方案图。输出用于方案讨论，不是施工图。

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
- Which uncertain ideas should the approved option set compare rather than decide now?

Ask 1-3 questions at a time. Separate hard constraints from preferences. Do not turn examples into requirements without confirmation.
```

## Residential Option Direction Approval

Use after needs rounds and before any scheme image generation.

Use this template only when the artifact audit confirms the same exact locked `base_id` and version across current authoritative and accepted files and required room and fixed-function mappings are consistent. Classify demo, historical, rejected, superseded, and unrelated files before comparison. If the authoritative set conflicts, stop with a conflict report and focused correction questions; do not fill this template with tentative directions.

```text
阶段：方案方向确认

已确认方案数量：[N]

对每个方案重复：
方案 [ID]：[core idea] | 改动程度：[independent risk assessment] | 主要解决：[problem] | 主动取舍：[tradeoff]

请确认/补充：
1. 哪些方向保留、替换或合并？
2. 哪个方向可以更大胆，哪个必须稳妥？
3. 是否批准按以上保留方向生成同底图、同尺寸的概念图？

下一步：
仅生成获批方向，并在展示前完成结构漂移和基本功能检查。
```

## Residential Case Strategy Extraction

Use after needs are known and before the approved option intents.

```text
For each reference case, extract strategy only:

Case: [name/source]
Observed idea: [what is interesting]
Problem solved: [what use problem it addresses]
Why it works: [relationship / access / furniture / storage / privacy / light / perception logic]
Conditions: [what must be true]
Failure modes: [how the same move becomes implausible]
Current plan mapping: [room/zone/object]
Risk level: [low / medium / high]
Required validation: [clearance / demolition feasibility / wet-zone risk / curved geometry / door swing]
Use in option: [approved option ID / none]
Visual proof: [what the final output must visibly demonstrate]

Do not copy reference geometry directly.
Do not let case images override the source plan.
```

## Residential Scheme Logic Manifest

Use after option directions are approved and before deterministic drafting or image generation.

```text
Option: [Option ID and version]
Primary problem: [one named user problem]
Core move: [one main spatial decision]
Linked obligations: [one to three related duties that must remain satisfied]
User routines: [daily activities supported]
Functional relationships: [near / connected / separated / protected]
Circulation story: [entry, doors, major destinations, work zones]
Furniture logic: [orientation, use side, seating, viewing, storage, access]
Core proof objects: [objects whose fit/use/access proves the core move]
Support functions: [only relevant laundry / drying / cleaning / food / waste / entry / linen / child / elder / pet / maintenance needs]
Concurrent use: [one to three relevant simultaneous activities]
Environmental comfort: [affected daylight / glare / ventilation / exhaust / privacy / noise / odor relationships]
Fixed elements: [unchanged base relationships]
Tradeoff: [what becomes less convenient or is sacrificed]
Visual proof: [what the requested view must visibly show]
Blocking unknowns: [empty before normal generation]

If the core move cannot be explained or visibly demonstrated without contradicting the base, revise the option before generating an image.
```

## Residential Differentiated Options

Use to create the user-approved option set before visual rendering. Repeat the block for each option; do not assign its strategy from its letter or list position.

```text
Option [ID] - [short name]
Primary problem: [confirmed need]
Core move: [spatial decision]
Linked obligations: [related duties preserved]
Functional/circulation consequence: [what changes in daily use]
Furniture/support strategy: [how use is supported]
Core proof objects: [objects requiring pre-generation fit/use/access validation]
Environmental or concurrent-use consequence: [only when relevant]
Tradeoff: [what becomes less convenient]
Alteration risk: [low / medium / high, assessed after the core move]
Must validate: [option-specific blockers]
Visual proof: [what the requested view must visibly demonstrate]
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

Read `image-generation-control.md` first. Build one immutable handoff for one option and one view; use the generated image only after drift review passes.

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
The structural reference controls layout. Style references control appearance only.

Design intent:
[scheme-specific intent]

Scheme logic:
- primary problem: [problem]
- core move: [decision]
- furniture/use logic: [short statement]
- tradeoff: [short statement]
- required visual proof: [what must be visible]

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

## Residential Perspective Visual Prompt

Use for a 45-degree or room perspective only after a selected option has stable placement. Supply a camera-controlled proxy when spatial fidelity matters; if none exists, state that perspective consistency is approximate.

```text
Purpose: Visually deepen one [45-degree / room-perspective] view of [Option ID].

Locked lineage: [base_id / option version / view_id]
Structural reference: [camera-controlled proxy path and hash]
Projection or camera: [fixed definition]
Vertical/building context: [path/hash/status or concept-height assumptions]
Perspective limitations: [unknown beam/sill/equipment/level facts that remain approximate]

The structural reference controls walls, openings, fixed services, furniture placement, camera, and framing.
Style references control only [materials / furniture language / lighting / mood].

Scheme logic:
- primary problem: [problem]
- core move: [decision]
- required furniture/use relationships: [relationships]
- tradeoff: [short statement]
- required visual proof: [what this view must visibly show]

Authorized visual changes:
[appearance-only changes]

Authorized structural changes:
[stable object operations, empty by default]

Hard constraints:
- preserve the supplied camera and all unchanged structural anchors
- preserve required access, kitchen, bathroom, balcony, and bedroom functions
- do not invent rooms, openings, built-ins, level changes, or exterior views
- no labels, dimensions, arrows, UI, watermarks, or generated construction details

Avoid:
- reinterpreting the proxy as loose inspiration
- changing furniture count or orientation without authorization
- claiming exact multi-view consistency without shared object-model proxies
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
- the approved options are meaningfully different when multiple directions were requested
- no garbled labels, watermarks, UI, or dense fake dimensions
- the image visibly proves the scheme's core move and does not contradict its tradeoff, fixed elements, or furniture-use logic
- no fake openings, ghost spaces, repeated furniture, impossible joins, or other obvious AI artifacts

Register the output against the locked base and compare unchanged outline corners, wall junctions, opening endpoints, fixed-service anchors, and main dimension anchors. Any unexplained shift, stretch, crop, or object drift is blocking.

Create a `visual_plausibility_review_v1` package according to `scheme-logic-and-visual-plausibility.md` and run `scripts/evaluate_visual_plausibility.py` when available.

The package must record actual image inspection metadata plus an `evidence_artifacts` registry. Every referenced file must exist, include its SHA-256 hash, and match the current option/view package. Use `review_scope: view` for one image; `view_passed` is not a delivery decision. Use `review_scope: scheme_package` for final delivery, which alone may return `displayable`.

Set result:
- view_passed
- displayable
- needs_repair
- needs_review
- rejected

Repair only the smallest failed layer: prompt, scheme intent, deterministic draft, or generated visual. Do not repair or unlock the confirmed base unless the user requested a specific base correction.
```

## Provider Failure Recovery

Use when an approved image-generation request fails, times out, or returns an incomplete artifact.

```text
阶段：[unchanged interaction checkpoint]

当前判断：
本次生成未形成可验收的方案图；已确认底图、需求、方案方向和提示包保持不变。

失败记录：
- request_id: [same lineage]
- option_id: [option ID]
- base_id: [locked base ID]
- attempt: [number]
- failure_class: provider-error | provider-timeout | partial-output | invalid-output
- prompt_package_hash: [hash]
- valid_generated_version_created: false

保留：
- locked base, canvas, coordinate frame, scale, and anchors
- approved option intent and visual direction
- confirmed reference roles and hard negatives

重试规则：
- reuse the same immutable request package
- increment attempt only
- do not advance the checkpoint before normal post-generation review passes
- treat partial artifacts as untrusted

下一步：
在连接恢复后重试同一请求；若需要更改比例、视角、风格、参考图角色、方案数量或输出位置，请先确认变更。
```
