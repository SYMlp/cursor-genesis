import os
import argparse
import json
from pathlib import Path

CATEGORY_META_LEVEL_MAP = {
    "executor": "L0",
    "generator": "L2",
    "analyzer": "L1",
    "orchestrator": "L1",
    "researcher": "L1",
}

VALID_CATEGORIES = list(CATEGORY_META_LEVEL_MAP.keys())


def create_skill(name, scope, description, target_dir=".", category="executor", meta_level=None):
    """
    Generates a standard Anthropic-style AI Skill structure with Meta Layer support.
    """
    full_name = f"{scope}-{name}" if scope else name
    skill_path = Path(target_dir) / ".cursor" / "skills" / full_name

    if meta_level is None:
        meta_level = CATEGORY_META_LEVEL_MAP.get(category, "L0")

    print(f"🚀 Generating Skill: {full_name} at {skill_path}...")
    print(f"   Category: {category} | Meta Level: {meta_level}")

    dirs = [
        "scripts",
        "references",
        "assets/templates",
        "assets/images",
        "assets/data",
        "tests"
    ]

    if meta_level in ("L1", "L2"):
        dirs.append(".meta")

    for d in dirs:
        (skill_path / d).mkdir(parents=True, exist_ok=True)
        print(f"  + Created directory: {d}")

    skill_md_content = f"""---
name: {full_name}
description: {description}
metadata:
  version: "1.0"
  freedom_level: medium
category: {category}
meta_level: {meta_level}
maturity: experimental
tags: []
---

# Skill: {name.replace('-', ' ').title()}

## 1. Description
{description}

> **Best Practice**: If this skill involves complex logic (e.g., refactoring, migration),
> explicitly recommend using `Plan Mode` (via `todo_write`) in step 1.

## 2. Requirements
*   Python 3.10+ (if using scripts)
*   [Add other dependencies]

## 3. Interface (CLI)

> **Standard**: See `.cursor/standards/skill-meta-standard.md`

**Script**: `scripts/core.py`

**Parameters**:

| Flag | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `--input` | String | Yes | Input data. |

## 4. Workflow (Logic)
1.  **Explore**: [Optional] Read files or search context.
2.  **Plan**: [Optional] Define steps if complex.
3.  **Execute**: Run the core logic.
4.  **Verify**: Check results.

## 5. Verification (The Loop)
> **Rule**: Every skill must have a way to verify its own success.
1.  **Test**: Run `python scripts/core.py --input "test"`
2.  **Check**: Output contains "Processing input: test"
3.  **Correction**: If failed, analyze error -> fix -> re-run.

## 6. Context & Side Effects
*   **Reads**: [List files read]
*   **Writes**: [List files written]
*   **Context Cost**: [Low/Medium/High] - Recommend `/clear` after usage if High.
"""
    with open(skill_path / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(skill_md_content)
    print("  + Created file: SKILL.md")

    if meta_level in ("L1", "L2"):
        _generate_guide_md(skill_path, full_name, name)

    if meta_level == "L2":
        _generate_factory_records(full_name, target_dir)

    # 4. Generate README.md (Human Readable)
    readme_content = f"""# {full_name}

> {description}

## Structure
*   `SKILL.md`: The AI Prompt definition.
*   `scripts/`: Executable logic.
*   `tests/`: Unit test configurations.
"""
    with open(skill_path / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("  + Created file: README.md")

    # 5. Generate Test Config (tests/test_config.json)
    test_config = {
        "skills": [full_name],
        "cases": [
            {
                "query": "Test query for this skill",
                "files": [],
                "expected_behavior": [
                    "Step 1 executed successfully",
                    "Output file generated"
                ]
            }
        ]
    }
    with open(skill_path / "tests" / "test_config.json", "w", encoding="utf-8") as f:
        json.dump(test_config, f, indent=2)
    print("  + Created file: tests/test_config.json")

    # 6. Generate Placeholder Script (scripts/core.py)
    script_content = """import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Core logic for skill.")
    parser.add_argument("--input", required=True, help="Input data")
    args = parser.parse_args()

    print(f"Processing input: {args.input}")
    # Add logic here

if __name__ == "__main__":
    main()
"""
    with open(skill_path / "scripts" / "core.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    print("  + Created file: scripts/core.py")

    # 7. Generate Test Verification Script (tests/test_gen.py)
    meta_test_block = ""
    if meta_level in ("L1", "L2"):
        meta_test_block = '''
    def test_meta_layer(self):
        """Verify Meta Layer exists for L1+ Skill"""
        self.assertTrue((self.skill_path / ".meta" / "GUIDE.md").exists(),
                        "Missing .meta/GUIDE.md for L1+ Skill")
'''

    test_gen_content = f"""import unittest
import os
from pathlib import Path

class TestSkillStructure(unittest.TestCase):
    def setUp(self):
        self.skill_path = Path(__file__).parent.parent

    def test_directory_structure(self):
        \"\"\"Verify the 7-Layer Directory Standard\"\"\"
        required_dirs = [
            "scripts",
            "references",
            "assets/templates",
            "assets/images",
            "assets/data",
            "tests"
        ]
        for d in required_dirs:
            self.assertTrue((self.skill_path / d).exists(), f"Directory missing: {{d}}")

    def test_required_files(self):
        \"\"\"Verify Standard Files exist\"\"\"
        required_files = ["SKILL.md", "README.md", "tests/test_config.json", "scripts/core.py"]
        for f in required_files:
            self.assertTrue((self.skill_path / f).exists(), f"File missing: {{f}}")

    def test_frontmatter_has_category(self):
        \"\"\"Verify Frontmatter contains category field\"\"\"
        content = (self.skill_path / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("category:", content, "SKILL.md missing 'category' in Frontmatter")
{meta_test_block}
if __name__ == "__main__":
    unittest.main()
"""
    with open(skill_path / "tests" / "test_gen.py", "w", encoding="utf-8") as f:
        f.write(test_gen_content)
    print("  + Created file: tests/test_gen.py")

    print(f"✅ Skill {full_name} created successfully! (category={category}, meta_level={meta_level})")


def _generate_guide_md(skill_path: Path, full_name: str, short_name: str):
    """Generate .meta/GUIDE.md for L1+ Skills."""
    title = short_name.replace("-", " ").title()
    guide_content = f"""# {title} 修改与优化指南

## 1. 架构速览 (Architecture at a Glance)

> 用 1-2 段话说明这个 Skill 的核心设计思路。不是"做什么"（那是 SKILL.md 的职责），
> 而是"为什么这样做"。

[待填写]

## 2. 修改地图 (Modification Map)

| 想要改的行为 | 应该修改的文件/位置 | 注意事项 |
|:-------------|:--------------------|:---------|
| [示例] | [示例] | [示例] |

## 3. 优化方向 (Optimization Roadmap)

| 方向 | 描述 | 优先级 | 发现时间 |
|:-----|:-----|:-------|:---------|
| [示例] | [示例] | 低 | [日期] |

## 4. 不可动区域 (Invariants)

- `SKILL.md` 的 Frontmatter `name` 字段不能改（与目录名绑定，被 inventory 索引）
- `scripts/core.py` 的 `main()` 入口签名不能改（被 Command 直接调用）
"""
    with open(skill_path / ".meta" / "GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    print("  + Created file: .meta/GUIDE.md")


def _generate_factory_records(skill_name: str, target_dir: str):
    """Generate _meta/data/skill-meta/<name>/ factory records for L2 Skills."""
    meta_dir = Path(target_dir) / "_meta" / "data" / "skill-meta" / skill_name
    meta_dir.mkdir(parents=True, exist_ok=True)

    design_content = f"""# {skill_name} 设计记录

## 创建背景
> 为什么需要这个 Skill？解决什么问题？

[待填写]

## 设计讨论

### 讨论 1：[主题]
- **问题**：...
- **方案 A**：...
- **方案 B**：...
- **选择**：方案 X，因为...

## 关键设计决策摘要

| 决策点 | 选择 | 替代方案 | 选择理由 |
|:-------|:-----|:---------|:---------|
"""
    with open(meta_dir / "DESIGN.md", "w", encoding="utf-8") as f:
        f.write(design_content)

    references_content = f"""# {skill_name} 参考来源

## 内部参考（项目内）

| 文件 | 参考了什么 | 如何影响设计 |
|:-----|:-----------|:-------------|

## 外部参考

| 来源 | 链接/出处 | 参考了什么 |
|:-----|:----------|:-----------|

## 同类 Skill 参考

| Skill 名称 | 借鉴了什么 | 差异点 |
|:-----------|:-----------|:-------|
"""
    with open(meta_dir / "REFERENCES.md", "w", encoding="utf-8") as f:
        f.write(references_content)

    print(f"  + Created factory records: _meta/data/skill-meta/{skill_name}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a standard AI Skill structure with Meta Layer.")
    parser.add_argument("--name", required=True, help="Name of the skill (e.g., 'data-processor')")
    parser.add_argument("--scope", default="base", help="Scope prefix (meta/base/app). Default: base")
    parser.add_argument("--description", default="A new capability.", help="Short description.")
    parser.add_argument("--target", default=".", help="Target project root. Default: current dir")
    parser.add_argument("--category", default="executor", choices=VALID_CATEGORIES,
                        help="Skill category tag. Default: executor")
    parser.add_argument("--meta-level", default=None, choices=["L0", "L1", "L2"],
                        help="Meta layer level. Auto-determined from category if omitted.")

    args = parser.parse_args()

    create_skill(args.name, args.scope, args.description, args.target,
                 args.category, args.meta_level)
