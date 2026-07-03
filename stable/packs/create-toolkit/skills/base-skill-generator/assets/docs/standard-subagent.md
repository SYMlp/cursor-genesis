# Standard: Subagents (Workers)

> **Context**: Autonomous, non-deterministic tasks.
> **Source**: Cursor Documentation & Best Practices.
> **Model Selection**: See `model-selection-guide.md` — Subagent **MUST** explicitly specify `model` in Frontmatter.

## 1. Definition

Subagents are **Autonomous Workers**. They run in isolated contexts to perform complex, non-deterministic tasks (Research, Review, Code).

**Core purpose of isolation**: Subagent = Context Isolation Wall. The caller doesn't see (or pay for) the intermediate reasoning/search/read tokens.

## 2. When to Create a Subagent

See `skill-composition-theory.md` Section 2.3 for the full decision framework.

**Quick check**: If the task needs reasoning, search, or judgment — and its intermediate process is noise to the caller — it's a Subagent.

## 3. When a Subagent Step Needs Sub-Isolation

A Subagent itself has a context window. If its workflow contains steps that would pollute its own context, consider further isolation:

| Step Characteristic | → Skill / Inline | → Sub-Subagent |
|---------------------|-------------------|----------------|
| 结果简短，后续步骤依赖它 | ✅ | |
| 必须串行且上下步骤紧密耦合 | ✅ | |
| 中间过程对本 Subagent 后续无价值 | | ✅ |
| 需要不同的专业角色/知识库 | | ✅ |
| 重复循环，每次迭代独立 | | ✅ (if platform supports) |

> **Platform caveat**: Cursor nested subagent support is uncertain. Design for "inline first, isolate later" — mark steps as "isolation-ready" for future upgrade.

## 4. Cascade Rule: Skill Dependencies

Before creating a Subagent, check if all Skills it needs exist:
- **Exist** → Reference them in the Agent definition
- **Don't exist** → Create Skills first, then the Subagent

This is the Cascade Pattern (see `skill-composition-theory.md` Section 6).

## 5. File Structure

*   **Path**: `.cursor/agents/[agent-name].md`
*   **Format**: Markdown with specific Frontmatter configuration.

## 6. Template

```markdown
---
name: [agent-name]
description: [Short description of the agent's role]
model: [composer-1.5 | gemini-3-pro | claude-4.6-opus-high-thinking | gpt-5.2 | ...]  # MUST specify; see model-selection-guide.md
globs: ["**/*.md", "**/*.json"]   # optional
tools:
  - name: read_file
  - name: run_script
  - name: grep
---

# Identity
You are the **[Role Name]**. Your goal is [Goal].

# Knowledge Base
*   Always read `@core/docs/standard.md` before starting.

# Workflow
1.  **Analyze**: Understand the request.
2.  **Explore**: Use tools to gather context.
3.  **Execute**: Perform the task.
4.  **Verify**: Prove it worked.

# Constraints
*   Do not hallucinate files.
*   Always use the provided tools.
```

## 7. Invocation Standard (Role Injection)

Since Cursor does not support custom `subagent_type` registration, you must use the **Role Injection Pattern**.

### Caller Code Example
```python
Task(
    subagent_type="generalPurpose",
    prompt=f"""
    You are the **[Agent Name]**.
    Read definition: `.cursor/agents/[agent-file].md`.
    
    Task: {user_task}
    """
)
```
**Constraint**: All Subagents must be designed to be "Hydratable" via this method.
