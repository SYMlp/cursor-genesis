---
description: Cursor 薄入口；通过公共 create-command-workflow 创建 Command Contract，再渲染 Cursor 斜杠命令。
---

# /create-command · Cursor Adapter

本文件只负责 Cursor 的类型路由、`.cursor/commands` 渲染和 Agent Role Injection 绑定。公共控制流由：

`@.agents/skills/create-command-workflow/SKILL.md`

统一定义。

## 1. 类型路由

- 单一确定性动作 → `/create-skill`。
- 整体需要自主探索、判断或隔离上下文 → `/create-subagent`。
- 用户反复执行相同的固定顺序 SOP → 继续创建 Command。

## 2. 建立分析 Gate

初始化后必须明确：

- 用户最终得到什么；
- 所需 `.agents/skills` 与 `.agents/agents` 依赖；
- SOP 风险等级和 Human Gate；
- 1–7 个有序步骤，最后一步必须验证。

缺失依赖必须先用公共 create-skill / create-subagent Workflow 创建。

## 3. 生成并校验公共契约

按公共 Skill 的 `init → analyzed → run → refined → run` 流程执行。公共产物是：

`.agents/commands/<name>.md`

它是作者源，不是 Cursor 原生斜杠命令。

## 4. 渲染 Cursor adapter

若 Contract 依赖 Agent，必须先确认相应 `.cursor/agents/<name>.md` 已由 Cursor subagent renderer 生成，再运行：

```powershell
python .cursor/adapters/create-command/render_command.py `
  --project-root . `
  --contract .agents/commands/<name>.md
```

Renderer 会调用公共 Validator，拒绝依赖缺失、路径越界和覆盖已有命令，并在 Cursor 产物末尾生成 Agent Role Injection bindings。

## 5. 闭合 Workflow

```powershell
python .agents/skills/create-command-workflow/scripts/workflow.py resume `
  --state docs/state/create-command/<name>.json `
  --event adapted `
  --adapter cursor `
  --artifact .cursor/commands/<name>.md `
  --note "Cursor command rendered from shared Command Contract"
```

具体斜杠触发方式、`Task(...)` 语法和 Cursor Agent 文件路径只能存在于本适配层，不能回写公共 Contract。
