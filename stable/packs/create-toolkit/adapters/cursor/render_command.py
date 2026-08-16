#!/usr/bin/env python3
"""Render a validated tool-neutral Command Contract as a Cursor command."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


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
        / "create-command-workflow"
        / "scripts"
        / "validate_command.py"
    )
    if not validator_path.is_file():
        raise FileNotFoundError(f"Shared validator not found: {validator_path}")
    spec = importlib.util.spec_from_file_location("create_command_validate_command", validator_path)
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


def _cursor_agent_bindings(agent_names: list[str]) -> str:
    if not agent_names:
        return "No Cursor Agent bindings are required for this Command."
    blocks = []
    for name in agent_names:
        blocks.append(
            f"""### `{name}`

```text
Task(
  subagent_type = "generalPurpose",
  prompt = \"""
  Read and adopt `.cursor/agents/{name}.md`.
  Mission: <the step-specific mission from the Command Contract>
  Return only the evidence required by its Verification Contract.
  \"""
)
```"""
        )
    return "\n\n".join(blocks)


def render_cursor_command(
    project_root: Path,
    contract_path: Path,
    output_path: Path | None = None,
) -> Path:
    project_root = project_root.resolve()
    contract_path = (
        contract_path.resolve()
        if contract_path.is_absolute()
        else (project_root / contract_path).resolve()
    )
    if not _inside(contract_path, project_root):
        raise ValueError("Command Contract must be inside the project root")

    validator = _load_validator(project_root)
    report = validator.validate_command_contract(contract_path, project_root)
    if not report["ok"]:
        codes = ", ".join(issue["code"] for issue in report["issues"])
        raise ValueError(f"Command Contract validation failed: {codes}")
    contract = validator.read_command_contract(contract_path)
    frontmatter = contract["frontmatter"]

    for agent in contract["agents"]:
        cursor_agent = project_root / ".cursor" / "agents" / f"{agent}.md"
        if not cursor_agent.is_file():
            raise FileNotFoundError(f"Cursor Agent adapter is missing: {cursor_agent}")

    cursor_root = (project_root / ".cursor" / "commands").resolve()
    if output_path is None:
        output_path = cursor_root / f"{frontmatter['name']}.md"
    else:
        output_path = (
            output_path.resolve()
            if output_path.is_absolute()
            else (project_root / output_path).resolve()
        )
    if not _inside(output_path, cursor_root):
        raise ValueError("Cursor command output must stay under .cursor/commands")
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite Cursor command: {output_path}")

    description = json.dumps(frontmatter["description"], ensure_ascii=False)
    source = contract_path.relative_to(project_root).as_posix()
    rendered = f"""---
description: {description}
---

<!-- Generated from {source}; edit the Command Contract, then render a new adapter. -->

{contract['body'].lstrip()}

## Cursor Agent Bindings

{_cursor_agent_bindings(contract['agents'])}
"""
    _atomic_write(output_path, rendered)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Cursor command from a shared Command Contract")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        output = render_cursor_command(
            Path(args.project_root),
            Path(args.contract),
            Path(args.output) if args.output else None,
        )
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 4
    print(f"[OK] Cursor command rendered: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
