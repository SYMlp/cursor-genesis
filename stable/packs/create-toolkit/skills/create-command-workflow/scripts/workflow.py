#!/usr/bin/env python3
"""Persistent, tool-neutral create-command workflow."""

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

from validate_command import ALLOWED_RISK_LEVELS, validate_command_contract


EXIT_SUCCESS = 0
EXIT_WAITING = 2
EXIT_RETRYABLE = 3
EXIT_BLOCKED = 4
VALID_GATE_EVENTS = ("analyzed", "refined", "adapted", "adaptation-not-required")
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


def _relative_path(value: str, field: str) -> Path:
    path = Path(value)
    if not value.strip() or path == Path("."):
        raise ValueError(f"{field} must not be empty or '.'")
    if path.is_absolute() or path.anchor or path.drive or ".." in path.parts:
        raise ValueError(f"{field} must be an unanchored project-relative path without '..'")
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
    outcome: str,
    commands_root: str = ".agents/commands",
    max_dependency_attempts: int = 3,
    max_validation_attempts: int = 3,
) -> dict[str, Any]:
    state_path = state_path.resolve()
    if state_path.exists():
        raise FileExistsError(f"State file already exists: {state_path}")
    if not description.strip() or not outcome.strip():
        raise ValueError("--description and --outcome must not be empty")
    if max_dependency_attempts < 1 or max_validation_attempts < 1:
        raise ValueError("attempt limits must be >= 1")

    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise ValueError(f"Project root does not exist: {project_root}")
    commands_root_path = _relative_path(commands_root, "--commands-root")
    full_name = _full_name(name, scope)
    command_file = project_root / commands_root_path / f"{full_name}.md"

    state: dict[str, Any] = {
        "schema_version": 1,
        "workflow_id": str(uuid.uuid4()),
        "workflow_name": "create-command-workflow",
        "status": "waiting",
        "current_stage": "analyze",
        "created_at": _now(),
        "updated_at": _now(),
        "project_root": str(project_root),
        "spec": {
            "name": name,
            "scope": scope,
            "full_name": full_name,
            "description": description.strip(),
            "outcome": outcome.strip(),
            "commands_root": commands_root_path.as_posix(),
            "risk_level": None,
            "skills": [],
            "agents": [],
            "composition_note": None,
            "max_dependency_attempts": max_dependency_attempts,
            "max_validation_attempts": max_validation_attempts,
        },
        "attempts": {"dependencies": 0, "scaffold": 0, "validate": 0},
        "history": [],
        "errors": [],
        "artifacts": {
            "command_contract": str(command_file),
            "dependency_report": None,
            "validation_report": None,
            "adapters": {},
        },
        "gate": {
            "type": "human_or_agent",
            "accepted_events": ["analyzed"],
            "message": "Complete SOP decomposition, dependencies, and risk analysis.",
        },
    }
    _record(state, "initialized", {"state_path": str(state_path)})
    _write_state(state_path, state)
    return state


def _contract_template(state: dict[str, Any]) -> str:
    spec = state["spec"]
    description = json.dumps(spec["description"], ensure_ascii=False)
    skills = json.dumps(spec["skills"], ensure_ascii=False)
    agents = json.dumps(spec["agents"], ensure_ascii=False)
    bindings = []
    bindings.extend(
        f"- Skill `{name}`: `.agents/skills/{name}/SKILL.md`" for name in spec["skills"]
    )
    bindings.extend(
        f"- Agent `{name}`: `.agents/agents/{name}.md`" for name in spec["agents"]
    )
    if not bindings:
        bindings.append("- No external Skill or Agent dependencies declared after explicit analysis.")
    return f"""---
name: {spec['full_name']}
description: {description}
kind: command-contract
execution_mode: ordered-workflow
risk_level: {spec['risk_level']}
skills: {skills}
agents: {agents}
---

# Command Contract: {spec['full_name']}

## User Outcome

{spec['outcome']}

## Inputs & Preconditions

TODO: Define required inputs, defaults, and preconditions.

## Dependency Bindings

{chr(10).join(bindings)}

## Workflow

1. TODO: Define the first deterministic or delegated step.
2. TODO: Verify the final result against the Verification Contract.

## Human Gates

TODO: Declare approval points, or explicitly state why none are required.

## Verification Contract

TODO: Define machine checks, evidence, and the user-visible completion signal.

## Failure & Resume

TODO: Define stop conditions, retry boundary, and persisted state needed to resume.

## Adapter Notes

Host adapters expose the operation using their current command or prompt mechanism.
They must preserve ordering, dependencies, gates, failure semantics, and verification.
"""


