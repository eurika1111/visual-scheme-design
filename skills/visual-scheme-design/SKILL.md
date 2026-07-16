---
name: visual-scheme-design
description: Direct visually credible residential design, interior styling, live-stream staging, temporary set design, and controlled space-scheme workflows. Use when Codex should interpret a floor plan, develop logically coherent spatial options, explain why a scheme is usable, create image prompts or client boards, produce top-view or 45-degree execution views, preserve a confirmed base, reject obvious spatial or AI-generated errors, repair similar or drifting options, recover failed image-generation requests without losing approved state, or prepare a real-time-engine handoff.
---

# Space Scheme Design

Route spatial design work to the smallest relevant workflow. Optimize for a visually credible proposal whose spatial logic is easy to understand and free of obvious contradictions. Keep geometry, approved decisions, option versions, generated visuals, and client presentation as separate layers.

## Runtime Rule

1. Classify the domain, mode, current checkpoint, audience, and final use.
2. Inspect project-local files and state before creating anything.
3. Read only the references required for the current action.
4. Execute one phase or one approved transition.
5. Run deterministic checks when available.
6. Update state, option registry, operation log, or validation report.
7. Report the current result and one useful next action.

Do not reconstruct approved facts from chat when project files exist. Do not use generated images as geometry or version authority.

## Non-Negotiable Contracts

- Treat a confirmed residential base as read-only. Change it only through a specific user-requested correction and a newly confirmed base version.
- Bind every residential option to one locked `base_id`, canvas, coordinate frame, scale, framing, and dimension-anchor set.
- Store authorized changes as option-specific object operations. Never redraw the whole base from visual guesswork.
- Keep source facts, object models, operation logs, validation reports, generated images, and presentation boards separate.
- Require every residential option to explain one primary problem, one core move, its use logic, its tradeoff, and the visual proof that makes it believable.
- Describe residential outputs as visual design proposals or review references, not construction drawings.
- Preserve approved state across provider errors. A failed request is not a generated option, accepted version, or completed checkpoint.
- When the user asks only for structure, a plan, or an outline, do not generate images, videos, boards, or other extra assets.

These contracts override downstream generation, repair, export, and UE instructions.

## Interaction Contract

For residential first-use, new-project, or clean-test requests:

- Introduce the service boundary and staged process briefly.
- Stop at every material checkpoint defined in `references/home-design-workflow.md`.
- Use staged guidance by default. When the user supplies complete evidence and explicitly asks for a faster route, combine only the non-critical checkpoints allowed by the workflow's accelerated confirmation package.
- Treat `继续` as approval for only the next declared action.
- Ask before acting when ambiguity changes structure, room function, resident needs, alteration scope, budget, style, option count, or output type.
- Accept fuzzy answers such as `不确定`, `先看看方向`, or `都可以比较` without converting them into hard requirements.
- Require separate approval for the confirmation-base lock and for image-generation directions.

At a checkpoint, return only the current finding, 1-3 focused questions or a confirmation request, and the next single action.

## Modes And Phases

Use one mode per turn:

- `explore`: develop directions, options, or prompt strategy.
- `select`: compare, preserve, combine, rank, or reject options.
- `execute`: produce object operations, prompts, diagrams, boards, or validation outputs.
- `repair`: diagnose a failure before changing prompts, data, or versions.

Track one current phase: `classification`, `intake`, `constraints`, `strategy`, `production`, `diagnosis`, or `delivery`. Store multi-turn state according to `references/runtime-state.md`.

## Domain Routing

