---
name: create-skill-workflow
description: 创建或重试一个跨 Cursor、Claude Code、Codex CLI 共用的项目 Skill 时使用；以持久化状态驱动 scaffold、refine、validate、register 五阶段，并在机器校验与人工门之间安全恢复。
metadata:
  version: "1.0.0"
category: orchestrator
meta_level: L1
maturity: stable
tags: ["creation", "workflow", "state-persistence", "validator", "human-gate", "multi-host"]
---

# Create Skill Workflow

工具无关的 Skill 创建工作流。公共产物写入项目 `.agents/skills/`；Cursor、Claude Code、Codex CLI 的入口只负责触发，不复制本工作流。

## 适用边界

- 适用：创建一个已确认属于 Skill 的可复用能力，并要求阶段、失败和重试可追踪。
- 不适用：需要自主调研/判断的 Agent，或多个能力编排而成的产品级 Workflow。
- 本 Skill 不替用户或 Agent 做类型判断；入口适配器必须先完成类型路由。

## 控制流

```text
scaffold
  → refine（Human / Agent Gate）
  → validate（机器 Validator）
  → register（Human / Adapter Gate）
  → complete
```

状态保存在调用方明确指定的 JSON 文件中。运行器不会把进度写入宿主 memory。

## 接口

**运行器**：`scripts/workflow.py`

| 子命令 | 作用 |
|:---|:---|
| `init` | 创建状态文件，记录 Skill 规格、输出根和重试上限 |
| `run` | 从当前阶段执行到下一个 Gate、失败或完成 |
| `resume` | 用 `refined` / `registered` / `registration-not-required` 事件通过 Gate |
| `retry` | 在机器校验失败且未超上限时重新进入 validate |
| `status` | 输出当前持久化状态 |

**Validator**：`scripts/validate_skill.py`

```powershell
python <skill-dir>/scripts/validate_skill.py --skill-dir <created-skill-dir> --json
```

退出码：

- `0`：校验通过或状态成功推进；
- `2`：工作流正在等待 Gate；
- `3`：校验失败但仍可重试；
- `4`：状态被阻塞、事件非法或重试次数耗尽。

## 标准执行

```powershell
# 1. 初始化状态
python <skill-dir>/scripts/workflow.py init `
  --state docs/state/create-skill/example.json `
  --project-root . `
  --name example `
  --scope base `
  --description "Describe the capability" `
  --category executor

# 2. 生成骨架，停在 refine gate
python <skill-dir>/scripts/workflow.py run `
  --state docs/state/create-skill/example.json

# 3. Agent 或人编辑生成的 SKILL.md，补全 Workflow / Verification / Side Effects
python <skill-dir>/scripts/workflow.py resume `
  --state docs/state/create-skill/example.json `
  --event refined `
  --note "Workflow and verification completed"

# 4. 运行机器校验
python <skill-dir>/scripts/workflow.py run `
  --state docs/state/create-skill/example.json

# 5. 若退出码为 3：修复后显式重试
python <skill-dir>/scripts/workflow.py retry `
  --state docs/state/create-skill/example.json `
  --note "Fixed validator findings"
python <skill-dir>/scripts/workflow.py run `
  --state docs/state/create-skill/example.json

# 6. 由宿主 adapter 或人完成注册，再关闭工作流
python <skill-dir>/scripts/workflow.py resume `
  --state docs/state/create-skill/example.json `
  --event registered `
  --note "Added to project inventory"
```

## 不变量

- 默认作者层是 `.agents/skills`，不创建 `.Codex/skills`。
- 已存在的目标 Skill 目录不会被覆盖；冲突会进入 `blocked`。
- `refine` 和 `register` 必须由显式事件通过，运行器不伪造 Agent 判断或注册结果。
- 每次状态变化都追加 `history`；校验报告与错误留在 state，支持跨会话恢复。
- 机器校验失败只允许在配置上限内重试；超过上限进入 `blocked`。

## 验证

```powershell
python -m unittest discover `
  -s <skill-dir>/tests `
  -p "test_*.py"
```
