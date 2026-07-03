# 创建 Command (Create Command)

## 概述

创建一个新的 Command（SOP / 用户可直接调用的斜杠命令）。

这是**最高层的创建入口**。用户只需说"我想要一个能做 X 的命令"，本流程会自动分析背后需要哪些 Subagent 和 Skill，并级联创建。

**定位参考**（来自 `.cursor/skills/base-skill-generator/assets/docs/skill-composition-theory.md`）：

| 层级 | 隐喻 | 定义 |
|------|------|------|
| Skill | 原子 (Brick) | 最小的、不可分割的执行单元。 |
| **Command** | 分子 (Wall) | Skill 的固定序列（SOP）。高频、确定性。用户直接调用。 |
| Subagent | 有机体 (Builder) | 自主使用 Skill 解决问题的智能体。 |

**Command 与 Subagent 的区别**：
- Command 是**确定性的 SOP**：步骤固定、顺序明确、每次执行逻辑一致
- Subagent 是**非确定性的工作者**：需要推理、判断、自主决策
- 一个 Command 可以在步骤中**调用 Subagent**（用 Role Injection Pattern）

## 执行步骤

### Step 1: 需求理解

理解用户想要什么样的命令：
- **名称**：英文短横线格式（如 `deep-research`、`code-review`）
- **触发方式**：用户通过 `/command-name` 调用
- **预期效果**：执行完后用户能得到什么

### Step 2: 架构分析（最关键的一步）

分析这个 Command 背后的复杂度，决定需要什么支撑设施。

#### 何时需要 Subagent（隔离判断规则）

不是所有步骤都需要 Subagent。判断一个步骤是否应该隔离为 Subagent，使用以下规则：

| 条件 | 结论 | 原因 |
|------|------|------|
| 用户**明确要求**用独立 Agent 处理 | → Subagent | 尊重用户意图 |
| 该步骤的**中间过程对用户无价值**，大量中间输出会**污染主 Agent 上下文** | → Subagent | 上下文隔离，避免噪音影响后续步骤的推理质量 |
| 该步骤需要**自主推理、搜索、多轮决策**，过程不确定 | → Subagent | 非确定性任务天然适合隔离执行 |
| 该步骤产生的**token 量很大**（如批量搜索、大量文件读取） | → Subagent | 保护主 Agent 的上下文窗口 |
| 该步骤是**确定性的、结果简短**、用户需要实时看到 | → Skill / 内联 | 无需隔离，直接执行更高效 |

**核心原则**：Subagent = 上下文隔离墙。凡是"过程不需要被主 Agent 或用户看到"的工作，都应该隔离到 Subagent。

```
<thinking>
## 复杂度判断

1. 这个 Command 的工作流有几步？
2. 每一步的性质是什么？
   - 确定性操作（读文件、写文件、运行脚本）→ 用 Skill
   - 需要自主推理/搜索/判断 → 用 Subagent
   - 简单逻辑（格式化、模板填充）→ 直接在 Command 中完成
3. 每一步的中间产出是否需要被用户/主Agent看到？
   - 不需要 + 产出量大 → 强烈建议 Subagent
   - 需要用户确认 → 保留在主 Agent 中

## 架构决策

根据分析结果，选择架构模式：

### 模式 A: 纯 SOP（简单）
- 所有步骤都是确定性的
- 只需要引用现有 Skill
- 例：`/checkpoint`（保存进度 → 写文件）

### 模式 B: SOP + 已有 Subagent（中等）
- 部分步骤需要自主推理
- 可以复用现有 Subagent
- 例：`/fix-bug`（调用 base-debugger）

### 模式 C: SOP + 新 Subagent + 新 Skill（复杂）
- 需要全新的推理能力
- 需要级联创建 Skill → Subagent → Command
- 例：`/deep-research`（需要 planner agent + executor agent + 各自的 skill）

## 产出清单

列出需要创建的所有资产：
- [ ] Skill: {name} — {purpose}
- [ ] Skill: {name} — {purpose}
- [ ] Subagent: {name} — {purpose}
- [ ] Command: {name} — {purpose}（本体）
</thinking>
```

