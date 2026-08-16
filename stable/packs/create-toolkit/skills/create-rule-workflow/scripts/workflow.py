#!/usr/bin/env python3
"""Persistent, tool-neutral create-rule workflow."""

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

from validate_rule import ACTIVATIONS, extract_rule_block, validate_rule_file


EXIT_SUCCESS = 0
EXIT_WAITING = 2
EXIT_RETRYABLE = 3
EXIT_BLOCKED = 4
VALID_GATE_EVENTS = (
    "analyzed",
    "refined",
    "registered",
    "adapted",
    "adaptation-not-required",
)
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


def _single_line(value: str, field: str) -> str:
    value = value.strip()
    if not value or "\n" in value or "\r" in value or "<!--" in value:
        raise ValueError(f"{field} must be a non-empty single line without HTML markers")
    return value


def initialize_state(
    state_path: Path,
    project_root: Path,
    name: str,
    description: str,
    agents_file: str = "AGENTS.md",
    draft_root: str = "docs/state/create-rule/drafts",
    max_validation_attempts: int = 3,
) -> dict[str, Any]:
    state_path = state_path.resolve()
    if state_path.exists():
        raise FileExistsError(f"State file already exists: {state_path}")
    if not SLUG_PATTERN.fullmatch(name):
        raise ValueError("--name must be a lowercase kebab-case slug")
    description = _single_line(description, "--description")
    if max_validation_attempts < 1:
        raise ValueError("--max-validation-attempts must be >= 1")

    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise ValueError(f"Project root does not exist: {project_root}")
    agents_relative = _relative_path(agents_file, "--agents-file")
    if agents_relative.name != "AGENTS.md":
        raise ValueError("--agents-file must point to an AGENTS.md file")
    agents_path = project_root / agents_relative
    if not agents_path.is_file():
        raise FileNotFoundError(f"AGENTS.md does not exist: {agents_path}")
    draft_relative = _relative_path(draft_root, "--draft-root") / f"{name}.md"

    state: dict[str, Any] = {
        "schema_version": 1,
        "workflow_id": str(uuid.uuid4()),
        "workflow_name": "create-rule-workflow",
        "status": "waiting",
        "current_stage": "analyze",
        "created_at": _now(),
        "updated_at": _now(),
        "project_root": str(project_root),
        "spec": {
            "name": name,
            "description": description,
            "activation": None,
            "paths": [],
            "trigger": None,
            "rationale": None,
            "max_validation_attempts": max_validation_attempts,
        },
        "attempts": {"scaffold": 0, "validate": 0},
        "history": [],
        "errors": [],
        "artifacts": {
            "draft": str(project_root / draft_relative),
            "agents_file": str(agents_path),
            "validation_report": None,
            "adapters": {},
        },
        "gate": {
            "type": "human_or_agent",
            "accepted_events": ["analyzed"],
            "message": "Confirm Rule type, activation, scope, trigger, and rationale.",
        },
    }
    _record(state, "initialized", {"state_path": str(state_path)})
    _write_state(state_path, state)
    return state


def _rule_template(state: dict[str, Any]) -> str:
    spec = state["spec"]
    title = spec["name"].replace("-", " ").title()
    paths = json.dumps(spec["paths"], ensure_ascii=False)
    return f"""<!-- cg-rule-contract:{spec['name']}:start -->
## Rule: {title}
- ID: `{spec['name']}`
- Activation: {spec['activation']}
- Description: {spec['description']}
- Paths: {paths}
- Trigger: {spec['trigger']}
- Rationale: {spec['rationale']}

### Behavior
- MUST TODO: State the required behavior.

### Exclusions
- TODO: State what this Rule does not govern.

### Verification
- TODO: State how a reviewer can observe compliance.
<!-- cg-rule-contract:{spec['name']}:end -->
"""


def _scaffold(state: dict[str, Any]) -> tuple[int, str]:
    draft = Path(state["artifacts"]["draft"])
    state["attempts"]["scaffold"] += 1
    if draft.exists():
        state["status"] = "blocked"
        error = {
            "at": _now(),
            "stage": "scaffold",
            "code": "TARGET_EXISTS",
            "message": f"Refusing to overwrite existing Rule draft: {draft}",
            "retryable": False,
        }
        state["errors"].append(error)
        _record(state, "blocked", error)
        return EXIT_BLOCKED, error["message"]
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(_rule_template(state), encoding="utf-8")
    state["current_stage"] = "refine"
    state["status"] = "waiting"
    state["gate"] = {
        "type": "human_or_agent",
        "accepted_events": ["refined"],
        "message": "Refine the thin Rule draft, then resume with event 'refined'.",
    }
    _record(state, "scaffolded", {"draft": str(draft)})
    return EXIT_WAITING, state["gate"]["message"]


def _validate(state: dict[str, Any]) -> tuple[int, str]:
    state["attempts"]["validate"] += 1
    report = validate_rule_file(
        Path(state["artifacts"]["draft"]),
        expected_id=state["spec"]["name"],
    )
    state["artifacts"]["validation_report"] = report
    if report["ok"]:
        state["current_stage"] = "register"
        state["status"] = "waiting"
        state["gate"] = {
            "type": "human",
            "accepted_events": ["registered"],
            "message": "Review the AGENTS.md diff, register the validated block, then confirm.",
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
        "message": f"Rule validation failed with {len(report['issues'])} issue(s)",
        "retryable": retryable,
        "attempt": state["attempts"]["validate"],
        "max_attempts": limit,
        "issues": report["issues"],
    }
    state["errors"].append(error)
    _record(state, "validation_failed", error)
    if retryable:
        return EXIT_RETRYABLE, f"{error['message']}; fix the draft and run retry."
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


