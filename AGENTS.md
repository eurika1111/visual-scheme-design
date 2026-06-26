# 通用工作约定

- 默认使用中文，先给结论，表达简洁；复杂任务再补充必要细节。
- 开始工作前先检查现有文件和项目结构，优先复用已有成果，避免重复创建。
- 修改现有项目时保持改动范围最小，不擅自扩大任务或重做无关内容。
- 用户要求“只整理结构、方案或大纲”时，不生成图片、视频或其他额外资产。
- 先识别真实项目目录；最终文件保存在对应项目的 `outputs`、`assets` 或用户指定目录，不把应用缓存目录当作交付位置。
- 搜索时优先读取入口文档、源文件和当前版本；除非任务需要，不扫描缓存、导出物、生成图片和历史版本目录。
- 完成修改后执行与风险相称的验证；无法验证时明确说明未验证部分。
- 只有会实质改变结果的歧义才询问用户，其余采用保守、可逆的假设继续推进。
- 可行性不确定时，区分事实、推断和建议；客观说明风险，不默认顺从用户设想。
- 简单查找、整理和机械修改优先采用轻量路径；复杂设计、排错和最终审核再提高推理强度。

# 本地工具规避规则

- 不直接使用裸 `python` 命令。当前 Windows 环境中 `python.exe` 指向 `C:\Users\eurik\AppData\Local\Microsoft\WindowsApps\python.exe` 占位启动器，可能无输出或异常退出。需要 Python 时优先使用 Codex bundled Python：`C:\Users\eurik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。
- `skill-creator/scripts/quick_validate.py` 依赖 `PyYAML`，当前 bundled Python 未安装该依赖。验证 skill 时若缺少 `yaml` 模块，不要反复重试或联网安装，改用目标 skill 自带的无依赖轻量校验脚本，或运行一段无依赖 frontmatter/引用检查。
- 对 `C:\Users\eurik\.codex\skills\...` 下的 skill 文件做读写时，当前沙箱可能触发 Windows 权限错误；需要时直接使用 `require_escalated` 并说明是读写用户显式指定的 Codex skill 文件。


- 维护 `assets/home-geometry-engine-v01` 时，优先运行 `D:\Codex\视觉方案\assets\home-geometry-engine-v01\scripts\run_geometry_demo.ps1` 做语法检查、示例校验和 SVG 渲染，不要反复手拼长命令。

