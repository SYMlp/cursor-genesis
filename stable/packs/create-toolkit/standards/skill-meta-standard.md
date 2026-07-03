# Skill 认知元层规范 (Skill Meta Layer Standard) V1.0

> **Purpose**: 定义 Skill 的第二维度——认知元层（Meta/Cognition Layer）的结构、格式与治理规则。
> **Prerequisite**: 本规范建立在现有 `skill-package-standard.md`、`anthropic-skill-standard.md`、`directory-structure.md` 之上，不替代它们，而是扩展。
> **Design Rationale**: 见 `_meta/docs/concept/2026-03-02-skill-meta-layer-design.md`

---

## 1. 适用范围

本规范适用于所有需要认知元层的 Skill。是否需要、需要到什么级别，由 Skill 的 **分类标签（Category Tag）** 和 **元层级别（Meta Level）** 决定。

---

## 2. 分类标签 (Category Tags)

每个 Skill 在 Frontmatter 中必须声明一个 `category` 标签。

### 2.1 标签定义

| 标签 | 代码 | 判断标准 | 典型特征 |
|:-----|:-----|:---------|:---------|
| 执行型 | `executor` | 输入→输出完全确定性，无设计判断 | 参数驱动、模板渲染、文件操作 |
| 生成型 | `generator` | 创建新资产，过程中包含设计决策 | 生成代码/文档/配置，创建其他 Skill |
| 分析型 | `analyzer` | 读取数据/代码，产出判断或报告 | 校验、审计、扫描、统计 |
| 编排型 | `orchestrator` | 管理上下文，协调多个组件协作 | 上下文加载、初始化、状态管理 |
| 研究型 | `researcher` | 信息检索与汇总 | 搜索、调研、笔记生成 |

### 2.2 标签的机器用途

- **create-skill** 在创建新 Skill 时，先判断标签，再检索同标签 Skill 的元数据作为 few-shot 范例
- **base-inventory-updater** 可按标签聚合统计
- **base-prompt-auditor** 可按标签应用不同的审计标准

---

## 3. 元层级别 (Meta Level)

元层级别决定了一个 Skill 需要多少认知元数据。

| 级别 | 代码 | 适用标签 | 所需元数据 |
|:-----|:-----|:---------|:-----------|
| **L0 — 最小** | `L0` | `executor` | 仅 Frontmatter 增强字段 |
| **L1 — 标准** | `L1` | `analyzer`, `researcher`, `orchestrator`(简单) | + Skill 内 `.meta/GUIDE.md` |
| **L2 — 完整** | `L2` | `generator`, `orchestrator`(复杂) | + 完整工厂记录 |

> **升级原则**：如果一个 `executor` Skill 在实践中发现其设计决策比预期复杂，可以升级到 L1。级别只升不降（不可降级丢弃已有元数据）。

---

## 4. Frontmatter 增强字段（所有级别）

在现有 `SKILL.md` Frontmatter 中新增以下可选字段：

```yaml
---
name: base-skill-generator
description: Stack-agnostic code generation engine...

# === 现有字段（保持不变） ===
metadata:
  version: "2.2"
  freedom_level: medium

# === 新增：认知元层字段 ===
category: generator          # executor | generator | analyzer | orchestrator | researcher
meta_level: L2               # L0 | L1 | L2
maturity: stable             # experimental | stable | deprecated
tags: ["creation", "scaffolding", "meta"]   # 自由标签，用于检索
---
```

### 字段说明

| 字段 | 类型 | 必须 | 说明 |
|:-----|:-----|:-----|:-----|
| `category` | string | L0+ 必须 | 分类标签，决定元层级别和创建时的参考策略 |
| `meta_level` | string | L0+ 推荐 | 当前 Skill 的元数据详尽程度 |
| `maturity` | string | L0+ 推荐 | 成熟度。与 `skill-package-standard.md` 中定义一致 |
| `tags` | list | 可选 | 自由标签，用于语义检索和分组 |

---

## 5. In-Skill 元数据：`.meta/GUIDE.md`（L1+）

**位置**：`<skill-root>/.meta/GUIDE.md`
**受众**：想要修改或优化此 Skill 的人（人类或 AI）
**原则**：只放"修改者需要的"信息，不放工厂历史

### 5.1 模板

