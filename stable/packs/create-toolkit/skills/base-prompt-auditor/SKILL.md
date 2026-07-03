---
name: base-prompt-auditor
description: Quality Assurance tool that checks Agent/Skill files against the V2.1 Engineering Rubric.
scope: base
package:
  id: base-prompt-auditor
  version: "0.1.0"
  maturity: stable
  owner: template-maintainers
  tags: ["governance", "qa", "rubric", "audit"]
platform:
  runtimes: ["cursor"]
dependencies:
  skills: []
io_contract:
  outputs:
    - name: audit_context
      type: markdown
      required: true
defaults:
  rubric_path: ".cursor/skills/base-prompt-auditor/assets/rubric.yaml"
max_response_tokens: 2500
tools:
  - name: run_script
    description: Generates an audit context for a given file.
    args:
      command: "python .cursor/skills/base-prompt-auditor/scripts/audit.py [file_path]"
---

# Base Prompt Auditor

## Description
This skill provides the capability to audit files (Agents, Skills, Commands) against the official **Agent Engineering Rubric (V2.1)**. It separates the *Logic* (fetching file & rubric) from the *Cognition* (evaluating the content).

## Usage
When asked to "Audit", "Review", or "Check" a prompt file:

1.  **Execute** the audit script:
    ```bash
    python .cursor/skills/base-prompt-auditor/scripts/audit.py "path/to/target_file.md"
    ```

2.  **Analyze** the output:
    The script returns a structured prompt containing:
    *   The Target File content.
    *   The Engineering Rubric (from `assets/rubric.yaml`).
    *   Evaluation Instructions.

3.  **Generate** the Report:
    Act as the **Quality Gatekeeper** and produce the report as requested by the script's output.

## Configuration
The rubric is stored in `assets/rubric.yaml`. To update the criteria, edit that file.