- Residential workflow, checkpoints, readiness authority, and generation gates: read `references/home-design-workflow.md` first.
- Residential needs programming, adjacency, priorities, evaluation, alteration risk, and evidence levels: read `references/residential-design-knowledge.md` after the workflow when developing or comparing options.
- Scheme logic manifests, visible proof, obvious-error blockers, quality review, and delivery decisions: read `references/scheme-logic-and-visual-plausibility.md` before generating or accepting a residential visual.
- Case strategy, human-use patterns, professional heuristics, product facts, or named safety concerns: read `references/professional-knowledge-sourcing.md` before searching or citing them.
- Residential relationship maps, named access routes, furniture-use logic, constraint propagation, and option distinctness: read `references/residential-computational-design.md` when they would prevent an obvious contradiction or clarify a decision.
- Geometry-tool discovery, CLI contracts, project adapters, and honest no-tool degradation: read `references/geometry-tool-adapter.md` before claiming an `L2/L3` tool result outside a known project workflow.
- Object IDs, version isolation, operations, migration, rollback, and contamination control: read `references/home-object-model.md`.
- Geometry checks, openings, wall topology, furniture clearance, kitchen clearance, and curved partitions: read `references/home-geometry-validation.md`.
- Raster plans, listing screenshots, source interpretation, and confirmation-base reconstruction: read `references/residential-plan-redraw.md`.
- Live-stream sets, temporary staging, interior styling, spatial mood, top views, and 45-degree execution views: read `references/scene-and-space-workflows.md`.
- Provider failures, similar options, visual feedback, and minimal repair: read `references/repair-and-iteration.md`.
- Client-facing boards, option copy, ranking, and delivery QA: read `references/client-board-output.md`.
- Copy-paste or staged image prompts and recovery messages: read `references/prompt-templates.md`.
- Reference-image editing, GPT Image handoff, geometry-preserving generation, and post-generation drift acceptance: read `references/image-generation-control.md` before generating a residential visual from a locked base.
- UE or another real-time-engine handoff: read `references/ue-visualization-workflow.md` after the relevant spatial reference.
- User asks how to use the skill: read `references/usage-guide.md`.

## Residential Object Data Gate

Use `references/home-design-workflow.md` as the only authority for `L0-L4` definitions and checkpoint order.

- Do not create residential schemes before the exact base is confirmed, locked, and at least `L2`.
- Treat text-only option directions as scheme work. Compare only the current authoritative and accepted artifacts after classifying historical, rejected, superseded, and demo files. If the authoritative set disagrees on the active `base_id`, version, lock status, required room identity, or fixed-function mapping, stop and resolve the conflict; do not provide tentative directions.
- Do not enter selected-scheme visual deepening or reference export before `L3`.
- Reuse accepted staged object data before attempting fresh source extraction.
- Keep technical diagnostics separate from the client confirmation base.
- Apply corrections to object data and rerender. Never patch a review image or replace an accepted redraw with a weaker diagnostic render.
- Reject unexplained canvas, scale, wall, opening, fixed-service, or framing drift instead of writing it back to the base.

## Option And Generation Rules

- Use the user-approved option count and assign stable client-facing IDs such as `方案 A / 方案 B`; three options are a comparison default, not a fixed requirement.
- Keep each option in an isolated branch with an explicit parent, status, round, and short reason.
- Require at least two meaningful differentiation dimensions when multiple directions are requested.
- Reject obvious structural, functional, access, furniture-use, scheme-logic, cross-view, or AI-artifact failures before presentation. Do not let style or a weighted total hide an invalid scheme.
- Use one image prompt for one coherent visual. Split viewpoints, dense labels, exact Chinese text, floor plans, execution diagrams, and board assembly into controlled stages.
- Use image models for appearance and communication. Supply a deterministic structural reference for layout-sensitive outputs, and never ask an image model to infer an exact perspective from a floor plan when a camera-controlled proxy can be produced.
- Add small text, dimensions, legends, and Chinese labels later with deterministic layout tools.
- Use dimensions and geometry as guardrails where they prevent visible or functional mistakes; do not equate parameter density with design reasonableness.
- Validate any furniture, island, cabinet, operable partition, or door that carries the option's core promise before generating its concept image; other loose furniture may remain approximate at quick-concept depth.
- Confirm only output-changing generation inputs: option IDs, count, ratio, viewpoint, reference roles, differentiation map, hard negatives, and destination.

For live scenes, keep viewer-facing frames free of cameras, lights, cables, monitor screens, UI, captions, watermarks, phone frames, and black borders unless requested. Produce execution views separately and keep temporary solutions movable, affordable, and buildable.

## Failure And Recovery Rule

Classify failures before retrying. For a provider error, timeout, or incomplete response:

1. Keep the current checkpoint and all approved spatial state unchanged.
2. Record a failed generation attempt against its request ID, option ID, `base_id`, and prompt-package hash.
3. Do not create an option version or mark the checkpoint complete.
4. Retry from the same immutable request package unless the user explicitly changes an output parameter.
5. Review any partial artifact as untrusted; never use it as geometry, a parent version, or proof of success.

Use `references/runtime-state.md` for retry state and `references/repair-and-iteration.md` for failure labels.

## Output Schema

For normal package mode:

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
<one action after confirmation>
```

## Maintenance Rule

Keep `SKILL.md` as a lean router. Put domain knowledge in `references/`, deterministic behavior in `scripts/`, and evaluation fixtures in the project repository. Do not add untested business domains, duplicate readiness definitions, or vendor-specific generation recipes to the core workflow.
