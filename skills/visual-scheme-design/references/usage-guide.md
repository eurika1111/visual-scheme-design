# Usage Guide

## How To Trigger

Use the skill explicitly:

```text
用 $visual-scheme-design 帮我把这个空间方案需求拆成阶段和 GPT Image 2 prompts。
```

Natural language should also trigger it after Codex is restarted:

```text
我要做一个直播场景方案板，帮我拆成手机视图、顶视图、45 度执行视图的提示词。
```

```text
帮我做一个低预算直播置景方案板，需要 3 个差异明显的方向，最后整理成客户能看的方案。
```

```text
根据这张原始户型图，先判断能不能进入家装快速概念方案。
```

```text
这批空间方案图生成得不准，帮我诊断问题并给下一轮修复策略。
```

## What To Provide

Best input:
- project goal
- scheme type: live-stream set, temporary scene, home design, interior styling, or client-board cleanup
- target image model
- final use: exploration, client proposal, execution planning, or reference only
- required panels or viewpoints
- hard constraints
- budget/buildability level
- reference images and their roles
- what failed in the last generation

For home-design tasks, provide the original source floor plan first. The skill should judge objectization and geometry readiness before producing renovation schemes.

Minimal input also works:

```text
用 $visual-scheme-design 优化：钱币博物馆三人坐播方案板，低预算，现代展陈感，需要手机直播视图、顶视图、45 度执行视图。
```

## How To Use The Output

1. Confirm the scheme type and scope.
2. Define the visual differentiation map or home-design readiness gate.
3. Generate separate directions only after upstream constraints are stable.
4. Keep stable option IDs while selecting and repairing.
5. Pick or rank final options.
6. Generate separate viewer-facing, top-view, full-view, or execution-view images when needed.
7. Assemble the board outside the image model.
8. Add readable Chinese labels and callouts after assembly.

## Fast Commands

```text
用 $visual-scheme-design 按阶段模式做一个直播置景方案板。
```

```text
用 $visual-scheme-design 判断这个户型图是否达到 L2，可以开始快速概念方案吗？
```

```text
用 $visual-scheme-design 只生成下一轮 GPT Image 2 prompt，不要解释太多。
```

```text
用 $visual-scheme-design 诊断这批空间方案图的问题，并给我一版 repair prompt。
```

```text
用 $visual-scheme-design 把完整方案板拆成单图生成顺序。
```

```text
用 $visual-scheme-design 把这 4 个方案整理成客户方案板文案和排序。
```
