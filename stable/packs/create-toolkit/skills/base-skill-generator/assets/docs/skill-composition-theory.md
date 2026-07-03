# Skill Composition Theory (The Architecture of Capability)

> **Context**: V2.2 Architecture Definition (upgraded 2026-03-04).
> **Purpose**: To define how Skills are composed into higher-order capabilities, and **when to create each type**.
> **Upgrade note**: V2.1→V2.2 将组件关系从刚性调用约束升级为三层分析（语义/实现/实践）。
> 推导记录：knowledge-graph/meta/derivation/component-calling-relationship-revision-2026-03-04.md

## 1. The Hierarchy of Capability

All components are fundamentally "Markdown documents for the Agent to read." Differences lie in loading timing and execution environment.

| Entity | Definition | Context Impact | Key Trait |
| :--- | :--- | :--- | :--- |
| **Skill** | Knowledge package with optional assets directory | **High**. Executed in current context. | Agent-detected or user-invoked; can carry reference docs, templates, scripts |
| **Command** | User-facing prompt shortcut | **High**. Executed in current context. | Only triggered via `/command`; thinnest entry point |
| **Subagent** | Agent with isolated context window | **Zero** on parent. Own context. | Core value: context isolation, not parallelism |

## 2. Decision Hooks: When to Create What

This is the **canonical decision framework** referenced by all create-* commands and the `base-skill-engineer`.

### 2.1 When the User's Need → Skill

| Signal | Explanation |
|--------|-------------|
| 任务是**确定性**的，输入 → 输出可预测 | 不需要推理或判断，每次执行结果一致 |
| 任务是**原子**的，只做一件事 | "解析 PDF"、"写文件"、"校验格式" |
| 执行结果**简短**，对上下文无污染 | 不会产生大量中间数据 |

**反向信号（不应该是 Skill）**：
- 描述中出现"先...然后...再..."的多步串联 → 考虑 Command
- 描述中出现"判断"、"决策"、"自主选择" → 考虑 Subagent
- 描述中出现"搜索"、"调研"、"推理" → 几乎一定需要 Subagent

### 2.2 When the User's Need → Command

| Signal | Explanation |
|--------|-------------|
| 用户想要一个**可重复的流程** | "每次做 X 都是这几步" |
| 流程步骤**固定、顺序明确** | 不需要运行时判断该走哪条路 |
| 流程中每一步是**确定性**的（可以是 Skill，也可以调 Subagent） | 但编排逻辑本身是线性的 |
| 用户期望通过**斜杠命令**触发 | `/deep-research`、`/fix-bug` |

**Command 内部何时需要 Subagent**：
- 某个步骤的**中间过程对用户无价值**，大量输出会污染主 Agent 上下文 → Subagent
- 某个步骤**需要自主推理**（搜索/判断/多轮决策）→ Subagent
- 某个步骤**token 消耗很大** → Subagent（保护主 Agent 上下文窗口）
- 用户**明确要求**该步骤用独立 Agent → Subagent
- 步骤结果**简短、确定性、用户需要实时看到** → Skill / 内联

### 2.3 When the User's Need → Subagent

| Signal | Explanation |
|--------|-------------|
| 任务**非确定性**，需要推理、搜索、判断 | "调研 X"、"审查代码"、"诊断 Bug" |
| 任务的**中间过程不需要被调用者看到** | 过程噪音大，只需要最终结果 |
| 任务会产生**大量 token** | 搜索结果、文件读取、多轮推理 |
| 任务需要**不同的专业角色/知识库** | 与当前上下文的关注点不同 |

**Subagent 内部何时需要子 Subagent**：
- 子任务的中间过程**对本 Subagent 后续步骤无价值**，会污染其上下文 → 子 Subagent
- 子任务**需要不同的认知模式** → 子 Subagent（如：规划 vs 执行）
- 子任务是**重复循环，每次迭代独立** → 子 Subagent（如平台支持并行）
- 子任务**结果简短、后续步骤依赖它** → Skill / 内联
- 子任务**必须串行且紧密依赖** → Skill / 内联

