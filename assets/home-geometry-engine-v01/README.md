# 家装几何校验器 V1

这个小工具先不做“从图片自动识别户型”，也不做完整 CAD。

它只做一件事：

```text
读取一份户型对象 JSON，检查这些墙、门窗、家具在几何上是否说得通。
```

## 坐标规则

固定使用 CAD/DCC 友好的坐标：

```text
原点：(0, 0) 在户型图左下角
X 轴：向右为正
Y 轴：向上为正
单位：毫米 mm
角度：逆时针为正
```

可以理解为：

```text
        Y+
        ↑
        |
(0,0) ─────→ X+
左下角
```

## 第一版能检查什么

- 墙是不是零长度。
- 墙和墙是否相交。
- 墙和墙是不是 T 型、十字、端点连接。
- 两堵墙差一点没接上时，标记为 `near_miss`。
- 门窗是否能绑定到唯一一堵墙。
- 家具矩形是否和墙发生明显碰撞。
- 根据错误和警告给出 L0-L4 数据等级建议。

## 数据等级

```text
L0：不可用，不应出方案
L1：可读草模，只适合列疑点
L2：可概念设计，可以做快速方案
L3：可深化设计，可以做更稳妥的布局深化
L4：施工前资料整理，仍需现场复尺和专业确认
```

第一版通常只能判断到 L2/L3，不承诺施工级准确。

## 一键验证脚本

为了减少 Windows 权限、Python 路径和长命令拼写造成的中断，项目提供了一个固定脚本：

```powershell
& 'D:\Codex\视觉方案\assets\home-geometry-engine-v01\scripts\run_geometry_demo.ps1'
```

它会一次性完成：

- 检查 `geometry_validator.py` 和 `simple_renderer.py` 语法。
- 重新生成 `scheme_A_v1.json`。
- 校验正常底图、方案 A、问题样例。
- 校验源户型图对象抽取包，确认识图输出是否符合入口规范。
- 运行源数据质量门，判断对象化底图是否允许进入快速概念或稳妥深化。
- 重新渲染三张 SVG 检查图。
- 输出 readiness、error、warning、厨房对象和通道数量摘要。
- 更新 `project_state.json`，记录当前底图、方案、L0-L4 等级、校验状态和关键输出文件。

这个脚本固定使用 Codex bundled Python，避免误触发 WindowsApps 的 `python.exe` 占位启动器。
## 使用方法

使用 Codex bundled Python，不要使用裸 `python`：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\geometry_validator.py' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\base_object_model.sample.json' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.json'
```

输出是一个 `validation.json`，里面包含：

- readiness：L0-L4 建议
- errors：必须修的问题
- warnings：建议确认的问题
- junctions：墙体连接点
- opening_bindings：门窗绑定结果
- furniture_checks：家具碰撞检查结果
## 两个示例

`examples/base_object_model.sample.json` 是一份基本有效的数据，用来确认正常路径。

`examples/base_object_model.problem-sample.json` 是一份故意有问题的数据，用来确认程序能发现：

- 墙端点差一点没接上。
- 门声明的宿主墙不包含门的位置。
- 家具矩形撞到了墙。

`examples/base_object_model.door-swing-sample.json` 是一份门扇冲突样例，用来确认程序能发现门扇打开时碰到临时家具、门扇安全距离不足和通道阻挡。

`examples/base_object_model.island-move-sample.json` 是一份岛台保留移动样例，用来确认程序能在岛台净距不足时生成 `move_object` 草案，而不是直接删除复制来的岛台。

`examples/base_object_model.arc-partition-sample.json` 是一份弧形隔断样例，用来确认 `geometry.kind = "arc"` 能参与通道和家具碰撞校验。

## 生成检查图

可以把对象 JSON 和校验报告渲染成 SVG 检查图：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\simple_renderer.py' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\base_object_model.sample.json' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\plan.svg' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.json'
```

渲染图只用于检查对象数据，不是最终方案图。
## 项目状态文件

一键验证脚本会生成：

```text
D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\project_state.json
```

它不是完整模型，而是一个轻量状态指针，用来告诉后续流程：

