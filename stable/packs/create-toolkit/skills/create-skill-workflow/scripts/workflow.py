#!/usr/bin/env python3
"""Persistent, tool-agnostic create-skill workflow."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_skill import validate_skill_dir


EXIT_SUCCESS = 0
EXIT_WAITING = 2
EXIT_RETRYABLE = 3
EXIT_BLOCKED = 4
VALID_CATEGORIES = ("executor", "generator", "analyzer", "orchestrator", "researcher")
VALID_GATE_EVENTS = ("refined", "registered", "registration-not-required")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def load_state(path: Path) -> dict[str, Any]:
    with path.resolve().open("r", encoding="utf-8") as stream:
        state = json.load(stream)
    if state.get("schema_version") != 1:
        raise ValueError(f"Unsupported state schema: {state.get('schema_version')}")
    return state


def _record(state: dict[str, Any], event: str, details: dict[str, Any] | None = None) -> None:
    state["history"].append(
        {
            "sequence": len(state["history"]) + 1,
            "at": _now(),
            "stage": state["current_stage"],
            "event": event,
            "details": details or {},
        }
    )
    state["updated_at"] = _now()


def _validate_relative_root(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("--skills-root must be a project-relative path without '..'")
    return path


def _full_name(name: str, scope: str) -> str:
    if not SLUG_PATTERN.fullmatch(name):
        raise ValueError("--name must be a lowercase kebab-case slug")
    if scope and not SLUG_PATTERN.fullmatch(scope):
        raise ValueError("--scope must be empty or a lowercase kebab-case slug")
    return f"{scope}-{name}" if scope else name


def initialize_state(
    state_path: Path,
    project_root: Path,
    name: str,
    scope: str,
    description: str,
    category: str,
    skills_root: str = ".agents/skills",
    max_validation_attempts: int = 3,
) -> dict[str, Any]:
    state_path = state_path.resolve()
    if state_path.exists():
        raise FileExistsError(f"State file already exists: {state_path}")
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Unsupported category: {category}")
    if not description.strip():
        raise ValueError("--description must not be empty")
    if max_validation_attempts < 1:
        raise ValueError("--max-validation-attempts must be >= 1")

    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise ValueError(f"Project root does not exist: {project_root}")
    skills_root_path = _validate_relative_root(skills_root)
    full_name = _full_name(name, scope)
    skill_dir = project_root / skills_root_path / full_name

    state: dict[str, Any] = {
        "schema_version": 1,
        "workflow_id": str(uuid.uuid4()),
        "workflow_name": "create-skill-workflow",
        "status": "ready",
        "current_stage": "scaffold",
        "created_at": _now(),
        "updated_at": _now(),
        "project_root": str(project_root),
        "spec": {
            "name": name,
            "scope": scope,
            "full_name": full_name,
            "description": description.strip(),
            "category": category,
            "skills_root": skills_root_path.as_posix(),
            "max_validation_attempts": max_validation_attempts,
        },
        "attempts": {"scaffold": 0, "validate": 0},
        "history": [],
        "errors": [],
        "artifacts": {"skill_dir": str(skill_dir), "validation_report": None},
        "gate": None,
    }
    _record(state, "initialized", {"state_path": str(state_path)})
    _write_state(state_path, state)
    return state


def _skill_template(state: dict[str, Any]) -> str:
    spec = state["spec"]
    description = json.dumps(spec["description"], ensure_ascii=False)
    return f"""---
name: {spec['full_name']}
description: {description}
metadata:
  version: "0.1.0"
category: {spec['category']}
---

# Skill: {spec['full_name']}

## Workflow

TODO: Replace this placeholder with the concrete workflow.

## Verification

TODO: Define a deterministic verification command or observable result.

## Context & Side Effects

TODO: List reads, writes, external calls, and meaningful human gates.
"""


def _readme_template(state: dict[str, Any]) -> str:
    spec = state["spec"]
    return f"""# {spec['full_name']}

> {spec['description']}

This Skill was scaffolded by `create-skill-workflow`.