> **平台限制注意**：Cursor 当前对嵌套 subagent 支持不确定。设计时优先保证"内联可运行"，标注"适合隔离"的步骤，预留升级路径。

### 2.4 Decision Flowchart

```
用户需求进入
    │
    ├── 单步、确定性、原子操作？
    │   └── YES → 创建 Skill
    │
    ├── 多步、固定顺序、可重复流程？
    │   └── YES → 创建 Command
    │       └── 其中某步需要推理/大量中间输出？
    │           └── YES → 该步骤用 Subagent（级联创建）
    │
    └── 需要自主推理、搜索、判断？
        └── YES → 创建 Subagent
            └── 需要的原子能力不存在？
                └── YES → 先创建 Skill（级联创建）
```

## 3. Atomicity as Design Preference (not Absolute Rule)

> Upgraded from V2.1 "MUST be Atomic" to V2.2 "prefer atomic, but can orchestrate."

**Prefer atomic Skills.** Atomic skills are easier to compose and reason about.

*   **❌ Bad**: A Skill that "Fixes a Bug" (Too vague, requires reasoning).
*   **✅ Good**: A Skill that "Applies a Patch File" (Deterministic, atomic).
*   **✅ Also Good**: A Skill that orchestrates a multi-step workflow with attached assets (e.g., new-project-setup with templates, checklists, docs).

**When to go beyond atomic:**
*   Skill 需要携带大量参考资料（模板、文档、检查清单）→ 用 assets/ 目录承载
*   Skill 的某些步骤需要上下文隔离 → SKILL.md 中指示 Agent 启动 Subagent
*   多个 atomic skills 总是一起使用 → 考虑合并为一个编排 Skill

**约束：SKILL.md 本身保持精简（流程指引），具体资料放 assets/ 子目录。避免 God Skill。**

## 4. Designing for Composition

When creating a Skill, ask: **"Who will use this?"**

### Scenario A: Designed for Commands (SOPs)
*   **Requirement**: Strict Input/Output interfaces.
*   **Focus**: Reliability and Speed.
*   **Example**: `base-git-commit` (Used by `/save` command).

### Scenario B: Designed for Subagents (Agents)
*   **Requirement**: Rich, verbose logging (for the Agent to read).
*   **Focus**: Observability and Error Reporting.
*   **Example**: `base-code-search` (Used by `Explorer` subagent).

## 5. The Anti-Pattern: "The God Skill"

Do NOT create a Skill that does "Research + Plan + Execute".
*   **Break it down**:
    1.  `base-research` (Skill) -> Used by `Researcher` (Subagent).
    2.  `base-plan` (Skill) -> Used by `Architect` (Subagent).
    3.  `base-execute` (Skill) -> Used by `Builder` (Subagent).

## 6. The Cascade Pattern

When creating higher-order capabilities, **start from the user's entry point** and build as needed:

```
实践推荐路径：
Step 1: 先做 Command（用户最便捷的入口）
Step 2: 发现需要附件/参考资料/自动检测 → 升级为 Skill（或 Command + Skill 搭配）
Step 3: 发现某步骤需要隔离执行 → 该步骤用 Subagent

经典搭配模式：
/new-project (Command, 薄壳入口)
  └── new-project-setup/ (Skill, 知识容器)
        ├── SKILL.md (流程指引)
        ├── assets/templates/ (项目模板)
        └── assets/docs/ (约定文档)
```

> V2.1 推荐 bottom-up（先 Skill → 再 Subagent → 最后 Command）。
> V2.2 升级为 top-down（先 Command → 按需添加 Skill/Subagent），因为实践表明
> 多数场景 Command 已够用，过早拆分原子 Skill 常常导致过度设计。
