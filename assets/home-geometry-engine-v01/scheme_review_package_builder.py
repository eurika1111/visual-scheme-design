#!/usr/bin/env python3
"""Build a client-visible, same-scale review package for isolated scheme options."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image

from geometry_validator import validate
from scheme_draft_renderer import merge_scheme, unresolved_placements
from simple_renderer import collect_points, render_model


ENGINE_DIR = Path(__file__).resolve().parent
SCHEME_CODES = {"方案 A": "A", "方案 B": "B", "方案 C": "C"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fixed_bounds(base: dict[str, Any]) -> tuple[float, float, float, float]:
    points = collect_points(base, None)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return (min(xs), min(ys), max(xs), max(ys))


def base_versions(base: dict[str, Any]) -> set[str]:
    versions = {str(value) for value in (base.get("version"), base.get("schema_version")) if value}
    for key in ("walls", "rooms", "openings", "fixed_fixtures"):
        versions.update(str(item["version"]) for item in base.get(key, []) or [] if item.get("version"))
    return versions


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def option_code(intent: dict[str, Any], index: int) -> str:
    return SCHEME_CODES.get(intent.get("scheme_id"), chr(ord("A") + index))


def compact_fallbacks(intent: dict[str, Any]) -> list[str]:
    lines = []
    for item in intent.get("proposal_objects", []) or []:
        if item.get("placement_variant") != "compact_fallback":
            continue
        size = (item.get("geometry") or {}).get("size", [])
        size_text = " x ".join(str(round(float(value))) for value in size) if size else "unknown"
        lines.append(f"{item.get('name', item.get('id'))} `{item.get('id')}`: {size_text} mm")
    return lines


def object_lines(intent: dict[str, Any]) -> list[str]:
    lines = []
    for item in intent.get("proposal_objects", []) or []:
        geom = item.get("geometry") or {}
        size = geom.get("size") or []
        size_text = " x ".join(str(round(float(value))) for value in size) if size else "unknown"
        lines.append(
            f"{item.get('name', item.get('category', '对象'))} `{item.get('id')}`"
            f"，位置 `{item.get('target_space_id', 'unknown')}`，尺寸 {size_text} mm"
        )
    return lines


def deferred_lines(intent: dict[str, Any]) -> list[str]:
    return [
        f"`{item.get('id')}`：{item.get('purpose', '待确认事项')}"
        for item in intent.get("placement_requests", []) or []
        if item.get("status") == "deferred_confirmation"
    ]


def feedback_lines(intent: dict[str, Any]) -> list[str]:
    lines = []
    for item in intent.get("feedback_operations", []) or []:
        prefix = f"`{item.get('feedback_id')}`："
        if item.get("action") in {"copy_object", "replace_object"}:
            detail = (
                f"从 `{item.get('source_scheme')}` 复制对象 `{item.get('source_object_id')}`，"
                f"生成 `{item.get('new_object_id')}`"
            )
            if item.get("replace_target_object_id"):
                detail += f"，替换 `{item.get('replace_target_object_id')}`"
        elif item.get("action") == "move_object":
            detail = f"移动对象 `{item.get('target_object_id')}` 到 `{', '.join(item.get('target_spaces', []))}`"
        elif item.get("action") == "rotate_object":
            detail = f"将对象 `{item.get('target_object_id')}` 旋转到 {item.get('rotation')} 度"
        elif item.get("action") == "remove_object":
            detail = f"删除方案对象 `{item.get('target_object_id')}`"
        else:
            detail = f"执行 `{item.get('action')}`"
        lines.append(prefix + detail)
    return lines


def markdown_list(items: list[str], empty: str = "无") -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {empty}"


def build_markdown(options: list[dict[str, Any]], output_dir: Path, manifest_path: Path) -> str:
    sections = []
    for option in options:
        intent = option["intent"]
        report = option["validation"]
        operations = [item.get("description", item.get("type", "方案操作")) for item in intent.get("operations", []) or []]
        sections.append(
            f"""## {intent.get('scheme_id')}：{intent.get('name')}

![{intent.get('scheme_id')}](<{relative(option['svg'], output_dir)}>)

- 方向：{intent.get('intent_summary', '未填写')}
- 版本：`{intent.get('version', 'unknown')}`，父版本 `{intent.get('parent_intent', 'root')}`
- 风险等级：`{intent.get('risk_level', 'unknown')}`
- 校验：`{report.get('readiness', 'unknown')}`，错误 {len(report.get('errors', []) or [])}，提醒 {len(report.get('warnings', []) or [])}
- 统一坐标：左下角 `(0,0)`，单位 `mm`

主要变化：

{markdown_list(operations)}

客户反馈操作：

{markdown_list(feedback_lines(intent))}

已落位对象：

{markdown_list(object_lines(intent))}

紧凑尺寸后备：

{markdown_list(compact_fallbacks(intent))}

仍需确认：

{markdown_list(deferred_lines(intent))}
"""
        )

    single = len(options) == 1
    title = "选定方案确认包" if single else "A/B/C 方案草图复核包"
    usage = (
        "- 当前页面用于确认已选方案的结构、家具、尺寸与待确认事项。"
        if single
        else "- 各方案使用同一底图边界、同一比例、同一左下角坐标原点和毫米单位，可直接横向比较。"
    )
    return f"""# {title}

## 使用说明

{usage}
- 图中墙体、门窗、房间和家具来自对象数据；AI 图片尚未参与本阶段。
- 这是方案讨论图，不是施工图。需要施工或深化时仍需现场复尺。
- 复核清单数据：`{relative(manifest_path, output_dir)}`