- 当前领域：`residential`
- 当前阶段：`production`
- 当前底图：`base_v1`
- 当前方案：`scheme_A_v1`
- 当前等级：例如 `L3`
- 校验状态：`passed`、`warning` 或 `failed`
- 相关模型、校验报告和问题样例报告的位置

后续 Codex 工作应优先读取这个状态文件，再按需读取具体模型或校验报告，避免每次从长对话里重新推断项目进度。
也可以单独读取状态摘要：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\read_project_state.py' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\project_state.json'
```

它会输出当前 `level`、`validation_status`、`active_base`、`active_option`、`source_quality`，以及是否满足快速概念和稳妥深化门槛。
## 一键运行方案操作链路

`run_scheme_operation.py` 用来把一次方案操作串起来：

```text
应用 operations JSON
→ 生成新方案模型
→ 运行几何校验
→ 可选渲染 SVG
→ 写入 project_state.json
→ 输出 state gate 摘要
```

示例：把方案 A 的岛台意图复制到方案 B，并自动校验和切换当前方案：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\run_scheme_operation.py' `
  --state 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\project_state.json' `
  --base-model 'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\base_object_model.sample.json' `
  --operations 'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\operations.copy-island.sample.json' `
  --output-model 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\scheme_B_v1.json' `
  --validation-output 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.scheme_B_v1.json' `
  --render-output 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\plan.scheme_B_v1.svg' `
  --option-id '方案 B' `
  --version 'scheme_B_v1' `
  --parent 'base_v1' `
  --last-action 'copy_island_to_scheme_B' `
  --source-model 'scheme_A=D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\scheme_A_v1.json'
```

如果新方案有 warning，它会被登记为 `待修改`，并关闭该方案的稳妥深化 gate；但不会降低底图 gate。

## 源户型图对象抽取包

`templates/source_object_extraction_prompt.md` 是给 AI 或人工整理者使用的入口提示模板。它要求先输出 `source_extraction_package_v1`，再进入几何校验，而不是直接从图片生成方案。

抽取包包含：

- `source_images`：原始图、截图、扫描件等来源记录。
- `dimension_chains`：可读尺寸链和来源。
- `source_facts`：从源图得到的事实，必须引用对象 ID。
- `candidate_model`：候选墙、房间、门窗、家具等对象模型。
- `unresolved_questions`：低置信或需要用户确认的问题。
- `extraction_notes`：抽取说明，不代替结构化字段。

示例文件：

```text
D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\source_extraction_package.sample.json
```

校验命令：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\validate_source_extraction.py' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\source_extraction_package.sample.json' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\source_extraction.validation.json'
```

典型输出：

```text
extraction_gate=passed extraction_level=L3
can_quick_concept=true can_stable_deepening=true
```

这个校验位于识图和几何校验之间：先检查抽取包有没有来源、尺寸、事实、候选模型和未确认项，再把候选模型交给 `geometry_validator.py` 和 `source_quality_gate.py`。

## 源数据质量门

`source_quality_gate.py` 用来检查“原始户型图已经被抽取成对象 JSON 之后，这份数据是否可靠”。它不负责从图片里识别墙体，也不会把生成图反写成数据。

可以把它理解为底图验收：

```text
对象 JSON + 几何校验报告
→ 检查坐标规则、墙/房间/门窗数量、置信度、重复 ID、源信息可追溯性
→ 输出 source_gate、source_level、是否允许快速概念/稳妥深化
```

示例：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\source_quality_gate.py' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\base_object_model.sample.json' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\source_quality.base.json' `
  --validation 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.json'
```

典型输出：

```text
source_gate=passed source_level=L3 validation=L3
can_quick_concept=true can_stable_deepening=true
```

如果输出 `failed/L0` 或 `failed/L1`，不要继续出家装方案；应该先回到底图对象数据，修墙体、房间、门窗、坐标或低置信度对象。缺少 `source_facts`、`dimension_chains`、`source_images` 等追溯信息时，质量门最多只放到 L2，不直接进入稳妥深化。

## 校验问题摘要

`summarize_validation.py` 可以把很长的 validation JSON 压缩成几条可执行问题：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\summarize_validation.py' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.scheme_B_v1.json'
```