- `SKILL.md`: authoring source
- `scripts/`: deterministic helpers, if needed
- `references/`: on-demand reference material
- `assets/`: templates or static resources
- `tests/`: machine-verifiable checks
"""


def _scaffold(state: dict[str, Any]) -> tuple[int, str]:
    skill_dir = Path(state["artifacts"]["skill_dir"])
    state["attempts"]["scaffold"] += 1
    if skill_dir.exists():
        state["status"] = "blocked"
        error = {
            "at": _now(),
            "stage": "scaffold",
            "code": "TARGET_EXISTS",
            "message": f"Refusing to overwrite existing Skill directory: {skill_dir}",
            "retryable": False,
        }
        state["errors"].append(error)
        _record(state, "blocked", error)
        return EXIT_BLOCKED, error["message"]

    for relative in ("scripts", "references", "assets", "tests"):
        (skill_dir / relative).mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(_skill_template(state), encoding="utf-8")
    (skill_dir / "README.md").write_text(_readme_template(state), encoding="utf-8")

    state["current_stage"] = "refine"
    state["status"] = "waiting"
    state["gate"] = {
        "type": "human_or_agent",
        "accepted_events": ["refined"],
        "message": "Edit the generated SKILL.md, then resume with event 'refined'.",
    }
    _record(state, "scaffolded", {"skill_dir": str(skill_dir)})
    return EXIT_WAITING, state["gate"]["message"]


def _validate(state: dict[str, Any]) -> tuple[int, str]:
    state["attempts"]["validate"] += 1
    report = validate_skill_dir(Path(state["artifacts"]["skill_dir"]))
    state["artifacts"]["validation_report"] = report
    if report["ok"]:
        state["current_stage"] = "register"
        state["status"] = "waiting"
        state["gate"] = {
            "type": "human_or_adapter",
            "accepted_events": ["registered", "registration-not-required"],
            "message": "Register the Skill in the project inventory, then resume explicitly.",
        }
        _record(state, "validation_passed", {"attempt": state["attempts"]["validate"]})
        return EXIT_WAITING, state["gate"]["message"]

    max_attempts = state["spec"]["max_validation_attempts"]
    retryable = state["attempts"]["validate"] < max_attempts
    state["status"] = "failed" if retryable else "blocked"
    state["gate"] = None
    error = {
        "at": _now(),
        "stage": "validate",
        "code": "VALIDATION_FAILED",
        "message": f"Skill validation failed with {len(report['issues'])} issue(s)",
        "retryable": retryable,
        "attempt": state["attempts"]["validate"],
        "max_attempts": max_attempts,
        "issues": report["issues"],
    }
    state["errors"].append(error)
    _record(state, "validation_failed", error)
    if retryable:
        return EXIT_RETRYABLE, f"{error['message']}; fix the Skill and run retry."
    return EXIT_BLOCKED, f"{error['message']}; retry limit exhausted."


def run_current_stage(state_path: Path) -> tuple[int, dict[str, Any], str]:
    state = load_state(state_path)
    if state["status"] == "completed":
        return EXIT_SUCCESS, state, "Workflow already complete."
    if state["status"] == "waiting":
        return EXIT_WAITING, state, state["gate"]["message"]
    if state["status"] in ("failed", "blocked"):
        code = EXIT_RETRYABLE if state["status"] == "failed" else EXIT_BLOCKED
        return code, state, f"Workflow is {state['status']}; use retry when allowed."

    stage = state["current_stage"]
    if stage == "scaffold":
        code, message = _scaffold(state)
    elif stage == "validate":
        code, message = _validate(state)
    elif stage == "complete":
        state["status"] = "completed"
        state["gate"] = None
        _record(state, "completed")
        code, message = EXIT_SUCCESS, "Workflow complete."
    else:
        state["status"] = "blocked"
        message = f"Unsupported executable stage: {stage}"
        error = {
            "at": _now(),
            "stage": stage,
            "code": "INVALID_STAGE",
            "message": message,
            "retryable": False,
        }
        state["errors"].append(error)
        _record(state, "blocked", error)
        code = EXIT_BLOCKED
    _write_state(state_path, state)
    return code, state, message


def resume_gate(state_path: Path, event: str, note: str) -> tuple[int, dict[str, Any], str]:
    state = load_state(state_path)
    if event not in VALID_GATE_EVENTS:
        return EXIT_BLOCKED, state, f"Unsupported gate event: {event}"
    if state["status"] != "waiting" or not state.get("gate"):
        return EXIT_BLOCKED, state, "Workflow is not waiting at a gate."
    if event not in state["gate"]["accepted_events"]:
        return EXIT_BLOCKED, state, f"Event '{event}' is not accepted at stage '{state['current_stage']}'."

    stage = state["current_stage"]
    if stage == "refine" and event == "refined":
        state["current_stage"] = "validate"
        state["status"] = "ready"
        message = "Refine gate accepted; validation is ready."
    elif stage == "register" and event in ("registered", "registration-not-required"):
        state["current_stage"] = "complete"
        state["status"] = "completed"
        message = "Registration gate accepted; workflow complete."
    else:
        return EXIT_BLOCKED, state, f"Event '{event}' does not match stage '{stage}'."

    state["gate"] = None
    _record(state, f"gate:{event}", {"note": note})
    _write_state(state_path, state)
    return EXIT_SUCCESS, state, message


def retry_validation(state_path: Path, note: str) -> tuple[int, dict[str, Any], str]:
    state = load_state(state_path)
    if state["status"] != "failed" or state["current_stage"] != "validate":
        return EXIT_BLOCKED, state, "Only a retryable validation failure can be retried."
    if state["attempts"]["validate"] >= state["spec"]["max_validation_attempts"]:
        state["status"] = "blocked"
        _record(state, "retry_exhausted", {"note": note})
        _write_state(state_path, state)
        return EXIT_BLOCKED, state, "Validation retry limit exhausted."
    state["status"] = "ready"
    _record(state, "retry_requested", {"note": note})
    _write_state(state_path, state)
    return EXIT_SUCCESS, state, "Validation retry is ready."


def _print_result(code: int, state: dict[str, Any], message: str, as_json: bool = False) -> int:
    if as_json:
        print(json.dumps({"exit_code": code, "message": message, "state": state}, ensure_ascii=False, indent=2))
    else:
        print(f"[{state['status'].upper()}] stage={state['current_stage']} {message}")
        print(f"state workflow_id={state['workflow_id']}")
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persistent create-skill workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize workflow state")
    init_parser.add_argument("--state", required=True)
    init_parser.add_argument("--project-root", default=".")
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--scope", default="base")
    init_parser.add_argument("--description", required=True)
    init_parser.add_argument("--category", choices=VALID_CATEGORIES, default="executor")
    init_parser.add_argument("--skills-root", default=".agents/skills")
    init_parser.add_argument("--max-validation-attempts", type=int, default=3)

    for command in ("run", "status"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--state", required=True)
        command_parser.add_argument("--json", action="store_true")

    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--state", required=True)
    resume_parser.add_argument("--event", required=True, choices=VALID_GATE_EVENTS)
    resume_parser.add_argument("--note", default="")
    resume_parser.add_argument("--json", action="store_true")

    retry_parser = subparsers.add_parser("retry")
    retry_parser.add_argument("--state", required=True)
    retry_parser.add_argument("--note", default="")
    retry_parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    state_path = Path(args.state)
    try:
        if args.command == "init":
            state = initialize_state(
                state_path=state_path,
                project_root=Path(args.project_root),
                name=args.name,
                scope=args.scope,
                description=args.description,
                category=args.category,
                skills_root=args.skills_root,
                max_validation_attempts=args.max_validation_attempts,
            )
            return _print_result(EXIT_SUCCESS, state, f"State initialized at {state_path.resolve()}.")
        if args.command == "run":
            return _print_result(*run_current_stage(state_path), as_json=args.json)
        if args.command == "resume":
            return _print_result(*resume_gate(state_path, args.event, args.note), as_json=args.json)
        if args.command == "retry":
            return _print_result(*retry_validation(state_path, args.note), as_json=args.json)
        if args.command == "status":
            state = load_state(state_path)
            return _print_result(EXIT_SUCCESS, state, "Current state.", as_json=args.json)
    except (FileExistsError, FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return EXIT_BLOCKED
    return EXIT_BLOCKED


if __name__ == "__main__":
    sys.exit(main())
