import importlib.util
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_ROOT / "scripts" / "validate_rule.py"
SPEC = importlib.util.spec_from_file_location("create_rule_validate_rule", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


def valid_rule(
    rule_id: str = "safe-edit",
    activation: str = "always",
    paths: str = "[]",
) -> str:
    return f"""<!-- cg-rule-contract:{rule_id}:start -->
## Rule: Safe Edit
- ID: `{rule_id}`
- Activation: {activation}
- Description: Bound risky changes before editing
- Paths: {paths}
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


class RuleValidatorTests(unittest.TestCase):
    def _validate(self, content: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "rule.md"
            path.write_text(content, encoding="utf-8")
            return validator.validate_rule_file(path)

    def test_valid_rule(self):
        report = self._validate(valid_rule())
        self.assertTrue(report["ok"], report["issues"])
        self.assertEqual("safe-edit", report["rule"]["id"])

    def test_paths_activation_accepts_public_multi_path_scope(self):
        report = self._validate(
            valid_rule(
                activation="paths",
                paths='["src/critical/**", "config/*.yaml"]',
            )
        )
        self.assertTrue(report["ok"], report["issues"])

    def test_activation_path_contract_is_enforced(self):
        missing = self._validate(valid_rule(activation="paths", paths="[]"))
        extra = self._validate(valid_rule(activation="always", paths='["src/**"]'))
        self.assertIn("PATHS_REQUIRED", {issue["code"] for issue in missing["issues"]})
        self.assertIn("PATHS_NOT_ALLOWED", {issue["code"] for issue in extra["issues"]})

    def test_host_syntax_and_placeholders_are_rejected(self):
        content = valid_rule().replace(
            "- MUST identify the exact modification scope before writing.",
            "- MUST write .cursor/rules/example.mdc with alwaysApply: true.\n- SHOULD TODO refine this.",
        )
        report = self._validate(content)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("HOST_SPECIFIC_RULE_CORE", codes)
        self.assertIn("PLACEHOLDER_REMAINS", codes)

    def test_behavior_directives_and_thin_limit_are_enforced(self):
        invalid = valid_rule().replace(
            "- MUST identify the exact modification scope before writing.",
            "- Consider identifying scope.",
        )
        report = self._validate(invalid)
        self.assertIn(
            "BEHAVIOR_DIRECTIVE_INVALID",
            {issue["code"] for issue in report["issues"]},
        )
        oversized = valid_rule().replace(
            "### Exclusions",
            "\n".join([""] * 65) + "\n### Exclusions",
        )
        report = self._validate(oversized)
        self.assertIn("RULE_TOO_LONG", {issue["code"] for issue in report["issues"]})

    def test_draft_may_only_contain_one_block(self):
        report = self._validate("preface\n" + valid_rule())
        self.assertIn(
            "RULE_DRAFT_EXTRA_CONTENT",
            {issue["code"] for issue in report["issues"]},
        )


if __name__ == "__main__":
    unittest.main()