典型输出会列出 readiness、错误/警告数量、问题类型统计，以及前几条关键冲突对象，例如家具重叠、厨房操作距离不足、门扇冲突、通道不足等。

默认还会给每条问题追加一条修复建议，用来指导下一次对象操作。例如：移动哪个家具、删除哪个重复对象、重新检查哪一段厨房操作距离。

如果只想要更省 token 的摘要，可以关闭建议：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\summarize_validation.py' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.scheme_B_v1.json' `
  --no-suggestions
```

如果后续要让程序读取问题摘要，可以使用 JSON 输出：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\summarize_validation.py' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.scheme_B_v1.json' `
  --json
```
## 修复 operations 草案

`draft_repair_operations.py` 可以把校验报告里的冲突转换成一份待确认的 operations 草案。它不会修改模型，也不会更新 `project_state.json`。

示例：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\draft_repair_operations.py' `
  --model 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\scheme_B_v1.json' `
  --validation 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.scheme_B_v1.json' `
  --output 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\repair_operations.scheme_B_v1.draft.json' `
  --parent-version 'scheme_B_v1' `
  --new-version 'scheme_B_v2_draft'
```

第一版采用保守策略：如果严重冲突来自 `operation` 新增对象或 `copied_from` 复制对象，优先生成 `remove_furniture` 草案，而不是盲目移动到未知位置。草案需要人工确认后才能作为正式方案版本继续使用。

当前草案器也会读取门扇和通道校验报告里的家具字段，例如 `collides_with_furniture`、`furniture_id`、`collides_or_too_close_furniture`，从而把门口临时凳子、临时柜体等对象转成待确认的移除草案。

对于 `furniture_clearance_warning` 和 `kitchen_workflow_clearance_warning`，草案器会优先保留 `operation` / `copied_from` 对象并生成 `move_object`，用于表达“保留岛台但换位置”的设计意图。
## 确认修复草案

`confirm_repair_draft.py` 用于在人工确认草案后，把修复草案转成正式方案版本。它会执行：

```text
应用 repair draft
→ 生成新方案模型
→ 重新校验
→ 可选渲染 SVG
→ 更新 project_state.json
→ 输出 state gate 摘要
```

为了避免误操作，脚本必须带 `--confirm` 才会执行：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\confirm_repair_draft.py' `
  --state 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\project_state.json' `
  --current-model 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\scheme_B_v1.json' `
  --repair-draft 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\repair_operations.scheme_B_v1.draft.json' `
  --output-model 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\scheme_B_v2_confirmed.json' `
  --validation-output 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.scheme_B_v2_confirmed.json' `
  --render-output 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\plan.scheme_B_v2_confirmed.svg' `
  --option-id '方案 B' `
  --version 'scheme_B_v2_confirmed' `
  --confirm
```

如果不带 `--confirm`，脚本会拒绝执行。确认后的版本仍然必须通过校验；如果校验失败或只有 L2，就不能进入稳妥深化。
## 切换当前方案

当对象操作生成一个新方案后，先运行校验，再用 `set_active_option.py` 把它写入 `project_state.json`。例如把方案 B 设为当前方案：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\set_active_option.py' `
  --state 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\project_state.json' `
  --option-id '方案 B' `
  --version 'scheme_B_v1' `
  --model 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\scheme_B_v1.json' `
  --validation 'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\validation.scheme_B_v1.json' `
  --parent 'base_v1'
```

状态文件会分开记录：

- 底图 gate：`base_level`、`base_validation_status`
- 当前方案 gate：`active_option_level`、`active_option_validation_status`

因此，一个方案有 warning 时，只会阻止该方案进入稳妥深化，不会把已通过的底图降级。
## 应用对象操作

`operation_applier.py` 用来把用户修改变成对象级操作，并生成新版本 JSON。它不会覆盖原始底图。

