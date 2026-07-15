# Repair And Iteration

Use this reference when generated images fail, options are too similar, or the user gives visual feedback.

## Feedback First

Before writing a new prompt, translate the feedback into:
- affected option ID
- status change
- failure type
- visual cause
- smallest useful fix

Example:

```text
方案 B：待替换
失败类型：style-collapse
视觉原因：色调、灯光和背景层次都接近方案 A
修复动作：保留三人坐播逻辑，但改成冷灰高对比、低装饰密度、材质从木质转为石材/金属
```

## Failure Types

Use these labels:
- `style-collapse`: options look like the same direction
- `scope-drift`: the model redesigned the room when only set dressing was needed
- `budget-drift`: result is too expensive, heavy, or hard to build
- `studio-drift`: result feels like a generic TV studio
- `prop-packing`: too many decorative objects
- `reference-domination`: reference copied too literally
- `camera-drift`: viewpoint or framing is wrong
- `furniture-mismatch`: furniture conflicts with background or concept
- `taste-mismatch`: result feels cheap, old-fashioned, or off-brand
- `text-failure`: generated text, labels, or UI are wrong
- `base-drift`: a residential option shifts, stretches, crops, or changes locked base geometry without authorization

## Repair Rule

Change one layer at a time when possible:
- structure
- scope
- palette
- material
- lighting
- furniture
- camera/viewpoint
- reference role
- budget/buildability

For image edits, preserve everything except the requested change. For regenerations, state what must be kept and what must be changed.

For residential `base-drift`, keep the locked base immutable. Re-register or regenerate only the failed option from its locked `base_id` and isolated intent. Do not patch the base, borrow geometry from another option, or treat the failed image as a new parent.

## Similarity Repair

When options are too similar:
1. Identify which dimensions are identical.
2. Pick new differentiation dimensions before prompting.
3. Replace the weaker option instead of lightly editing it.
4. Keep a stable registry entry such as `方案 B 已替换为 方案 B2`.

Useful repair dimensions:
- switch warm to cool or high contrast
- switch wood-heavy to stone/metal/paper/textile
- reduce or increase background density
- change lighting from soft wash to directional side light
- change furniture relationship from long-table to smaller round-table or lounge
- shift mood from exhibition formal to editorial minimal or natural craft

## Repair Prompt Pattern

```text
Keep:
- [what worked]

Change:
- [specific layer to change]

Do not change:
- [elements that must remain]

New visual direction:
- palette:
- materials:
- lighting:
- set/furniture:
- background:

Avoid:
- [specific failure]
```
