# Cursor Rules 生命周期管理指南

> 本文档是 knowledge-graph 抽象原则的 Cursor 实现指南。
> 抽象原则来源：`knowledge-graph/meta/derivation/rules-lifecycle-design-2026-03-02.md`
> 关联洞察：`declarative-behavior-control`（声明式行为控制是通用刚需）

## 一、Rule 是什么

在 Cursor 中，Rule（`.mdc` 或 `.md` 文件）是声明式行为控制机制的实现单元。每条 Rule 回答一个问题：**Agent 在特定场景下应该做什么？**

Rule 不是代码，是给 Agent 的行为约束。它通过 Cursor 的上下文注入机制，在 Agent (Chat) 对话时被加载到 Agent 的"记忆"中。

> **作用范围限制**：Rules 只对 Agent (Chat) 生效，不影响 Cursor Tab（自动补全）和 Inline Edit (Cmd/Ctrl+K)。
> 参考来源：`meta/sources/cursor-rules-spec.md`（FAQ 段）

## 二、Rule 来源分类

创建 Rule 前，先确认它属于哪种来源：

| 来源类型 | 定义 | 适用场景 | 触发模式建议 |
|:---|:---|:---|:---|
| 规范映射 | 将已有规范文件翻译为 Agent 行为 | 项目有 spec/paradigm 等规范文件 | `alwaysApply: true` |
| 人格定义 | 定义 Agent 角色和思维框架 | 项目需要定制化的 Agent 行为 | `alwaysApply: true` |
| 意图路由 | 识别用户意图并分发行为 | 需要"说某类话 → Agent 做某事" | `alwaysApply: true` |
| 质量守护 | 写入/修改时的约束 | 需要防止特定类型的错误 | `alwaysApply: true` 或 `globs` |
| 联动同步 | 变更后检查关联位置 | A 改了 → B 是否要跟着改 | `alwaysApply: true` |
| 流程约束 | 特定流程的行为规范 | 只在编辑特定文件时需要约束 | `globs: path/**` |

## 三、.mdc 文件结构规范

每个 Rule 文件必须包含 frontmatter。Cursor 支持 `.mdc`（带 frontmatter 的 Markdown）和 `.md`（纯 Markdown）两种格式。使用 `.mdc` 可以通过 `description` 和 `globs` 精确控制触发行为：

```yaml
---
description: 一句话说明这条 rule 做什么（英文，供 Cursor UI 显示）
# 以下三选一（决定触发模式，详见§四）：
alwaysApply: true           # Always Apply：每次对话都加载
# globs: roots/**,index/**   # Apply to Specific Files：匹配文件路径时加载
# （都不填）                  # Apply Intelligently：Agent 根据 description 自主判断
---
```

### 正文结构

```markdown
# Rule 标题

> 来源规范：`path/to/spec.md`（规范映射类必填，其他类型选填）
> 推导记录：`path/to/derivation.md`（如有）

## 触发条件

描述什么情况下这条 rule 生效。用"当...时"的句式。

## 行为

描述 Agent 应该做什么。用明确的指令句式。
```

### 关键约束

- **必须有 frontmatter**：没有 frontmatter 的 rule 不符合规范
- **description 用英文**：Cursor UI 原生显示用
- **触发条件必须明确**：避免"大概/可能"等模糊表述
- **行为定义必须可执行**：Agent 能根据描述直接行动
- **单文件不超过 500 行**：Cursor 官方最佳实践（2026-03 确认）明确建议 "Keep rules under 500 lines"。超过后 Agent 注意力分配和规则遵从度均可能劣化。当文件逼近阈值时，按功能段拆分为多个文件

## 四、触发模式选择

> **重要**：本节内容基于 Cursor 官方文档（2026-03-02 确认）。如果 Cursor 版本更新导致机制变更，应以官方文档为准并更新本节。
> 参考来源：`meta/sources/cursor-rules-spec.md`（Rule anatomy 段）

Cursor 提供 **4 种** Rule 触发模式（对应 Cursor UI 中的 type dropdown）：