```markdown
# <Skill 名称> 修改与优化指南

## 1. 架构速览 (Architecture at a Glance)

> 用 1-2 段话说明这个 Skill 的核心设计思路。不是"做什么"（那是 SKILL.md 的职责），
> 而是"为什么这样做"。

## 2. 修改地图 (Modification Map)

> 列出常见修改场景和应该修改的具体位置。

| 想要改的行为 | 应该修改的文件/位置 | 注意事项 |
|:-------------|:--------------------|:---------|
| 示例：新增一种模板类型 | `assets/templates/<type>/` + `scripts/scaffold.py` 的 type 映射 | 需同步更新 SKILL.md 的参数表 |
| 示例：修改输出格式 | `scripts/core.py` 的 `format_output()` | 注意不要破坏下游 Command 的解析 |

## 3. 优化方向 (Optimization Roadmap)

> 记录已知的不足和可能的改进方向。每条注明发现时间和严重程度。

| 方向 | 描述 | 优先级 | 发现时间 |
|:-----|:-----|:-------|:---------|
| 示例：性能 | 大型项目扫描时 gen.py 较慢 | 低 | 2026-02-15 |
| 示例：覆盖度 | 缺少 Go 语言模板 | 中 | 2026-02-20 |

## 4. 不可动区域 (Invariants)

> 列出修改时绝对不能改动的部分，以及原因。

- 示例：`SKILL.md` 的 Frontmatter `name` 字段不能改（与目录名绑定，被 inventory 索引）
- 示例：`scripts/core.py` 的 `main()` 入口签名不能改（被 Command 直接调用）
```

### 5.2 目录结构

```text
<skill-root>/
├── SKILL.md
├── scripts/
├── assets/
├── tests/
├── README.md
└── .meta/                    # 🆕 认知元层（In-Skill 部分）
    └── GUIDE.md              # 修改指南 + 优化方向
```

> `.meta/` 目录会随 Skill 一起复制到下游项目——这是有意为之的，因为下游维护者同样需要修改指引。

---

## 6. In-Factory 元数据（L2）

**位置**：`_meta/data/skill-meta/<skill-name>/`
**受众**：模板维护者、未来的 AI 训练流水线
**原则**：工厂知识，不复制到下游项目

### 6.1 目录结构

```text
_meta/data/skill-meta/<skill-name>/
├── DESIGN.md                # 设计决策与讨论过程
├── REFERENCES.md            # 创建时参考的资料
├── TRIALS.md                # 试错记录（可选）
└── training-data/           # 结构化训练数据（可选）
    └── decisions.jsonl      # 决策对
```

### 6.2 DESIGN.md 模板

```markdown
# <Skill 名称> 设计记录

## 创建背景
> 为什么需要这个 Skill？解决什么问题？

## 设计讨论
> 按时间线记录关键讨论点。每个讨论点包含：问题、候选方案、选择、理由。

### 讨论 1：<主题>
- **问题**：...
- **方案 A**：... → 理由
- **方案 B**：... → 理由
- **选择**：方案 X，因为...

### 讨论 2：<主题>
...

## 关键设计决策摘要

| 决策点 | 选择 | 替代方案 | 选择理由 |
|:-------|:-----|:---------|:---------|

## 参考的聊天记录
> 如有，标注对话 ID 或日期。
```

### 6.3 REFERENCES.md 模板

```markdown
# <Skill 名称> 参考来源

## 内部参考（项目内）

| 文件 | 参考了什么 | 如何影响设计 |
|:-----|:-----------|:-------------|

## 外部参考

| 来源 | 链接/出处 | 参考了什么 |
|:-----|:----------|:-----------|

## 同类 Skill 参考

| Skill 名称 | 借鉴了什么 | 差异点 |
|:-----------|:-----------|:-------|
```

### 6.4 TRIALS.md 模板

```markdown
# <Skill 名称> 试错记录

> 记录创建或重大修改过程中"走不通的路"，帮助后来者避免重复踩坑。

## 试错 1：<简述>

- **尝试了什么**：...
- **期望结果**：...
- **实际结果**：...
- **失败原因**：...
- **教训**：...
- **日期**：YYYY-MM-DD
```

### 6.5 decisions.jsonl 格式（训练数据）

每行一个 JSON 对象，记录一次设计决策。格式设计兼顾人类可读与机器可解析。

