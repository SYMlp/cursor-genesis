---
name: base-closure-validator
description: Validates that AI-modified content forms a closed loop. Checks reference integrity, inventory consistency, and detects broken links.
scope: base
package:
  id: base-closure-validator
  version: "0.1.0"
  maturity: stable
  owner: template-maintainers
  tags: ["governance", "closure", "inventory", "references"]
platform:
  runtimes: ["cursor"]
dependencies:
  skills: ["base-inventory-updater"]
io_contract:
  outputs:
    - name: report
      type: text
      required: true
max_response_tokens: 3000
---

# Skill: Base Closure Validator

闭环检验器。验证 AI 修改后的内容是否形成闭环：引用有效、清单一致、无断链。

## Description

This skill runs automated checks to ensure:

1. **Inventory Consistency**: `v2-asset-inventory.md` matches actual files on disk.
2. **Reference Integrity**: Paths referenced in Rules, Skills, Commands, and docs point to existing files.
3. **Orphan Detection**: Files in inventory that no longer exist (stale entries).

## Capabilities

### 1. Inventory Check

Compares the asset inventory with disk state. Reports:

- **Stale**: Listed in inventory but file missing.
- **Missing**: Exists on disk but not in inventory.

### 2. Reference Check

Scans `_meta/`, `.cursor/`, `prompts-library/` for path references (e.g. `core/base/base-xxx/`, `_meta/docs/`) and verifies targets exist.

### 3. Full Audit

Runs both checks and outputs a structured report.

## Script Specification

**Script Path**: `.cursor/skills/base-closure-validator/scripts/validate.py`

**Parameters**:

| Flag          | Type                                    | Required | Description                                                                              |
| :------------ | :-------------------------------------- | :------- | :--------------------------------------------------------------------------------------- |
| `--mode`      | Enum[`inventory`, `references`, `full`] | No       | Default `full`. `inventory` = inventory check only; `references` = reference check only. |
| `--inventory` | String (Path)                           | No       | Path to inventory file. Default `_meta/docs/v2-asset-inventory.md`.                      |
| `--root`      | String (Path)                           | No       | Project root. Default: current working directory.                                        |
| `--config`    | String (Path)                           | No       | Override config. Default: `assets/default_config.json`.                                  |

**Config** (`assets/default_config.json`): `reference_check.scan_dirs`, `exclude_dirs`, `exclude_path_contains`, `include_extensions` 控制目录细粒度。

**Example**:

```bash
python .cursor/skills/base-closure-validator/scripts/validate.py --mode full
python .cursor/skills/base-closure-validator/scripts/validate.py --mode inventory --inventory _meta/docs/v2-asset-inventory.md
```

## Usage

When to run:

- After Workflow D (Refactor): **MUST** run to verify no broken references.
- After Workflow B (New Asset): Run to verify inventory sync.
- On demand: Use `/meta-verify-closure` Command.

## Output

The script prints a report to stdout. Zero exit code = all checks pass. Non-zero = issues found.