| 模式 | frontmatter 配置 | 机制 | 上下文成本 |
|:---|:---|:---|:---|
| **Always Apply** | `alwaysApply: true` | 每次 Agent (Chat) 对话都加载 | 高（始终占用） |
| **Apply Intelligently** | `alwaysApply: false`（或不填），必须提供 `description` | Agent 根据 description 自主判断是否相关，决定是否加载 | 低（按需） |
| **Apply to Specific Files** | `globs: pattern` | 当对话涉及的文件匹配 glob 模式时加载 | 低（按路径） |
| **Apply Manually** | 不设 `alwaysApply`、不设 `globs`、`description` 可选 | 用户在对话中 @-mention 该 rule 名称时加载（如 `@my-rule`） | 最低（手动） |

> **注意**：所有 4 种模式均只对 Agent (Chat) 生效，不影响 Cursor Tab 和 Inline Edit (Cmd/Ctrl+K)。

### 选择决策树

```text
这条规则是否在每次对话中都需要？（如 Agent 人格、模式识别）
 ├─ 是 → Always Apply
 └─ 否 → 这条规则是否有明确的文件路径触发边界？
          ├─ 是 → 目标路径是否能用 glob 模式表达？
          │        ├─ 是 → Apply to Specific Files (globs)
          │        └─ 否 → Apply Intelligently
          └─ 否 → 这条规则是否只在用户主动请求时才需要？
                   ├─ 是 → Apply Manually
                   └─ 否 → Apply Intelligently
```

### 各模式的适用场景

| 来源类型 | 推荐触发模式 | 理由 |
|:---|:---|:---|
| 人格定义 | Always Apply | Agent 角色在每次对话中都需要 |
| 规范映射（全局性） | Always Apply | 模式识别等全局行为每次都需要 |
| 意图路由 | Always Apply | 用户随时可能提出特定意图 |
| 质量守护 | Apply to Specific Files 或 Apply Intelligently | 只在操作受保护的文件时需要 |
| 联动同步 | Always Apply 或 Apply Intelligently | 取决于变更范围是否可预测 |
| 流程约束 | Apply to Specific Files | 只在编辑特定路径的文件时需要 |

### 反模式：alwaysApply + 提示词触发条件

**避免**以下模式：

```yaml
---
alwaysApply: true  # ← 物理层面：每次都加载
---
## 触发条件
当操作涉及 X 时本规则生效  # ← 提示词层面：又说不是每次都需要
```

如果一条规则的正文里写了"触发条件"来限定生效场景，说明它**不是**每次都需要。应该用 `globs` 或 Apply Intelligently 代替 `alwaysApply`，让 Cursor 的物理机制替代提示词层面的逻辑判断。

### 反模式：globs 值加双引号

**避免**在 frontmatter 的 `globs` 值中使用双引号：

```yaml
# 错误
globs: "roots/**,index/**"

# 正确
globs: roots/**,index/**
```

### 上下文预算

Always Apply 的规则加上 CLAUDE.md 共同占用上下文窗口。建议：

- **单项目 Always Apply 规则不超过 8 条**（含 CLAUDE.md）
- 超过时优先合并功能相近的规则
- 次选降级为 Apply Intelligently 或 globs

#### 多根工作区的预算叠加

在 Cursor 的 Multi-root Workspace 中，所有项目的 `alwaysApply` 规则会**叠加**到同一个对话上下文。4 个项目各 4-7 条 alwaysApply 规则 = 20+ 条同时加载，远超单项目 8 条预算。

缓解策略：

1. **缩小工作区**：日常工作时只打开当前关注的 1-2 个项目
2. **合并同质规则**：从同一模板创建的项目（如共用 cursor-genesis 脚手架）的 00-03 规则内容相似，可在模板层面合并
3. **降级非频繁规则**：将使用频率低的 alwaysApply 规则降级为 Apply Intelligently，利用 `description` 让 Agent 自主判断

## 五、生命周期决策

### 5.1 何时创建新 Rule

满足以下**全部**条件时创建：

1. 识别到"Agent 需要在场景 X 下执行行为 Y"的明确需求
2. 该行为无法通过修改现有 Rule 覆盖
3. 该场景有独立的触发边界

