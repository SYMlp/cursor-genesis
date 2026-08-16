# cursor-genesis

> **The Human–Agent Development Collaboration Mechanisms Leaf**
> 
> *"Stop writing code. Start engineering how your AI writes code."*

## What is this?

`cursor-genesis` (CG) is the **Human–Agent Development Collaboration Mechanisms Leaf**: it studies and publishes human operation entry points, context assembly, Rule / Skill / Workflow selection, agent/model/tool invocation, deterministic guards, human gates, and capability composition, injection, distribution, and refinement.

CG is tool-independent. Cursor remains:

1. a **founding sample** whose history and design rationale are preserved;
2. a **reference implementation** from which Rules, multi-model entry points, explicit commands, Agent modes, and project-context mechanisms are generalized;
3. a **non-core platform** with no long-term compatibility promise and no role as CG's runtime dependency.

In short: **Cursor keeps its textbook role, not a constitutional role.**

Current stable assets are primarily Rules, Skills, Commands, Agent/Capability definitions, Patterns, Atoms + Packs, knowledge guides, and backflow mechanisms. `create-skill-workflow`, `create-subagent-workflow`, `create-command-workflow`, and `create-rule-workflow` now provide persisted gates/retries and machine Validators. Rule Contracts register into the project `AGENTS.md` author source; Cursor activation frontmatter remains an adapter concern. `audit-agent-assets` provides read-only, evidence-based review with Agent judgment, while `harvest-session` provides tool-neutral session-outcome triage; neither is represented as a machine Validator. Agent and Command Contracts stay tool-neutral while concrete model IDs, slash-command formats, and invocation syntax stay in host adapters. Additional Workflows, a generalized Validator framework, Hooks, and versioned runtime contracts remain planned.

CG mechanisms may be consumed during project initialization, but CG does not own concrete project-directory creation, personal workspace registration, or end-to-end workspace bootstrap.

When configuring AI for large-scale enterprise software (e.g., 50+ modules, tens of thousands of lines of code), default AI behavior degrades: it hallucinates architectures, relies too much on legacy patterns, and loses context. 

Instead of writing manual prompts for every module, CG crystallizes robust Human–Agent working mechanisms into an **Atom** and packages compatible atoms into a **Pack** for projects or peer Leaves to inject primarily during init/build. Existing `.mdc` assets are Cursor-format reference implementations, not the definition of the Atom model.

## Proven Assets: Enterprise Meta-Rules

Extracted from a real-world enterprise system delivery (6 domains, 50+ modules, zero to acceptance in 2 weeks), this repository still physically contains meta-rules that govern how an Agent should behave in a massive codebase. In KG, the enterprise-delivery concern has already been logically split from CG; the physical assets remain here until a later, separately approved triage or move.

Located in `stable/atoms/rules/enterprise/`:

1. **`design-authority.mdc` (Design is Authority)**
   Strictly forbids the agent from scanning legacy code to guess architecture patterns. It mandates that the Agent must read the Domain Ontology and declarative configs first, saving 60%+ in wasted, hallucinatory token reads.

2. **`routing-engine.mdc` (Intent-Based Route Engine)**
   Automatically intercepts vague natural language inputs (e.g., "the dropdown is empty") and routes them into deterministic diagnostic and file-reading pipelines. 

3. **`ontology-driven-dev.mdc` (ODD Paradigm)**
   A structured pipeline governing how the Agent should extract entity boundaries from PM specification documents, map them into a `model.yaml`, and deterministically generate code without missing fields.

4. **`rule-evolution.mdc` (Agent Self-Evolution)**
   A closed-loop system constraint. Whenever the AI detects its own behavior or cognitive path was suboptimal, it must document the failure, analyze the root cause, and rewrite its own rules to prevent future mistakes.

## Provenance & Validation Status

These meta-rules are **not theoretical**. They were extracted and generalized from a real production enterprise system (a 50+ module, full-stack Java + Vue 3 platform) delivered from zero to acceptance review in ~2 weeks — and the same workflow is still in active use in my current work.

| Rule | Origin | Production Validation |
|:---|:---|:---|
| `design-authority` | Discovered after observing 60%+ wasted token reads from legacy code scanning | Eliminated architecture drift across 50+ modules |
| `routing-engine` | Evolved through 5 documented optimization rounds with quantified before/after metrics | Reduced diagnostic file reads from 9+ to 4-6; search operations from 5+ to 0-1 |
| `ontology-driven-dev` | Created after measuring 35% field omission rate in first ontology extraction | Brought omission rate to near-zero across all modules |
| `rule-evolution` | Meta-rule created to prevent recurring behavioral failures | 5 optimization records with full root-cause analysis |

The generalized mechanisms can inform Human–Agent collaboration across tools. Their existing Cursor-format distribution remains a reference path; backflow from real adoption continues to refine the tool-independent mechanism.

## Architecture

This repository is split into two layers:

### 1. Atoms (`stable/atoms/`)
The smallest reusable units of AI cognition. Context-agnostic.
- `rules/enterprise/`: **Enterprise Meta-Rules** — the core governance system (4 rules)
- `rules/`: Additional base rules (production safety, project conventions)
- `capabilities/`: Four-layer cognition bounds (insight, architecture, engineering, quality)
- `patterns/`: Team orchestration templates (6 team patterns)

### 2. Packs (`stable/packs/`)
User-facing scenario combinations. Users don't pick atoms; they install packs.
- **`enterprise/`**: **Enterprise ODD Pack** — Meta-Rules + Ontology-Driven Development methodology, validated on a 50+ module production system. [→ View Pack](stable/packs/enterprise/README.md)
- `v1-talk/`: A conversational orchestration pack with 6 team patterns.
- `deep-research/`: A Plan → Execute → Synthesize research workflow.
- `knowledge-manage/`: Knowledge system management pack.
- `create-toolkit/`: Project scaffolding toolkit.

## Current Cursor Reference Usage

The repository still supports injecting its existing Cursor-format assets with Git sparse-checkout. This documents current assets; it is not a promise that Cursor remains a core platform or long-term compatibility target.

```bash
# In your new project's root directory:
git clone --filter=blob:none --sparse https://github.com/LSRabbit6/cursor-genesis.git .cursor-genesis
cd .cursor-genesis

# Option A: Inject the full enterprise pack (meta-rules + ODD methodology)
git sparse-checkout set stable/packs/enterprise stable/atoms/rules/enterprise

# Option B: Inject only the 4 meta-rules
git sparse-checkout set stable/atoms/rules/enterprise

# Copy the rules to your local cursor directory
cp -r stable/atoms/rules/enterprise/* ../.cursor/rules/
```

See [`stable/packs/enterprise/README.md`](stable/packs/enterprise/README.md) for the full ODD methodology guide and setup instructions.

## The Vision

CG aims to turn hard-to-understand Agent capabilities into Human–Agent operating mechanisms that are easy to understand, trigger, compose, validate, correct, and distribute—without letting any one tool's file format define the domain.

---
*Built for the future of AI-native engineering.*