示例：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\operation_applier.py' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\base_object_model.sample.json' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\operations.sample.json' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\scheme_A_v1.json'
```

第一版支持：

- `demolish_wall`：拆除一堵允许拆改的墙。
- `set_wall_status`：修改墙状态。
- `add_furniture`：新增家具或岛台等矩形对象。
- `move_object`：移动矩形家具对象。
- `remove_furniture`：移除 `operation` 新增、`copied_from` 复制或标记为新建/修改的临时家具对象。
- `copy_furniture`：从另一个模型复制家具意图。

如果操作违反规则，例如拆 `do_not_alter` 墙，脚本会把错误写进 `operation_log`，而不是假装成功。
## 跨方案迁移示例

用户说“把方案 A 厨房里的岛台融合到方案 B”时，不应该混合两张方案图。

正确方式是复制对象意图：

```text
scheme_A 的 F-ISLAND-01
→ copy_furniture 操作
→ scheme_B 的 F-ISLAND-FROM-A-01
→ 重新校验和渲染
```

示例命令：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\operation_applier.py' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\base_object_model.sample.json' `
  'D:\Codex\视觉方案\assets\home-geometry-engine-v01\examples\operations.copy-island.sample.json' `
  'D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\scheme_B_v1.json' `
  'scheme_A=D:\Codex\视觉方案\outputs\geometry-engine-demo-v01\scheme_A_v1.json'
