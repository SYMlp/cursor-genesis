---
name: base-inventory-updater
description: Auto-updates the Asset Inventory markdown file by scanning agents, skills, and commands.
scope: base
package:
  id: base-inventory-updater
  version: "0.1.0"
  maturity: stable
  owner: template-maintainers
  tags: ["governance", "inventory", "registry"]
platform:
  runtimes: ["cursor"]
dependencies:
  skills: []
io_contract:
  outputs:
    - name: updated_inventory
      type: markdown
      required: false
defaults:
  target: "_meta/docs/v2-asset-inventory.md"
max_response_tokens: 2000
---

# Skill: Base Inventory Updater

This skill automatically scans the project's capability assets and updates the inventory documentation.
It ensures that `_meta/docs/v2-asset-inventory.md` (or any other target) reflects the actual state of the codebase.

## 🚀 Capabilities

*   **Scan**: Recursively reads `.cursor/agents`, `.cursor/skills`, and `.cursor/commands`.
*   **Extract**: Parses descriptions from frontmatter or content.
*   **Sync**: Updates the Markdown tables in the target inventory file.

## 🛠️ Usage

To run the updater:

```bash
./scripts/py ".cursor/skills/base-inventory-updater/scripts/update_inventory.py" --target "_meta/docs/v2-asset-inventory.md"
```

For app-level docs:

```bash
./scripts/py ".cursor/skills/base-inventory-updater/scripts/update_inventory.py" --target "docs/project-capabilities.md"
```

## ⚙️ Logic

1.  **Agents**: Scans `.cursor/agents/*.md`.
2.  **Skills**: Scans `.cursor/skills/*/SKILL.md`.
3.  **Commands**: Scans `.cursor/commands/*.md`.
4.  **Table Generation**: Creates a standard markdown table with ID, Scope, Description, Status.
5.  **Injection**: Replaces the content under specific headers (`## 1. Agents`, etc.) in the target file.
