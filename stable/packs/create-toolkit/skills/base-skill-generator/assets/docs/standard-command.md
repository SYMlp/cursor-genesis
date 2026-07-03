# Standard: Custom Commands (SOPs)

> **Context**: High-frequency, deterministic workflows.
> **Source**: Cursor Documentation & Best Practices.

## 1. Definition

Commands are **Standard Operating Procedures (SOPs)**. They are deterministic, linear, and high-frequency.
Users trigger them via `/command-name` in Chat.

## 2. File Structure

*   **Path**: `.cursor/commands/[command-name].md`
*   **Format**: Plain Markdown with Frontmatter.

## 3. When to Create a Command

See `skill-composition-theory.md` Section 2.2 for the full decision framework.

**Quick check**: If the user says "每次做 X 都是这几步" or wants a repeatable `/slash-command`, it's a Command.

## 4. When a Command Step Needs a Subagent

Not every step runs inline. Use this decision hook for each step:

| Step Characteristic | → Inline (Skill) | → Subagent (Isolated) |
|---------------------|-------------------|-----------------------|
| 结果简短、确定性 | ✅ | |
| 用户需要实时看到过程 | ✅ | |
| 中间过程对用户无价值 | | ✅ |
| 产生大量 token（搜索/读取） | | ✅ |
| 需要自主推理/判断 | | ✅ |
| 用户明确要求隔离 | | ✅ |

如果某步骤需要 Subagent，Command 中**必须包含 Role Injection 调用代码块**。
参考: `subagent-invocation-pattern.md`

## 5. Template

```markdown
---
description: [Short description of what this command does]
---
# Command: [Name]

## Goal
[One sentence goal]

## Steps
1.  **Step 1**: Run skill X.
    *   `@.cursor/skills/skill-x/SKILL.md`
2.  **Step 2**: Call subagent Y (if step needs reasoning/isolation).
    *   Use Role Injection Pattern (see subagent-invocation-pattern.md)
3.  **Step 3**: Verify result.
```

## 6. Best Practices

*   **Reference Skills**: Do NOT write complex logic in a Command. Call a Skill instead.
*   **Atomic Steps**: Each step should be one clear action.
*   **Subagent Steps**: If a step needs reasoning, use a Subagent with Role Injection — never embed reasoning logic in the Command itself.
*   **Verification**: The last step must always be a verification step.
*   **Cascade Awareness**: If the Command needs capabilities that don't exist yet, create them first (Skill → Subagent → Command). See `skill-composition-theory.md` Section 6.
