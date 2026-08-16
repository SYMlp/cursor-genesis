import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER_PATH = REPO_ROOT / "scripts" / "install-pack.py"
RENDERER_PATH = (
    REPO_ROOT
    / "stable"
    / "packs"
    / "create-toolkit"
    / "adapters"
    / "cursor"
    / "render_command.py"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


installer = _load("install_pack_for_cursor_command_adapter", INSTALLER_PATH)
renderer = _load("render_cursor_command", RENDERER_PATH)


class CursorCommandAdapterTests(unittest.TestCase):
    def _contract(self, root: Path) -> Path:
        agent_contract = root / ".agents" / "agents" / "base-reviewer.md"
        agent_contract.parent.mkdir(parents=True)
        agent_contract.write_text("# agent\n", encoding="utf-8")
        cursor_agent = root / ".cursor" / "agents" / "base-reviewer.md"
        cursor_agent.parent.mkdir(parents=True, exist_ok=True)
        cursor_agent.write_text("# cursor agent\n", encoding="utf-8")
        contract = root / ".agents" / "commands" / "review.md"
        contract.parent.mkdir(parents=True)
        contract.write_text(
            """---
name: review
description: "Run a repeatable review SOP"
kind: command-contract
execution_mode: ordered-workflow
risk_level: low
skills: []
agents: ["base-reviewer"]
---

# Command Contract: review

## User Outcome
Return verified findings.

## Inputs & Preconditions
The caller supplies a scope.

## Dependency Bindings
- Agent `base-reviewer`: `.agents/agents/base-reviewer.md`

## Workflow
1. Delegate review to `base-reviewer`.
2. Verify the returned findings.

## Human Gates
No approval is required for this read-only SOP.

## Verification Contract
Return evidence and unresolved risks.

## Failure & Resume
Stop on missing evidence and resume from persisted state.

## Adapter Notes
The host exposes its current operation entry.
""",
            encoding="utf-8",
        )
        return contract

    def test_renderer_adds_cursor_agent_binding_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            installer.install_pack("create-toolkit", root, REPO_ROOT)
            contract = self._contract(root)

            output = renderer.render_cursor_command(root, contract)

            content = output.read_text(encoding="utf-8")
            self.assertIn("Generated from .agents/commands/review.md", content)
            self.assertIn('subagent_type = "generalPurpose"', content)
            self.assertIn(".cursor/agents/base-reviewer.md", content)
            with self.assertRaises(FileExistsError):
                renderer.render_cursor_command(root, contract)

    def test_renderer_requires_cursor_agent_adapter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            installer.install_pack("create-toolkit", root, REPO_ROOT)
            contract = self._contract(root)
            (root / ".cursor" / "agents" / "base-reviewer.md").unlink()
            with self.assertRaises(FileNotFoundError):
                renderer.render_cursor_command(root, contract)


if __name__ == "__main__":
    unittest.main()
