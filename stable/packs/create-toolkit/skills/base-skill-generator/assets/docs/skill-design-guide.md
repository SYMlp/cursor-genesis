# Skill Design Best Practices (The "Red Book")

> **Purpose**: This document contains the distilled wisdom from Claude Code best practices.
> **Usage**: Every Agent creating a new Skill MUST read this first to ensure high-quality output.

## 1. The Core Philosophy: "Verification Loop"

A Skill is not just code that runs; it is code that **proves it worked**.

* **❌ Bad Pattern**: "I ran the script. It should be fine."
* **✅ Good Pattern**: "I ran the script, then I checked the output file size, and it is >0 bytes. Success confirmed."

**Requirement**: Every `SKILL.md` must have a `Verification` section defining explicit checks (exit codes, file existence, grep output).

## 2. The Context Hygiene

Skills must be "Socially Responsible" citizens of the context window.

* **Avoid**: Printing 500 lines of logs to stdout.
* **Prefer**: Writing logs to a file, and printing only a summary.
* **Atomic Design**: One Skill = One Specific Capability. Don't make a "God Skill" that does git + db + ui.

## 3. The Plan Mode Integration

Complex Skills should invite the user/agent to "Think before Acting".

* **Instruction**: In the Skill Description, add: "For complex tasks, use `todo_write` to outline steps first."

## 4. The "Hybrid Generation" Workflow

How to build a Skill using `base-skill-generator`:

1. **Analyze**: Understand the user's need.
2. **Design**: Draft the `Verification Strategy` and `Parameters` mentally.
3. **Scaffold**: Run `gen.py` to create the folder structure and `SKILL.md` skeleton.
4. **Refine (Crucial)**: Immediately edit the generated `SKILL.md` to inject the specific Logic, Verification Steps, and Context rules you designed in Step 2.
## 5. The "Self-Contained Assets" Rule
Skills must be self-sufficient packages.

*   **Rule**: Do NOT reference files outside the skill's directory (except generic project config).
*   **Action**: If a Skill needs a standard or a template, COPY it into the skill's `assets/` folder.
*   **Why**:
    1.  **Portability**: The skill can be moved to another project without breaking links.
    2.  **Versioning**: The skill can evolve its own copy of the standard without affecting others.
    3.  **Context**: The Agent doesn't need to hunt for external files.