def _dependency_guard(state: dict[str, Any]) -> tuple[int, str]:
    state["attempts"]["dependencies"] += 1
    project_root = Path(state["project_root"])
    missing = []
    for skill in state["spec"]["skills"]:
        path = project_root / ".agents" / "skills" / skill / "SKILL.md"
        if not path.is_file():
            missing.append({"kind": "skill", "name": skill, "path": str(path)})
    for agent in state["spec"]["agents"]:
        path = project_root / ".agents" / "agents" / f"{agent}.md"
        if not path.is_file():
            missing.append({"kind": "agent", "name": agent, "path": str(path)})
    report = {"ok": not missing, "missing": missing}
    state["artifacts"]["dependency_report"] = report
    if not missing:
        state["current_stage"] = "scaffold"
        state["status"] = "ready"
        _record(state, "dependencies_passed", {"attempt": state["attempts"]["dependencies"]})
        return EXIT_SUCCESS, "Skill and Agent dependencies are present."

    limit = state["spec"]["max_dependency_attempts"]
    retryable = state["attempts"]["dependencies"] < limit
    state["status"] = "failed" if retryable else "blocked"
    error = {
        "at": _now(),
        "stage": "dependencies",
        "code": "DEPENDENCIES_MISSING",
        "message": f"{len(missing)} declared dependency item(s) are missing",
        "retryable": retryable,
        "attempt": state["attempts"]["dependencies"],
        "max_attempts": limit,
        "missing": missing,
    }
    state["errors"].append(error)
    _record(state, "dependencies_failed", error)
    if retryable:
        return EXIT_RETRYABLE, f"{error['message']}; create them, then run retry."
    return EXIT_BLOCKED, f"{error['message']}; retry limit exhausted."


def _scaffold(state: dict[str, Any]) -> tuple[int, str]:
    command_file = Path(state["artifacts"]["command_contract"])
    state["attempts"]["scaffold"] += 1
    if command_file.exists():
        state["status"] = "blocked"
        error = {
            "at": _now(),
            "stage": "scaffold",
            "code": "TARGET_EXISTS",
            "message": f"Refusing to overwrite existing Command Contract: {command_file}",
            "retryable": False,
        }
        state["errors"].append(error)
        _record(state, "blocked", error)
        return EXIT_BLOCKED, error["message"]

    command_file.parent.mkdir(parents=True, exist_ok=True)
    command_file.write_text(_contract_template(state), encoding="utf-8")
    state["current_stage"] = "refine"
    state["status"] = "waiting"
    state["gate"] = {
        "type": "human_or_agent",
        "accepted_events": ["refined"],
        "message": "Refine the Command Contract, then resume with event 'refined'.",
    }
    _record(state, "scaffolded", {"command_contract": str(command_file)})
    return EXIT_WAITING, state["gate"]["message"]


