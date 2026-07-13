#!/usr/bin/env python3
"""Unified lightweight entrypoint for home scheme-base checks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ENGINE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = Path(r"D:\Codex\视觉方案\outputs\geometry-engine-workflow")


def run_step(label: str, args: list[str]) -> None:
    print(f"== {label}", flush=True)
    completed = subprocess.run([sys.executable, *args], cwd=ENGINE_DIR)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def check_source(package: Path, output_dir: Path) -> None:
    output_dir = ensure_dir(output_dir)
    validation = output_dir / "source_extraction.validation.json"
    audit = output_dir / "dimension_chain_audit.json"
    run_step("validate scheme base", ["validate_source_extraction.py", str(package), str(validation)])
    run_step("audit dimensions", ["dimension_chain_audit.py", str(package), str(audit)])
    print(f"validation={validation}")
    print(f"dimension_audit={audit}")


def make_checklist(package: Path, output_dir: Path) -> None:
    output_dir = ensure_dir(output_dir)
    draft = output_dir / "dimension_anchor_draft.json"
    checklist_json = output_dir / "dimension_anchor_confirmation_checklist.json"
    checklist_md = output_dir / "dimension_anchor_confirmation_checklist.md"
    run_step("draft dimension anchors", ["dimension_chain_anchor_drafter.py", str(package), str(draft)])
    run_step(
        "build confirmation checklist",
        [
            "dimension_anchor_confirmation_checklist.py",
            str(draft),
            str(checklist_json),
            str(checklist_md),
            "--title",
            "Dimension Anchor Confirmation Checklist",
        ],
    )
    print(f"anchor_draft={draft}")
    print(f"checklist_json={checklist_json}")
    print(f"checklist_md={checklist_md}")


def apply_confirmation(package: Path, checklist: Path, response: Path, output_dir: Path, version: str) -> None:
    output_dir = ensure_dir(output_dir)
    confirmed = output_dir / "source_extraction.anchors_confirmed.json"
    report = output_dir / "dimension_anchor_confirmation_apply.report.json"
    validation = output_dir / "source_extraction.anchors_confirmed.validation.json"
    run_step(
        "apply confirmation response",
        [
            "apply_dimension_anchor_confirmation.py",
            str(package),
            str(checklist),
            str(response),
            str(confirmed),
            str(report),
            "--version",
            version,
        ],
    )
    run_step("validate confirmed scheme base", ["validate_source_extraction.py", str(confirmed), str(validation)])
    print(f"confirmed_package={confirmed}")
    print(f"apply_report={report}")
    print(f"validation={validation}")


def render_review(package: Path, output_svg: Path) -> None:
    ensure_dir(output_svg.parent)
    run_step("render dimension anchor review", ["dimension_anchor_review_svg.py", str(package), str(output_svg)])
    print(f"review_svg={output_svg}")


def build_handoff(
    base_model: Path,
    review_svg: Path,
    preview_png: Path | None,
    validation: Path,
    output: Path,
    project_root: Path,
    source_image: Path | None,
    dimension_audit: Path | None,
    checklist: Path | None,
    checklist_md: Path | None,
    title: str | None,
) -> None:
    ensure_dir(output.parent)
    child_args = [
        "base_handoff_builder.py",
        "--project-root",
        str(project_root),
        "--base-model",
        str(base_model),
        "--review-svg",
        str(review_svg),
        "--validation",
        str(validation),
        "--output",
        str(output),
    ]
    for flag, value in [
        ("--source-image", source_image),
        ("--preview-png", preview_png),
        ("--dimension-audit", dimension_audit),
        ("--checklist", checklist),
        ("--checklist-md", checklist_md),
    ]:
        if value:
            child_args.extend([flag, str(value)])
    if title:
        child_args.extend(["--title", title])
    run_step("build client base handoff", child_args)

def build_base_review(
    base_model: Path,
    validation: Path,
    output_dir: Path,
    project_root: Path,
    source_image: Path | None,
    dimension_audit: Path | None,
    checklist: Path | None,
    checklist_md: Path | None,
    title: str | None,
    stem: str,
) -> None:
    output_dir = ensure_dir(output_dir)
    review_svg = output_dir / f"{stem}.client_base.svg"
    preview_png = output_dir / f"{stem}.client_base.preview.png"
    handoff = output_dir / f"{stem}.base_handoff.md"
    run_step(
        "render client base SVG",
        [
            "simple_renderer.py",
            str(base_model),
            str(review_svg),
            str(validation),
            "--mode",
            "client",
            "--title",
            title or "Client Base Confirmation",
        ],
    )
    run_step("render client base PNG preview", ["svg_preview_renderer.py", str(review_svg), str(preview_png), "--max-width", "1600"])
    build_handoff(
        base_model,
        review_svg,
        preview_png,
        validation,
        handoff,
        project_root,
        source_image,
        dimension_audit,
        checklist,
        checklist_md,
        title or "Client Base Review Package",
    )
    print(f"review_svg={review_svg}")
    print(f"preview_png={preview_png}")
    print(f"handoff={handoff}")


def build_needs_brief(response: Path, output_dir: Path, stem: str) -> None:
    response = response.resolve()
    output_dir = ensure_dir(output_dir.resolve())
    output_json = output_dir / f"{stem}.needs_brief.json"
    output_md = output_dir / f"{stem}.needs_brief.md"
    run_step(
        "build needs brief",
        [
            "needs_brief_builder.py",
            str(response),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ],
    )
    print(f"needs_brief_json={output_json}")
    print(f"needs_brief_md={output_md}")


def plan_options(base_model: Path, needs_brief: Path, output_dir: Path, case_strategy: Path | None) -> None:
    base_model = base_model.resolve()
    needs_brief = needs_brief.resolve()
    case_strategy = case_strategy.resolve() if case_strategy else None
    output_dir = ensure_dir(output_dir.resolve())
    child_args = [
        "scheme_option_planner.py",
        str(base_model),
        str(needs_brief),
        "--output-dir",
        str(output_dir),
    ]
    if case_strategy:
        child_args.extend(["--case-strategy", str(case_strategy)])
    run_step("plan isolated scheme options", child_args)


def resolve_layout(base_model: Path, scheme_intent: Path, output_dir: Path, version: str | None) -> None:
    base_model = base_model.resolve()
    scheme_intent = scheme_intent.resolve()
    output_dir = ensure_dir(output_dir.resolve())
    stem = version or scheme_intent.stem.replace("_intent", "")
    resolved_intent = output_dir / f"{stem}.layout_intent.json"
    report = output_dir / f"{stem}.placement_report.json"
    child_args = [
        "scheme_placement_resolver.py",
        str(base_model),
        str(scheme_intent),
        "--output-intent",
        str(resolved_intent),
        "--report-output",
        str(report),
    ]
    if version:
        child_args.extend(["--version", f"{version}_layout_v1"])
    run_step("resolve scheme placements", child_args)


def build_scheme_review(base_model: Path, scheme_intents: list[Path], output_dir: Path) -> None:
    base_model = base_model.resolve()
    scheme_intents = [path.resolve() for path in scheme_intents]
    output_dir = ensure_dir(output_dir.resolve())
    run_step(
        "build same-scale scheme review package",
        [
            "scheme_review_package_builder.py",
            str(base_model),
            *(str(path) for path in scheme_intents),
            "--output-dir",
            str(output_dir),
        ],
    )


def apply_scheme_feedback(
    base_model: Path,
    source_intent: Path,
    target_intent: Path,
    feedback: Path,
    output_dir: Path,
) -> None:
    base_model = base_model.resolve()
    source_intent = source_intent.resolve()
    target_intent = target_intent.resolve()
    feedback = feedback.resolve()
    output_dir = ensure_dir(output_dir.resolve())
    stem = feedback.stem
    run_step(
        "apply controlled scheme feedback",
        [
            "scheme_feedback_migrator.py",
            str(base_model),
            str(source_intent),
            str(target_intent),
            str(feedback),
            "--output-intent",
            str(output_dir / f"{stem}.migrated_intent.json"),
            "--report-output",
            str(output_dir / f"{stem}.migration_report.json"),
        ],
    )


def manage_scheme_history(history: Path, history_args: list[str]) -> None:
    if not history_args:
        raise SystemExit("scheme-history requires an action such as register, activate, set-status, branch, or show")
    history_args = list(history_args)
    if history_args[0] == "register" and len(history_args) > 1:
        history_args[1] = str(Path(history_args[1]).resolve())
        for flag in ("--validation", "--review"):
            if flag in history_args and history_args.index(flag) + 1 < len(history_args):
                index = history_args.index(flag) + 1
                history_args[index] = str(Path(history_args[index]).resolve())
    if history_args[0] == "branch" and "--output-intent" in history_args:
        index = history_args.index("--output-intent") + 1
        if index < len(history_args):
            history_args[index] = str(Path(history_args[index]).resolve())
    run_step(
        "manage scheme version history",
        ["scheme_history_manager.py", str(history.resolve()), *history_args],
    )


def render_scheme_draft(base_model: Path, scheme_intent: Path, output_dir: Path, version: str | None) -> None:
    base_model = base_model.resolve()
    scheme_intent = scheme_intent.resolve()
    output_dir = ensure_dir(output_dir.resolve())
    stem = version or scheme_intent.stem.replace("_intent", "")
    draft_model = output_dir / f"{stem}.draft_model.json"
    validation = output_dir / f"{stem}.validation.json"
    svg = output_dir / f"{stem}.draft.svg"
    report = output_dir / f"{stem}.draft_report.json"
    run_step(
        "render deterministic scheme draft",
        [
            "scheme_draft_renderer.py",
            str(base_model),
            str(scheme_intent),
            "--output-model",
            str(draft_model),
            "--validation-output",
            str(validation),
            "--svg-output",
            str(svg),
            "--report-output",
            str(report),
        ],
    )


def run_demo(output_dir: Path) -> None:
    script = ENGINE_DIR / "scripts" / "run_geometry_demo.ps1"
    print("== run geometry demo", flush=True)
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-OutputDir",
            str(output_dir),
        ],
        cwd=ENGINE_DIR,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Home scheme-base workflow entrypoint.")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check-source", help="Validate a source extraction package and audit dimensions.")
    check.add_argument("package", type=Path)
    check.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)

    checklist = sub.add_parser("make-checklist", help="Create dimension anchor draft and confirmation checklist.")
    checklist.add_argument("package", type=Path)
    checklist.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)

    apply = sub.add_parser("apply-confirmation", help="Apply human confirmation response and revalidate.")
    apply.add_argument("package", type=Path)
    apply.add_argument("checklist", type=Path)
    apply.add_argument("response", type=Path)
    apply.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    apply.add_argument("--version", default="source_extraction_confirmed_v1")

    review = sub.add_parser("render-review", help="Render a dimension anchor review SVG.")
    review.add_argument("package", type=Path)
    review.add_argument("output_svg", type=Path)

    handoff = sub.add_parser("build-handoff", help="Build a client-visible base handoff markdown.")
    handoff.add_argument("--base-model", type=Path, required=True)
    handoff.add_argument("--review-svg", type=Path, required=True)
    handoff.add_argument("--preview-png", type=Path)
    handoff.add_argument("--validation", type=Path, required=True)
    handoff.add_argument("--output", type=Path, required=True)
    handoff.add_argument("--project-root", type=Path, default=Path.cwd())
    handoff.add_argument("--source-image", type=Path)
    handoff.add_argument("--dimension-audit", type=Path)
    handoff.add_argument("--checklist", type=Path)
    handoff.add_argument("--checklist-md", type=Path)
    handoff.add_argument("--title")

    base_review = sub.add_parser("build-base-review", help="Render client SVG, PNG preview, and handoff markdown.")
    base_review.add_argument("--base-model", type=Path, required=True)
    base_review.add_argument("--validation", type=Path, required=True)
    base_review.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    base_review.add_argument("--project-root", type=Path, default=Path.cwd())
    base_review.add_argument("--source-image", type=Path)
    base_review.add_argument("--dimension-audit", type=Path)
    base_review.add_argument("--checklist", type=Path)
    base_review.add_argument("--checklist-md", type=Path)
    base_review.add_argument("--title")
    base_review.add_argument("--stem", default="base_review")

    needs = sub.add_parser("build-needs-brief", help="Build structured residential needs brief from client answers.")
    needs.add_argument("response", type=Path)
    needs.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    needs.add_argument("--stem", default="client")

    options = sub.add_parser("plan-options", help="Build isolated A/B/C scheme intents from base and needs brief.")
    options.add_argument("base_model", type=Path)
    options.add_argument("needs_brief", type=Path)
    options.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    options.add_argument("--case-strategy", type=Path)

    placement = sub.add_parser("resolve-layout", help="Resolve placement requests into validated furniture coordinates.")
    placement.add_argument("base_model", type=Path)
    placement.add_argument("scheme_intent", type=Path)
    placement.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    placement.add_argument("--version")

    scheme_review = sub.add_parser("build-scheme-review", help="Build a same-scale client review package for two or three schemes.")
    scheme_review.add_argument("base_model", type=Path)
    scheme_review.add_argument("scheme_intents", type=Path, nargs="+")
    scheme_review.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)

    feedback = sub.add_parser("apply-scheme-feedback", help="Apply controlled furniture feedback to a new scheme version and revalidate.")
    feedback.add_argument("base_model", type=Path)
    feedback.add_argument("source_intent", type=Path)
    feedback.add_argument("target_intent", type=Path)
    feedback.add_argument("feedback", type=Path)
    feedback.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)

    history = sub.add_parser("scheme-history", help="Register, activate, reject, show, or branch immutable scheme versions.")
    history.add_argument("history", type=Path)
    history.add_argument("history_args", nargs=argparse.REMAINDER)

    draft = sub.add_parser("render-scheme-draft", help="Render a deterministic SVG draft from base model and scheme intent.")
    draft.add_argument("base_model", type=Path)
    draft.add_argument("scheme_intent", type=Path)
    draft.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    draft.add_argument("--version")

    demo = sub.add_parser("run-demo", help="Run the bundled demo workflow.")
    demo.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "check-source":
        check_source(args.package, args.output_dir)
    elif args.command == "make-checklist":
        make_checklist(args.package, args.output_dir)
    elif args.command == "apply-confirmation":
        apply_confirmation(args.package, args.checklist, args.response, args.output_dir, args.version)
    elif args.command == "render-review":
        render_review(args.package, args.output_svg)
    elif args.command == "build-handoff":
        build_handoff(
            args.base_model,
            args.review_svg,
            args.preview_png,
            args.validation,
            args.output,
            args.project_root,
            args.source_image,
            args.dimension_audit,
            args.checklist,
            args.checklist_md,
            args.title,
        )
    elif args.command == "build-base-review":
        build_base_review(
            args.base_model,
            args.validation,
            args.output_dir,
            args.project_root,
            args.source_image,
            args.dimension_audit,
            args.checklist,
            args.checklist_md,
            args.title,
            args.stem,
        )
    elif args.command == "build-needs-brief":
        build_needs_brief(args.response, args.output_dir, args.stem)
    elif args.command == "plan-options":
        plan_options(args.base_model, args.needs_brief, args.output_dir, args.case_strategy)
    elif args.command == "resolve-layout":
        resolve_layout(args.base_model, args.scheme_intent, args.output_dir, args.version)
    elif args.command == "build-scheme-review":
        build_scheme_review(args.base_model, args.scheme_intents, args.output_dir)
    elif args.command == "apply-scheme-feedback":
        apply_scheme_feedback(args.base_model, args.source_intent, args.target_intent, args.feedback, args.output_dir)
    elif args.command == "scheme-history":
        manage_scheme_history(args.history, args.history_args)
    elif args.command == "render-scheme-draft":
        render_scheme_draft(args.base_model, args.scheme_intent, args.output_dir, args.version)
    elif args.command == "run-demo":
        run_demo(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
