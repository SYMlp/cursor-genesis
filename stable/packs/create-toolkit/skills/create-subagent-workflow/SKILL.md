---
name: create-subagent-workflow
description: 创建、恢复或重试一个跨宿主 Agent Contract 时使用；把职责、上下文隔离、依赖 Skill、抽象模型画像和验收契约写入公共作者层，再由 Cursor、Claude Code 或 Codex 的薄适配器选择具体运行格式。
metadata:
  version: "1.0.0"
category: orchestrator
meta_level: L1
maturity: stable
tags: ["agent-contract", "workflow", "state-persistence", "validator", "context-isolation", "multi-host"]
---

# Create Subagent Workflow

工具无关的 Agent Contract 创建工作流。公共契约写入项目 `.agents/agents/`；该目录是作者层，不代表任何宿主会原生发现其中的 Agent。

## 适用边界

- 适用：任务需要自主推理、搜索或判断，并应在隔离上下文中执行。
- 不适用：单一确定性动作应创建 Skill；固定线性 SOP 应创建 Command / Workflow。
- 本 Skill 生成 Agent Contract，不注册宿主原生 Agent，也不静态承诺某个模型 ID 长期可用。

## Workflow

```text
analyze（Human / Agent Gate）
  → dependencies（机器检查）
  → scaffold（确定性动作）
  → refine（Human / Agent Gate）
  → validate（机器 Validator）
  → adapt（Human / Adapter Gate）
  → complete
```

依赖检查只确认 `.agents/skills/<name>/SKILL.md` 是否存在。缺失依赖时，调用方应先使用 `create-skill-workflow` 创建，随后显式重试。

## 接口

**运行器**：`scripts/workflow.py`

| 子命令 | 作用 |
|:---|:---|
| `init` | 建立状态文件并停在能力分析 Gate |
| `resume --event analyzed` | 写入依赖 Skill、模型画像和隔离说明 |
| `run` | 执行依赖检查、脚手架或 Validator，直到下一个 Gate / 失败 / 完成 |
| `resume --event refined` | 确认公共 Agent Contract 已完成 |
| `retry` | 重试依赖检查或机器校验 |
| `resume --event adapted` | 记录真实存在的宿主适配产物 |
| `status` | 输出完整持久化状态 |

退出码沿用 Create Toolkit 约定：

- `0`：成功推进或完成；
- `2`：等待 Human / Agent / Adapter Gate；
- `3`：机器检查失败但可重试；
- `4`：阻塞、事件非法或重试耗尽。

## 标准执行

```powershell
# 1. 初始化：此时尚未假装完成能力拆分
python <skill-dir>/scripts/workflow.py init `
  --state docs/state/create-subagent/reviewer.json `
  --project-root . `
  --name reviewer `
  --scope base `
  --description "Review changes and return evidence-backed findings" `
  --goal "Find correctness and maintainability risks"

# 2. 显式提交分析结果；--skill 可重复，也可以不声明依赖
python <skill-dir>/scripts/workflow.py resume `
  --state docs/state/create-subagent/reviewer.json `
  --event analyzed `
  --model-profile synthesis `
  --skill base-code-search `
  --isolation-note "Search traces are noise to the caller" `
  --note "Capability decomposition completed"

# 3. 检查依赖并生成 .agents/agents/base-reviewer.md
python <skill-dir>/scripts/workflow.py run `
  --state docs/state/create-subagent/reviewer.json

# 4. 编辑契约，补全 Identity / Workflow / Constraints / Verification Contract
python <skill-dir>/scripts/workflow.py resume `
  --state docs/state/create-subagent/reviewer.json `
  --event refined `
  --note "Agent contract completed"

# 5. 执行机器 Validator
python <skill-dir>/scripts/workflow.py run `
  --state docs/state/create-subagent/reviewer.json

# 6. 宿主 adapter 生成真实产物后闭合
python <skill-dir>/scripts/workflow.py resume `
  --state docs/state/create-subagent/reviewer.json `
  --event adapted `
  --adapter cursor `
  --artifact .cursor/agents/base-reviewer.md `
  --note "Cursor adapter rendered and verified"
```

## 不变量

- 公共契约使用抽象 `model_profile`，具体 model ID 只能由宿主 adapter 选择。
- 公共契约不得包含 `.cursor/agents`、`.claude/agents`、`Task(...)` 或 `subagent_type`。
- Agent Contract 必须自带 Identity、Workflow、Constraints 与 Verification Contract，不能假设父 Agent 的 Rules 会自动传入隔离上下文。
- 已存在的公共契约或宿主适配产物不会被覆盖。
- 所有 Gate 必须由显式事件通过；状态不会写入宿主 memory。

## Verification

```powershell
python -m unittest discover `
  -s <skill-dir>/tests `
  -p "test_*.py"
```

## Context & Side Effects

- 读取：项目 `.agents/skills/` 中声明的依赖。
- 写入：调用方指定的状态 JSON、`.agents/agents/<name>.md`。
- 外部调用：无。
- 宿主文件由 adapter 单独生成；公共 Workflow 只记录已经存在的适配产物。
