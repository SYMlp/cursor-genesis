# AGENTS.md

This file provides project-wide guidance to AI coding agents working in this repository.

## Project Overview

cursor-genesis (CG) is the **Human–Agent Development Collaboration Mechanisms Leaf** in the knowledge-graph system. It studies and publishes reusable ways to expose human operation entry points, assemble context, choose Rule / Skill / Workflow forms, invoke agents/models/tools, add deterministic guards and human gates, and compose, inject, distribute, and refine collaboration capabilities.

Cursor is CG's founding sample and a reference implementation. Its Rules, multi-model entry points, explicit commands, Agent modes, and project-context patterns are evidence to generalize from; Cursor is not CG's domain boundary, long-term compatibility target, or runtime dependency.

Current stable assets are primarily Rules, Skills, Commands, Agent/Capability definitions, Patterns, Atoms + Packs, knowledge guides, and backflow mechanisms. `create-skill-workflow`, `create-subagent-workflow`, `create-command-workflow`, and `create-rule-workflow` now provide persisted gates/retries and machine Validators. Rule Contracts register into the project `AGENTS.md` author source; Cursor activation frontmatter remains an adapter concern. `audit-agent-assets` provides read-only, evidence-based review with Agent judgment, while `harvest-session` provides tool-neutral session-outcome triage; neither is represented as a machine Validator. Agent and Command Contracts stay tool-neutral while concrete model IDs, slash-command formats, and invocation syntax stay in host adapters. Additional Workflows, a generalized Validator framework, Hooks, and versioned runtime contracts remain planned.

### Architecture Position

```
knowledge-graph (upper layer - indexing, association, Leaf governance)
    ↓
cursor-genesis (provider Leaf - collaboration mechanisms and reusable assets)
    ↓
projects or peer Leaves (primarily init/build injection; local execution)
```

CG is a capability provider, not a manager of other Leaves and not a central runtime. Leaf identity, topology, routing, and relationship authority remain in knowledge-graph.

### Responsibilities

- Produce tool-independent Human–Agent development collaboration mechanisms and knowledge
- Package reusable mechanisms as Atoms + Packs for init/build-time composition and injection
- Accept improvement backflow from projects and refine reusable mechanisms
- Preserve Cursor as founding evidence and a reference implementation without granting it platform privilege
- Expose standardized index (`stable/knowledge/index.yaml`) for upper-layer retrieval

### Out of Scope

- Cross-domain knowledge association (knowledge-graph responsibility)
- Leaf Registry, topology, relationship authority, routing, and governance (knowledge-graph responsibility)
- Other Leaves' domain semantics and concrete project facts
- Personal entry-point layout, approval UI, and workbench preferences (Desk responsibility)
- Concrete project-directory creation, personal workspace registration, or end-to-end workspace bootstrap; CG only provides reusable collaboration mechanisms and Packs used by such flows
- Long-term Cursor compatibility or a mandatory central runtime

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
│   ├── rules/          # Rule assets; current .mdc files are Cursor reference-format implementations
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

### Current Cursor Reference Distribution

```bash
git clone --filter=blob:none --sparse https://github.com/LSRabbit6/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set stable/packs/v1-talk stable/atoms/rules stable/atoms/capabilities
```

This is a currently available reference path for the existing Cursor-format assets, not a long-term platform compatibility promise. Future tool-specific formats belong in adapters, frozen areas, or historical references after asset-by-asset triage.

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
