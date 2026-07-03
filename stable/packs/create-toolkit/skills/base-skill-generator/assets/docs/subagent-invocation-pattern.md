# Design Pattern: Subagent Invocation (The Role Injection)

> **Context**: Cursor `Task` tool limitations.
> **Problem**: Cursor currently only supports a fixed set of `subagent_type` values (e.g., `generalPurpose`, `explore`). It does NOT support custom types like `my-custom-agent`.
> **Solution**: The **Role Injection Pattern**.

## 1. The Pattern
Instead of defining a new *Type*, we use the *General* type and inject the *Definition* via the Prompt.

### ❌ Wrong Way
```python
Task(
    subagent_type="meta-refactoring-manager",  # This will FAIL or default to generic
    prompt="Do the job."
)
```

### ✅ Right Way
```python
Task(
    subagent_type="generalPurpose",            # Use the standard type
    prompt="""
    # Role Injection
    You are the **Refactoring Manager**.
    Please read and adopt the persona defined in `.cursor/agents/meta-refactoring-manager.md`.

    # The Mission
    [Your actual task here...]
    """
)
```

## 2. Why this works
*   **Context Loading**: By telling the Subagent to "read and adopt" the definition file, we effectively "hydrate" the generic agent with our specific instructions.
*   **Tool Access**: The `generalPurpose` agent usually has access to `read_file` and `run_script`, which is sufficient for most custom agents.

## 3. Best Practices
1.  **File Existence**: Ensure the definition file (`.cursor/agents/xxx.md`) actually exists before invoking.
2.  **Explicit Instruction**: Use the phrase **"Read and adopt the persona..."** to trigger the behavior.
3.  **Parameter Passing**: Pass arguments clearly in the `prompt`, as there are no structured args for the custom persona.