```

这样方案之间的复用有记录、有来源、有新 ID，也能继续做几何校验。
## 房间校验

`rooms` 表示已经登记好的房间边界。第一版不自动猜房间，只检查给定房间是否靠谱。

房间对象示例：

```json
{
  "id": "ROOM-WEST",
  "type": "room",
  "name": "west room",
  "polygon": [[0, 0], [3200, 0], [3200, 5000], [0, 5000]],
  "area_label_sqm": 16.0,
  "confidence": 0.85
}
```

当前会检查：

- polygon 至少有 3 个点。
- 自动计算面积 `computed_area_sqm`。
- 如果标注面积和计算面积相差超过 0.5㎡，输出 `room_area_mismatch`。
- 每条房间边界是否靠近墙；离墙太远会输出 `room_edge_off_wall`。
- SVG 检查图会用浅色块显示房间区域和房间 ID。

有了 `rooms` 后，正常示例可以达到 `L3 deepening ready`，代表对象数据已经足够做更稳妥的布局深化；仍然不代表施工图准确。




## 厨房操作间距校验

厨房对象不只看“有没有放进去”，还要检查岛台、橱柜、灶台、水槽、冰箱之间是否保留了可操作距离。

第一版会识别这些 `category`：

```text
kitchen_island, base_cabinet, cabinet, countertop, sink_cabinet, stove, fridge
```

校验器会计算这些矩形对象之间的最短距离。如果重叠，会输出 `kitchen_workflow_collision`；如果没有重叠但距离小于要求，会输出 `kitchen_workflow_clearance_warning`。

默认操作距离来自 `tolerance.kitchen_work_clearance_mm`，默认 900mm。单个对象也可以用 `work_clearance_mm` 覆盖。

这个规则用于控制类似“把方案 A 的厨房岛台融合到方案 B”这类操作：对象可以复制，但复制后必须重新校验，不能只看生成图是否好看。

## 通道宽度校验

`circulation_paths` 用来登记需要保持可通行的路径。第一版不自动生成全屋动线，而是检查给定路径是否被墙或家具侵占。

示例：

```json
"circulation_paths": [
  {"id": "P-WEST-CLEAR", "start": [800, 700], "end": [2600, 700], "required_width_mm": 800}
]
```

校验器会把这条线当作通道中心线，要求墙和家具距离中心线至少达到 `required_width_mm / 2`。如果不足，会输出 `circulation_width_warning`。

默认通道宽度来自 `tolerance.circulation_width_mm`，默认 800mm。真实项目中可以按空间类型提高或降低，例如厨房操作区、床边通道、玄关主通道分别设置不同路径。
## 家具碰撞和安全距离

家具对象如果使用矩形 `geometry.kind = "rect"`，校验器会检查家具之间是否重叠，以及家具之间的最短距离是否满足 `clearance_mm`。

可能输出：

- `furniture_furniture_collision`：两个家具矩形发生重叠或相交。
- `furniture_clearance_warning`：两个家具没有重叠，但距离小于要求的 `clearance_mm`。
- `door_swing_clearance_warning`：家具虽然没有直接挡住门扇，但离门扇开启线太近。

默认家具间距容差来自家具自己的 `clearance_mm`，如果没有设置，则使用 `tolerance.furniture_clearance_mm`，默认 100mm。门扇安全距离使用 `tolerance.door_clearance_mm`，默认 50mm。
## 门扇开启范围校验

门对象如果带有 `width` 和 `swing`，校验器会估算门扇从关闭到约 90 度打开时的扫掠范围，并输出 `door_swing_checks`。

第一版采用轻量近似：把门扇当成一条线段，按 15、30、45、60、75、90 度采样，检查是否碰到非宿主墙或矩形家具。

可能输出的警告包括：

- `door_swing_wall_collision`：门扇打开时碰到墙。
- `door_swing_furniture_collision`：门扇打开时碰到家具。
- `door_swing_incomplete`：门不在声明的宿主墙上，或缺少门宽、开启方向、铰链侧等信息。

当前门扇方向使用简化约定：相对宿主墙从 start 到 end 的方向，`inward` 默认向左侧旋转，`outward` 默认向右侧旋转。真实项目中如果门方向与现场不一致，应先修正对象数据再校验。

## 弧形隔断校验

弧形墙使用 `geometry.kind = "arc"` 表示，字段包括：

```json
{
  "kind": "arc",
  "center": [6100, 3300],
  "radius": 1600,
  "start_angle": 210,
  "end_angle": 330,
  "thickness": 100
}
```

第一版不会做完整 CAD 曲线布尔运算，而是把弧线按角度采样成短线段，再复用已有的墙体、家具碰撞和通道宽度校验。校验报告会增加 `wall_segment_count`，用于说明实际参与计算的墙段数量。

## 房间边界覆盖率

房间 `polygon` 的每条边现在会输出 `boundary_edges`，用于说明这条边：

- 离最近墙多远。
- 被哪些墙支撑。
- 墙体覆盖比例 `wall_coverage` 是多少。
- 是否是允许开放的边界 `open_edge`。

如果一条房间边离墙很近，但墙只覆盖了其中一小段，校验器会输出 `room_edge_under_supported`。这能帮助发现“看起来是一个房间边界，但墙其实只画了一半”的问题。

开放式客餐厅、半墙、垭口、连续空间等可以在 room 对象里标记：

```json
"open_edges": [2]
```

`open_edges` 使用 polygon 边的序号：第 0 条边是第 1 个点到第 2 个点，第 1 条边是第 2 个点到第 3 个点，依此类推。
## 几何后端

这个工具不追求所有几何算法都从零手写。优先策略是：

```text
对象模型、版本、操作记录：我们自己控制
底层几何计算：能用成熟库就用成熟库
```

当前支持两种后端：

- `builtin`：无依赖内置算法，当前本机默认使用它。
- `shapely`：如果 Python 环境安装了 Shapely，校验器会自动使用它处理线段距离、相交、多边形面积等底层计算。

校验报告里会显示：

```json
"geometry_backend": "builtin"
```

或：

```json
"geometry_backend": "shapely"
```

本机当前 Codex bundled Python 尚未安装 Shapely，所以不会强行联网安装。以后如果环境允许，可以安装：

```powershell
& 'C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pip install shapely
```

安装后无需修改对象 JSON，重新运行校验器即可自动切换到 Shapely。
## 当前代码分层

现在代码分成三层：

```text
geometry_backend.py
  底层几何计算适配层。有 Shapely 就用 Shapely，没有就用 builtin。

geometry_validator.py
  家装对象校验规则。负责 Wall / Door / Window / Room / Furniture 的业务判断和 L0-L4 等级。

operation_applier.py
  对象级操作。负责拆墙、加家具、移动对象、跨方案复制对象意图。

simple_renderer.py
  SVG 检查图。只用于看清对象数据和警告位置，不是最终方案图。
```

后续如果替换 Shapely、增加别的几何库，优先改 `geometry_backend.py`，不要把库调用散落到业务规则里。
