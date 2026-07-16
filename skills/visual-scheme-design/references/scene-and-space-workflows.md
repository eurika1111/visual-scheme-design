# Scene And Space Workflows

## Contents

- Domain classification and visual direction
- Viewer, layout, execution, and board outputs
- Temporary buildability and validation

Use this reference for live-stream set design, temporary staging, interior styling, spatial mood, and execution-view planning. Residential renovation and whole-home layout work are routed to the home-design references.

## Scope Split

Classify the task before prompting:
- `set dressing`: furniture, table, chairs, backdrop, props, plants, fabric, light objects
- `temporary set`: movable scenic pieces, portable walls, light boxes, display plinths, brand-safe decoration
- `interior style`: palette, material language, furniture temperament, lighting mood
- `space design`: zones, circulation, wall/floor/ceiling treatment, architectural composition
- `execution view`: top view, 45-degree view, equipment positions, buildability notes

If the user asks for set dressing, keep the base space neutral unless a real venue must be preserved. Do not redesign architecture, floor plan, ceiling, or full room identity.

## Stage Sequence

For scene or space work, use this order:
1. Confirm project type and final viewer.
2. Separate scope: set dressing, interior style, space planning, or execution view.
3. Lock hard constraints: budget, people count, viewpoint, must-avoid items, venue limits.
4. Choose the domain sequence:
   - For residential renovation or whole-home layout work, switch to `home-design-workflow.md`.
   - For styling, decoration, mood exploration, or temporary staging that does not alter the floor plan, define visual directions first.
5. Define 2-4 clearly differentiated spatial or visual directions as appropriate.
6. Select or repair the upstream direction.
7. Generate viewer-facing room images, top view, full view, 45-degree execution view, or detail references only when their upstream spatial or visual direction is stable.

Do not generate execution diagrams before the visual direction is accepted unless the user asks for production planning first.

## Residential Routing Note

For residential renovation, whole-home design, source-plan redraw, or layout deepening, do not use this file as the primary workflow. Read `home-design-workflow.md` first, then `home-object-model.md`, `home-geometry-validation.md`, and `residential-plan-redraw.md` as needed.

## Budget And Buildability Tiers

Use a buildability tier for every set-design or temporary staging option:
- `low`: rented furniture, movable backdrops, paper/fabric/acrylic panels, floor lights, plants, small objects, no heavy construction
- `medium`: custom but lightweight scenic panels, modular platforms, integrated lighting, larger movable pieces
- `high`: custom scenic fabrication, large sculptural pieces, complex built-in lighting, major venue transformation

For low-budget or temporary live setups, avoid:
- large custom sculptural installations
- permanent-looking construction
- full LED walls unless requested
- heavy platforms or walls
- dense props that make the frame hard to read

## Differentiation Dimensions

When creating multiple directions, vary at least two dimensions per option:
- palette: warm neutral, cool gray, black-white contrast, green/natural, muted color
- brightness: high-key, low-key, balanced, spotlight-driven
- material: wood, paper, textile, stone, metal, acrylic, plant-based
- background density: blank, layered panels, framed display, soft texture, graphic surface
- furniture relation: round-table salon, long-table forum, low-table lounge, standing demo
- lighting: soft museum wash, dramatic side light, table glow, backlit panels, practical lamps
- cultural tone: contemporary exhibition, editorial minimal, natural craft, formal institutional, intimate salon

Minor swaps such as cup color, chair shape, or table edge do not create a new direction by themselves.

## Live-Stream Set Rules

For viewer-facing live frames:
- Keep guests as the visual center.
- Do not show cameras, tripods, cables, monitors, phone UI, comments, likes, captions, or watermarks.
- Use a clean frame that could be the final audience image.
- Keep table scale believable for conversation and camera framing.
- Do not make the scene look like a generic TV studio unless requested.

For execution views:
- Equipment may appear.
- Use top view or 45-degree view as separate images.
- Keep the arrangement consistent with the selected viewer-facing direction.


## Output self-check

Before finalizing live-stream, temporary set, interior styling, or execution-view outputs, run this lightweight check:

- `Scope`: did the output stay within set dressing, temporary set, interior style, space design, or execution view as requested?
- `Viewer frame`: if this is a viewer-facing live image, are cameras, tripods, cables, monitors, UI, captions, watermarks, and black borders absent?
- `Execution view`: if this is a top or 45-degree view, is it consistent with the selected viewer-facing direction?
- `Buildability`: does the option match its declared low/medium/high tier and avoid hidden heavy construction when the brief is temporary or low budget?
- `Differentiation`: if multiple options exist, does each option differ by at least two meaningful dimensions?
- `Text`: are labels and notes kept out of the generated image unless deliberately large and minimal?
- `Option status`: are kept, revised, replaced, and rejected options still clearly separated?

If the output fails one item, repair that layer only. Do not regenerate every option unless the upstream direction itself is wrong.

## Interior And Space Rules

For interior style boards:
- Focus on mood, materials, furniture language, lighting, and overall taste.
- Do not over-specify exact floor plans unless the user gives dimensions.

For space planning boards:
- Ask for function, zones, people flow, fixed constraints, and view priorities.
- Separate beauty render references from plan-like diagrams.
- Add labels, dimensions, and callouts after image generation in a layout tool.