def _validate(state: dict[str, Any]) -> tuple[int, str]:
    state["attempts"]["validate"] += 1
    report = validate_command_contract(
        Path(state["artifacts"]["command_contract"]),
        Path(state["project_root"]),
    )
    state["artifacts"]["validation_report"] = report
    if report["ok"]:
        state["current_stage"] = "adapt"
        state["status"] = "waiting"
        state["gate"] = {
            "type": "human_or_adapter",
            "accepted_events": ["adapted", "adaptation-not-required"],
            "message": "Render a host operation entry or explicitly record why none is required.",
        }
        _record(state, "validation_passed", {"attempt": state["attempts"]["validate"]})
        return EXIT_WAITING, state["gate"]["message"]

    limit = state["spec"]["max_validation_attempts"]
    retryable = state["attempts"]["validate"] < limit
    state["status"] = "failed" if retryable else "blocked"
    state["gate"] = None
    error = {
        "at": _now(),
        "stage": "validate",
        "code": "VALIDATION_FAILED",
        "message": f"Command Contract validation failed with {len(report['issues'])} issue(s)",
        "retryable": retryable,
        "attempt": state["attempts"]["validate"],
        "max_attempts": limit,
        "issues": report["issues"],
    }
    state["errors"].append(error)
    _record(state, "validation_failed", error)
    if retryable:
        return EXIT_RETRYABLE, f"{error['message']}; fix the contract and run retry."
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

    code = EXIT_SUCCESS
    message = ""
    while state["status"] == "ready" and code == EXIT_SUCCESS:
        stage = state["current_stage"]
        if stage == "dependencies":
            code, message = _dependency_guard(state)
        elif stage == "scaffold":
            code, message = _scaffold(state)
        elif stage == "validate":
            code, message = _validate(state)
        elif stage == "complete":
            state["status"] = "completed"
            state["gate"] = None
            _record(state, "completed")
            message = "Workflow complete."
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


def resume_gate(
    state_path: Path,
    event: str,
    note: str,
    risk_level: str | None = None,
    skills: list[str] | None = None,
    agents: list[str] | None = None,
    composition_note: str | None = None,
    adapter: str | None = None,
    artifact: str | None = None,
) -> tuple[int, dict[str, Any], str]:
    state = load_state(state_path)
    if event not in VALID_GATE_EVENTS:
        return EXIT_BLOCKED, state, f"Unsupported gate event: {event}"
    if state["status"] != "waiting" or not state.get("gate"):
        return EXIT_BLOCKED, state, "Workflow is not waiting at a gate."
    if event not in state["gate"]["accepted_events"]:
        return EXIT_BLOCKED, state, f"Event '{event}' is not accepted at stage '{state['current_stage']}'."

    stage = state["current_stage"]
    if stage == "analyze" and event == "analyzed":
        if risk_level not in ALLOWED_RISK_LEVELS:
            return EXIT_BLOCKED, state, "analyzed requires a supported --risk-level."
        if not composition_note or not composition_note.strip():
            return EXIT_BLOCKED, state, "analyzed requires --composition-note."
        normalized: dict[str, list[str]] = {"skills": [], "agents": []}
        for kind, values in (("skills", skills or []), ("agents", agents or [])):
            for value in values:
                if not SLUG_PATTERN.fullmatch(value):
                    return EXIT_BLOCKED, state, f"Invalid {kind[:-1].title()} slug: {value}"
                if value not in normalized[kind]:
                    normalized[kind].append(value)
        state["spec"]["risk_level"] = risk_level
        state["spec"]["skills"] = normalized["skills"]
        state["spec"]["agents"] = normalized["agents"]
        state["spec"]["composition_note"] = composition_note.strip()
        state["current_stage"] = "dependencies"
        state["status"] = "ready"
        message = "Analysis gate accepted; dependency check is ready."
    elif stage == "refine" and event == "refined":
        state["current_stage"] = "validate"
        state["status"] = "ready"
        message = "Refine gate accepted; validation is ready."
    elif stage == "adapt" and event == "adapted":
        if not adapter or not SLUG_PATTERN.fullmatch(adapter):
            return EXIT_BLOCKED, state, "adapted requires a lowercase kebab-case --adapter."
        if not artifact:
            return EXIT_BLOCKED, state, "adapted requires --artifact."
        try:
            relative_artifact = _relative_path(artifact, "--artifact")
        except ValueError as error:
            return EXIT_BLOCKED, state, str(error)
        artifact_path = Path(state["project_root"]) / relative_artifact
        if not artifact_path.is_file():
            return EXIT_BLOCKED, state, f"Adapter artifact does not exist: {artifact_path}"
        state["artifacts"]["adapters"][adapter] = str(artifact_path)
        state["current_stage"] = "complete"
        state["status"] = "completed"
        message = f"Adapter '{adapter}' recorded; workflow complete."
    elif stage == "adapt" and event == "adaptation-not-required":
        if not note.strip():
            return EXIT_BLOCKED, state, "adaptation-not-required requires an explicit --note."
        state["current_stage"] = "complete"
        state["status"] = "completed"
        message = "No host adapter required; workflow complete."
    else:
        return EXIT_BLOCKED, state, f"Event '{event}' does not match stage '{stage}'."

    state["gate"] = None
    _record(state, f"gate:{event}", {"note": note})
    _write_state(state_path, state)
    return EXIT_SUCCESS, state, message


