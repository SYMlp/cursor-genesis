---
name: base-research-planner
description: Distills vague user input (descriptions, voice transcripts, context dumps) into a clear research intent, then generates a structured execution plan. Use when the user asks for deep research, topic exploration, or provides raw material that needs to be turned into an actionable research plan.
metadata:
  version: "2.0"
  freedom_level: high
scope: base
package:
  id: base-research-planner
  version: "2.0.0"
  maturity: stable
  owner: "template-maintainers"
  tags: ["research", "planning", "intent-extraction", "requirement-distillation"]
platform:
  runtimes: ["cursor"]
io_contract:
  inputs:
    - name: user_input
      type: string
      required: true
      description: "用户原始输入：可能是明确问题、模糊描述、语音转录文本、或上下文材料"
    - name: context_material
      type: string
      required: false
      description: "附加上下文材料：如与其他 AI 的对话记录、会议纪要、需求文档片段"
    - name: depth_preference
      type: string
      required: false
      description: "广度优先 | 深度优先（默认由 Planner 根据输入判断）"
  outputs:
    - name: research_brief
      type: object
      required: true
      description: "提炼后的调研简报（含意图、核心问题、边界）"
    - name: research_plan
      type: object
      required: true
      description: "结构化调研计划（含 Tasks、Queries、Success Criteria）"
max_response_tokens: 4000
---

# Skill: Base Research Planner

## 目标

把用户的**原始输入**（不论多模糊）转化为可执行的 **Research Plan**（调研计划书）。

关键能力：先**听懂用户到底想干什么**，再设计"如何回答问题"的路径。

## 输入类型识别

用户输入不一定是清晰的调研题目。Planner 必须先判断输入属于哪种类型，再选择对应的处理策略。

### Type A: 明确问题

用户直接给出了具体调研主题或问题列表。

**特征**：有明确的主语和动词，如"调研 X"、"对比 A 和 B"、"总结这 10 篇论文"。

**处理**：跳过提炼，直接进入计划生成。

**示例**：
- "帮我调研 2026 年 AI Agent 架构趋势"
- "对比 Kafka、RabbitMQ、Pulsar 的优劣"
- "总结 Anthropic 的 15 篇核心论文"

### Type B: 模糊描述

用户有想法但说不清楚，给出一段散漫的描述。

**特征**：长段落、多个发散方向、没有明确的"请帮我做 X"、可能自相矛盾。

**处理**：执行 Phase 0 需求提炼 → 输出调研简报 → 请用户确认 → 再生成计划。

**示例**：
- "我最近在想能不能把我们的单体应用拆成微服务，但又觉得团队太小了可能搞不定，而且现在性能问题主要在数据库那边，不知道是不是该先优化数据库还是直接上微服务..."
- "我想做个 AI 产品，大概是让用户跟 AI 聊天然后自动帮他们整理笔记，但不确定市面上有没有类似的，也不确定技术上该用什么方案"

### Type C: 上下文材料 / 对话记录

用户提供了与其他 AI 的语音聊天转录、会议纪要、或者一段别人写的需求描述，让你基于这些材料去调研。

**特征**：对话体（"我说...他说..."）、多人讨论、有大量背景信息但缺乏聚焦的 action item。

**处理**：执行 Phase 0 需求提炼（从材料中萃取意图和关键问题） → 输出调研简报 → 请用户确认 → 再生成计划。

**示例**：
- "这是我跟 ChatGPT 聊了半小时的记录，帮我整理一下然后深入调研里面提到的几个方向"
- "这是今天产品会的纪要，帮我把里面的技术选型问题拎出来做个调研"
- "朋友推荐了几个框架，我记了个语音备忘录，你看看帮我对比一下"

### Type D: 混合型

用户给了一些上下文材料，同时也表达了模糊的意图。

**处理**：同 Type C，但额外关注用户自己表达的意图（权重高于材料中的信息）。

## Phase 0: 需求提炼（仅 Type B/C/D 触发）

