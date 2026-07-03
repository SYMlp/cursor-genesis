# Rule Governance Quick Reference

## Activation Mode Decision Tree

```
Every conversation? ─Yes─→ alwaysApply: true
       │
       No
       │
Clear file boundaries? ─Yes─→ Expressible as glob?
       │                              │          │
       No                            Yes         No
       │                              │          │
Only on explicit request?    globs: pattern   description only
       │          │          (Specific Files)  (Intelligently)
      Yes         No
       │          │
  (Manual)    description only
 @rule-name   (Intelligently)
```

## Context Budget

| Metric | Limit | Why |
|:---|:---|:---|
| `alwaysApply` rules per project | ≤ 8 | Context window is finite; each always-on rule competes for space |
| Single rule length | ≤ 500 lines | Long rules degrade Agent compliance |
| Recommended rule length | 50-150 lines | Sweet spot for clarity and compliance |

## Naming Conventions

| Aspect | Convention | Example |
|:---|:---|:---|
| Format | kebab-case | `api-response-format.mdc` |
| Length | 3-4 words | `user-auth-guard.mdc` |
| Content | Describe function, not implementation | `prevent-sql-injection.mdc` not `add-escape-function.mdc` |
| Priority prefix | Optional `00-` to `99-` | `00-architecture-constraints.mdc` |
| Module rules | Module name | `user-management.mdc` |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|:---|:---|:---|
| `alwaysApply` + prompt trigger condition | Physical load contradicts logical scope | Use `globs` or Apply Intelligently instead |
| Quoted globs values | May cause matching failures | `globs: src/**` not `globs: "src/**"` |
| Copying code into rules | Gets stale, wastes context | Reference with `@filename` instead |
| Mega-rule (>500 lines) | Agent compliance drops | Split into composable focused rules |
| Duplicate rules | Drift and conflicts | One rule per concern, reference shared |

## Conflict Resolution

| Conflict Type | Detection | Resolution |
|:---|:---|:---|
| Behavioral contradiction | Rule A: "auto-execute", Rule B: "wait for confirmation" | Stricter rule wins |
| Glob overlap | Two rules match same file pattern | Check if behaviors complement or conflict |
| Priority conflict | Multiple rules claim authority | Meta-rule > module rule > ad-hoc rule |
| Cross-project | Team Rules vs Project Rules | Team Rules take precedence (Cursor built-in) |

## Rule Priority Order (Cursor Built-in)

1. **Team Rules** (highest — dashboard managed)
2. **Project Rules** (`.cursor/rules/`)
3. **User Rules** (Cursor Settings)

Within Project Rules, the implicit priority:
1. Meta-rules (`alwaysApply: true`, architectural)
2. Module rules (`globs`-scoped)
3. Ad-hoc rules (Apply Intelligently / Manual)

## Monthly Audit Checklist

- [ ] Count `alwaysApply` rules — still within budget?
- [ ] Any rules inactive > 3 months? → deprecate
- [ ] Any rules referencing deleted specs/files? → update or remove
- [ ] Any glob overlaps causing unintended behavior? → narrow scopes
- [ ] Naming still consistent? → enforce convention