### 5.2 何时更新现有 Rule

满足以下**任一**条件时更新：

- 对应的规范文件更新了（规范映射类）
- 触发条件需要扩大或缩小
- 行为定义需要修正或补充
- 发现与其他 Rule 的冲突需要调和

### 5.3 何时废弃 Rule

以下情况触发废弃评估：

- 对应的规范文件被删除
- 场景不再存在（系统架构变更导致）
- 功能被另一条 Rule 合并
- 长期未触发（> 3 个月无相关场景）

### 5.4 废弃流程

1. 在 Rule 文件头部添加标注：`> ⚠️ 即将废弃：{原因}，预计 {日期} 移除`
2. 记录到项目的 changelog
3. 保留 2 周（一个迭代周期）
4. 删除文件并更新相关索引

## 六、规范-规则同步

对于规范映射类 Rule：

- **规范变 → Rule 必须跟**：规范文件更新后，检查对应 Rule 是否需要同步
- **Rule 变 → 规范不一定动**：Rule 可以独立调整触发条件和行为细节
- **在 Rule 头部标注来源**：让 Agent 和人都能追溯

## 七、冲突检测

两种冲突类型：

| 类型 | 表现 | 处理方式 |
|:---|:---|:---|
| 行为矛盾 | Rule A 说"直接执行"，Rule B 说"等人确认" | 以更严格的为准 |
| 触发重叠 | 多条 Rule 覆盖同一场景 | 检查行为是否互补（OK）还是矛盾（需修改） |

**定期审计**：每月检查一次 rules 清单，确认无冲突、无冗余。

## 八、命名规范

### knowledge-graph 项目

- 格式：`{功能描述}.mdc`（kebab-case）
- 示例：`content-status-enforcement.mdc`、`user-query-routing.mdc`
- 不用序号（规则较少，alwaysApply 为主）

### cursor-genesis 项目

- 格式：`{序号}-{功能描述}.mdc`
- 示例：`00-production-safety.mdc`、`01-project-rules.mdc`
- 用序号暗示优先级（00 = 最高安全约束）

### 通用原则

- 描述功能而非实现
- 用 kebab-case
- 避免过长（3-4 个词为宜）

## 九、补充：Rule 的多种载体与优先级

> 参考来源：`meta/sources/cursor-rules-spec.md`

Cursor 支持多种 Rule 载体，优先级从高到低：

| 载体 | 格式 | 适用场景 |
|:---|:---|:---|
| **Team Rules** | 纯文本（Dashboard 管理） | 团队/企业级统一标准 |
| **Project Rules** | `.cursor/rules/*.mdc` 或 `.md` | 项目级规范和约束 |
| **AGENTS.md** | 项目根目录或子目录的 Markdown | 简单场景的轻量替代方案 |
| **User Rules** | Cursor Settings → Rules | 个人全局偏好 |
| **`.cursorrules`** | 项目根目录（legacy） | 已弃用，建议迁移 |

**冲突解决规则**：Team Rules > Project Rules > User Rules。所有适用规则会被合并，冲突时高优先级源为准。

**AGENTS.md 的特殊性**：支持嵌套子目录，子目录的指令与父目录合并，更具体的指令优先。适合不需要 frontmatter 元数据的简单场景。

## 十、规则与设计文档的关系模式

> 推导来源：`knowledge-graph/meta/derivation/rule-dual-growth-modes-2026-03-14.md` §六

### 10.1 激活层模型

规则是设计文档的**激活层**：

- **设计文档**（如 `docs/architecture.md`）= 不被主动注入的知识。存在于项目中但不被 Cursor 自动加载
- **规则**（`.mdc`）= 主动触发器。被 Cursor 自动加载后，告诉 Agent "去读某个设计文档"
- 没有规则指向的设计文档 = **未激活知识**——Agent 仍可通过搜索或用户 `@file` 引用访问，但不在自动行为路径上

### 10.2 双链路激活

规则激活设计文档有两条正交链路：