当输入不够明确时，Planner 必须先执行这一步。

### 提炼流程

1. **通读全部输入**：包括用户的描述和任何附加的上下文材料。
2. **萃取意图**：
   - 用户**想解决什么问题**？（痛点）
   - 用户**想达到什么目标**？（期望）
   - 用户**提到了哪些关键词/概念**？（锚点）
   - 用户**明确排除了什么**？（边界）
3. **识别分歧与矛盾**：如果用户的描述中有自相矛盾的地方，列出来。
4. **提炼为调研简报**（Research Brief）。

### 调研简报模板（Research Brief）

```markdown
## 调研简报

### 输入类型
{Type B: 模糊描述 / Type C: 上下文材料 / Type D: 混合型}

### 用户核心意图（1-2 句话）
{用一句话概括用户到底想搞清楚什么}

### 提炼出的核心问题
1. {Q1: 最重要的问题}
2. {Q2: 次重要的问题}
3. {Q3: ...}

### 关键约束 / 偏好
- {从输入中识别的约束，如"团队规模小"、"预算有限"、"偏好 Python"}

### 信息缺口（需用户补充）
- {Planner 无法从输入中推断的关键信息}

### 矛盾点（如有）
- {用户描述中自相矛盾的地方}

### 建议调研方向
1. {Direction 1}
2. {Direction 2}
```

### 确认机制

Phase 0 的输出（调研简报）**必须返回给主 Agent / 用户确认**，再进入 Phase 1 计划生成。
原因：模糊输入的理解可能偏差大，必须让用户看到"我理解你想做这件事"并确认。

## Phase 1: 计划生成（所有类型）

确认调研方向后，将核心问题转化为可执行的调研计划。

### 工作流

1. **知识图谱预判**：基于现有知识，列出该主题可能的关键子领域。
2. **输入分类**：
   - **列表类任务**（如"15 篇文章"、"10 个竞品"）：生成 N 个并行的阅读/搜索任务。
   - **探索类任务**（如"架构趋势"、"技术选型"）：生成"搜索 → 阅读 → 发现新词 → 再搜索"的迭代路径。
   - **对比类任务**（如"A vs B vs C"）：生成维度矩阵 + 按维度搜索的任务。
3. **策略选择**：
   - **广度优先**（快速扫盲）：关注定义、主要流派、关键人物。适合用户对领域完全陌生。
   - **深度优先**（专家视角）：关注底层原理、源码实现、论文细节。适合用户已有基础知识。
4. **输出计划**：供 Executor 执行。

### 调研计划模板（Research Plan）

```markdown
# Research Plan: {Topic}

## 0. 调研简报摘要
{如果经过了 Phase 0，在这里附上简报的核心结论}

## 1. 核心问题拆解
- Q1: ...
- Q2: ...
- Q3: ...

## 2. 调研路径（Execution Path）

### Phase 1: 广度搜索
- **Query**: "..."
- **Target**: 维基百科 / 官方文档概览
- **Goal**: 确定核心术语定义

### Phase 2: 深度挖掘（循环执行）
- **Task 1**: 针对 Q1 进行专项搜索
  - Query: "..."
  - Source: Arxiv / GitHub Issues / 官方文档
  - Focus: {关注什么}
  - Success Criteria: {怎样算搜到了}
- **Task 2**: 针对 Q2 进行专项搜索
  - ...

## 3. 预期产物结构
- 最终报告应包含：{根据调研类型定制}
```

## 约束

- **只规划，不执行**：不要自己去搜索，只生成搜索关键词和策略。
- **任务粒度**：每个 Task 应该是 Executor 可以单次执行的（如"搜索 X 并总结"）。
- **Type B/C/D 必须先提炼**：不允许跳过 Phase 0 直接生成计划——理解偏差比计划不完美代价更大。
- **尊重原始表达**：提炼时要尽量保留用户原话中的关键词，不要过度抽象化。
