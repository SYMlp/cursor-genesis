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
    / "render_subagent.py"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


installer = _load("install_pack_for_cursor_adapter", INSTALLER_PATH)
renderer = _load("render_cursor_subagent", RENDERER_PATH)


class CursorSubagentAdapterTests(unittest.TestCase):
    def _contract(self, root: Path) -> Path:
        contract = root / ".agents" / "agents" / "base-reviewer.md"
        contract.parent.mkdir(parents=True)
        contract.write_text(
            """---
name: base-reviewer
description: "Review changes and return evidence"
kind: agent-contract
model_profile: synthesis
context_isolation: required
skills: []
---

# Agent Contract: base-reviewer

## Identity
Review the declared change.

## Skills
- No deterministic Skill dependencies declared after explicit analysis.

## Workflow
1. Inspect.
2. Return findings.

## Constraints
- Do not modify files.

## Verification Contract
- Return evidence.

## Adapter Notes
The host chooses its invocation format.
""",
            encoding="utf-8",
        )
        return contract

    def test_renderer_uses_shared_contract_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            installer.install_pack("create-toolkit", root, REPO_ROOT)
            contract = self._contract(root)

            output = renderer.render_cursor_agent(
                root,
                contract,
                "current-model-id",
            )

            content = output.read_text(encoding="utf-8")
            self.assertIn("model: current-model-id", content)
            self.assertIn("Generated from .agents/agents/base-reviewer.md", content)
            self.assertIn("## Verification Contract", content)
            with self.assertRaises(FileExistsError):
                renderer.render_cursor_agent(root, contract, "current-model-id")

    def test_renderer_rejects_output_outside_cursor_agents(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            installer.install_pack("create-toolkit", root, REPO_ROOT)
            contract = self._contract(root)
            with self.assertRaises(ValueError):
                renderer.render_cursor_agent(
                    root,
                    contract,
                    "current-model-id",
                    root / "outside.md",
                )


if __name__ == "__main__":
    unittest.main()
