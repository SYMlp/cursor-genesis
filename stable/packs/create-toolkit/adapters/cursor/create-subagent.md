---
description: Cursor 薄入口；通过公共 create-subagent-workflow 创建 Agent Contract，再渲染 Cursor agent 定义。
---

# /create-subagent · Cursor Adapter

本文件只负责 Cursor 的类型路由、具体 model ID 选择、`.cursor/agents` 渲染和 Role Injection 示例。公共控制流由：

`@.agents/skills/create-subagent-workflow/SKILL.md`

统一定义。

## 1. 类型路由

- 单一确定性动作 → `/create-skill`。
- 固定线性 SOP → `/create-command`。
- 需要自主推理、搜索、判断或隔离大量中间过程 → 继续创建 Subagent。

## 2. 建立分析 Gate

初始化后，必须完成能力拆分：

- 哪些原子能力已经是 `.agents/skills/<name>/SKILL.md`；
- 缺失能力是否应先走 `create-skill-workflow`；
- 中间过程为什么应该与调用方隔离；
- 需要 exploration / balanced / execution / synthesis 中哪种抽象模型画像。

不要在公共 Agent Contract 中写 Cursor model ID。

## 3. 生成并校验公共契约

按公共 Skill 的 `init → analyzed → run → refined → run` 流程执行。机器检查失败时必须根据 state 中的依赖报告或校验报告修复并显式 `retry`。

公共产物是：

`.agents/agents/<scope>-<name>.md`

它是作者源，不是 Cursor 原生 Agent 文件。

## 4. 渲染 Cursor adapter

从当前 Cursor 运行时确认一个真实可用的 model ID，再运行：

```powershell
python .cursor/adapters/create-subagent/render_subagent.py `
  --project-root . `
  --contract .agents/agents/<scope>-<name>.md `
  --model <current-cursor-model-id>
```

Renderer 会先调用公共 Validator，拒绝无效契约、路径越界和覆盖已有 `.cursor/agents/<name>.md`。

## 5. 闭合 Workflow

```powershell
python .agents/skills/create-subagent-workflow/scripts/workflow.py resume `
  --state docs/state/create-subagent/<name>.json `
  --event adapted `
  --adapter cursor `
  --artifact .cursor/agents/<scope>-<name>.md `
  --note "Cursor adapter rendered from shared Agent Contract"
```

## 6. Cursor 调用示例

Cursor 当前需要 Role Injection 时，只在本适配层使用宿主语法：

```text
Task(
  subagent_type = "generalPurpose",
  prompt = """
  Read and adopt `.cursor/agents/<scope>-<name>.md`.
  Mission: <task>
  Return only the evidence and summary required by its Verification Contract.
  """
)
```

如果当前 Cursor 运行时已提供不同的原生 Agent 调用方式，以运行时事实为准；不要回写污染公共 Agent Contract。
