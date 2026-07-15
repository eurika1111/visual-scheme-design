#!/usr/bin/env python3
"""Check locked-canvas metadata and build honest visual review aids for a concept image."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dimension_text(model: dict[str, Any], axis: str) -> str:
    chains = model.get("dimension_chains", []) or model.get("dimensions", []) or []
    for chain in chains:
        if chain.get("axis") != axis:
            continue
        segments = chain.get("segments_mm", []) or []
        if segments:
            values = " + ".join(f"{float(value):g}" for value in segments)
            return f"{chain.get('id', axis.upper())}: {values} = {sum(float(value) for value in segments):g} mm"
    return f"{axis.upper()}: no confirmed dimension chain"


def annotate(image: Image.Image, lock: dict[str, Any], model: dict[str, Any]) -> Image.Image:
    margin_left, margin_top, margin_right, margin_bottom = 84, 86, 76, 62
    result = Image.new(
        "RGB",
        (image.width + margin_left + margin_right, image.height + margin_top + margin_bottom),
        "white",
    )
    result.paste(image.convert("RGB"), (margin_left, margin_top))
    draw = ImageDraw.Draw(result)
    frame = (margin_left, margin_top, margin_left + image.width - 1, margin_top + image.height - 1)
    draw.rectangle(frame, outline="#111827", width=2)
    draw.text((margin_left, 18), dimension_text(model, "x"), fill="#111827")
    draw.text((margin_left, 38), dimension_text(model, "y"), fill="#111827")
    draw.text(
        (margin_left, margin_top + image.height + 20),
        f"base={lock.get('base_id')} | origin=lower-left | canvas={image.width}x{image.height}px | dimensions=locked",
        fill="#374151",
    )
    return result


def build_review(args: argparse.Namespace) -> dict[str, Any]:
    lock = load_json(args.base_lock)
    if lock.get("base_lock_status") != "locked":
        raise ValueError("base lock is not locked")
    locked_visual = Path((lock.get("confirmation_visual") or {}).get("path", ""))
    if not locked_visual.exists():
        raise ValueError("locked confirmation visual is missing")
    if sha256(locked_visual) != (lock.get("confirmation_visual") or {}).get("sha256"):
        raise ValueError("locked confirmation visual has changed")
    if locked_visual.suffix.lower() == ".svg":
        raise ValueError("concept review needs a raster confirmation preview; lock the matching PNG preview")

    generated = args.generated_image.resolve()
    with Image.open(locked_visual) as base_source, Image.open(generated) as generated_source:
        base = base_source.convert("RGB")
        concept = generated_source.convert("RGB")
    expected = (int(lock["canvas"]["width"]), int(lock["canvas"]["height"]))
    canvas_match = base.size == expected and concept.size == expected
    args.output_dir.mkdir(parents=True, exist_ok=True)

    files: dict[str, str | None] = {"side_by_side": None, "overlay_50": None, "annotated_output": None}
    if canvas_match:
        side = Image.new("RGB", (expected[0] * 2, expected[1]), "white")
        side.paste(base, (0, 0))
        side.paste(concept, (expected[0], 0))
        side_path = args.output_dir / "concept_compare_side_by_side.png"
        side.save(side_path)
        overlay_path = args.output_dir / "concept_compare_overlay_50.png"
        Image.blend(base, concept, 0.5).save(overlay_path)
        model = load_json(Path((lock.get("base_model") or {})["path"]))
        annotated_path = args.output_dir / "concept_output_annotated.png"
        annotate(concept, lock, model).save(annotated_path)
        files = {
            "side_by_side": str(side_path.resolve()),
            "overlay_50": str(overlay_path.resolve()),
            "annotated_output": str(annotated_path.resolve()),
        }

    result = args.review_result
    if not canvas_match:
        status = "rejected_canvas_mismatch"
        result = "rejected"
    elif result == "passed":
        status = "reviewed_passed"
    elif result in {"needs_repair", "rejected"}:
        status = result
    else:
        status = "ready_for_structural_review"
    return {
        "schema_version": "concept_output_review_v1",
        "status": status,
        "base_id": lock.get("base_id"),
        "generated_image": str(generated),
        "generated_sha256": sha256(generated),
        "expected_canvas_px": list(expected),
        "actual_canvas_px": list(concept.size),
        "canvas_match": canvas_match,
        "structure_review_result": result,
        "review_notes": args.notes,
        "review_files": files,
        "automatic_scope": ["locked file integrity", "exact canvas size", "fixed comparison outputs"],
        "manual_or_ai_scope": [
            "outline and wall junction drift", "door and window drift", "fixed-service drift",
            "authorized operation accuracy", "furniture and circulation plausibility"
        ],
        "image_is_geometry_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Review one generated concept against a locked residential base.")
    parser.add_argument("--base-lock", type=Path, required=True)
    parser.add_argument("--generated-image", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--review-result", choices=("pending", "passed", "needs_repair", "rejected"), default="pending")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    args.base_lock = args.base_lock.resolve()
    args.output_dir = args.output_dir.resolve()
    report = build_review(args)
    report_path = args.output_dir / "concept_output_review.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"concept_review={report_path}")
    print(f"concept_review_status={report['status']} canvas_match={report['canvas_match']}")
    return 0 if report["canvas_match"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