```jsonl
{"id": "001", "skill": "base-skill-generator", "topic": "目录结构层数", "context": "Skill 需要一个标准化的目录结构", "option_a": "5 层：SKILL.md, scripts, assets, tests, README", "option_b": "7 层：增加 references 和 assets 子目录", "chosen": "B", "reason": "references 独立有助于区分'参考文档'和'运行时资源'，assets 子目录（templates/images/data）提供更好的组织性", "date": "2026-02-06", "type": "preference"}
{"id": "002", "skill": "base-skill-generator", "topic": "生成方式", "context": "需要决定 Skill 是手写还是脚本生成", "option_a": "纯手写，用模板文档指导", "option_b": "gen.py 脚本自动生成骨架 + 手动注入灵魂", "chosen": "B", "reason": "Hybrid Generation：骨架保证结构一致性，手动注入保证内容质量。纯手写会导致结构不一致", "date": "2026-02-06", "type": "preference"}
```

**字段说明**：

| 字段 | 类型 | 必须 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 该 Skill 内的决策序号 |
| `skill` | string | 是 | 所属 Skill 名称 |
| `topic` | string | 是 | 决策主题 |
| `context` | string | 是 | 决策背景（为什么需要做这个决策） |
| `option_a` | string | 是 | 候选方案 A |
| `option_b` | string | 是 | 候选方案 B（可扩展 option_c 等） |
| `chosen` | string | 是 | 选择了哪个（A/B/C） |
| `reason` | string | 是 | 选择理由 |
| `date` | string | 是 | 决策日期 |
| `type` | string | 是 | `preference`（偏好）/ `constraint`（约束）/ `tradeoff`（权衡） |

---

## 7. 完整目录结构示例

### L0 Skill（执行型，最小元数据）

```text
base-doc-manager/
├── SKILL.md              # Frontmatter 中增加 category: executor, meta_level: L0
├── scripts/
├── assets/
├── tests/
└── README.md
```

### L1 Skill（分析型，标准元数据）

```text
base-closure-validator/
├── SKILL.md              # category: analyzer, meta_level: L1
├── scripts/
├── assets/
├── tests/
├── README.md
└── .meta/
    └── GUIDE.md          # 修改指南 + 优化方向
```

### L2 Skill（生成型，完整元数据）

```text
base-skill-generator/
├── SKILL.md              # category: generator, meta_level: L2
├── scripts/
├── assets/
├── tests/
├── README.md
└── .meta/
    └── GUIDE.md          # 修改指南 + 优化方向

_meta/data/skill-meta/base-skill-generator/
├── DESIGN.md             # 设计决策与讨论过程
├── REFERENCES.md         # 创建时参考的资料
├── TRIALS.md             # 试错记录
└── training-data/
    └── decisions.jsonl   # 结构化决策对
```

---

## 8. 与 create-skill 的集成

### 创建时（写入）

create-skill 在创建新 Skill 时，应根据判定的 category 和 meta_level：

1. **L0**：在 SKILL.md Frontmatter 中自动填入 `category` 和 `meta_level`
2. **L1**：额外创建 `.meta/GUIDE.md`（使用模板，标注"待填写"）
3. **L2**：额外创建 `_meta/data/skill-meta/<name>/` 目录及模板文件

### 创建时（读取 — 学习型工厂）

create-skill 在创建前，应执行以下检索流程：

```
1. 分析需求 → 判断 category 标签
2. 扫描 _meta/data/skill-meta/ 下同 category 的 Skill
3. 读取最佳范例的 DESIGN.md 和 GUIDE.md
4. 将范例作为 few-shot 上下文注入创建流程
5. 创建完成后，记录本次创建的设计过程为新的元数据
```

---

## 9. 治理规则

1. **创建时必须声明 category**：新 Skill 的 Frontmatter 中 `category` 为必填
2. **L2 Skill 修改后必须更新 GUIDE.md**：修改了 L2 Skill 的代码/逻辑后，检查 GUIDE.md 是否需要同步更新
3. **设计讨论不可删除**：`_meta/data/skill-meta/*/DESIGN.md` 只追加不删除（Append-only）
4. **训练数据格式不可随意变更**：`decisions.jsonl` 的 schema 变更需要在本规范中更新
5. **向下兼容**：已有 Skill 无需立即适配，按需渐进式添加元数据

---

## 10. 门禁检查（建议）

| 场景 | 检查项 |
|:-----|:-------|
| 新建 Skill | Frontmatter 包含 `category` 字段 |
| 新建 L1+ Skill | `.meta/GUIDE.md` 存在 |
| 新建 L2 Skill | `_meta/data/skill-meta/<name>/DESIGN.md` 存在 |
| 修改 L2 Skill | GUIDE.md 的"优化方向"或"修改地图"已更新 |

> 上述检查可集成到 `base-closure-validator` 的检查流程中。
