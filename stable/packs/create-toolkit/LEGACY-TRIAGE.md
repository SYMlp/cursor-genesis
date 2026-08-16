# Create Toolkit Legacy Triage

v1.4 起，legacy 资产退出 active manifest；v1.6 的 active manifest 安装四个公共 Workflow、`audit-agent-assets`、四个 Cursor 薄入口和三个 Cursor renderer。下表中的旧源文件全部原位保留，但不再进入新安装。

<!--
WHY（2026-07-26）：三个创建入口完成公共作者层迁移后，active manifest 仍默认分发九项硬编码 Cursor / V2 inventory 的旧资产，并夹带不属于资产创建域的 create-project 与 session-summary。
参照系：`.agents` 作者层 + 宿主薄适配、仓内真实引用，以及“通用机制进 CG 核心，Cursor 格式留 adapter / 冻结区 / 历史参考区”的边界。
本次决定：create-toolkit v1.4 默认只安装已验收的公共 Workflow 与 Cursor 薄适配；legacy 源文件原位保留，升级不自动删除旧副本。
排除项：不把旧目录整包复制到 `.agents`，不把候选资产冒充现货，不删除历史材料，也不在本刀创建 Rule / workspace / session 新契约。
-->

对账事实：

- 仓内引用扫描只命中本 Pack 的 README、resources catalog 和 install manifest，没有发现其他代码或 Pack 调用这些 legacy 入口。
- 四个公共 Workflow、四个 Cursor 薄入口和三个 renderer 均有安装或行为测试；legacy 资产没有等价的跨宿主验收证据。
- 本仓没有下游机器的使用遥测，因此只能停止未来默认分发，不能据此删除消费项目里的既有副本。

| 资产 | 判决 | 退出 active manifest 的事实依据 | 后续入口 |
|:---|:---|:---|:---|
| `commands/create-skill.md` | 历史冻结 | 已由公共 `create-skill-workflow` + Cursor 薄入口替代 | 仅保留 P1 前设计史 |
| `commands/create-subagent.md` | 历史冻结 | 已由公共 Agent Contract Workflow + Cursor renderer 替代 | 仅保留 P2 前设计史 |
| `commands/create-command.md` | 历史冻结 | 已由公共 Command Contract Workflow + Cursor renderer 替代 | 仅保留 P3 前设计史 |
| `commands/create-project.md` | 越界冻结 | 写死 Windows、`.cursor/rules`、旧安装记录和“自动成为 KG runtime”声明；且不属于协作资产创建域 | 完整 bootstrap 已由用户级 `new-workspace` Skill 承接；CG 只保留可复用的 Pack / Rule / 注入机制 |
| `commands/session-summary.md` | 历史冻结 | 只处理描述性聊天复盘且默认写入个人路径，不创建协作资产 | 工具无关分诊机制已提炼为 `stable/atoms/skills/harvest-session`；用户级 `session-harvest` 保留个人适配 |
| `agents/base-skill-engineer.md` | 历史冻结 | 写死 Cursor Project、`model: fast` 和 `.cursor` Role Injection 依赖 | 公共创建逻辑已由对应 Workflow 承接 |
| `skills/base-skill-generator/` | 历史冻结 | 写死 `.cursor/skills` 与旧 7-layer / L2 工厂约束；已被公共 create-skill Workflow 替代 | 保留生成器设计材料，不再默认分发 |
| `skills/base-rule-generator/` | 历史冻结 | 薄行为契约机制已提炼到公共 `create-rule-workflow`，Cursor 激活格式进入独立 renderer；旧 `.mdc` 工厂、meta-rule 模板和优先级声明不进入核心 | 保留迁移前样本，不再默认分发 |
| `skills/base-closure-validator/` | 历史冻结 | 明示 `runtimes: [cursor]`，绑定旧 `v2-asset-inventory.md` 和 Cursor 扫描面 | 新 Validator 框架建成前不迁 |
| `skills/base-inventory-updater/` | 历史冻结 | 只扫描 `.cursor/agents`、`.cursor/skills`、`.cursor/commands` 和旧 inventory | 未来应从公共 registry / manifest 推导 |
| `skills/base-prompt-auditor/` | 历史冻结 | 可复用的审计包机制已提炼到公共 `audit-agent-assets`；旧 frontmatter、Cursor 路径和 V2.1 rubric 不进入新核心 | 保留迁移前样本，不再默认分发 |
| `standards/skill-meta-standard.md` | 历史参考 | 依赖本 Pack 不存在的旧标准和工厂记录，并把过时 generator / inventory / auditor 当机器消费者 | 仅作为认知元层设计史，不作为当前规范安装 |

## 安装与升级语义

- 全新安装：只得到 active manifest 的 12 项资产。
- 从旧版本升级：installer 不删除之前部署的 legacy 文件；它们会被记录为 `retained_unmanaged` 并提示人工分诊。
- 卸载 v1.6：只删除当前管理的 12 项，不触碰 `retained_unmanaged`。
- 源仓：上表全部资产继续留在原路径，下一阶段按单资产证据处理。

## 剩余处置项

未分诊项为 0，值得继续建设的 legacy 项也已归零：

- `create-project` 已完成越界判决，不在 CG 重建。
- `session-summary` 的通用机制已升入 CG 核心，旧入口保留为历史参考。
