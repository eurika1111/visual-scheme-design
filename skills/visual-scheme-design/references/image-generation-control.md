# Image Generation Control

## Contents

- Authority and reference roles
- Handoff and prompt contracts
- Drift, evidence-backed review, and multi-view rules
- Failure recovery

Use this reference when a locked residential base, deterministic scheme draft, proxy render, or accepted scene layout will be visually deepened with an image model. Keep image generation in the presentation layer.

## Authority Boundary

Treat these inputs in descending order of authority:

1. locked base object data and lock manifest
2. accepted option operations and validated placement data
3. current scheme logic manifest and its required visual proof
4. deterministic top view, line render, depth render, or camera-controlled proxy
5. approved material, furniture, lighting, and mood references
6. text prompt
7. generated image

Never reverse this order. A generated image cannot correct, unlock, or become the parent of geometry data.

## Choose The Input Package

- For a styled top view, supply the exact-size deterministic scheme draft plus the lock manifest.
- For a 45-degree or room perspective, supply a camera-controlled proxy whenever spatial fidelity matters. Do not expect a top-down plan alone to define exact perspective geometry.
- For a material or atmosphere study, supply the accepted structural view and separate style references with explicit roles.
- For a local change, use an edit or mask workflow when supported instead of regenerating the whole image.
- For multi-turn refinement, preserve the same request lineage and structural reference. Do not silently switch from edit to fresh generation.

If the user specifically requests GPT Image or current OpenAI image-model behavior, verify the current official OpenAI documentation through the `openai-docs` skill before promising model names, parameters, resolutions, transparency, latency, pricing, or API behavior.

## Handoff Contract

Build one immutable handoff per option and view:

```json
{
  "schema_version": "controlled_image_handoff_v1",
  "request_id": "gen_scheme_A_top_v1",
  "option_id": "方案 A",
  "option_version": "scheme_A_v1",
  "base_id": "base_v1",
  "view_id": "top|axonometric|room-perspective",
  "canvas_px": [1536, 1024],
  "camera_or_projection": {},
  "structural_reference": "path/to/deterministic-reference.png",
  "structural_reference_hash": "sha256:...",
  "logic_reference": "path/to/scheme_logic_manifest.yaml",
  "logic_reference_hash": "sha256:...",
  "visual_proof": [],
  "vertical_context_reference": "path/to/vertical_and_building_context.json|null",
  "vertical_context_status": "confirmed|estimated|unknown|not_required_for_top_view",
  "style_references": [
    {"path": "path/to/reference.jpg", "role": "material|lighting|furniture-language|mood"}
  ],
  "authorized_base_changes": [],
  "visual_changes": [],
  "protected_anchors": [],
  "hard_negatives": [],
  "output_path": "outputs/...",
  "status": "approved_for_generation"
}
```

Require one option and one coherent view per request. Hash the structural reference and prompt package. A retry reuses the package and increments only the attempt number unless the user approves an output-changing parameter.

## Prompt Order

Write prompts in this order:

1. purpose and view
2. structural reference role
3. authorized proposal objects
4. visual treatment
5. protected geometry and fixed-service constraints
6. exclusions

State explicitly that the reference controls layout while style references control appearance only. Keep dimensions, Chinese labels, legends, arrows, and small text out of the generated image; add them later with deterministic layout tools.

Require the prompt to name the option's core move and the visual proof the output must show. Do not let the image model silently redesign the use logic for a stronger composition.

For a perspective, 45-degree view, built-in elevation, or any image whose credibility depends on height, include known clear height, beams/columns, window and door heights, sills, level changes, shafts, vents, ducts, and major equipment from `vertical_and_building_context`. When these facts are unknown, constrain the image to concept-height assumptions and label it approximate; never let generated vertical geometry become accepted base data.

## Drift Acceptance

Set the result to `generated_pending_review` before it is shown as a valid option. Review in two stages:

### Automatic or deterministic checks

- output file exists and is readable
- expected canvas and aspect ratio match
- locked input files and hashes remain unchanged
- fixed comparison framing is preserved
- deterministic overlays and labels can be reapplied without rescaling

### Geometry and design review

- outline corners and major wall junctions remain registered
- door/window endpoints and fixed-service anchors remain plausible
- authorized operations appear and unauthorized structural changes do not
- kitchen, bathroom, balcony, bedrooms, and primary access remain complete
- furniture orientation and circulation remain usable
- option identity remains distinct
- the core move, furniture-use relationships, and required visual proof remain visible
- obvious fake openings, ghost spaces, repeated furniture, impossible joins, or other AI artifacts are absent

Treat any unexplained crop, stretch, wall/opening movement, missing required function, or camera mismatch as blocking. Repair the prompt, reference package, mask, or proxy view; do not repair the locked base.

Use `scheme-logic-and-visual-plausibility.md` for the complete blocking and quality review. A successful provider response remains untrusted until that review passes.

Create the structured review only after actual visual inspection. Record `image_reviewed`, `review_method`, a non-future timezone-aware `reviewed_at`, reviewer, and an evidence artifact registry whose files exist and whose SHA-256 hashes match. Each structured evidence reference must resolve to one registered artifact. A list of self-authored `pass` values is not evidence. A `view_passed` result approves one inspected image only; final delivery requires a `scheme_package` result of `displayable`.

## Multi-View Rule

Do not claim exact same-space consistency merely because several images look similar. For comparable multi-view output:

1. derive all views from one accepted object model
2. record a camera or projection definition per view
3. render deterministic proxy references from that shared model
4. generate or edit each view separately
5. compare persistent anchors and repeated furniture/material identities

If no camera-controlled proxy is available, label perspective consistency as approximate.

## Failure Recovery

Provider errors, moderation blocks, timeouts, and partial outputs change attempt state only. Preserve the base, option, reference roles, hashes, prompt package, and checkpoint. Retry transient failures idempotently; revise the package only when the failure requires a content or output change.
