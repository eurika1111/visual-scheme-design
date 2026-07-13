#!/usr/bin/env python3
"""Maintain an immutable scheme-version registry with safe activate and branch operations."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {"candidate", "accepted", "rejected"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def empty_history() -> dict[str, Any]:
    return {
        "schema_version": "scheme_version_history_v1",
        "updated_at": now(),
        "active_versions": {},
        "versions": [],
        "events": [],
    }


def load_history(path: Path) -> dict[str, Any]:
    return load_json(path) if path.exists() else empty_history()


def find_entry(history: dict[str, Any], version: str) -> dict[str, Any] | None:
    return next((item for item in history.get("versions", []) if item.get("version") == version), None)


def add_event(history: dict[str, Any], action: str, version: str, note: str | None = None) -> None:
    history.setdefault("events", []).append({
        "timestamp": now(),
        "action": action,
        "version": version,
        "note": note,
    })
    history["updated_at"] = now()


def register(
    history: dict[str, Any],
    intent_path: Path,
    status: str,
    validation: Path | None,
    review: Path | None,
) -> tuple[bool, str]:
    if status not in ALLOWED_STATUSES:
        return False, f"unsupported status: {status}"
    intent_path = intent_path.resolve()
    intent = load_json(intent_path)
    version = intent.get("version")
    scheme_id = intent.get("scheme_id")
    if not version or not scheme_id:
        return False, "intent requires version and scheme_id"
    digest = file_hash(intent_path)
    existing = find_entry(history, version)
    if existing:
        if existing.get("sha256") != digest:
            return False, f"version {version} already exists with different content"
        existing.update({
            "status": status,
            "validation": str(validation.resolve()) if validation else existing.get("validation"),
            "review": str(review.resolve()) if review else existing.get("review"),
        })
        add_event(history, "register_existing", version, f"status={status}")
        return True, "existing version metadata updated"

    parent = intent.get("parent_intent")
    parent_entry = find_entry(history, parent) if parent else None
    if parent_entry and parent_entry.get("status") == "rejected":
        return False, f"rejected version cannot be a parent: {parent}"
    history.setdefault("versions", []).append({
        "scheme_id": scheme_id,
        "version": version,
        "parent": parent,
        "parent_registered": bool(parent_entry) if parent else None,
        "parent_base": intent.get("parent_base"),
        "status": status,
        "intent": str(intent_path),
        "sha256": digest,
        "validation": str(validation.resolve()) if validation else None,
        "review": str(review.resolve()) if review else None,
        "created_at": now(),
    })
    add_event(history, "register", version, f"status={status}")
    return True, "version registered"


def set_status(history: dict[str, Any], version: str, status: str) -> tuple[bool, str]:
    if status not in ALLOWED_STATUSES:
        return False, f"unsupported status: {status}"
    entry = find_entry(history, version)
    if not entry:
        return False, f"version not registered: {version}"
    if status == "rejected" and history.get("active_versions", {}).get(entry.get("scheme_id")) == version:
        return False, "activate another accepted version before rejecting the current version"
    entry["status"] = status
    add_event(history, "set_status", version, f"status={status}")
    return True, "status updated"


def activate(history: dict[str, Any], version: str) -> tuple[bool, str]:
    entry = find_entry(history, version)
    if not entry:
        return False, f"version not registered: {version}"
    if entry.get("status") != "accepted":
        return False, f"only accepted versions can be active: {version} is {entry.get('status')}"
    scheme_id = entry.get("scheme_id")
    previous = history.setdefault("active_versions", {}).get(scheme_id)
    history["active_versions"][scheme_id] = version
    add_event(history, "activate", version, f"previous={previous}")
    return True, "active version updated"


def branch(
    history: dict[str, Any],
    parent_version: str,
    new_version: str,
    output_intent: Path,
) -> tuple[bool, str]:
    parent = find_entry(history, parent_version)
    if not parent:
        return False, f"parent version not registered: {parent_version}"
    if parent.get("status") != "accepted":
        return False, f"only accepted versions can create branches: {parent_version} is {parent.get('status')}"
    if find_entry(history, new_version):
        return False, f"new version already registered: {new_version}"
    parent_path = Path(parent["intent"])
    if not parent_path.exists() or file_hash(parent_path) != parent.get("sha256"):
        return False, "parent intent file is missing or changed after registration"

    intent = copy.deepcopy(load_json(parent_path))
    intent["parent_intent"] = parent_version
    intent["version"] = new_version
    intent["status"] = "branch_candidate"
    intent["generation_report"] = {
        "status": "not_rendered",
        "geometry_authority": intent.get("parent_base"),
        "image_authority": False,
    }
    intent.setdefault("version_events", []).append({
        "action": "branch",
        "parent": parent_version,
        "version": new_version,
    })
    output_intent = output_intent.resolve()
    write_json(output_intent, intent)
    ok, message = register(history, output_intent, "candidate", None, None)
    if not ok:
        output_intent.unlink(missing_ok=True)
        return False, message
    add_event(history, "branch", new_version, f"parent={parent_version}")
    return True, "branch created"


def print_summary(history: dict[str, Any]) -> None:
    print(f"history_versions={len(history.get('versions', []))}")
    for scheme_id, version in history.get("active_versions", {}).items():
        print(f"active {scheme_id}={version}")
    for item in history.get("versions", []):
        print(
            f"- {item.get('scheme_id')} {item.get('version')}: {item.get('status')}, "
            f"parent={item.get('parent')}"
        )


def history_markdown(history: dict[str, Any]) -> str:
    active = history.get("active_versions", {})
    active_lines = [f"- {scheme_id}：`{version}`" for scheme_id, version in active.items()] or ["- 暂未选择"]
    version_lines = []
    for item in history.get("versions", []):
        current = "，当前" if active.get(item.get("scheme_id")) == item.get("version") else ""
        version_lines.append(
            f"- {item.get('scheme_id')} `{item.get('version')}`：`{item.get('status')}`{current}；"
            f"父版本 `{item.get('parent') or 'root'}`"
        )
    if not version_lines:
        version_lines.append("- 暂无版本")
    return "# 方案版本记录\n\n## 当前版本\n\n" + "\n".join(active_lines) + "\n\n## 全部版本\n\n" + "\n".join(version_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage scheme history without overwriting version files.")
    parser.add_argument("history", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)

    register_cmd = sub.add_parser("register")
    register_cmd.add_argument("intent", type=Path)
    register_cmd.add_argument("--status", choices=sorted(ALLOWED_STATUSES), default="candidate")
    register_cmd.add_argument("--validation", type=Path)
    register_cmd.add_argument("--review", type=Path)

    status_cmd = sub.add_parser("set-status")
    status_cmd.add_argument("version")
    status_cmd.add_argument("status", choices=sorted(ALLOWED_STATUSES))

    activate_cmd = sub.add_parser("activate")
    activate_cmd.add_argument("version")

    branch_cmd = sub.add_parser("branch")
    branch_cmd.add_argument("parent_version")
    branch_cmd.add_argument("new_version")
    branch_cmd.add_argument("--output-intent", type=Path, required=True)

    sub.add_parser("show")
    args = parser.parse_args()
    history = load_history(args.history)

    if args.command == "register":
        ok, message = register(history, args.intent, args.status, args.validation, args.review)
    elif args.command == "set-status":
        ok, message = set_status(history, args.version, args.status)
    elif args.command == "activate":
        ok, message = activate(history, args.version)
    elif args.command == "branch":
        ok, message = branch(history, args.parent_version, args.new_version, args.output_intent)
    else:
        print_summary(history)
        return 0

    if ok:
        history_path = args.history.resolve()
        write_json(history_path, history)
        history_path.with_suffix(".md").write_text(history_markdown(history), encoding="utf-8")
    print(f"history_status={'applied' if ok else 'blocked'} message={message}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
