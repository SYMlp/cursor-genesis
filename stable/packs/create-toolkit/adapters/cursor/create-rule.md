---
description: Cursor 薄入口；通过公共 create-rule-workflow 把 Rule 登记到 AGENTS.md，再按需渲染 .cursor/rules 投影。
---

# /create-rule · Cursor Adapter

本入口只负责 Cursor 操作入口和 `.mdc` 激活格式。公共 Rule 类型判断、状态、Validator、Human Gate 与 `AGENTS.md` 登记由：

`@.agents/skills/create-rule-workflow/SKILL.md`

统一定义。

## 1. 先做类型判断

- 必须常驻或条件生效的薄行为约束 → Rule。
- 多步固定 SOP → `/create-command`。
- 按需操作知识 → `/create-skill`。
- 自主判断或探索 → `/create-subagent`。

不要把模板、长决策表或完整工作流塞进 Rule。

## 2. 运行公共 Workflow

按公共 Skill 完成 `init → analyze → scaffold → refine → validate`，审阅 diff 后使用：

```powershell
python .agents/skills/create-rule-workflow/scripts/register_rule.py `
  --project-root . `
  --rule-file docs/state/create-rule/drafts/<name>.md `
  --agents-file AGENTS.md `
  --confirm-id <name>
```

登记后恢复 `registered` Gate。`AGENTS.md` 是唯一公共作者源，不在 `.cursor/rules` 手写另一份正文。

## 3. 渲染 Cursor Project Rule

```powershell
python .cursor/adapters/create-rule/render_rule.py `
  --project-root . `
  --agents-file AGENTS.md `
  --rule-id <name>
```

映射：

| 公共 Activation | Cursor 投影 |
|:---|:---|
| `always` | `alwaysApply: true` |
| `paths` | Auto Attached；当前 renderer 只接受一个 glob |
| `intent` | description 驱动的 Agent Requested |
| `manual` | 无 description / glob 的 Manual rule |

多个公共 path glob 不会被猜测性拼接；请拆成独立 Rule 或等待经过实测的 adapter 升级。

## 4. 记录真实适配产物

```powershell
python .agents/skills/create-rule-workflow/scripts/workflow.py resume `
  --state docs/state/create-rule/<name>.json `
  --event adapted `
  --adapter cursor `
  --artifact .cursor/rules/<name>.mdc `
  --note "Cursor projection rendered and reviewed"
```

Renderer 会拒绝无效 block、路径越界、同名覆盖和未验证的多 glob 映射。
