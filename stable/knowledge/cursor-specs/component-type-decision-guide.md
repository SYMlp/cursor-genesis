# 组件类型选择指南：Rule / Skill / Command / Agent

> 回答：我新增的内容应该做成什么类型的组件？

## 核心概念：上下文加载时机梯度

组件类型的选择不是功能分类，而是**上下文加载时机**的选择。加载时机从"始终在场"到"按需触发"形成梯度：

```
Rule (Always/Auto)  →  Skill (Agent-detected)  →  Command (Manual)
     高置信度              中置信度                    低置信度
   "总是相关"            "可能相关"                "只在触发时"
   始终占用上下文        按需占用上下文             触发时才占用
```

## 选择矩阵

| 你的内容是... | 选择 | 理由 |
|:---|:---|:---|
| 项目级约定（框架、语言、风格） | **Rule** (.mdc) | 每次对话都相关，需要始终注入 |
| 领域工作流、复杂操作指南 | **Skill** (SKILL.md) | Agent 判断是否需要加载，或用户 `/` 调用 |
| 重复性 prompt 快捷方式 | **Command** (.md) | 用户显式触发，不常用时不占上下文 |
| 需要独立推理的专家角色 | **Agent/Subagent** (.md) | 需要隔离的上下文和独立的认知空间 |

## 判断流程

```
1. 这个内容被使用的概率有多高？
   ├─ 几乎每次对话都需要 → Rule
   ├─ 某些场景需要，但不是每次 → 继续判断 ↓
   └─ 很少用，但用时很重要 → Command

2. 这个内容需要执行脚本或带参考资料吗？
   ├─ 是，有脚本/资料/多步骤流程 → Skill
   └─ 否，是一段可复用的 prompt → Command

3. 这个内容需要独立的认知空间吗？
   ├─ 是，需要隔离上下文避免污染 → Subagent
   └─ 否，在主对话中执行即可 → Skill 或 Command
```

## 组件间的协作关系（三层分析）

> 升级于 2026-03-04。旧版为二元"能/不能"判断，现升级为三层分析。
> 推导记录：knowledge-graph/meta/derivation/component-calling-relationship-revision-2026-03-04.md

所有组件本质上都是"写给 Agent 看的 Markdown 文档"。没有传统意义上的"调用"——Agent 读到指令后用自己的工具执行。

### 语义自然度（设计意图）

| 方向 | 自然度 | 说明 |
|:---|:---|:---|
| Command → Skill / Subagent | 自然 | 用户入口编排执行，最推荐的搭配模式 |
| Skill → Subagent | 自然 | 知识容器的某步骤需要隔离执行 |
| Subagent → Skill | 自然 | 隔离 Agent 需要专业知识指引 |
| Skill / Subagent → Command | 不自然 | Command 是用户入口语义，内部编排没有理由"调用"用户入口 |

### 实现约束（Cursor 平台）

| 场景 | 可行性 | 原因 |
|:---|:---|:---|
| 主 Agent 读 Skill 并执行 | ✅ | 核心 Skill 机制 |
| Skill 指示"启动 subagent"（主 Agent 执行） | ✅ | 主 Agent 有 Task 工具 |
| Subagent 读 SKILL.md 文件 | ⚠️ 部分 | 能读文件，但无自动检测机制，须在 prompt 中指定路径 |
| Subagent 启动子 Subagent | ⚠️ 视类型 | generalPurpose 可能支持，explore/shell 大概率不支持 |
| 任何 Agent "触发" Command | ❌ | Command 是 UI 层 `/` 机制，不是工具 API |

### 设计原则

1. **顺流优先**：User → Command → Skill/Subagent 方向最自然
2. **薄壳 + 厚容器**：Command 是薄入口（几行），Skill 是知识容器（目录结构承载资产）
3. **隔离有边界**：Subagent 的能力受 subagent_type 限制，不假设它拥有主 Agent 所有工具
4. **避免 God Skill**：Skill 可以编排，但 SKILL.md 保持精简，具体资料放 assets/

## 实践原则

1. **从 Command 开始**：不确定选什么时，先做 Command。需要附件/参考资料/自动检测时升级为 Skill
2. **Command + Skill 搭配**：Command 是用户最便捷的入口（`/触发`），Skill 是知识容器（目录结构承载模板、文档、脚本）。两者协作而非二选一
3. **Rule 保持轻量**：Rule 文件超过 50 行，考虑是否有逻辑泄漏。Rule 只做路由，不做执行
4. **Thin Agent, Fat Skill**：Agent 负责决策和意图识别，具体的重活交给 Skill
5. **Tool 设计即契约**：Skill 的输入/输出是与 Agent 的契约，追求高信号、Token 高效
