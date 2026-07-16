# Client Board Output

Use this reference after visual options are selected or when the user asks to prepare a client-facing scheme board.

## Option Registry

Keep stable IDs visible:
- use one stable ID for every option in the approved set
- keep the same ID through selection, repair, ranking, and board assembly
- do not create unused A/B/C placeholders when the user approved fewer options

If presentation order changes, write a mapping:

```text
客户展示顺序：
1. 方案 C：灰绿自然型
2. 方案 A：黑灰白质感型
3. 方案 D：暖棕展陈型
```

Do not rename options silently during sorting.

## Client-Facing Copy

For each option, prepare:
- option ID and short name
- one-sentence positioning
- 3 keywords
- suitable use case
- one practical note or risk

Keep copy concrete and visual. Avoid over-explaining prompts or image-generation process in client-facing text.

## Board Structure

A simple client board can include:
1. title and project name
2. one short purpose sentence
3. ranked visual options
4. recommendation note
5. comparison notes: atmosphere, budget, buildability, risk
6. next-step notes: top view, full view, execution view, material/detail references

Use generated images without small in-image labels. Add Chinese titles, labels, arrows, and notes in the layout tool.

## Local Deliverable Rules

When the user wants a final board or needs files later:
- Save source images, assembled board, and editable layout source into the project folder when possible.
- Prefer a clear output folder such as `outputs/方案板整理/`.
- Keep source images in a `source-images/` subfolder.
- If generated images only exist in the chat and stable local paths are not available, say so early and ask for uploads or use available export/download mechanisms.


## Delivery QA

Before calling a board finished, check:

- option IDs are stable and match the latest option registry
- rejected or replaced options are not accidentally presented as active
- Chinese labels, titles, arrows, and notes are added in the layout tool, not trusted to the image model
- every option has one practical note or risk, not only mood words
- residential boards include the base version and validation/readiness status when geometry matters
- residential delivery boards include a `scheme_package` plausibility decision of `displayable`; `view_passed` alone is insufficient
- live-stream or temporary set boards identify whether each image is viewer-facing or execution-facing

If a board is visually good but fails registry, version, or label QA, fix the board assembly rather than regenerating design images.

## When To Stop Generating

When enough acceptable options exist, stop generating more directions and move to selection, ranking, or board assembly unless the user explicitly asks for more options.

Do not keep generating minor variants when the issue is selection or layout.

