# Design Pattern: Hybrid Scaffolding (The "Skeleton & Soul" Model)

> **Context**: Best Practices for Generative Skills.
> **Source**: User Insight & V2.1 Architecture.

## 1. The Problem

* **Pure Script**: Can create directories and boilerplate, but cannot handle complex, context-dependent logic (e.g., specific business rules).
* **Pure AI**: Can write complex logic, but often forgets files, messes up directory structures, or deviates from standards.

## 2. The Solution: Hybrid Scaffolding

A two-phase approach where **Scripts provide the Structure (Skeleton)** and **AI provides the Content (Soul)**.

### Phase 1: The Skeleton (Script)

* **Role**: The Deterministic Builder.
* **Responsibility**:
    * Create the "Physical" assets: Directories, Standard Files (`README.md`, `SKILL.md`).
    * Enforce "Hard" constraints: Naming conventions, file encoding, required sections.
    * **Input**: Minimal arguments (`--name`, `--type`).
    * **Output**: A valid, compilable/runnable "Blank Canvas".

### Phase 2: The Soul (AI Injection)

* **Role**: The Contextual Architect.
* **Responsibility**:
    * **Read**: Analyze the "Blank Canvas" created by the script.
    * **Contextualize**: Read project-specific docs (`assets/docs/`, `project-map.md`).
    * **Inject**: Overwrite the generic placeholders with specific, high-value content.
        * *Example*: Replace `def main(): pass` with actual business logic.
        * *Example*: Replace `## Verification` with specific `npm test` commands.

## 3. Implementation Guide

### 3.1 Directory Structure

Store this pattern documentation in `assets/docs/` of any generative skill.

### 3.2 Workflow Definition (in `SKILL.md`)

Explicitly define the hand-off between Script and AI:

```markdown
1.  **Scaffold**: Run `python scripts/gen.py ...` (Creates the skeleton).
2.  **Analyze**: Read the generated `SKILL.md`.
3.  **Inject**: Edit `SKILL.md` to add specific logic defined in `assets/docs/rules.md`.
```

## 4. Why this matters

* **Consistency**: Every asset has the same structure (guaranteed by script).
* **Intelligence**: Every asset has unique, high-quality content (guaranteed by AI).
* **Evolution**: We can update the script to change the structure globally, or update the AI prompt to improve content quality.

## 5. Future Extensions

* As we gather more "Claude Code Best Practices", add them to the **Phase 2 (Injection)** instructions.
* The Script should remain "dumb" and stable; the AI instructions should be "smart" and evolving.
