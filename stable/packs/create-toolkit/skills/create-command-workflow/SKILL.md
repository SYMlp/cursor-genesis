---
name: create-command-workflow
description: 创建、恢复或重试一个跨宿主 Command Contract 时使用；把用户结果、依赖 Skill/Agent、有序 SOP、Human Gate、失败恢复和验收契约写入公共作者层，再由各宿主 adapter 生成具体操作入口。
metadata:
  version: "1.0.0"
category: orchestrator
meta_level: L1
maturity: stable
tags: ["command-contract", "workflow", "state-persistence", "validator", "human-gate", "multi-host"]
---

# Create Command Workflow

工具无关的 Command Contract 创建工作流。公共契约写入项目 `.agents/commands/`；该目录是作者层，不代表任何宿主会原生发现其中的斜杠命令。

## 适用边界

- 适用：用户反复执行同一个固定顺序 SOP，步骤和终止条件可显式表达。
- 不适用：单一确定性动作应创建 Skill；需要自主判断或探索的整体任务应创建 Agent。
- Command 可以依赖 Agent，但分支判断属于 Agent Contract，不能藏在 Command 的路由中。

## Workflow

```text
analyze（Human / Agent Gate）
  → dependencies（机器 Guard）
  → scaffold（确定性动作）
  → refine（Human / Agent Gate）
  → validate（机器 Validator）
  → adapt（Human / Adapter Gate）
  → complete
```

依赖 Guard 只接受公共作者层资产：

- Skill：`.agents/skills/<name>/SKILL.md`
- Agent：`.agents/agents/<name>.md`

缺失依赖时，调用方应分别使用 `create-skill-workflow` 或 `create-subagent-workflow` 创建，随后显式重试。

## 接口

**运行器**：`scripts/workflow.py`

| 子命令 | 作用 |
|:---|:---|
| `init` | 建立状态文件并停在 SOP 分析 Gate |
| `resume --event analyzed` | 写入依赖、风险等级和组合说明 |
| `run` | 执行依赖检查、脚手架或 Validator，直到下一个 Gate / 失败 / 完成 |
| `resume --event refined` | 确认公共 Command Contract 已完成 |
| `retry` | 重试依赖检查或机器校验 |
| `resume --event adapted` | 记录真实存在的宿主入口 |
| `status` | 输出完整持久化状态 |

退出码：

- `0`：成功推进或完成；
- `2`：等待 Human / Agent / Adapter Gate；
- `3`：机器检查失败但可重试；
- `4`：阻塞、事件非法或重试耗尽。

## 标准执行

```powershell
python <skill-dir>/scripts/workflow.py init `
  --state docs/state/create-command/review.json `
  --project-root . `
  --name review `
  --description "Run a repeatable change-review SOP" `
  --outcome "Return verified findings and unresolved risks"

python <skill-dir>/scripts/workflow.py resume `
  --state docs/state/create-command/review.json `
  --event analyzed `
  --risk-level low `
  --skill base-diff-loader `
  --agent base-reviewer `
  --composition-note "Load deterministically, isolate review reasoning, verify the returned evidence" `
  --note "SOP decomposition completed"

python <skill-dir>/scripts/workflow.py run `
  --state docs/state/create-command/review.json

# 编辑 .agents/commands/review.md，Workflow 必须为 1–7 个有序步骤，最后一步是验证
python <skill-dir>/scripts/workflow.py resume `
  --state docs/state/create-command/review.json `
  --event refined `
  --note "Command Contract completed"

python <skill-dir>/scripts/workflow.py run `
  --state docs/state/create-command/review.json

python <skill-dir>/scripts/workflow.py resume `
  --state docs/state/create-command/review.json `
  --event adapted `
  --adapter cursor `
  --artifact .cursor/commands/review.md `
  --note "Cursor command rendered and verified"
```

## 不变量

- 公共 Contract 不包含 `.cursor/commands`、`.claude/commands`、`Task(...)` 或 `subagent_type`。
- Workflow 必须有 1–7 个连续编号步骤，最后一步必须显式验证。
- 依赖必须存在且在契约正文中有绑定；不能用隐式宿主上下文补洞。
- 高风险 SOP 必须声明 Human Gate。
- 已存在的公共契约或宿主入口不会被覆盖。
- 所有 Gate 由显式事件通过；状态不写入宿主 memory。

## Verification

```powershell
python -m unittest discover `
  -s <skill-dir>/tests `
  -p "test_*.py"
```

## Context & Side Effects

- 读取：项目 `.agents/skills/`、`.agents/agents/` 中声明的依赖。
- 写入：调用方指定的状态 JSON、`.agents/commands/<name>.md`。
- 外部调用：无。
- 宿主入口由 adapter 单独生成；公共 Workflow 只记录已经存在的适配产物。
