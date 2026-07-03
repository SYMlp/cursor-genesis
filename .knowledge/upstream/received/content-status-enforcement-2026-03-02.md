# 上游下达：内容确认状态管理规范 + 个人认知系统新场景

> 来源：knowledge-graph 推导
> 推导记录：meta/derivation/content-confirmation-status-2026-03-02.md
> 规范位置：meta/spec.md §八
> 下达时间：2026-03-02
> 状态：待 cursor-genesis 消化处理

---

## 一、规范核心（knowledge-graph 已落地）

### 1.1 原则

knowledge-graph 新增了内容确认状态管理规范：**AI 可以写入内容，但内容能否被用作推导基础、检索结果、输出素材，取决于用户是否确认**。

推导依据：
- `subjective-irreducibility`：知识判断的终审权在主体
- `automation/human-judges-root`：根事实识别只能由人完成
- `knowledge-decay`：确认状态必须持久化，不能只存在于对话流程中

### 1.2 状态定义

| 状态 | 含义 | 可用于推导/输出 |
|:---|:---|:---|
| `draft` | AI 生成，用户未审阅 | 否 |
| `candidate` | 经分析，等待用户终审 | 否 |
| `confirmed` | 用户已确认 | 是 |
| `deprecated` | 已过时 | 否 |

### 1.3 已创建的 Cursor Rule

knowledge-graph 中已创建 `.cursor/rules/content-status-enforcement.mdc`，约束 Agent 在 ingestion/derivation 时遵循状态管理。

---

## 二、对 cursor-genesis 的意义

### 2.1 新使用场景：个人认知系统管理

cursor-genesis 原来的定位是"面向程序员开发协作的 Cursor 组件生产"。现在用户在实践中发现了一个新场景：**个人认知系统管理**。

| 维度 | 开发协作场景 | 个人认知系统场景 |
|:---|:---|:---|
| 目标 | 代码质量、开发效率 | 知识质量、认知准确性 |
| 操作对象 | 代码文件 | YAML/Markdown 知识文件 |
| 核心约束 | 编译通过、测试通过 | 用户确认、根事实可追溯 |
| Rule 侧重 | 编码规范、架构守护 | 内容状态管控、ingestion/derivation 流程 |
| 用户角色 | 开发者 | 知识管理者（可以是同一人） |

### 2.2 场景特征

个人认知系统管理场景有以下特征，与开发场景不同：

1. **有理论设计**：基于根事实推导，不是经验堆砌
2. **有实践方式**：ingestion/derivation/search/assemble 工具链
3. **能推广使用**：任何人都可以用同样的架构管理个人认知
4. **状态敏感**：内容的"可用性"由主体确认决定，不是由编译器决定

### 2.3 建议处理方向

cursor-genesis 可自主决定如何处理，以下是参考建议：

**短期**：
- 将 `content-status-enforcement.mdc` 作为一个 rule atom 纳入管理
- 在 atoms/rules/ 中归类为"个人认知系统"类别

**中期**：
- 考虑是否需要一个新的 pack（如 `packs/knowledge-manage/personal-cognition/`），面向使用个人认知系统的用户
- 该 pack 包含：内容状态管理 rule + ingestion/derivation 提示词 + GM 角色 rule

**远期**：
- 如果"个人认知系统管理"成为一个成熟场景，可能需要独立的团队编排模式（类似 v1-talk 的 6 种团队）
- 知识管理者角色的 capability 设计

---

## 三、回流的内容清单

| 内容 | 来源 | 用途 |
|:---|:---|:---|
| `.cursor/rules/content-status-enforcement.mdc` | knowledge-graph 实践产物 | 可提炼为 rule atom |
| `.cursor/rules/cognitive-gm.mdc` | knowledge-graph 角色定义 | 可提炼为 standalone role |
| `.cursor/rules/session-narrative.mdc` | knowledge-graph 叙事规范 | 可提炼为 rule atom |
| `.cursor/prompts/knowledge-ingestion.md` | 加工流程 | 可提炼为 command 或 skill |
| `.cursor/prompts/knowledge-derivation.md` | 推导流程 | 可提炼为 command 或 skill |
| `.cursor/prompts/first-principles-training.md` | 训练流程 | 可提炼为 command 或 skill |

以上内容都是 knowledge-graph 在实践中产生的 Cursor 组件，本质上属于 cursor-genesis 的管理范围，但因为是在 knowledge-graph 中直接使用而就地创建的。

cursor-genesis 可根据 `flexible-governance` 原则自主决定是否纳入、如何组织。
