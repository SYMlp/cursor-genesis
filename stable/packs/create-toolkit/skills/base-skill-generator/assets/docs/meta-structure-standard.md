# The Meta-Structure of Agentic Capabilities (V2.1)

> **Context**: The DNA of all Skills, Commands, and Subagents.
> **Source**: Meta-Prompting & VIGIL Architecture.

## 1. The "Five Elements" (五行)

Every Agentic Capability (whether a simple Skill or a complex Subagent) MUST possess these 5 meta-components.

| Component           | Purpose                 | Manifestation (File)                      | Criticality |
| :------------------ | :---------------------- | :---------------------------------------- | :---------- |
| **1. Identity**     | Definition & Boundaries | Frontmatter, System Prompt                | ⭐⭐⭐⭐⭐       |
| **2. Context**      | Knowledge & State       | `read_file`, `assets/`, Memory            | ⭐⭐⭐⭐        |
| **3. Process**      | Logic & Reasoning       | Workflow, Python Script                   | ⭐⭐⭐⭐⭐       |
| **4. Verification** | Quality & Correction    | Tests, Exit Codes, `verification` section | ⭐⭐⭐⭐⭐       |
| **5. Interface**    | Contract & I/O          | CLI Args, Input Schema                    | ⭐⭐⭐⭐        |

## 2. Component Details

### 2.1 Identity (我是谁)

* **Must Have**: Name, Description, Model (for Agents), Tools (for Agents).
* **Meta-Rule**: Principle of Least Privilege. Only ask for what you need.

### 2.2 Context (我知什么)

* **Must Have**: References to Standards (e.g., `skill-design-guide.md`).
* **Meta-Rule**: **Lazy Loading**. Do not read `project-map.md` unless you are navigating the project.
* **Hygiene**: Subagents must use isolated context. Skills must clean up temp files.

### 2.3 Process (我做什么)

* **Must Have**: A clear, deterministic workflow.
* **Meta-Rule**: **EPE Loop** (Explore -> Plan -> Execute).
    * *Skill*: `gen.py` script logic.
    * *Subagent*: `Workflow` section in `.md`.

### 2.4 Verification (我做对了吗)

* **Must Have**: A way to prove success programmatically.
* **Meta-Rule**: **The Adversarial Trinity**.
    * *Generator*: The Agent writing code.
    * *Auditor*: The Test Script / Linter.
    * *Optimizer*: The logic that fixes code based on Auditor's feedback.

### 2.5 Interface (怎么用我)

* **Must Have**: Typed inputs (CLI args, JSON schema).
* **Meta-Rule**: **No Magic Numbers**. Everything must be explicit.

## 3. Application Guide

| If creating... | Focus heavily on...                                           |
| :------------- | :------------------------------------------------------------ |
| **Skill**      | **Interface** (Strict CLI) & **Verification** (Unit Tests).   |
| **Command**    | **Process** (Linear Steps) & **Identity** (User Intent).      |
| **Subagent**   | **Context** (Isolation) & **Verification** (Self-Correction). |
