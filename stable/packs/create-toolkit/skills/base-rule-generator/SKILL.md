---
name: base-rule-generator
description: >
  [Base] Factory for creating Cursor Rules (.mdc). Supports single rule creation
  with full governance, and meta-rule driven batch generation for module-specific rules.
metadata:
  version: "1.0"
  freedom_level: low
category: generator
meta_level: L2
maturity: stable
tags: ["creation", "rules", "meta-rules", "governance", "module-binding", "ddd"]
---

# Skill: Base Rule Generator

## 1. Description

Creates high-quality Cursor Rules (`.mdc` files) with two operating modes:

- **Mode A — Single Rule**: Create one rule for a specific need, with proper format, activation mode, and governance checks.
- **Mode B — Meta-Driven Generation**: Read project-level meta-rules (architectural constraints) → accept module specification → generate module-specific rules that inherit root constraints and bind to module paths.

## 2. Prerequisites

- Write access to `.cursor/rules/`
- For Mode B: at least one meta-rule in the project (`alwaysApply: true` rule defining architectural constraints)

## 3. Knowledge Base (Progressive Loading)

Load references **in order** and **only when needed**.

### Tier 1: Rule Format (Always Load)

Every `.mdc` rule file has YAML frontmatter + Markdown body:

```yaml
---
description: English one-liner (shown in Cursor UI, used for intelligent matching)
globs: src/modules/user/**    # omit if not file-scoped
alwaysApply: false             # true = every conversation
---
```

Frontmatter fields:

| Field | Type | When to use |
|:---|:---|:---|
| `description` | string | **Required** for Apply Intelligently; recommended for all |
| `globs` | string | File pattern — activates when matching files are in context |
| `alwaysApply` | boolean | `true` = loads every conversation (budget: ≤8 per project) |

### Tier 2: Activation Mode Decision (Always Load)

```
Is this rule needed in EVERY conversation?
 ├─ Yes → alwaysApply: true               [Always Apply]
 └─ No → Does it have clear file-path boundaries?
          ├─ Yes → Can paths be expressed as glob?
          │        ├─ Yes → globs: pattern    [Apply to Specific Files]
          │        └─ No  → description only  [Apply Intelligently]
          └─ No → Only needed on explicit user request?
                   ├─ Yes → (no frontmatter flags) [Apply Manually, via @rule-name]
                   └─ No  → description only       [Apply Intelligently]
```

### Tier 3: Rule Source Classification (Load for Mode A)

| Source Type | Definition | Typical Activation |
|:---|:---|:---|
| Spec Mapping | Translates existing spec into Agent behavior | alwaysApply / globs |
| Persona | Defines Agent role and thinking framework | alwaysApply |
| Intent Routing | Recognizes user intent → dispatches behavior | alwaysApply |
| Quality Guard | Write/modify constraints | globs |
| Sync Link | Change in A → check if B needs update | alwaysApply / Intelligently |
| Process Constraint | Behavior rules for specific workflows | globs |

### Tier 4: Meta-Rule Knowledge (Load for Mode B)

Read these references when doing meta-driven generation:

1. `read_file .cursor/skills/base-rule-generator/assets/meta-rule-template.md`
2. `read_file .cursor/skills/base-rule-generator/references/governance-checklist.md`

## 4. Workflow

### Mode A: Single Rule Creation

**Step 1 — Gather Requirements**

Determine from user input or conversation context:
- **Purpose**: What should this rule enforce or teach?
- **Scope**: Always / file-specific / on-demand?
- **File patterns**: If file-specific, which globs?

If ambiguous, ask:
- "Should this rule always apply, or only when working with specific files?"
- "Which file patterns?" (e.g., `src/**/*.tsx`, `backend/modules/auth/**`)

**Step 2 — Classify & Select Activation**

1. Match to Source Type (Tier 3 table)
2. Walk the Decision Tree (Tier 2)
3. Determine frontmatter configuration

**Step 3 — Scan Existing Rules**

```
List all files in .cursor/rules/
```

Check:
- Naming conflicts (same or too-similar names)
- Behavioral conflicts (if Rule A says "auto-execute" and Rule B says "wait for confirmation" → stricter wins)
- Context budget: count `alwaysApply: true` rules, must stay ≤ 8

**Step 4 — Generate Rule File**

File path: `.cursor/rules/{kebab-case-name}.mdc`

Naming conventions:
- kebab-case, 3-4 words, describe **function** not implementation
- Optional numeric prefix for priority: `00-`, `01-` (lower = higher priority)
- Examples: `api-response-format.mdc`, `00-architecture-constraints.mdc`

Structure template:

```markdown
---
description: {English one-liner describing what this rule does}
globs: {pattern, or omit}
alwaysApply: {true/false}
---

# {Rule Title}

> Source: `{path/to/spec-or-derivation}` (if applicable)

## Trigger Condition

When {describe the situation where this rule activates}.

## Behavior

{Imperative instructions. Use MUST/SHOULD/MAY language.
Include concrete examples where helpful.
Reference files with @filename rather than copying content.}
```

**Step 5 — Validate**

- [ ] Frontmatter syntactically correct (YAML between `---` fences)
- [ ] `description` is English, concise, unambiguous
- [ ] `globs` values NOT quoted (correct: `globs: src/**`, wrong: `globs: "src/**"`)
- [ ] No `alwaysApply: true` combined with prompt-level trigger conditions
- [ ] No conflict with existing rules
- [ ] Content is actionable (Agent can follow without guessing)
- [ ] Under 500 lines

---

### Mode B: Meta-Driven Generation

For projects with established meta-rules that define system-wide architectural constraints. Generates module-specific rules that inherit from meta-rules.

**Step 1 — Identify Meta-Rules**

Scan `.cursor/rules/` for rules that:
- Have `alwaysApply: true`
- Define **architectural constraints** (layer structure, dependency rules, naming standards, code generation conventions)

These are the **root constraints**. All generated module rules MUST NOT contradict them.

If no meta-rules exist, offer to create one first using the template:
```
read_file .cursor/skills/base-rule-generator/assets/meta-rule-template.md
```

**Step 2 — Accept Module Specification**

From user input, extract:

| Field | Example | Required |
|:---|:---|:---|
| Module path | `src/modules/user-management/` | Yes |
| Module name | User Management | Yes |
| Domain type | Core / Supporting / Generic | Yes |
| Responsibilities | User CRUD, authentication, role assignment | Yes |
| Allowed dependencies | `common`, `infrastructure` | Recommended |
| Forbidden dependencies | Other core domain modules | Recommended |
| Special conventions | Beyond inherited meta-rules | Optional |

If a **module manifest** is provided (list of all modules), proceed to batch mode (Step 4).

**Step 3 — Derive Module Rule**

Generate `.cursor/rules/{module-name}.mdc`:

```markdown
---
description: Development rules for {module-name} module ({domain-type} domain)
globs: {module-path}/**
alwaysApply: false
---

# {Module Name} — Module Rules

> Inherited from: @{meta-rule-filename}
> Domain type: {Core Domain / Supporting Domain / Generic Domain}

## Module Boundary

- **Path**: `{module-path}/`
- **Responsibilities**: {brief list}
- **Allowed dependencies**: {list modules/layers this module may import}
- **Forbidden dependencies**: {list what this module must NOT import}

## Module Conventions

{Module-specific structure, naming, interfaces.
Reference the meta-rule for inherited conventions: @meta-rule-name}

## Quality Gates

{Module-specific validation rules. Examples:
- All public APIs must have request/response DTOs
- Domain entities must not leak to interface layer
- Test coverage threshold for this module}
```

**Step 4 — Batch Generation** (optional)

When given a module manifest:

1. For each module in the manifest, run Step 3
2. After all generated, cross-validate:
   - No two module rules have overlapping globs
   - All reference the same meta-rules
   - Total `alwaysApply` count still ≤ 8
   - No circular dependencies between module boundaries

**Step 5 — Validate**

All Mode A Step 5 checks, plus:
- [ ] Generated rule references (not copies) meta-rule constraints
- [ ] `globs` pattern correctly scoped to module path
- [ ] Module boundary dependencies don't contradict meta-rule's architecture
- [ ] Domain type classification is consistent with meta-rule definitions

## 5. Lifecycle Management

### When to Create
- New module added to the system
- Repeated Agent mistakes in a specific area
- New architectural constraint identified

### When to Update
- Source spec or meta-rule changed → cascade to affected module rules
- Module boundary or responsibilities changed
- Trigger scope needs adjustment

### When to Deprecate
- Module removed from system
- Rule merged into another
- Inactive > 3 months

### Deprecation Flow
1. Add: `> WARNING: Deprecating — {reason}. Removal by {date}.`
2. Log to project changelog
3. Keep 2 weeks, then delete and update indexes

## 6. Verification

### Success Criteria

- Generated `.mdc` passes frontmatter validation
- Activation mode matches decision tree logic
- No naming or behavioral conflicts
- Content actionable and under 500 lines
- Mode B: module rules correctly inherit meta-rule constraints

### Quick Checks

```bash
# List all rules
ls .cursor/rules/*.mdc

# Count alwaysApply rules (budget ≤ 8)
grep -rl "alwaysApply: true" .cursor/rules/ | wc -l

# Check for glob conflicts between module rules
grep "globs:" .cursor/rules/*.mdc
```
