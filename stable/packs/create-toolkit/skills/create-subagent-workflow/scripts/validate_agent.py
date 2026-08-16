#!/usr/bin/env python3
"""Deterministic validator for a tool-neutral Agent Contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_MODEL_PROFILES = {"exploration", "balanced", "execution", "synthesis"}
REQUIRED_FIELDS = (
    "name",
    "description",
    "kind",
    "model_profile",
    "context_isolation",
    "skills",
)
REQUIRED_HEADINGS = (
    "## Identity",
    "## Skills",
    "## Workflow",
    "## Constraints",
    "## Verification Contract",
    "## Adapter Notes",
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\[待填写\]"),
    re.compile(r"\[Add [^\]]+\]", re.IGNORECASE),
)
HOST_SPECIFIC_PATTERNS = (
    re.compile(r"\.cursor/agents", re.IGNORECASE),
    re.compile(r"\.claude/agents", re.IGNORECASE),
    re.compile(r"\.codex/", re.IGNORECASE),
    re.compile(r"\bsubagent_type\b"),
    re.compile(r"\bTask\s*\("),
)
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


def _parse_skills(raw_value: str) -> list[str]:
    parsed = json.loads(raw_value)
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("skills must be a JSON string array")
    return parsed


def read_agent_contract(agent_file: Path) -> dict[str, Any]:
    content = agent_file.read_text(encoding="utf-8")
    frontmatter_text, body = _split_frontmatter(content)
    if frontmatter_text is None:
        raise ValueError("Agent Contract must start with closed YAML frontmatter")
    frontmatter = _parse_frontmatter(frontmatter_text)
    skills = _parse_skills(frontmatter.get("skills", "null"))
    return {
        "content": content,
        "frontmatter_text": frontmatter_text,
        "frontmatter": frontmatter,
        "skills": skills,
        "body": body,
    }


def validate_agent_contract(agent_file: Path, project_root: Path) -> dict[str, Any]:
    agent_file = agent_file.resolve()
    project_root = project_root.resolve()
    issues: list[dict[str, str]] = []

    if not agent_file.is_file():
        issues.append(_issue("AGENT_FILE_MISSING", "Agent Contract does not exist", agent_file))
        return {"ok": False, "agent_file": str(agent_file), "issues": issues}

    content = agent_file.read_text(encoding="utf-8")
    frontmatter_text, body = _split_frontmatter(content)
    frontmatter: dict[str, str] = {}
    skills: list[str] = []
    if frontmatter_text is None:
        issues.append(_issue("FRONTMATTER_MISSING", "Agent Contract must start with closed YAML frontmatter", agent_file))
    else:
        frontmatter = _parse_frontmatter(frontmatter_text)
        for field in REQUIRED_FIELDS:
            if field not in frontmatter or (field != "skills" and not frontmatter[field]):
                issues.append(_issue("FRONTMATTER_FIELD_MISSING", f"Missing frontmatter field: {field}", agent_file))

        if "model" in frontmatter:
            issues.append(
                _issue(
                    "CONCRETE_MODEL_IN_CORE",
                    "Concrete model IDs belong in host adapters; use model_profile in the core contract",
                    agent_file,
                )
            )
        if frontmatter.get("kind") and frontmatter["kind"] != "agent-contract":
            issues.append(_issue("INVALID_KIND", "kind must be agent-contract", agent_file))
        if (
            frontmatter.get("model_profile")
            and frontmatter["model_profile"] not in ALLOWED_MODEL_PROFILES
        ):
            issues.append(_issue("INVALID_MODEL_PROFILE", "Unsupported model_profile", agent_file))
        if frontmatter.get("context_isolation") and frontmatter["context_isolation"] != "required":
            issues.append(
                _issue(
                    "CONTEXT_ISOLATION_REQUIRED",
                    "Subagent contracts must declare context_isolation: required",
                    agent_file,
                )
            )
        if frontmatter.get("name") and frontmatter["name"] != agent_file.stem:
            issues.append(
                _issue(
                    "NAME_FILE_MISMATCH",
                    f"Frontmatter name '{frontmatter['name']}' does not match file '{agent_file.stem}'",
                    agent_file,
                )
            )

        try:
            skills = _parse_skills(frontmatter.get("skills", "null"))
        except (json.JSONDecodeError, ValueError):
            issues.append(
                _issue(
                    "SKILLS_FORMAT_INVALID",
                    "skills must be a JSON string array, for example [\"base-code-search\"]",
                    agent_file,
                )
            )

    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            issues.append(_issue("REQUIRED_SECTION_MISSING", f"Missing section: {heading}", agent_file))

    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(content):
            issues.append(_issue("PLACEHOLDER_REMAINS", f"Unresolved placeholder matched: {pattern.pattern}", agent_file))

    for pattern in HOST_SPECIFIC_PATTERNS:
        if pattern.search(content):
            issues.append(
                _issue(
                    "HOST_SPECIFIC_CORE_CONTENT",
                    f"Host-specific content belongs in an adapter: {pattern.pattern}",
                    agent_file,
                )
            )

    for skill_name in skills:
        if not SLUG_PATTERN.fullmatch(skill_name):
            issues.append(_issue("SKILL_NAME_INVALID", f"Invalid Skill slug: {skill_name}", agent_file))
            continue
        skill_file = project_root / ".agents" / "skills" / skill_name / "SKILL.md"
        if not skill_file.is_file():
            issues.append(
                _issue(
                    "SKILL_DEPENDENCY_MISSING",
                    f"Declared Skill is missing: {skill_name}",
                    skill_file,
                )
            )

    return {
        "ok": not issues,
        "agent_file": str(agent_file),
        "project_root": str(project_root),
        "issues": issues,
        "contract": {
            "name": frontmatter.get("name"),
            "model_profile": frontmatter.get("model_profile"),
            "skills": skills,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a tool-neutral Agent Contract")
    parser.add_argument("--agent-file", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = validate_agent_contract(Path(args.agent_file), Path(args.project_root))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        print(f"[OK] Agent Contract is valid: {report['agent_file']}")
    else:
        print(f"[ERROR] Agent Contract validation failed: {report['agent_file']}")
        for issue in report["issues"]:
            print(f"  - [{issue['code']}] {issue['message']} ({issue['path']})")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
