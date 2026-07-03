---
name: base-skill-generator
description: [Base] Standardized factory for creating new AI Skills following Anthropic best practices.
metadata:
  version: "1.0"
  freedom_level: low

# === 认知元层字段 ===
category: generator
meta_level: L2
maturity: stable
tags: ["creation", "scaffolding", "skill-factory", "7-layer", "hybrid-generation"]
---

# Skill: Base Skill Generator

## 1. Description

This skill is the **Factory of Skills**. It automates the creation of a standardized AI Skill directory structure, ensuring compliance with V2.1 Engineering Standards.

It generates:

* **7-Layer Directory**: `scripts`, `references`, `assets`, `tests`, etc.
* **Standard Files**: `SKILL.md` (with Frontmatter), `README.md`, `test_config.json`.
* **Boilerplate**: Basic Python script template.

## 2. Requirements

* Python 3.10+
* Write access to `.cursor/skills/`

## 3. Interface (CLI)

> **Standard**: See `.cursor/skills/base-skill-generator/assets/docs/script-interface-standard.md`

**Script**: `scripts/gen.py`

**Parameters**:

| Flag            | Type   | Required | Description                                                |
| :-------------- | :----- | :------- | :--------------------------------------------------------- |
| `--name`        | String | Yes      | The core name of the skill (e.g., `data-processor`).       |
| `--scope`       | String | No       | The scope prefix (`meta`, `base`, `app`). Default: `base`. |
| `--description` | String | No       | A short summary for Frontmatter.                           |
| `--target`      | Path   | No       | Project root. Default: `.`                                 |

## 4. Usage Examples

### Example 1: Create a Base Skill

```bash
python .cursor/skills/base-skill-generator/scripts/gen.py --name "pdf-parser" --scope "base" --description "Extracts text from PDF files."
```

> **Result**: Creates `.cursor/skills/base-pdf-parser/`

### Example 2: Create an App Skill

```bash
python .cursor/skills/base-skill-generator/scripts/gen.py --name "order-validator" --scope "app" --description "Validates e-commerce orders."
```

> **Result**: Creates `.cursor/skills/app-order-validator/`

## 5. Progressive Workflow (The Hybrid Thinking Process)

### Phase 1: Preparation (Read & Design)
>
> **Goal**: Absorb best practices and design the skill mentally.

1. **Read Knowledge Base** (Priority Order):
    * **Tier 1 (The DNA)**: `read_file .cursor/skills/base-skill-generator/assets/docs/meta-structure-standard.md` (The "Five Elements" of Agentic Capability).
    * **Tier 2 (Best Practices)**: `read_file .cursor/skills/base-skill-generator/assets/docs/skill-design-guide.md` (The Red Book).
    * **Tier 3 (Design Pattern)**:
        * `read_file .cursor/skills/base-skill-generator/assets/docs/hybrid-scaffolding-pattern.md` (Skeleton & Soul).
        * `read_file .cursor/skills/base-skill-generator/assets/docs/subagent-invocation-pattern.md` (Role Injection).
    * **Tier 4 (Architecture)**:
        * `read_file .cursor/skills/base-skill-generator/assets/docs/skill-composition-theory.md` (Composition).
        * `read_file .cursor/skills/base-skill-generator/assets/docs/standard-command.md` (Commands).
        * `read_file .cursor/skills/base-skill-generator/assets/docs/standard-subagent.md` (Subagents).
2. **Define Strategy (Meta-Analysis)**:
    * **Identity Check**: What is the Scope and Name? Does it fit the `meta-structure`?
    * **Type Determination**: Skill vs Command vs Subagent.
    * **Process Design**: Does the Workflow follow the EPE Loop (Explore -> Plan -> Execute)?
    * **Verification Strategy**: What is the "Adversarial Trinity" (Generator-Auditor-Optimizer) for this capability?
    * **Interface Contract**: Define strict CLI arguments or JSON schema.

### Phase 2: Execution (The Scaffolding)
>
> **Goal**: Use the script to create the physical structure.

1. **Run Script**:

    ```bash
    python .cursor/skills/base-skill-generator/scripts/gen.py --name "your-skill-name" --description "Your short description"
    ```

    * *Note*: The script creates the directory structure and a *generic* `SKILL.md`. It does NOT write your complex logic yet.

### Phase 3: Refinement (The Injection)
>
> **Goal**: Inject intelligence into the skeleton.

1. **Edit `SKILL.md`**: IMMEDIATELY open the generated file.
2. **Inject Logic**: Replace the generic `## 4. Workflow` with your specific steps designed in Phase 1.
3. **Inject Verification**: Fill in `## 5. Verification` with concrete commands.
4. **Inject Context Rules**: define strict boundaries in `## 6. Context & Side Effects`.

## 6. Verification

### 6.1 Success Criteria

* 生成的目录结构与 7-Layer 标准完全一致；
* `SKILL.md` Frontmatter 字段完整，无语法错误；
* 执行 `python [skill-path]/tests/test_gen.py` 所有测试用例通过。

### 6.2 Verification Commands

```bash
# 检查目录结构
ls .cursor/skills/base-pdf-parser/ | grep -E "scripts|references|assets|tests|docs|config|logs"
# 运行测试用例
python .cursor/skills/base-pdf-parser/tests/test_gen.py
```
