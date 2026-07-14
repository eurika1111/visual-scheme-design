---
name: visual-scheme-design
description: Direct home-design, interior-space styling, live-stream staging, temporary set-design, and space-scheme workflows. Use when Codex should turn a residential or staging brief into staged space directions, GPT Image/Midjourney/Stable Diffusion/Flux prompts, client-facing concept boards, live-stream set boards, top-view or 45-degree execution views, decoration/style proposals, spatial mood references, real-time engine handoff plans, repair prompts, iteration rules, or deterministic post-layout assembly guidance. Also use when generated space options are too similar, inaccurate, cluttered, impractical, too expensive, too studio-like, or full of broken labels.
---

# Space Scheme Design

Use this skill as a lightweight router and execution guardrail for interior space, home-design, live-stream staging, temporary set design, spatial mood, option repair, and client-facing space boards. Do not use it for non-spatial posters, products, UI, logos, or general graphic design.

## Runtime Rule

Keep the active turn cheap and controlled:

1. Classify the domain and mode.
2. Read only the needed reference files.
3. Use project-local state when files or versions exist.
4. Execute the current phase.
5. Update state, option registry, operation log, or validation report when applicable.
6. Output only the current result and next useful action.

Do not re-explain the whole workflow during normal execution. Do not use generated images as geometry or version authority.

## Mode System

Use one mode per turn:

- `explore`: create directions, options, or prompt strategy.
- `select`: compare, rank, preserve, or reject options.
- `execute`: produce prompts, diagrams, boards, object operations, or validation outputs.
- `repair`: diagnose failures before rewriting prompts or changing data.

## Phase System

Use these checkpoints, skipping irrelevant ones only when the task is clearly narrower:

1. `classification`: identify domain, mode, audience, and final use.
2. `intake`: collect only the inputs needed for the current checkpoint.
3. `constraints`: separate hard constraints from taste or mood.
4. `strategy`: choose spatial/data workflow before visual generation.
5. `production`: create prompts, object operations, checks, or board content.
6. `diagnosis`: update option status and repair the smallest failed layer.
7. `delivery`: assemble or summarize client-facing outputs and QA notes.

## State Contract

When a project has local files, versions, options, or validation reports, look for or create a compact state record before doing multi-step work. Read `references/runtime-state.md` for the state schema and update rules.

Minimum runtime state fields:

```json
{
  "mode": "explore|select|execute|repair",
  "phase": "classification|intake|constraints|strategy|production|diagnosis|delivery",
  "domain": "residential|scene_set|interior_style|space_planning|client_board|repair",
  "level": "L0|L1|L2|L3|L4|null",
  "active_base": null,
  "active_option": null,
  "option_registry": [],
  "validation_status": "unknown|passed|warning|failed|null",
  "last_action": null,
  "evolution_flags": []
}
```

State summarizes the current project; it does not replace source facts, object models, validation reports, operation logs, or user confirmation.

## Domain Routing

Read references only as needed:

- Residential renovation, whole-home layout, source-plan objectization, quick concepts, stable deepening: read `references/home-design-workflow.md` first.
- Residential option migration, rollback, object IDs, generation reports, contamination control: read `references/home-object-model.md`.
- Residential readiness levels, wall topology, openings, curved partitions, furniture clearance, kitchen clearance, circulation checks: read `references/home-geometry-validation.md`.
- Raster floor-plan redraw, listing screenshots, dimensioned platform plans, source-plan confirmation gates: read `references/residential-plan-redraw.md`.
- Live-stream set design, temporary staging, interior styling, spatial mood, top view, 45-degree execution view: read `references/scene-and-space-workflows.md`.
- UE or another real-time engine handoff, object-driven 3D visualization, or MCP scene execution planning: read `references/ue-visualization-workflow.md` after the relevant residential or scene reference.
- Failed generations, similar options, user visual feedback, repair prompts: read `references/repair-and-iteration.md`.
- Client-facing option boards, ranking, copy, delivery QA: read `references/client-board-output.md`.
- Copy-paste image prompts or staged prompt packages: read `references/prompt-templates.md`.
- User asks how to use this skill: read `references/usage-guide.md`.