| 链路 | 触发条件 | 机制 | 适用场景 |
|:---|:---|:---|:---|
| **A: 文件驱动** | 用户打开/编辑了匹配 globs 的文件 | globs 规则加载 → 规则中的"首读文档"指令 → Agent 读取 | 开发过程中自然触发 |
| **B: 意图驱动** | 用户在对话中提问（无相关文件打开） | alwaysApply 的路由规则 → 路由表匹配意图 → 指定首读文档 | 用户直接提问、规划阶段 |

**链路 B 是链路 A 的互补层**。当用户说"怎么做本体提取"但没有打开 `docs/domain/**` 下的任何文件时，globs 规则不触发，只有 alwaysApply 的路由规则能将 Agent 引导到正确的设计文档。

### 10.3 两种将设计文档内容带入上下文的方式

| 方式 | 机制 | 优势 | 代价 | 选择标准 |
|:---|:---|:---|:---|:---|
| **"首读文档"指令** | 规则正文写 `首读: docs/xxx.md`，Agent 运行时用 Read Tool 读取 | 按需加载，大文档不浪费上下文 | 额外 Tool call，增加 1-2s 延迟 | 文档 > 50 行 |
| **`@file` 引用** | 规则正文写 `@docs/xxx.md`，Cursor 直接注入文件内容 | 零延迟，内容直接在上下文中 | 文档越大，上下文占用越高 | 文档 < 50 行 |

> `@file` 引用来自 Cursor 官方 FAQ："Use @filename.ts to include files in your rule's context." 官方最佳实践也建议 "Reference files instead of copying their contents"。

**实践建议**：大型设计文档（如 300+ 行的架构设计）用"首读文档"模式；频繁引用的小型参考（如 10-20 行的字段映射表、模板片段）用 `@file` 引用。

### 10.4 规则的建设-诊断双轨

规则体系由两种不同生长模式的规则组成：

| 维度 | 建设型规则 | 诊断型规则 |
|:---|:---|:---|
| 回答的问题 | 怎么造？ | 怎么查？怎么修？ |
| 与设计文档的关系 | 薄激活层 → 指向厚知识体 | 排查逻辑直接写在规则中 |
| 创建驱动力 | 架构设计决策（M2） | 实际问题暴露（M1 中发现，M3 固化） |
| 修改频率 | 低（架构稳定后几乎不动） | 高（每次新问题场景都可能新增） |
| 存放方式 | 规则文件的前段 | 同文件后段（标题格式 `### 调试<问题>？`） |

两类规则在同一 `.mdc` 文件中共存时，建设段在前、诊断段在后。当文件逼近 500 行硬限制、或诊断内容量超过建设内容量时，拆分为独立文件。

## 十一、Cursor 官方最佳实践速查（2026-03 确认）

> 来源：cursor.com/docs/context/rules（2026-03-14 拉取）

### 规则编写

- **引用而非复制**：用 `@filename` 引用文件内容，不要在规则中复制代码。防止规则与代码不同步
- **单文件不超过 500 行**：过长的规则影响 Agent 性能
- **一条规则一个关注点**：拆分大规范为多个可组合的小规则
- **从简单开始**：只在观察到 Agent 重复犯同一错误时才添加规则，不要预设优化

### 规则不应包含

- 代码库中已有的内容（指向典型示例即可）
- 极少触发的边缘场景指令
- Agent 已知的通用工具命令文档（npm, git, pytest 等）
- 完整的代码风格指南（应使用 linter）

### 文件格式

- 支持 `.md` 和 `.mdc` 两种扩展名
- `.mdc` 使用 YAML frontmatter 控制 `description`、`globs`、`alwaysApply`
- 规则文件可以组织在子目录中（如 `.cursor/rules/modules/`）
- 支持 `/create-rule` 命令在对话中直接创建规则

### AGENTS.md

- 支持嵌套子目录（`frontend/AGENTS.md`、`backend/AGENTS.md`）
- 子目录指令与父目录合并，更具体的优先
- 适合不需要 frontmatter 元数据的简单场景
- 作为 `.cursor/rules` 的轻量替代方案