def _registered_block_matches(state: dict[str, Any]) -> tuple[bool, str]:
    draft = Path(state["artifacts"]["draft"])
    agents_file = Path(state["artifacts"]["agents_file"])
    report = validate_rule_file(draft, expected_id=state["spec"]["name"])
    if not report["ok"]:
        return False, "Rule draft no longer passes validation."
    draft_block = extract_rule_block(draft.read_text(encoding="utf-8"), state["spec"]["name"])
    try:
        agents_block = extract_rule_block(
            agents_file.read_text(encoding="utf-8"),
            state["spec"]["name"],
        )
    except ValueError:
        return False, "Registered Rule block is missing from AGENTS.md."
    if agents_block.strip() != draft_block.strip():
        return False, "AGENTS.md Rule block differs from the validated draft."
    return True, "Registered Rule block matches the validated draft."


def resume_gate(
    state_path: Path,
    event: str,
    note: str,
    activation: str | None = None,
    paths: list[str] | None = None,
    trigger: str | None = None,
    rationale: str | None = None,
    adapter: str | None = None,
    artifact: str | None = None,
) -> tuple[int, dict[str, Any], str]:
    state = load_state(state_path)
    if event not in VALID_GATE_EVENTS:
        return EXIT_BLOCKED, state, f"Unsupported gate event: {event}"
    if not note.strip():
        return EXIT_BLOCKED, state, "Every Gate event requires a non-empty --note."
    if state["status"] != "waiting" or not state.get("gate"):
        return EXIT_BLOCKED, state, "Workflow is not waiting at a Gate."
    if event not in state["gate"]["accepted_events"]:
        return EXIT_BLOCKED, state, f"Event '{event}' is not accepted at stage '{state['current_stage']}'."

    stage = state["current_stage"]
    if stage == "analyze" and event == "analyzed":
        if activation not in ACTIVATIONS:
            return EXIT_BLOCKED, state, "analyzed requires a supported --activation."
        try:
            normalized_trigger = _single_line(trigger or "", "--trigger")
            normalized_rationale = _single_line(rationale or "", "--rationale")
        except ValueError as error:
            return EXIT_BLOCKED, state, str(error)
        normalized_paths: list[str] = []
        for value in paths or []:
            value = value.strip()
            if value and value not in normalized_paths:
                normalized_paths.append(value)
        if activation == "paths" and not normalized_paths:
            return EXIT_BLOCKED, state, "paths activation requires at least one --path."
        if activation != "paths" and normalized_paths:
            return EXIT_BLOCKED, state, "Only paths activation accepts --path."
        state["spec"]["activation"] = activation
        state["spec"]["paths"] = normalized_paths
        state["spec"]["trigger"] = normalized_trigger
        state["spec"]["rationale"] = normalized_rationale
        state["current_stage"] = "scaffold"
        state["status"] = "ready"
        message = "Analysis Gate accepted; scaffold is ready."
    elif stage == "refine" and event == "refined":
        state["current_stage"] = "validate"
        state["status"] = "ready"
        message = "Refine Gate accepted; validation is ready."
    elif stage == "register" and event == "registered":
        matches, details = _registered_block_matches(state)
        if not matches:
            return EXIT_BLOCKED, state, details
        state["current_stage"] = "adapt"
        state["status"] = "waiting"
        state["gate"] = {
            "type": "human_or_adapter",
            "accepted_events": ["adapted", "adaptation-not-required"],
            "message": "Render a host adapter or explicitly record why none is required.",
        }
        _record(state, "gate:registered", {"note": note, "verification": details})
        _write_state(state_path, state)
        return EXIT_SUCCESS, state, details
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
    parser = argparse.ArgumentParser(description="Persistent create-rule workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--state", required=True)
    init_parser.add_argument("--project-root", default=".")
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--description", required=True)
    init_parser.add_argument("--agents-file", default="AGENTS.md")
    init_parser.add_argument("--draft-root", default="docs/state/create-rule/drafts")
    init_parser.add_argument("--max-validation-attempts", type=int, default=3)

    for command in ("run", "status"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--state", required=True)
        command_parser.add_argument("--json", action="store_true")

    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--state", required=True)
    resume_parser.add_argument("--event", required=True, choices=VALID_GATE_EVENTS)
    resume_parser.add_argument("--note", default="")
    resume_parser.add_argument("--activation", choices=sorted(ACTIVATIONS))
    resume_parser.add_argument("--path", action="append", default=[])
    resume_parser.add_argument("--trigger")
    resume_parser.add_argument("--rationale")
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
                description=args.description,
                agents_file=args.agents_file,
                draft_root=args.draft_root,
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
                    activation=args.activation,
                    paths=args.path,
                    trigger=args.trigger,
                    rationale=args.rationale,
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
    except (FileExistsError, FileNotFoundError, OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return EXIT_BLOCKED
    return EXIT_BLOCKED


if __name__ == "__main__":
    sys.exit(main())
