# Script Interface Standard (V2.1)

> **Purpose**: To ensure all Python/Shell scripts invoked by Skills are strictly documented, preventing "Magic Number" parameters and ambiguous usage.
> **Scope**: All `.cursor/skills/**/SKILL.md` files that wrap a script.

## 1. Documentation Requirement

Every Skill that wraps a script **MUST** include an `## Interface` or `## Script Specification` section containing:

1.  **Script Path**: Relative path from project root (e.g., `scripts/groomer.py`).
2.  **Purpose**: One sentence explaining what the script acts upon.
3.  **Parameter Table**:
    | Parameter | Type | Required | Description |
    | :--- | :--- | :--- | :--- |
    | `--mode` | Enum[audit, archive] | Yes | Operation mode. |
    | `--target` | String (Path) | No | Target file path. |
4.  **Example Usage**: Concrete CLI examples.

## 2. Formatting Template

```markdown
### Capability: [Name]

**Script**: `[path/to/script.py]`

**Parameters**:

| Flag | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `--input` | String | Yes | Path to source file. |
| `--verbose`| Boolean| No | Enable detailed logging. |

**Example**:
```bash
python .cursor/skills/my-skill/script.py --input "data.txt" --verbose
```
```

## 3. Compliance Check

The `base-prompt-auditor` will reject Skills that:
*   Call a script without documenting its arguments.
*   Use ambiguous types (e.g., failing to specify if an argument is a Path or a Content String).
*   Lack a copy-pasteable example.
