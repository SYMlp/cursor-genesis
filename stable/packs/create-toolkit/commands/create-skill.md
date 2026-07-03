# 创建 Skill (Create Skill)

## 概述

创建一个新的 AI Skill（原子能力单元）。Skill 是最小的、不可再分的执行单元。

**定位参考**（来自 `.cursor/skills/base-skill-generator/assets/docs/skill-composition-theory.md`）：

| 层级 | 隐喻 | 定义 |
|------|------|------|
| **Skill** | 原子 (Brick) | 最小的、不可分割的执行单元。在当前上下文中执行。 |
| Command | 分子 (Wall) | Skill 的固定序列（SOP）。高频、确定性。 |
| Subagent | 有机体 (Builder) | 自主使用 Skill 解决问题的智能体。隔离上下文。 |

## 执行步骤

### Step 0: 类型决策钩子（MUST，在创建前执行）

在创建任何东西之前，先判断用户要的到底是不是 Skill。

| 用户描述中的信号 | 判断 | 路由 |
|------------------|------|------|
| "解析 X"、"校验 X"、"转换 X"、"写入 X" — 单一确定性动作 | → **Skill** | 继续 Step 1 |
| "先...然后...再..." — 多步固定序列 | → **Command** | 告知用户改用 `/create-command`，它会自动级联创建需要的 Skill |
| "调研"、"搜索"、"判断"、"审查"、"诊断" — 需要推理 | → **Subagent** | 告知用户改用 `/create-subagent`，它会自动级联创建需要的 Skill |
| "我想要一个命令来做 X" — 用户明确想要斜杠命令 | → **Command** | 告知用户改用 `/create-command` |
| "帮我做一个能 X 的功能" — 模糊描述 | → **需要进一步分析** | 按上述规则拆解，大概率需要 `/create-command`（最高层入口会自动处理） |

**如果判断不是 Skill**：不要硬创建一个"上帝 Skill"。明确告知用户推荐的路由，并说明原因。

### Step 1: 需求理解 + 分类

确认是 Skill 后，确定以下信息：

**基本信息**：
- **名称**：英文短横线格式（如 `pdf-parser`、`log-cleaner`）
- **职责**：一句话描述这个 Skill 做什么
- **范围**：`base`（通用） / `meta`（母版维护） / `app`（项目专用） / `lib`（可选扩展）
- **消费者**：谁会用这个 Skill？
  - 被 Command 调用 → 接口要严格、结果要可靠
  - 被 Subagent 调用 → 日志要详细、错误报告要丰富

**分类标签（Category）**——决定元数据级别：

| 标签 | 判断标准 | 元数据级别 |
|:-----|:---------|:-----------|
| `executor` | 输入→输出完全确定性，无设计判断 | L0（仅增强 Frontmatter） |
| `generator` | 创建新资产，包含设计决策和创造性判断 | L2（完整认知元层） |
| `analyzer` | 读取数据/代码，产出判断或报告 | L1（标准：含修改指南） |
| `orchestrator` | 管理上下文，协调多个组件协作 | L1 ~ L2 |
| `researcher` | 信息检索与汇总 | L1 |

> **标准参考**：`.cursor/standards/skill-meta-standard.md`

### Step 1.5: 学习型工厂检索（推荐）

在创建前，检索同 category 的已有 Skill 的元数据作为参考：

```
1. 确定 category 标签（如 analyzer）
2. 扫描项目中所有 SKILL.md 的 Frontmatter，筛选 category 相同的 Skill
3. 如果找到同类 Skill：
   - 读取其 .meta/GUIDE.md（如存在）了解其设计思路
   - 读取其 SKILL.md 了解结构范式
   - 将最佳范例的关键信息作为 few-shot 上下文传递给 Skill Engineer
4. 如果没有同类 Skill：正常创建，本次创建将成为该类别的首个范例
```

### Step 2: 调用 Skill Engineer 创建

调用 `base-skill-engineer`（subagent）执行创建：

```
Task(
    subagent_type = "base-skill-engineer",
    description = "Create new skill",
    prompt = """
    # Role Injection
    You are the **Skill Engineer**.
    Read and adopt the persona defined in `.cursor/agents/base-skill-engineer.md`.

    # Mission
    Create a new Skill with the following spec:
    - Name: {skill_name}
    - Scope: {scope}
    - Description: {description}
    - Category: {category}
    - Meta Level: {meta_level}
    - Consumer: {Command / Subagent / Both}
    - Purpose: {detailed_purpose}

    # Few-shot Reference (if available)
    {same_category_skill_examples_or_"无同类范例"}

    # Important
    - Type has been confirmed as Skill by the caller (Step 0 already passed). Skip Phase 0 and proceed directly.
    - If during design you discover this is NOT atomic, report back with ESCALATE.

    # Execution
    1. Read the knowledge base docs (as specified in your agent definition)
    2. Run: python .cursor/skills/base-skill-generator/scripts/gen.py --name "{skill_name}" --scope "{scope}" --description "{description}" --category "{category}"
    3. Edit the generated SKILL.md: inject the actual workflow logic, input/output contract, constraints
    4. Edit the generated .meta/GUIDE.md (if L1+): fill in architecture overview, modification map, optimization roadmap
    5. Edit the generated _meta/data/skill-meta/{skill_name}/ factory records (if L2): fill in design decisions, references
    6. Verify the result
    """
)
```

**处理 Skill Engineer 的返回**：
- 如果返回 `ESCALATE: SUBAGENT_NEEDED` → 引导用户执行 `/create-subagent`
- 如果返回 `ESCALATE: COMMAND_NEEDED` → 引导用户执行 `/create-command`
- 如果正常完成 → 继续 Step 3

### Step 3: 验证

- 检查 `.cursor/skills/{scope}/{scope}-{skill_name}/SKILL.md` 是否存在且结构完整
- 检查 Frontmatter 是否含 `name`、`description`、`metadata.version`、`category`、`meta_level`
- 如果 L1+：检查 `.meta/GUIDE.md` 存在且非空
- 如果 L2：检查 `_meta/data/skill-meta/{scope}-{skill_name}/DESIGN.md` 存在
- 运行 `base-prompt-auditor`（可选）检查质量

### Step 4: 注册

- 运行 `base-inventory-updater` 更新资产清单

### Step 5: 输出总结

向用户展示创建结果：

```markdown
## 创建完成

### 已创建资产
- Skill: `.cursor/skills/{scope}/{scope}-{skill_name}/SKILL.md`
- Category: {category} | Meta Level: {meta_level}
- [L1+] 修改指南: `.cursor/skills/{scope}/{scope}-{skill_name}/.meta/GUIDE.md`
- [L2] 工厂记录: `_meta/data/skill-meta/{scope}-{skill_name}/`

### 引用方式
在 Command 或 Subagent 中通过以下方式引用：
- `@.cursor/skills/{scope}/{scope}-{skill_name}/SKILL.md`

### 建议的下一步
- 如需将此 Skill 编排进 SOP → `/create-command`
- 如需创建使用此 Skill 的自主 Agent → `/create-subagent`
- [L2] 建议填写工厂记录中的设计讨论和参考来源
```

## 不做什么

- **不创建 Command**：如果需要 SOP 编排 → `/create-command`
- **不创建 Subagent**：如果需要自主推理 → `/create-subagent`
- **不创建上帝 Skill**：如果一个 Skill 需要"推理"和"决策"，它不是 Skill。必须升级，不能将就。
