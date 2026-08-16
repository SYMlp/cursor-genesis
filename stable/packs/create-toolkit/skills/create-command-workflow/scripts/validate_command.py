#!/usr/bin/env python3
"""Deterministic validator for a tool-neutral Command Contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_RISK_LEVELS = {"low", "medium", "high"}
REQUIRED_FIELDS = (
    "name",
    "description",
    "kind",
    "execution_mode",
    "risk_level",
    "skills",
    "agents",
)
REQUIRED_HEADINGS = (
    "## User Outcome",
    "## Inputs & Preconditions",
    "## Dependency Bindings",
    "## Workflow",
    "## Human Gates",
    "## Verification Contract",
    "## Failure & Resume",
    "## Adapter Notes",
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\[待填写\]"),
    re.compile(r"\[Add [^\]]+\]", re.IGNORECASE),
)
HOST_SPECIFIC_PATTERNS = (
    re.compile(r"\.cursor/commands", re.IGNORECASE),
    re.compile(r"\.claude/commands", re.IGNORECASE),
    re.compile(r"\.codex/", re.IGNORECASE),
    re.compile(r"\bsubagent_type\b"),
    re.compile(r"\bTask\s*\("),
)
VERIFICATION_PATTERN = re.compile(r"\bverify\b|\bvalidate\b|验证|校验|检查", re.IGNORECASE)
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _issue(code: str, message: str, path: Path) -> dict[str, str]:
    return {"code": code, "message": message, "path": str(path)}


def _split_frontmatter(content: str) -> tuple[str | None, str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, content
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    return None, content


def _parse_scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, str) else value
        except json.JSONDecodeError:
            return value
    return value.strip("'")


def _parse_frontmatter(frontmatter: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in frontmatter.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if len(raw_line) != len(raw_line.lstrip()):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw_line)
        if match:
            key, value = match.groups()
            result[key] = _parse_scalar(value)
    return result


def _parse_list(raw_value: str, field: str) -> list[str]:
    parsed = json.loads(raw_value)
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError(f"{field} must be a JSON string array")
    return parsed


def _section(body: str, heading: str) -> str:
    marker = re.search(rf"(?m)^{re.escape(heading)}\s*$", body)
    if not marker:
        return ""
    remainder = body[marker.end() :]
    next_heading = re.search(r"(?m)^##\s+", remainder)
    return remainder[: next_heading.start()] if next_heading else remainder


def _workflow_steps(body: str) -> list[tuple[int, str]]:
    section = _section(body, "## Workflow")
    return [
        (int(match.group(1)), match.group(2).strip())
        for match in re.finditer(r"(?m)^\s*(\d+)\.\s+(.+)$", section)
    ]


def read_command_contract(command_file: Path) -> dict[str, Any]:
    content = command_file.read_text(encoding="utf-8")
    frontmatter_text, body = _split_frontmatter(content)
    if frontmatter_text is None:
        raise ValueError("Command Contract must start with closed YAML frontmatter")
    frontmatter = _parse_frontmatter(frontmatter_text)
    skills = _parse_list(frontmatter.get("skills", "null"), "skills")
    agents = _parse_list(frontmatter.get("agents", "null"), "agents")
    return {
        "content": content,
        "frontmatter": frontmatter,
        "skills": skills,
        "agents": agents,
        "body": body,
    }


def validate_command_contract(command_file: Path, project_root: Path) -> dict[str, Any]:
    command_file = command_file.resolve()
    project_root = project_root.resolve()
    issues: list[dict[str, str]] = []

    if not command_file.is_file():
        issues.append(_issue("COMMAND_FILE_MISSING", "Command Contract does not exist", command_file))
        return {"ok": False, "command_file": str(command_file), "issues": issues}

    content = command_file.read_text(encoding="utf-8")
    frontmatter_text, body = _split_frontmatter(content)
    frontmatter: dict[str, str] = {}
    skills: list[str] = []
    agents: list[str] = []
    if frontmatter_text is None:
        issues.append(_issue("FRONTMATTER_MISSING", "Command Contract must start with closed YAML frontmatter", command_file))
    else:
        frontmatter = _parse_frontmatter(frontmatter_text)
        for field in REQUIRED_FIELDS:
            if field not in frontmatter or (field not in ("skills", "agents") and not frontmatter[field]):
                issues.append(_issue("FRONTMATTER_FIELD_MISSING", f"Missing frontmatter field: {field}", command_file))

        if "model" in frontmatter:
            issues.append(_issue("MODEL_IN_COMMAND_CORE", "Model selection belongs to Agent or host adapters", command_file))
        if frontmatter.get("kind") and frontmatter["kind"] != "command-contract":
            issues.append(_issue("INVALID_KIND", "kind must be command-contract", command_file))
        if frontmatter.get("execution_mode") and frontmatter["execution_mode"] != "ordered-workflow":
            issues.append(_issue("INVALID_EXECUTION_MODE", "execution_mode must be ordered-workflow", command_file))
        if frontmatter.get("risk_level") and frontmatter["risk_level"] not in ALLOWED_RISK_LEVELS:
            issues.append(_issue("INVALID_RISK_LEVEL", "Unsupported risk_level", command_file))
        if frontmatter.get("name") and frontmatter["name"] != command_file.stem:
            issues.append(
                _issue(
                    "NAME_FILE_MISMATCH",
                    f"Frontmatter name '{frontmatter['name']}' does not match file '{command_file.stem}'",
                    command_file,
                )
            )

        for field, target in (("skills", skills), ("agents", agents)):
            try:
                target.extend(_parse_list(frontmatter.get(field, "null"), field))
            except (json.JSONDecodeError, ValueError):
                issues.append(
                    _issue(
                        f"{field.upper()}_FORMAT_INVALID",
                        f"{field} must be a JSON string array",
                        command_file,
                    )
                )

    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            issues.append(_issue("REQUIRED_SECTION_MISSING", f"Missing section: {heading}", command_file))
        elif not _section(body, heading).strip():
            issues.append(_issue("REQUIRED_SECTION_EMPTY", f"Section must not be empty: {heading}", command_file))

    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(content):
            issues.append(_issue("PLACEHOLDER_REMAINS", f"Unresolved placeholder matched: {pattern.pattern}", command_file))

    for pattern in HOST_SPECIFIC_PATTERNS:
        if pattern.search(content):
            issues.append(
                _issue(
                    "HOST_SPECIFIC_CORE_CONTENT",
                    f"Host-specific content belongs in an adapter: {pattern.pattern}",
                    command_file,
                )
            )

    steps = _workflow_steps(body)
    if not steps:
        issues.append(_issue("WORKFLOW_STEPS_MISSING", "Workflow must contain numbered steps", command_file))
    else:
        numbers = [number for number, _ in steps]
        if numbers != list(range(1, len(steps) + 1)):
            issues.append(_issue("WORKFLOW_NUMBERING_INVALID", "Workflow steps must be consecutively numbered from 1", command_file))
        if len(steps) > 7:
            issues.append(_issue("WORKFLOW_TOO_LONG", "Workflow must contain no more than seven steps", command_file))
        if not VERIFICATION_PATTERN.search(steps[-1][1]):
            issues.append(_issue("FINAL_STEP_NOT_VERIFICATION", "The final Workflow step must explicitly verify the result", command_file))

    human_gate = _section(body, "## Human Gates").strip()
    if frontmatter.get("risk_level") == "high" and (
        not human_gate or re.fullmatch(r"(?i)(none|无|不需要)[。.]?", human_gate)
    ):
        issues.append(_issue("HIGH_RISK_GATE_MISSING", "High-risk Commands must declare a Human Gate", command_file))

    dependency_bindings = _section(body, "## Dependency Bindings")
    for kind, names, relative_root, filename in (
        ("SKILL", skills, Path(".agents/skills"), "SKILL.md"),
        ("AGENT", agents, Path(".agents/agents"), None),
    ):
        for name in names:
            if not SLUG_PATTERN.fullmatch(name):
                issues.append(_issue(f"{kind}_NAME_INVALID", f"Invalid {kind.title()} slug: {name}", command_file))
                continue
            dependency = (
                project_root / relative_root / name / filename
                if filename
                else project_root / relative_root / f"{name}.md"
            )
            if not dependency.is_file():
                issues.append(_issue(f"{kind}_DEPENDENCY_MISSING", f"Declared {kind.title()} is missing: {name}", dependency))
            if name not in dependency_bindings:
                issues.append(_issue(f"{kind}_BINDING_MISSING", f"Declared {kind.title()} is not bound in the contract body: {name}", command_file))

    return {
        "ok": not issues,
        "command_file": str(command_file),
        "project_root": str(project_root),
        "issues": issues,
        "contract": {
            "name": frontmatter.get("name"),
            "risk_level": frontmatter.get("risk_level"),
            "skills": skills,
            "agents": agents,
            "step_count": len(steps),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a tool-neutral Command Contract")
    parser.add_argument("--command-file", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = validate_command_contract(Path(args.command_file), Path(args.project_root))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        print(f"[OK] Command Contract is valid: {report['command_file']}")
    else:
        print(f"[ERROR] Command Contract validation failed: {report['command_file']}")
        for issue in report["issues"]:
            print(f"  - [{issue['code']}] {issue['message']} ({issue['path']})")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
