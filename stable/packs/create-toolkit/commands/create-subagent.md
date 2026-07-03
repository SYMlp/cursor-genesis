# 创建 Subagent (Create Subagent)

## 概述

创建一个新的 AI Subagent（自主工作者）。Subagent 是能够自主推理、使用 Skill 来解决问题的智能体。

**定位参考**（来自 `.cursor/skills/base-skill-generator/assets/docs/skill-composition-theory.md`）：

| 层级 | 隐喻 | 定义 |
|------|------|------|
| Skill | 原子 (Brick) | 最小的、不可分割的执行单元。 |
| Command | 分子 (Wall) | Skill 的固定序列（SOP）。 |
| **Subagent** | 有机体 (Builder) | 自主使用 Skill 解决问题的智能体。在隔离上下文中执行。 |

**调用方式**（来自 `.cursor/skills/base-skill-generator/assets/docs/subagent-invocation-pattern.md`）：
Cursor 不支持自定义 subagent_type，必须使用 **Role Injection Pattern** — 用 `generalPurpose` 类型 + prompt 注入角色定义。

## 执行步骤

### Step 1: 需求理解

理解用户想要的 Subagent 做什么：
- **名称**：英文短横线格式（如 `code-reviewer`、`test-runner`）
- **职责**：这个 Agent 负责什么任务域
- **范围**：`base`（通用） / `meta`（母版维护） / `app`（项目专用）

### Step 2: 能力拆分分析

**关键步骤**：分析这个 Subagent 需要哪些原子能力（Skill），以及是否需要内部再隔离子 Subagent。

#### Subagent 内部的隔离判断规则

Subagent 自身也有上下文窗口。如果它的工作流中某个步骤会产生大量中间数据，或者某个子任务的过程对该 Subagent 的后续推理没有价值，就应该考虑再隔离。

| 条件 | 结论 | 示例 |
|------|------|------|
| 子任务的中间过程**对本 Subagent 后续步骤无价值**，会污染上下文 | → 子 Subagent | Executor 中的每个 Task 如果独立且产出量大 |
| 子任务**需要不同的专业角色/知识库** | → 子 Subagent | 规划任务 vs 执行任务需要不同的认知模式 |
| 子任务是**重复性循环**，每次迭代独立 | → 子 Subagent（如平台支持） | 对 10 个竞品分别调研，每个可独立执行 |
| 子任务**结果简短**，且后续步骤需要用到 | → Skill / 内联 | 文件读取、格式转换 |
| 子任务**必须串行**且上下步骤有紧密依赖 | → Skill / 内联 | 搜索 → 基于结果筛选 → 基于筛选结果抓取 |

**注意**：Cursor 当前对嵌套 subagent 的支持尚不确定。设计时应：
- 优先方案：Subagent 内部直接用工具串行执行（确保可运行）
- 理想方案：标注哪些步骤"适合隔离为子 Subagent"，等平台支持后可升级

```
<thinking>
1. 这个 Subagent 的工作流有哪几步？
2. 每一步是否已有现成 Skill 可用？
   - 有 → 在 Agent 定义中引用
   - 没有 → 需要先创建 Skill
3. 哪些步骤的中间过程会污染本 Subagent 的上下文？
   - 会 → 标记为"适合隔离为子 Subagent"（当前先内联执行，预留升级路径）
   - 不会 → 内联执行
4. 列出需要新建的 Skill 清单
</thinking>
```

**判断逻辑**：
- 如果所需 Skill **全部已存在** → 直接进入 Step 3
- 如果有 **需要新建的 Skill** → 先为每个新 Skill 执行 `/create-skill` 流程，全部创建完成后再进入 Step 3

### Step 3: 级联创建 Skill（按需）

对于每个需要新建的 Skill，调用 `base-skill-engineer`：

```
Task(
    subagent_type = "base-skill-engineer",
    description = "Create skill for subagent",
    prompt = """
    # Role Injection
    You are the **Skill Engineer**.
    Read and adopt the persona defined in `.cursor/agents/base-skill-engineer.md`.

    # Mission
    Create a new Skill:
    - Name: {skill_name}
    - Scope: {scope}
    - Description: {description}
    - Purpose: This skill will be used by the `{subagent_name}` subagent.

    # Execution
    1. Read knowledge base docs
    2. Run gen.py to scaffold
    3. Inject workflow logic into SKILL.md
    4. Verify
    """
)
```

**注意**：如果有多个 Skill 需要创建且相互独立，可以并行调用多个 Task。

### Step 4: 创建 Subagent 定义

所有依赖的 Skill 就绪后，创建 Agent 定义文件。

**读取规范**：先读 `.cursor/skills/base-skill-generator/assets/docs/standard-subagent.md` 和 `.cursor/skills/base-skill-generator/assets/docs/model-selection-guide.md`。

**创建文件**：`.cursor/agents/{scope}-{agent-name}.md`

**必须包含**：
- Frontmatter：`name`、`description`、`model`（MUST 显式指定，参考 model-selection-guide）
- Identity：角色定义
- Skills：引用所有相关 Skill（用 `@.cursor/skills/xxx/SKILL.md` 格式）
- Workflow：工作流步骤
- Constraints：约束条件

**Agent 模板**：

```markdown
---
name: {scope}-{agent-name}
description: '{description}'
model: {model_choice}
---
# Role: {Display Name}

You are the **{Role Name}**.
Your goal is {goal}.

## Skills
- **{Skill 1}**: `@.cursor/skills/{skill-1}/SKILL.md`
- **{Skill 2}**: `@.cursor/skills/{skill-2}/SKILL.md`

## Workflow
1. **Step 1**: {action}
2. **Step 2**: {action}
3. **Step 3**: {action}

## Constraints
- {constraint 1}
- {constraint 2}
```

### Step 5: 验证

- Agent 定义文件存在且格式正确
- `model` 字段已显式指定
- 所有引用的 Skill 路径存在
- 运行 `base-inventory-updater` 更新资产清单
- （可选）运行 `base-prompt-auditor` 检查 Agent 质量

### Step 6: 输出调用示例

创建完成后，输出该 Subagent 的 **Role Injection 调用示例**，方便其他 Command 或主 Agent 使用：

```
Task(
    subagent_type = "generalPurpose",
    description = "{short description}",
    prompt = """
    # Role Injection
    You are the **{Role Name}**.
    Read and adopt the persona defined in `.cursor/agents/{agent-file}.md`.

    # Mission
    {task description}
    """
)
```

## 不做什么

- **不创建 Command**：Subagent 不负责编排 SOP，那是 Command 的事
- **不跳过 Skill 拆分**：如果 Subagent 需要的能力不存在，必须先创建 Skill
