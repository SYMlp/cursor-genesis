# Model Selection Guide (Subagent 模型选型参考)

> **用途**：创建 Subagent 时，必须在 Frontmatter 中显式指定 `model` 字段。本指南提供选型依据。
> **引用**：`base-skill-generator` SKILL.md 的 Phase 1 必读；`standard-subagent.md` 模板。

## 1. 可选模型 ID（Cursor 可用）

创建 Subagent 时，`model` 字段必须使用以下之一（或运行环境支持的其他有效 ID）：

| 模型 ID | 说明 |
| :------ | :--- |
| `gemini-3-pro` | 高发散、战略探索型 |
| `claude-4.6-opus-high-thinking` | 稳定综合决策型 |
| `claude-4.5-sonnet-thinking` | 综合决策型（成本较 Opus 低） |
| `composer-1.5` | 严格执行与审计型 |
| `gpt-5.2` | 高发散、高执行稳定性 |

## 2. 能力矩阵（选型依据）

| 模型 | 发散能力 | 执行稳定性 | 审计能力 | 修辞风险 | 成本效率 |
| :--- | :------- | :--------- | :------- | :------- | :------- |
| GPT-5.2 | 高 | 高 | 高 | 低中 | 中 |
| Claude Opus | 中高 | 极高 | 极高 | 低 | 低（贵） |
| Gemini 3 Pro | 极高 | 中 | 中 | 中高 | 中 |
| Composer 1.5 | 低 | 高 | 高 | 极低 | 高 |
| 豆包 | 中 | 中 | 低中 | 中 | 高 |
| 千问 | 中高 | 中高 | 中高 | 低中 | 高 |
| Kimi 2.5 | 中 | 中高 | 中 | 中 | 高 |

## 3. 角色定位映射（快速选型）

| 模型 | 正确定位 |
| :--- | :------- |
| Gemini 3 Pro | 高发散战略探索型（规划、头脑风暴、多方案） |
| Composer 1.5 | 严格执行与审计型（检索、落盘、逐项执行） |
| Claude Opus / Sonnet | 稳定综合决策型（汇总、架构、最终决策） |

## 4. Subagent 典型映射

| Subagent 角色 | 推荐 model | 理由 |
| :------------ | :--------- | :--- |
| Planner / 规划者 | `gemini-3-pro` | 需要发散、探索路径、不急于结论 |
| Executor / 执行者 | `composer-1.5` | 需要稳定执行、低成本、高吞吐 |
| Synthesizer / 综合者 | `claude-4.6-opus-high-thinking` 或 `gpt-5.2` | 需要大上下文、强综合、低修辞风险 |

## 5. Frontmatter 示例

```yaml
---
name: base-research-executor-agent
description: [Subagent] Research Executor. Executes specific research tasks...
model: composer-1.5   # 必须显式指定，不可省略或写 fast/slow
globs: ["**/*.md", "**/*.json"]
---
```
