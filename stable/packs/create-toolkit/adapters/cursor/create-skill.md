---
description: Cursor 薄入口；把创建 Skill 请求交给 .agents 作者层的持久化 create-skill-workflow。
---

# /create-skill · Cursor Adapter

本文件只负责 Cursor 的显式命令入口。状态机、骨架生成、机器校验和重试语义由：

`@.agents/skills/create-skill-workflow/SKILL.md`

统一定义。不要在本 adapter 复制工作流正文。

## 1. 先做类型路由

- 单一、可复用的能力单元 → 继续创建 Skill。
- 多步固定 SOP → 路由 `/create-command`。
- 需要自主调研、判断或隔离上下文 → 路由 `/create-subagent`。

## 2. 初始化并生成骨架

根据用户需求确定 `name`、`scope`、`description`、`category`，然后运行：

```powershell
python .agents/skills/create-skill-workflow/scripts/workflow.py init `
  --state docs/state/create-skill/<name>.json `
  --project-root . `
  --name <name> `
  --scope <scope> `
  --description "<description>" `
  --category <category>

python .agents/skills/create-skill-workflow/scripts/workflow.py run `
  --state docs/state/create-skill/<name>.json
```

默认产物位于 `.agents/skills/<scope>-<name>/`，由 Cursor、Claude Code、Codex CLI 共用。

## 3. 通过 refine gate

读取生成的 `SKILL.md`，补全实际 Workflow、Verification、Context & Side Effects；不得留下 `TODO`。

```powershell
python .agents/skills/create-skill-workflow/scripts/workflow.py resume `
  --state docs/state/create-skill/<name>.json `
  --event refined `
  --note "Skill workflow and verification completed"
```

## 4. 执行 Validator 与重试

```powershell
python .agents/skills/create-skill-workflow/scripts/workflow.py run `
  --state docs/state/create-skill/<name>.json
```

退出码 `3` 表示可修复重试：根据 state 中的 `validation_report` 修正后运行 `retry`，再运行 `run`。退出码 `4` 表示已阻塞，不能绕过。

## 5. 注册并完成

若项目有资产清单且存在可验证的登记机制，按该项目自己的 registry / manifest 更新方式完成登记；不要假定某个 legacy Cursor updater 已安装。没有登记机制时必须明确记录“不需要登记”，不能假装已经执行。

```powershell
python .agents/skills/create-skill-workflow/scripts/workflow.py resume `
  --state docs/state/create-skill/<name>.json `
  --event registered `
  --note "Added to project inventory"
```

没有资产清单时改用：

```powershell
python .agents/skills/create-skill-workflow/scripts/workflow.py resume `
  --state docs/state/create-skill/<name>.json `
  --event registration-not-required `
  --note "Project has no Skill inventory"
```
