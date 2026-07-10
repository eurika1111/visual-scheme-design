# UE Visualization Workflow

Use this reference only when a spatial project needs Unreal Engine or another real-time engine for white-box generation, 3D option comparison, material and lighting previews, cameras, walkthroughs, or client presentation.

## Position

Treat the real-time engine as an optional downstream executor and visualization layer.

```text
source facts
-> base object model
-> client needs
-> scheme intent and operations
-> geometry validation
-> neutral scene handoff
-> version-specific engine adapter
-> scene execution report and visual outputs
```

Do not let UE, MCP, screenshots, imported SVG, or rendered images become geometry authority. Send accepted UE feedback back through scheme operations and validation before changing a controlled scheme.

## Readiness

- At residential `L2`, prepare a white-box or spatial-massing handoff candidate only when the base and scheme intent are controlled.
- At residential `L3`, prepare furniture, material, lighting, camera, and client-preview handoff candidates.
- For scene/set projects without residential levels, require confirmed dimensions, zones, viewpoints, and option IDs before handoff.
- Do not describe an engine handoff as working until it has been tested in the target project and engine version.

## Minimum Handoff

Keep the handoff engine-neutral and versioned. It should identify:

- source base version and scheme version
- units, lower-left origin, axis convention, and engine conversion rule
- walls, floors, ceilings, openings, fixed fixtures, furniture, zones, and curved elements by stable object ID
- object operation status: create, retain, modify, hide, or remove
- asset role or placeholder role without inventing unavailable assets
- material, lighting, camera, and output intent when known
- unresolved assumptions, validation status, and risk flags

Use the existing object model as the source. SVG remains a human review output, not the scene-import authority.

## Option Isolation

- Keep A/B/C in separate scheme versions and separate engine layers, folders, levels, or sandboxes.
- Apply cross-option changes through object operations, then regenerate the affected handoff.
- Record created, updated, skipped, missing, and failed objects in a scene execution report.
- Never write engine-side exploratory edits directly into `source_facts` or `base_object_model`.

## Adapter Boundary

Keep the neutral handoff stable and isolate engine-specific behavior in an adapter.

- Discover the tools available in the current engine project instead of assuming tool names or schemas.
- Prefer one validated batch scene operation over many conversational per-object calls.
- Map project asset IDs through an explicit asset registry; use placeholders when no suitable asset is registered.
- Keep coordinate and unit conversion in one adapter function.
- Treat engine API, MCP, plugin, Datasmith, USD, and import details as version-specific implementation choices.

## Framework-Only Rule

Until a real UE project has been tested, stop at workflow routing, neutral handoff planning, readiness checks, and required-input lists. Do not add speculative plugin code, detailed MCP schemas, large asset taxonomies, or version-specific automation rules to this skill.

Before implementation, require:

- target UE project path and engine version
- confirmed MCP or alternate automation availability
- a minimal asset inventory or placeholder policy
- one controlled base and one scheme intent
- a small acceptance test: generate a white box, preserve object IDs, update one object, render one fixed camera, and produce an execution report

Add tested implementation details only after this acceptance test succeeds.
