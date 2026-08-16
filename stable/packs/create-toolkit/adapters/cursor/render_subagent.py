#!/usr/bin/env python3
"""Render a validated tool-neutral Agent Contract as a Cursor agent definition."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]*$")


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _load_validator(project_root: Path) -> Any:
    validator_path = (
        project_root
        / ".agents"
        / "skills"
        / "create-subagent-workflow"
        / "scripts"
        / "validate_agent.py"
    )
    if not validator_path.is_file():
        raise FileNotFoundError(f"Shared validator not found: {validator_path}")
    spec = importlib.util.spec_from_file_location("create_subagent_validate_agent", validator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load shared validator: {validator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def render_cursor_agent(
    project_root: Path,
    contract_path: Path,
    model_id: str,
    output_path: Path | None = None,
) -> Path:
    project_root = project_root.resolve()
    contract_path = (
        contract_path.resolve()
        if contract_path.is_absolute()
        else (project_root / contract_path).resolve()
    )
    if not _inside(contract_path, project_root):
        raise ValueError("Agent Contract must be inside the project root")
    if not MODEL_ID_PATTERN.fullmatch(model_id):
        raise ValueError("model ID must be a non-empty host identifier without whitespace")

    validator = _load_validator(project_root)
    report = validator.validate_agent_contract(contract_path, project_root)
    if not report["ok"]:
        codes = ", ".join(issue["code"] for issue in report["issues"])
        raise ValueError(f"Agent Contract validation failed: {codes}")
    contract = validator.read_agent_contract(contract_path)
    frontmatter = contract["frontmatter"]

    cursor_root = (project_root / ".cursor" / "agents").resolve()
    if output_path is None:
        output_path = cursor_root / f"{frontmatter['name']}.md"
    else:
        output_path = (
            output_path.resolve()
            if output_path.is_absolute()
            else (project_root / output_path).resolve()
        )
    if not _inside(output_path, cursor_root):
        raise ValueError("Cursor agent output must stay under .cursor/agents")
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite Cursor agent: {output_path}")

    description = json.dumps(frontmatter["description"], ensure_ascii=False)
    source = contract_path.relative_to(project_root).as_posix()
    rendered = f"""---
name: {frontmatter['name']}
description: {description}
model: {model_id}
---

<!-- Generated from {source}; edit the Agent Contract, then render a new adapter. -->

{contract['body'].lstrip()}
"""
    _atomic_write(output_path, rendered)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Cursor agent from a shared Agent Contract")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        output = render_cursor_agent(
            Path(args.project_root),
            Path(args.contract),
            args.model,
            Path(args.output) if args.output else None,
        )
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 4
    print(f"[OK] Cursor agent rendered: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
