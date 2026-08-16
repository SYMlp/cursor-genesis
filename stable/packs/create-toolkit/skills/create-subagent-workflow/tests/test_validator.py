import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_agent import validate_agent_contract


class ValidateAgentContractTests(unittest.TestCase):
    def _project_with_contract(self, root: Path) -> Path:
        skill_file = root / ".agents" / "skills" / "base-code-search" / "SKILL.md"
        skill_file.parent.mkdir(parents=True)
        skill_file.write_text("# code search\n", encoding="utf-8")
        agent_file = root / ".agents" / "agents" / "base-reviewer.md"
        agent_file.parent.mkdir(parents=True)
        agent_file.write_text(
            """---
name: base-reviewer
description: "Review changes and return evidence"
kind: agent-contract
model_profile: synthesis
context_isolation: required
skills: ["base-code-search"]
---

# Agent Contract: base-reviewer

## Identity
Review changes within declared scope.

## Skills
- `base-code-search`: `.agents/skills/base-code-search/SKILL.md`

## Workflow
1. Inspect the requested change.
2. Return evidence-backed findings.

## Constraints
- Do not modify files.

## Verification Contract
- Return file paths and concise findings.

## Adapter Notes
The host adapter chooses its concrete model and invocation format.
""",
            encoding="utf-8",
        )
        return agent_file

    def test_valid_contract_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report = validate_agent_contract(self._project_with_contract(root), root)
        self.assertTrue(report["ok"], report["issues"])

    def test_host_specific_content_and_concrete_model_fail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            agent_file = self._project_with_contract(root)
            content = agent_file.read_text(encoding="utf-8")
            content = content.replace(
                "model_profile: synthesis",
                "model_profile: synthesis\nmodel: cursor-model",
            )
            content += '\nTask(subagent_type="generalPurpose")\n'
            agent_file.write_text(content, encoding="utf-8")
            report = validate_agent_contract(agent_file, root)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("CONCRETE_MODEL_IN_CORE", codes)
        self.assertIn("HOST_SPECIFIC_CORE_CONTENT", codes)

    def test_missing_skill_dependency_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            agent_file = self._project_with_contract(root)
            (root / ".agents" / "skills" / "base-code-search" / "SKILL.md").unlink()
            report = validate_agent_contract(agent_file, root)
        self.assertIn(
            "SKILL_DEPENDENCY_MISSING",
            {issue["code"] for issue in report["issues"]},
        )

    def test_placeholder_and_name_mismatch_fail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            agent_file = self._project_with_contract(root)
            content = agent_file.read_text(encoding="utf-8")
            content = content.replace("name: base-reviewer", "name: wrong-name")
            content = content.replace(
                "Review changes within declared scope.",
                "TODO: define identity",
            )
            agent_file.write_text(content, encoding="utf-8")
            report = validate_agent_contract(agent_file, root)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("NAME_FILE_MISMATCH", codes)
        self.assertIn("PLACEHOLDER_REMAINS", codes)


if __name__ == "__main__":
    unittest.main()
