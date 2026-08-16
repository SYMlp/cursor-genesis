import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


workflow = _load("create_rule_workflow", SCRIPTS_ROOT / "workflow.py")
register = _load("create_rule_register", SCRIPTS_ROOT / "register_rule.py")


def valid_rule(rule_id: str = "safe-edit") -> str:
    return f"""<!-- cg-rule-contract:{rule_id}:start -->
## Rule: Safe Edit
- ID: `{rule_id}`
- Activation: always
- Description: Bound risky changes before editing
- Paths: []
- Trigger: When a change may affect protected behavior
- Rationale: Missing the boundary can cause irreversible regressions

### Behavior
- MUST identify the exact modification scope before writing.
- MUST NOT modify protected files without explicit authorization.

### Exclusions
- Routine read-only inspection is outside this Rule.

### Verification
- Review the final diff and test evidence before reporting completion.
<!-- cg-rule-contract:{rule_id}:end -->
"""


class RuleWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "AGENTS.md").write_text("# Project Rules\n", encoding="utf-8")
        self.state = self.root / "docs" / "state" / "create-rule" / "safe-edit.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _to_refine(self):
        workflow.initialize_state(
            self.state,
            self.root,
            "safe-edit",
            "Bound risky changes before editing",
        )
        code, _, _ = workflow.resume_gate(
            self.state,
            "analyzed",
            "Rule type confirmed",
            activation="always",
            trigger="When a change may affect protected behavior",
            rationale="Missing the boundary can cause irreversible regressions",
        )
        self.assertEqual(workflow.EXIT_SUCCESS, code)
        code, state, _ = workflow.run_current_stage(self.state)
        self.assertEqual(workflow.EXIT_WAITING, code)
        return Path(state["artifacts"]["draft"])

    def test_happy_path_registers_and_completes_without_adapter(self):
        draft = self._to_refine()
        draft.write_text(valid_rule(), encoding="utf-8")
        workflow.resume_gate(self.state, "refined", "Draft completed")
        code, state, _ = workflow.run_current_stage(self.state)
        self.assertEqual(workflow.EXIT_WAITING, code)
        self.assertEqual("register", state["current_stage"])

        register.register_rule(
            self.root,
            draft,
            Path("AGENTS.md"),
            "safe-edit",
        )
        code, state, _ = workflow.resume_gate(
            self.state,
            "registered",
            "Diff reviewed",
        )
        self.assertEqual(workflow.EXIT_SUCCESS, code)
        self.assertEqual("adapt", state["current_stage"])
        code, state, _ = workflow.resume_gate(
            self.state,
            "adaptation-not-required",
            "AGENTS.md is sufficient for this consumer",
        )
        self.assertEqual(workflow.EXIT_SUCCESS, code)
        self.assertEqual("completed", state["status"])

    def test_registration_gate_verifies_exact_block(self):
        draft = self._to_refine()
        draft.write_text(valid_rule(), encoding="utf-8")
        workflow.resume_gate(self.state, "refined", "Draft completed")
        workflow.run_current_stage(self.state)
        code, state, message = workflow.resume_gate(
            self.state,
            "registered",
            "Claimed registration",
        )
        self.assertEqual(workflow.EXIT_BLOCKED, code)
        self.assertEqual("waiting", state["status"])
        self.assertIn("missing", message)

    def test_validation_failure_is_retryable(self):
        draft = self._to_refine()
        workflow.resume_gate(self.state, "refined", "Draft needs validation")
        code, state, _ = workflow.run_current_stage(self.state)
        self.assertEqual(workflow.EXIT_RETRYABLE, code)
        self.assertEqual("failed", state["status"])
        draft.write_text(valid_rule(), encoding="utf-8")
        code, _, _ = workflow.retry_failed_stage(self.state, "Fixed placeholders")
        self.assertEqual(workflow.EXIT_SUCCESS, code)
        code, state, _ = workflow.run_current_stage(self.state)
        self.assertEqual(workflow.EXIT_WAITING, code)
        self.assertEqual("register", state["current_stage"])

    def test_scaffold_refuses_overwrite(self):
        workflow.initialize_state(
            self.state,
            self.root,
            "safe-edit",
            "Bound risky changes before editing",
        )
        workflow.resume_gate(
            self.state,
            "analyzed",
            "Rule type confirmed",
            activation="always",
            trigger="When a change may affect protected behavior",
            rationale="Missing the boundary can cause irreversible regressions",
        )
        draft = self.root / "docs" / "state" / "create-rule" / "drafts" / "safe-edit.md"
        draft.parent.mkdir(parents=True)
        draft.write_text("existing", encoding="utf-8")
        code, state, _ = workflow.run_current_stage(self.state)
        self.assertEqual(workflow.EXIT_BLOCKED, code)
        self.assertEqual("blocked", state["status"])

    def test_register_script_refuses_duplicate_and_wrong_confirmation(self):
        draft = self.root / "rule.md"
        draft.write_text(valid_rule(), encoding="utf-8")
        with self.assertRaises(ValueError):
            register.register_rule(
                self.root,
                draft,
                Path("AGENTS.md"),
                "different-id",
            )
        register.register_rule(self.root, draft, Path("AGENTS.md"), "safe-edit")
        with self.assertRaises(FileExistsError):
            register.register_rule(self.root, draft, Path("AGENTS.md"), "safe-edit")


if __name__ == "__main__":
    unittest.main()
