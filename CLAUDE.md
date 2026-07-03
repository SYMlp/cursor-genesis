# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

cursor-genesis is a leaf node in the knowledge-graph system, providing Cursor AI collaboration components and knowledge assets. It produces reusable prompt engineering assets (Rules, Capabilities, Patterns, Code Templates) that downstream projects consume via sparse checkout.

### Architecture Position

```
knowledge-graph (upper layer - indexing, association, governance)
    ↓
cursor-genesis (this repo - content production)
    ↓
downstream projects (consumers via sparse checkout)
```

### Responsibilities

- Produce Cursor-related components and knowledge
- Accept improvement backflow from downstream projects
- Expose standardized index (`stable/knowledge/index.yaml`) for upper-layer retrieval

### Out of Scope

- Cross-domain knowledge association (knowledge-graph responsibility)
- Governance framework design (leaf-node-framework responsibility)

## Directory Structure

```
.knowledge/               # Knowledge management metadata
├── meta.yaml            # Node metadata
├── upstream/            # Interaction with knowledge-graph
│   ├── sync.yaml       # Sync configuration
│   ├── exports/        # Content to report upstream
│   └── received/       # Recommendations from upstream
└── downstream/          # Interaction with downstream projects
    ├── backflow.yaml   # Backflow configuration
    ├── pending/        # Pending backflow reviews
    └── processing/     # In-progress backflow

stable/                   # Published assets (sparse checkout target)
├── atoms/               # Atomic layer - smallest reusable units
│   ├── rules/          # Cursor Rules (.mdc files) → .cursor/rules/
│   ├── capabilities/   # Four-layer cognition (insight/architecture/engineering/quality)
│   ├── patterns/       # Team orchestration patterns
│   ├── standalone/     # Independent role definitions
│   ├── skills/         # Skill definitions (.skill.yaml)
│   └── code-templates/ # DDD/Java/Vue scaffolding
├── packs/               # Package layer - scenario-based combinations
│   ├── v1-talk/        # Talk-only package (6 team patterns)
│   ├── deep-research/  # Deep research (Plan→Execute→Synthesize)
│   └── knowledge-manage/ # Knowledge management package
└── knowledge/           # Knowledge layer (indexed by upper layer)
    ├── index.yaml      # Knowledge index with `solves` field
    └── ...categories/

scripts/                  # Maintenance tools (not part of assets)
├── install-pack.py      # Pack installer (deploy packs to target projects)
└── ...                  # Other scripts
```

## Key Concepts

### Template vs Published (Skill Ownership)

Skills/components fall into two categories by **who controls them**:

| Type | Control | Customization | cursor-genesis role |
|:---|:---|:---|:---|
| **Template** | User | Derive variants per project (backbone fixed, variants vary by context) | Produces these—scaffolds for customization |
| **Published** | Publisher | Use as-is or wrap externally; do not modify internals | Does not produce; user gets from external sources (e.g. `~/.cursor/skills/`) |

cursor-genesis produces **Template**-type components: atoms and packs are scaffolds that users adapt per project. Published skills (e.g. PPTX, xlsx, OpenClaw) come from elsewhere and are consumed directly.

See `knowledge-graph/meta/derivation/skill-template-vs-published-taxonomy-2026-03-08.md` for full derivation.

### Atoms + Packs Two-Layer Architecture

- **Atoms**: Smallest reusable units, context-agnostic
- **Packs**: User-facing scenario combinations (users choose packs, not atoms)

### Four-Layer Cognition (Capabilities)

- `01_insight/`: Insight and analysis (requirements, market analysis)
- `02_architecture/`: Structure and design (architecture, tech evaluation)
- `03_engineering/`: Implementation (coding, engineering)
- `04_quality/`: Quality assurance (auditing, acceptance criteria)

### v1-talk Package

Talk-only mode with 6 team patterns:
- Virtual Streamlit Team - Python/Streamlit development
- Strategic Research Team - Go/No-Go feasibility assessment
- Topic Research Team - Academic/technical deep research
- Domain Driven Design - DDD modeling
- AI Migration Team - Legacy system takeover
- Knowledge System Team - Knowledge management

Dynamic routing via `rules/teams/*.mdc` using Signal → Pattern → Role decision matrix.

## Common Operations

### Sparse Checkout for Downstream Projects

```bash
git clone --filter=blob:none --sparse https://github.com/you/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set stable/packs/v1-talk stable/atoms/rules stable/atoms/capabilities
```

### Legacy Code Scanner

```bash
cd scripts
pip install -r legacy_scanner_requirements.txt
python legacy_scanner.py --target /path/to/legacy/project
```

Environment variables: `LLM_API_BASE`, `LLM_API_KEY`, `LLM_MODEL`

## Backflow Process

When improvements are made in downstream projects:

1. Fork and create branch: `backflow/my-improvement`
2. Create directory: `.knowledge/downstream/pending/{project-hash}/{contributor}/{commit-id}/`
3. Copy and fill `TEMPLATE.md` as `SUBMISSION.md`
4. Add content to `content/` subdirectory
5. Submit PR

See `.knowledge/downstream/pending/README.md` and `docs/downstream-spec.md` for details.

## File Conventions

- Rules use `.mdc` extension (Markdown with Cursor metadata)
- Skills use `.skill.yaml` extension
- Knowledge index uses `solves` field for problem-oriented lookup
- Node metadata in `.knowledge/meta.yaml` follows leaf-node-framework spec

## Integration with knowledge-graph

Upper layer links to `stable/knowledge/` (not the entire repo):
```bash
# In knowledge-graph/data/nodes/
cursor-genesis -> ../../../cursor-genesis/stable/knowledge
```

Only `stable/knowledge/` contains cognitive content for upper-layer indexing.