**向用户确认**：将架构分析结果展示给用户，包括：
- 将要创建哪些资产（Skill / Subagent / Command）
- 各资产之间的关系
- 用户确认后再开始创建

### Step 3: 级联创建（自底向上）

按照 **Skill → Subagent → Command** 的顺序创建，因为上层依赖下层。

#### 3a. 创建 Skill（如需）

对每个需要新建的 Skill，执行 `/create-skill` 流程：

```
Task(
    subagent_type = "base-skill-engineer",
    description = "Create skill: {skill_name}",
    prompt = """
    # Role Injection
    You are the **Skill Engineer**.
    Read and adopt the persona defined in `.cursor/agents/base-skill-engineer.md`.

    # Mission
    Create a new Skill:
    - Name: {skill_name}
    - Scope: {scope}
    - Description: {description}

    # Execution
    1. Read knowledge base docs
    2. Run gen.py to scaffold
    3. Inject workflow logic
    4. Verify
    """
)
```

独立的 Skill 可以**并行创建**（多个 Task 同时调用）。

#### 3b. 创建 Subagent（如需）

所有依赖的 Skill 就绪后，创建 Subagent 定义文件。

参考 `/create-subagent` 的 Step 4 流程：
- 读取 `.cursor/skills/base-skill-generator/assets/docs/standard-subagent.md`
- 读取 `.cursor/skills/base-skill-generator/assets/docs/model-selection-guide.md`
- 创建 `.cursor/agents/{agent-name}.md`，引用刚创建的 Skill

#### 3c. 创建 Command 本体

所有支撑设施就绪后，创建 Command 文件。

**读取规范**：`.cursor/skills/base-skill-generator/assets/docs/standard-command.md`

**创建文件**：`.cursor/commands/{command-name}.md`

**Command 结构要求**：
1. 概述：一句话说明做什么
2. 执行步骤：每步清晰，包含调用指令
3. 如果涉及 Subagent：**必须包含 Role Injection 调用代码块**（参考 `deep-research.md` 的写法）
4. 验证步骤：最后一步必须是验证
5. 使用场景示例

**Subagent 调用模板**（写在 Command 步骤中）：

```
Task(
    subagent_type = "generalPurpose",
    description = "{short description}",
    prompt = """
    # Role Injection
    You are the **{Role Name}**.
    Read and adopt the persona defined in `.cursor/agents/{agent-file}.md`.

    # Mission
    {具体任务描述和参数}
    """
)
```

### Step 4: 验证

- Command 文件存在且步骤清晰
- 所有引用的 Skill 和 Subagent 路径存在
- 如有 Subagent 调用，包含完整的 Role Injection 代码块
- 运行 `base-inventory-updater` 更新资产清单
- 运行 `base-closure-validator`（可选）检查引用完整性

### Step 5: 输出总结

向用户展示创建结果：

```markdown
## 创建完成

### 已创建资产
- Command: `.cursor/commands/{command-name}.md`
- Subagent: `.cursor/agents/{agent-name}.md` (如有)
- Skill: `.cursor/skills/{skill-name}/SKILL.md` (如有)

### 使用方式
在 Chat 中输入 `/{command-name}` 即可触发。

### 架构图
Command → Subagent → Skill
```

## 设计原则

1. **用户只需说"我要什么"**：不需要知道底层需要 Skill 还是 Subagent
2. **自底向上创建**：先 Skill → 再 Subagent → 最后 Command
3. **复用优先**：如果已有可用的 Skill/Subagent，直接引用，不重复创建
4. **确认再行动**：架构分析结果必须给用户确认后再开始级联创建
5. **每个 Command 都能独立运行**：不依赖隐式知识，所有调用指令写在命令中