## Residential Object Data Gate

For residential renovation and whole-home space planning, object data controls images.

- `L0`: unusable; do not generate schemes.
- `L1`: readable draft; output only understanding draft, object list, uncertainty, and correction needs.
- `L2`: quick concept may start from a centimeter-level scheme base; each option needs structured intent and generation report.
- `L3`: visual deepening/reference export may start; structure, openings, key dimensions, fixed-service constraints, furniture footprints, and operation logs must be controlled.
- `L4`: reference documentation/export only; DWG/DXF/SVG outputs are for review and site measurement, not construction-ready drawings.

Do not produce residential concept schemes before `L2`. Do not use quick concept images as geometry authority for deepening. Residential outputs prioritize visual scheme design, not construction drawings.

Reuse accepted staged object data before fresh source extraction. Treat full-plan raster tracing as a local fallback.

Keep technical geometry review separate from the client confirmation base. Apply feedback as object-level candidate corrections and rerender from data; never patch the review image or replace a stronger accepted redraw with a weaker diagnostic render.

## Live Scene And Set-Design Rules

For live-stream sets, temporary staging, interior styling, and execution views:

- Separate viewer-facing frames from execution diagrams.
- Keep viewer-facing live images free of cameras, lights, cables, monitor screens, UI, captions, watermarks, phone frames, and black borders unless requested.
- Use top view or 45-degree execution views as separate outputs when accuracy matters.
- Keep temporary and low-budget solutions lightweight, movable, and buildable.
- Define 2-4 options with at least two meaningful differences when multiple directions are requested.

## Option Registry

Assign stable option IDs as soon as options exist. Prefer `方案 A / 方案 B / 方案 C` for client-facing options.

Track only the fields needed for the current project:

```json
{
  "id": "方案 A",
  "name": "short direction name",
  "status": "保留|待修改|淘汰|替换中|已替换",
  "source": "original|edited|uploaded_reference|copied_object|generated",
  "round": 1,
  "parent": null,
  "notes": "one short reason or requested change"
}
```

Translate user feedback into registry changes before prompting or rendering.

## Generation Rules

Use one image prompt only for one coherent visual. Split into staged outputs when the task includes multiple viewpoints, dense labels, exact Chinese text, floor plans, execution diagrams, or client-board assembly.

Keep small text, callouts, dimensions, legends, and Chinese labels outside generated images whenever possible. Add them later in deterministic layout tools.

Before image generation, confirm only the information that changes the output: option IDs, count, ratio, viewpoint, reference roles, differentiation map, hard negatives, and output destination.

## Repair Rules

In `repair` mode, classify the failure before rewriting:

- `style-collapse`
- `scope-drift`
- `budget-drift`
- `studio-drift`
- `prop-packing`
- `reference-domination`
- `camera-drift`
- `furniture-mismatch`
- `taste-mismatch`
- `text-failure`

Repair one layer at a time when possible: structure, scope, palette, material, lighting, furniture, camera/viewpoint, reference role, budget/buildability, object data, or validation state.

## Output Schema

For normal direct package mode:

```text
判断：
<one-sentence decision>

策略：
<short staged plan>

输出：
<current prompts, operations, validation summary, board copy, or repair instructions>

自检：
<3-6 checks or risks>

下一步：
<one useful next action>
```

For staged guidance mode:

```text
阶段：
<current checkpoint>

当前判断：
<1-2 short sentences>

请确认/补充：
<1-3 focused questions or a confirmation request>

下一步：
<what happens after the answer>
```

For maintenance work on this skill, keep `SKILL.md` lean; move domain details into `references/`, deterministic helpers into `scripts/`, and do not add untested future business domains.
