---
description: Synthesizes multiple research notes into a comprehensive, structured report with citations.
---
# Skill: Research Synthesizer

## Goal
To read a collection of structured research notes (Markdown) and synthesize them into a final "Deep Research Report" that answers the original research intent.

## Input
- **Base Path**: The root directory of the research topic (e.g., `docs/research/{topic-slug}/`).
- **Context**: The original Research Plan or Brief (optional, but helpful).

## Logic
1.  **Scan**: Look for all `.md` files in `{Base Path}/notes/`.
2.  **Read**: Read the content of all found notes.
3.  **Synthesize**:
    -   Identify common themes and patterns across notes.
    -   Resolve conflicting information (if any).
    -   Structure the findings logically (not just summarizing note-by-note).
4.  **Write**: Generate `report.md` in `{Base Path}/`.

## Report Structure (`report.md`)

```markdown
# Deep Research Report: {Topic}

## 1. Executive Summary
(High-level answer to the research question. 3-5 paragraphs.)

## 2. Key Findings
(The meat of the report. Structured by themes/dimensions, NOT by source tasks.)
### 2.1 {Theme A}
...
### 2.2 {Theme B}
...

## 3. Analysis & Implications
(Synthesized insights, "So What?", strategic recommendations.)

## 4. References
(List of key sources cited in the notes, with links to local fetched files.)
- [Title](URL) (Cached: `fetched/...`)
```

## Critical Constraints
-   **No Hallucinations**: Every claim must be backed by the notes.
-   **Traceability**: When making a claim, try to reference the source task or note (e.g., "As found in Task 1...").
-   **Independence**: The report should stand alone. The reader shouldn't need to read the raw notes.