def retry_failed_stage(state_path: Path, note: str) -> tuple[int, dict[str, Any], str]:
    state = load_state(state_path)
    if state["status"] != "failed" or state["current_stage"] not in ("dependencies", "validate"):
        return EXIT_BLOCKED, state, "Only a retryable machine-check failure can be retried."
    stage = state["current_stage"]
    limit_key = "max_dependency_attempts" if stage == "dependencies" else "max_validation_attempts"
    if state["attempts"][stage] >= state["spec"][limit_key]:
        state["status"] = "blocked"
        _record(state, "retry_exhausted", {"note": note})
        _write_state(state_path, state)
        return EXIT_BLOCKED, state, f"{stage} retry limit exhausted."
    state["status"] = "ready"
    _record(state, "retry_requested", {"note": note})
    _write_state(state_path, state)
    return EXIT_SUCCESS, state, f"{stage} retry is ready."


def _print_result(code: int, state: dict[str, Any], message: str, as_json: bool = False) -> int:
    if as_json:
        print(json.dumps({"exit_code": code, "message": message, "state": state}, ensure_ascii=False, indent=2))
    else:
        print(f"[{state['status'].upper()}] stage={state['current_stage']} {message}")
        print(f"state workflow_id={state['workflow_id']}")
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persistent create-command workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--state", required=True)
    init_parser.add_argument("--project-root", default=".")
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--scope", default="")
    init_parser.add_argument("--description", required=True)
    init_parser.add_argument("--outcome", required=True)
    init_parser.add_argument("--commands-root", default=".agents/commands")
    init_parser.add_argument("--max-dependency-attempts", type=int, default=3)
    init_parser.add_argument("--max-validation-attempts", type=int, default=3)

    for command in ("run", "status"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--state", required=True)
        command_parser.add_argument("--json", action="store_true")

    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--state", required=True)
    resume_parser.add_argument("--event", required=True, choices=VALID_GATE_EVENTS)
    resume_parser.add_argument("--note", default="")
    resume_parser.add_argument("--risk-level", choices=sorted(ALLOWED_RISK_LEVELS))
    resume_parser.add_argument("--skill", action="append", default=[])
    resume_parser.add_argument("--agent", action="append", default=[])
    resume_parser.add_argument("--composition-note")
    resume_parser.add_argument("--adapter")
    resume_parser.add_argument("--artifact")
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
                outcome=args.outcome,
                commands_root=args.commands_root,
                max_dependency_attempts=args.max_dependency_attempts,
                max_validation_attempts=args.max_validation_attempts,
            )
            return _print_result(EXIT_WAITING, state, f"State initialized at {state_path.resolve()}.")
        if args.command == "run":
            return _print_result(*run_current_stage(state_path), as_json=args.json)
        if args.command == "resume":
            return _print_result(
                *resume_gate(
                    state_path,
                    args.event,
                    args.note,
                    risk_level=args.risk_level,
                    skills=args.skill,
                    agents=args.agent,
                    composition_note=args.composition_note,
                    adapter=args.adapter,
                    artifact=args.artifact,
                ),
                as_json=args.json,
            )
        if args.command == "retry":
            return _print_result(*retry_failed_stage(state_path, args.note), as_json=args.json)
        if args.command == "status":
            state = load_state(state_path)
            return _print_result(EXIT_SUCCESS, state, "Current state.", as_json=args.json)
    except (FileExistsError, FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return EXIT_BLOCKED
    return EXIT_BLOCKED


if __name__ == "__main__":
    sys.exit(main())