{''.join(sections)}
## 请客户确认

1. {'当前方案的结构和主要功能是否可以继续深化？' if single else '哪个方案最接近希望继续深化的方向？'}
2. 是否要把另一方案中的某个已编号对象融合进来？请直接说方案和对象名称即可。
3. 哪些家具位置、尺寸或朝向明显不合适？
4. 标为“仍需确认”的拆墙或高风险想法，是否继续研究？
5. 确认后再进入视觉风格和材质表现，不用现在决定所有细节。
"""


def build_package(base_path: Path, intent_paths: list[Path], output_dir: Path) -> dict[str, Any]:
    base_path = base_path.resolve()
    intent_paths = [path.resolve() for path in intent_paths]
    output_dir = output_dir.resolve()
    base = load_json(base_path)
    authority_versions = base_versions(base)
    bounds = fixed_bounds(base)
    output_dir.mkdir(parents=True, exist_ok=True)
    intents = [load_json(path) for path in intent_paths]

    blockers = []
    seen_ids: dict[str, str] = {}
    for index, intent in enumerate(intents):
        label = intent.get("scheme_id") or f"option_{index + 1}"
        if intent.get("layout_gate") != "ready" or unresolved_placements(intent):
            blockers.append(f"{label}: unresolved placement requests")
        if intent.get("parent_base") not in authority_versions:
            blockers.append(f"{label}: parent_base does not match {sorted(authority_versions)}")
        for item in intent.get("proposal_objects", []) or []:
            object_id = item.get("id")
            if not object_id:
                blockers.append(f"{label}: proposal object missing id")
            elif object_id in seen_ids:
                blockers.append(f"{label}: object id {object_id} already belongs to {seen_ids[object_id]}")
            else:
                seen_ids[object_id] = label

    manifest_path = output_dir / "scheme_review_manifest.json"
    if blockers:
        manifest = {"schema_version": "scheme_review_manifest_v1", "status": "blocked", "blockers": blockers}
        write_json(manifest_path, manifest)
        return manifest

    options = []
    for index, intent in enumerate(intents):
        code = option_code(intent, index)
        stem = f"scheme_{code}"
        model = merge_scheme(base, intent)
        validation = validate(model)
        errors = validation.get("errors", []) or []
        if errors:
            blockers.append(f"{intent.get('scheme_id')}: validation has {len(errors)} errors")
            continue

        model_path = output_dir / f"{stem}.review_model.json"
        validation_path = output_dir / f"{stem}.review_validation.json"
        svg_path = output_dir / f"{stem}.review.svg"
        png_path = output_dir / f"{stem}.review.png"
        write_json(model_path, model)
        write_json(validation_path, validation)
        svg_path.write_text(
            render_model(
                model,
                validation,
                mode="client",
                title=f"{intent.get('scheme_id')} | {intent.get('name')}",
                bounds=bounds,
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, "svg_preview_renderer.py", str(svg_path), str(png_path), "--max-width", "1600"],
            cwd=ENGINE_DIR,
        )
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)
        options.append({
            "code": code,
            "intent": intent,
            "validation": validation,
            "model": model_path,
            "validation_path": validation_path,
            "svg": svg_path,
            "png": png_path,
            "preview_size_px": Image.open(png_path).size,
        })

    preview_sizes = {tuple(item["preview_size_px"]) for item in options}
    if len(preview_sizes) > 1:
        blockers.append(f"preview sizes differ: {sorted(preview_sizes)}")
    manifest = {
        "schema_version": "scheme_review_manifest_v1",
        "status": "ready" if not blockers and len(options) == len(intents) else "blocked",
        "base_model": str(base_path.resolve()),
        "base_version": intents[0].get("parent_base"),
        "coordinate_system": {"origin": "lower_left", "x_axis": "right", "y_axis": "up", "unit": "mm"},
        "shared_bounds_mm": {"min_x": bounds[0], "min_y": bounds[1], "max_x": bounds[2], "max_y": bounds[3]},
        "same_scale": len(preview_sizes) == 1,
        "shared_preview_size_px": list(next(iter(preview_sizes))) if len(preview_sizes) == 1 else None,
        "blockers": blockers,
        "options": [
            {
                "scheme_id": item["intent"].get("scheme_id"),
                "version": item["intent"].get("version"),
                "model": str(item["model"].resolve()),
                "validation": str(item["validation_path"].resolve()),
                "svg": str(item["svg"].resolve()),
                "png": str(item["png"].resolve()),
                "preview_size_px": list(item["preview_size_px"]),
                "proposal_object_ids": [obj.get("id") for obj in item["intent"].get("proposal_objects", []) or []],
                "deferred_request_ids": [
                    req.get("id") for req in item["intent"].get("placement_requests", []) or []
                    if req.get("status") == "deferred_confirmation"
                ],
            }
            for item in options
        ],
    }
    write_json(manifest_path, manifest)
    if manifest["status"] == "ready":
        (output_dir / "scheme_review.md").write_text(
            build_markdown(options, output_dir, manifest_path), encoding="utf-8"
        )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a same-scale client review package for scheme options.")
    parser.add_argument("base_model", type=Path)
    parser.add_argument("scheme_intents", type=Path, nargs="+")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= len(args.scheme_intents) <= 3:
        parser.error("provide one to three isolated scheme intents")
    manifest = build_package(args.base_model, args.scheme_intents, args.output_dir)
    print(f"review_manifest={args.output_dir / 'scheme_review_manifest.json'}")
    print(f"review_status={manifest['status']} options={len(manifest.get('options', []))}")
    return 0 if manifest["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
