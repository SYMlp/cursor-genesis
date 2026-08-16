---
description: Synthesizes a directory of research notes (Markdown) into a comprehensive, citation-backed Deep Research Report. Use after base-research-executor has produced notes/ files.
---

# Skill: Research Synthesizer

> 本文件是 **deep-research pack 的分发件**，由 `install-pack.py` 部署到目标项目 `.cursor/skills/`。
> 同一份契约的其他副本见 pack README「副本地图」——改契约要按那张表逐份动，不要只改一处。

## Goal

To read a collection of structured research notes (Markdown) and synthesize them into a final "Deep Research Report" that answers the original research intent.

## Input

- **base_path**: The root directory of the research topic (e.g., `docs/research/{topic-slug}/`).
- **Context**: The original Research Plan (`{base_path}/plan.md`) and / or Brief (`{base_path}/brief.md`) — helpful for understanding the original intent.

## Logic

1.  **Scan**: Find all `*.md` files in `{base_path}/notes/`.
2.  **Read context**: Read `{base_path}/plan.md` (and `brief.md` if it exists) to understand the original research question.
3.  **Read notes**: Read every note in `{base_path}/notes/`.
4.  **Synthesize**:
    -   Identify common themes and patterns across notes.
    -   Resolve conflicting information (if any) — note the conflict and pick the more authoritative source.
    -   Structure the findings logically by **theme/dimension**, NOT by source task (the reader doesn't care about task numbers).
    -   Trace every claim back to a note + URL.
5.  **Write**: Generate `{base_path}/report.md`.
6.  **Ledger**: Generate `{base_path}/source-ledger.jsonl` — one line per key claim (schema below). This is what makes the report machine-auditable rather than merely readable; do not skip it.
7.  **HTML Export (optional)**: If the repo has `tools/md-to-html.js`, run
    `node tools/md-to-html.js {base_path}/report.md {base_path}/html/{slug}.html`.
    Skip silently if it doesn't exist — HTML export is a kg-specific convenience, not a hard requirement.

## Report Structure (`report.md`)

```markdown
# Deep Research Report: {Topic}

## 1. Executive Summary
(High-level answer to the research question. 3-5 paragraphs. Should stand alone.)

## 2. Key Findings
(The meat of the report. Structured by themes/dimensions, NOT by source tasks.)
### 2.1 {Theme A}
...

## 3. Analysis & Implications
(Synthesized insights, "So What?", strategic recommendations.)

## 4. Open Questions / Gaps
(Things the research couldn't answer, conflicting evidence, areas needing follow-up.)

## 5. References
- [Title](URL) (Cached: `fetched/...`)
```

## Source Ledger (`source-ledger.jsonl`)

One JSON object per line, one line per key claim in the report:

```json
{"claim_id": "T06-adaptorch-01", "claim": "...", "source_url": "https://...", "source_type": "paper|doc|blog|forum", "primary_or_secondary": "primary|secondary", "supports_or_challenges": "supports|challenges", "measurement_context": "how/where measured; caveats", "retrieved_at": "YYYY-MM-DD", "confidence": "high|medium|low", "notes": "local cache path"}
```

Field set is fixed — the audit scanner detects a valid ledger by the presence of `claim` + `source` keys.

## Critical Constraints

-   **No Hallucinations**: Every claim must be backed by something in `notes/`. If notes don't say it, don't write it.
-   **Traceability (HARD REQUIREMENT)**: Every claim in *Key Findings* and *Analysis* MUST carry an inline `[Title](URL)`. **A note path such as "(see notes/task-03.md)" is NOT a source** — it points at a file that holds the source, it does not carry it. Note paths may appear *alongside* a URL, never *instead of* one. This exact escape hatch is what broke the chain historically: `notes/` accumulated 2,234 URLs that never reached any report, because citing the note file was permitted and cheaper.
-   **Mark the gaps**: If a claim's URL cannot be found in the notes, write it inline as `[未溯源]` rather than stating it bare. An unsourced claim that announces itself is safe; one that hides is not.
-   **Independence**: The report should stand alone. The reader shouldn't need to open the raw notes to follow the argument — but "standing alone" means carrying its sources with it, not shedding them.
-   **No task-by-task structure**: Don't write "Findings from Task 1: ... Findings from Task 2: ...". Reorganize by topic.
