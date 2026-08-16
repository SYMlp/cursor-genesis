import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from workflow import (
    EXIT_BLOCKED,
    EXIT_RETRYABLE,
    EXIT_SUCCESS,
    EXIT_WAITING,
    initialize_state,
    load_state,
    resume_gate,
    retry_validation,
    run_current_stage,
)


class CreateSkillWorkflowTests(unittest.TestCase):
    def _initialize(self, root: Path, max_attempts: int = 3) -> Path:
        state_path = root / "docs" / "state" / "create-skill" / "example.json"
        initialize_state(
            state_path=state_path,
            project_root=root,
            name="example",
            scope="base",
            description="Deterministic example.",
            category="executor",
            max_validation_attempts=max_attempts,
        )
        return state_path

    def _refine(self, state_path: Path) -> None:
        state = load_state(state_path)
        skill_md = Path(state["artifacts"]["skill_dir"]) / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        content = content.replace(
            "TODO: Replace this placeholder with the concrete workflow.",
            "Run one deterministic transformation.",
        )
        content = content.replace(
            "TODO: Define a deterministic verification command or observable result.",
            "Run python -m unittest and require exit code zero.",
        )
        content = content.replace(
            "TODO: List reads, writes, external calls, and meaningful human gates.",
            "Reads declared input and writes only the target Skill directory.",
        )
        skill_md.write_text(content, encoding="utf-8")

    def test_happy_path_persists_gates_and_completes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = self._initialize(root)

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual(("refine", "waiting"), (state["current_stage"], state["status"]))

            self._refine(state_path)
            code, _, _ = resume_gate(state_path, "refined", "Refinement complete")
            self.assertEqual(EXIT_SUCCESS, code)

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual(("register", "waiting"), (state["current_stage"], state["status"]))
            self.assertTrue(state["artifacts"]["validation_report"]["ok"])

            code, state, _ = resume_gate(state_path, "registration-not-required", "No inventory in fixture")
            self.assertEqual(EXIT_SUCCESS, code)
            self.assertEqual(("complete", "completed"), (state["current_stage"], state["status"]))
            self.assertGreaterEqual(len(state["history"]), 5)

    def test_validation_failure_is_retryable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = self._initialize(root)
            run_current_stage(state_path)
            resume_gate(state_path, "refined", "Intentionally incomplete")

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_RETRYABLE, code)
            self.assertEqual("failed", state["status"])
            self.assertEqual(1, state["attempts"]["validate"])

            self._refine(state_path)
            code, state, _ = retry_validation(state_path, "Fixed placeholders")
            self.assertEqual(EXIT_SUCCESS, code)
            self.assertEqual("ready", state["status"])

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual("register", state["current_stage"])
            self.assertEqual(2, state["attempts"]["validate"])

    def test_retry_limit_blocks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = self._initialize(root, max_attempts=1)
            run_current_stage(state_path)
            resume_gate(state_path, "refined", "Still incomplete")
            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_BLOCKED, code)
            self.assertEqual("blocked", state["status"])
            retry_code, _, _ = retry_validation(state_path, "Too late")
            self.assertEqual(EXIT_BLOCKED, retry_code)

    def test_existing_target_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / ".agents" / "skills" / "base-example"
            target.mkdir(parents=True)
            sentinel = target / "sentinel.txt"
            sentinel.write_text("keep", encoding="utf-8")
            state_path = self._initialize(root)

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_BLOCKED, code)
            self.assertEqual("keep", sentinel.read_text(encoding="utf-8"))
            self.assertEqual("TARGET_EXISTS", state["errors"][-1]["code"])

    def test_empty_existing_target_is_not_claimed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / ".agents" / "skills" / "base-example"
            target.mkdir(parents=True)
            state_path = self._initialize(root)

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_BLOCKED, code)
            self.assertEqual([], list(target.iterdir()))
            self.assertEqual("TARGET_EXISTS", state["errors"][-1]["code"])

    def test_scaffold_quotes_frontmatter_description(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = root / "docs" / "state" / "create-skill" / "quoted.json"
            initialize_state(
                state_path=state_path,
                project_root=root,
                name="quoted",
                scope="base",
                description='Route: "safe" and explicit',
                category="executor",
            )

            run_current_stage(state_path)
            skill_md = (
                root / ".agents" / "skills" / "base-quoted" / "SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn('description: "Route: \\"safe\\" and explicit"', skill_md)


if __name__ == "__main__":
    unittest.main()
