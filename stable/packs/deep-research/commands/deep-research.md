---
description: Deep Research Workflow (Plan -> Execute -> Synthesize) with Context Isolation
---
# Command: Deep Research (Refactored)

## Goal
Execute a systematic deep research process: **Plan** (Planner) → **Execute** (Executor) → **Synthesize** (Synthesizer).
Each stage runs in an isolated Subagent to preserve context and ensure stability.

## Steps

### Step 1: Initialize & Contextualize
1.  **Analyze Request**: Identify the user's research topic.
2.  **Create Directory**:
    -   Generate a slug (e.g., `my-research-topic`).
    -   Run: `mkdir -p "docs/research/{slug}/raw" "docs/research/{slug}/fetched" "docs/research/{slug}/notes" "docs/research/{slug}/html"`
    -   (Windows PowerShell: `New-Item -ItemType Directory -Force -Path "docs/research/{slug}/raw","docs/research/{slug}/fetched","docs/research/{slug}/notes","docs/research/{slug}/html"`)

### Step 2: Planning (Planner Agent)
Call the **Planner** to generate the research roadmap.

```python
Task(
    subagent_type="generalPurpose",
    description="Phase 1: Research Planning",
    prompt="""
    # Role Injection
    You are the **Strategic Research Planner**.
    Read and adopt the persona defined in `.cursor/agents/base-research-planner-agent.md`.

    # Mission
    Analyze the User Input and generate a Research Plan.
    1.  If input is vague, output a **Research Brief** to `docs/research/{slug}/brief.md` and ask for confirmation.
    2.  If input is clear, output a **Research Plan** to `docs/research/{slug}/plan.md`.

    # User Input
    {User's original query/input}

    # Context
    Topic Slug: {slug}
    Base Path: docs/research/{slug}/
    """
)
```

*(Wait for User Confirmation if a Brief was generated. If Plan is ready, proceed.)*

### Step 3: Execution (Executor Agent)
Call the **Executor** to perform the research tasks defined in the Plan.

```python
Task(
    subagent_type="generalPurpose",
    description="Phase 2: Research Execution",
    prompt="""
    # Role Injection
    You are the **Tactical Research Executor**.
    Read and adopt the persona defined in `.cursor/agents/base-research-executor-agent.md`.

    # Mission
    Execute the Research Plan found at `docs/research/{slug}/plan.md`.
    
    # Execution Rules
    1.  Read the Plan.
    2.  For each Task:
        -   **Search**: Use `brave_web_search`.
        -   **Save Raw**: Write to `docs/research/{slug}/raw/task-{N}-search.md`.
        -   **Fetch**: Use `WebFetch` for top URLs.
        -   **Save Fetched**: Write to `docs/research/{slug}/fetched/task-{N}-url-{i}.md`.
        -   **Note**: Summarize into `docs/research/{slug}/notes/task-{N}.md`.
    3.  **Strict Persistence**: All outputs MUST be written to disk. Do not just output text.

    # Base Path
    docs/research/{slug}/
    """
)
```

### Step 4: Synthesis (Synthesizer Agent)
Call the **Synthesizer** to compile the final report.

```python
Task(
    subagent_type="generalPurpose",
    description="Phase 3: Report Synthesis",
    prompt="""
    # Role Injection
    You are the **Research Synthesizer**.
    Read and adopt the persona defined in `.cursor/agents/base-research-synthesizer-agent.md`.

    # Mission
    Read all notes in `docs/research/{slug}/notes/` and compile a final **Deep Research Report**.

    # Output
    -   Markdown: `docs/research/{slug}/report.md`
    -   HTML: After writing report.md, run `node tools/md-to-html.js docs/research/{slug}/report.md docs/research/{slug}/html/{slug}.html` to generate an HTML version (filename matches report topic) for sharing with people without Markdown plugins.
    -   Format: Follow the structure in `.cursor/skills/base-research-synthesizer/SKILL.md`.
    """
)
```

### Step 5: Delivery
1.  Read the generated `report.md` (or just the Executive Summary).
2.  Present the key findings to the user.
3.  Provide the path to the full report (Markdown: `report.md`, HTML: `html/{slug}.html` for sharing without Markdown plugins).
