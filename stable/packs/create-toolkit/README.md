# Create Toolkit Pack

资产创建工具箱。四类创建入口已经完成核心 / 宿主分离：

- `.agents/skills/create-skill-workflow/`：工具无关作者层，保存阶段、Gate、校验报告与重试状态；
- `.agents/skills/create-subagent-workflow/`：创建宿主无关 Agent Contract，验证上下文隔离、Skill 依赖和返回契约；
- `.agents/skills/create-command-workflow/`：创建宿主无关 Command Contract，验证有序 SOP、依赖闭包、Human Gate 和最终验收；
- `.agents/skills/create-rule-workflow/`：把薄行为契约校验并登记到 `AGENTS.md`，再由宿主 adapter 投影激活格式；
- `.agents/skills/audit-agent-assets/`：只读审计 Agent / Skill / Command / Workflow / adapter，按公共 rubric 输出证据化判断；
- `.cursor/commands/create-*.md`：Cursor 薄入口，只负责类型路由、具体宿主格式和调用公共 Workflow。

<!--
WHY（2026-07-26）：P1 后继续拆依赖链时，发现旧 Subagent 定义把上下文隔离本体与 Cursor Task、目录和易漂移 model ID 混为一体。
参照系：KG 的“行为契约与工作流分载”、Subagent clean-context 证据，以及 `.agents` 作者层 + 宿主薄适配迁移模型。
本次决定：公共核心改为 Agent Contract + 状态型 Workflow；具体模型和调用格式只由宿主 adapter 注入。
排除项：不发明三宿主统一 Agent ABI，不静态映射模型 ID，不承诺嵌套 Subagent 或自动委派能力。
-->

<!--
WHY（2026-07-26）：Skill 与 Agent 依赖完成工具无关化后，旧 Command 仍把固定 SOP 本体等同于 Cursor 斜杠入口和 Task 语法。
参照系：KG 的“Agent 架构 = 控制流设计”、工作流型流程 ≤ 7，以及已落地的 Skill / Agent Contract 作者层。
本次决定：公共核心改为 Command Contract + 状态型 Workflow；斜杠入口和 Agent 调用绑定只由宿主 adapter 生成。
排除项：不发明统一斜杠命令 ABI，不让 Command 承担自主路由，不自动执行高风险步骤或绕过 Human Gate。
-->

<!--
WHY（2026-07-26）：legacy 分诊发现 base-prompt-auditor 的“目标 + rubric → 审计包”机制可复用，但旧 V2.1 rubric 把 Cursor 路径、model 字段和旧工厂约束误当通用质量标准。
参照系：单 Skill 迁移、渐进加载、确定性准备与 Agent 认知判断分载，以及当前 Skill / Agent / Command / Workflow 公共契约。
本次决定：新增工具无关 audit-agent-assets；脚本只校验输入并准备审计包，最终 PASS / WARN / FAIL 由 Agent 依据目标证据判断。
排除项：不复制旧 rubric，不把认知审计冒充机器 Validator，不生成 Codex 专属 UI 元数据，也不删除 base-prompt-auditor 历史样本。
-->

<!--
WHY（2026-07-26）：base-rule-generator 把“薄行为契约”与 Cursor `.mdc` 路径、激活 frontmatter、旧优先级和长模板混为一体，且另建规则目录会与项目 `AGENTS.md` 作者权威冲突。
参照系：KG“行为契约与工作流分载”、项目 `AGENTS.md` 唯一规则作者源、Cursor 官方四类 Project Rules，以及现有状态型创建 Workflow。
本次决定：公共 create-rule-workflow 只生成、校验并登记 `AGENTS.md` 受管 Rule block；Cursor renderer 单独生成 `.mdc`，多 glob 未验证时确定性拒绝。
排除项：不建立 `.agents/rules` 第二作者库，不搬运旧 meta-rule 模板，不声称 Claude / Codex 已有路径激活 adapter，也不删除 base-rule-generator 历史样本。
-->

v1.6 active manifest 只分发上述公共作者层与 Cursor 薄适配。三份旧厚命令和其他 legacy generator / validator 仍原位保留，但不再进入新安装；逐项判决见 [`LEGACY-TRIAGE.md`](LEGACY-TRIAGE.md)。

## 组件清单

| 类型 | 文件 | 说明 |
|:---|:---|:---|
| Workflow Skill | `skills/create-skill-workflow/` | 工具无关创建流程；持久化 scaffold/refine/validate/register/complete 状态 |
| Cursor Adapter | `adapters/cursor/create-skill.md` | `/create-skill` 薄入口，调用公共 Workflow |
| Historical Reference | `commands/create-skill.md` | P1 前的 Cursor 厚命令，保留设计史料，不再由 v1.1 manifest 安装 |
| Workflow Skill | `skills/create-subagent-workflow/` | 工具无关 Agent Contract 流程；持久化分析、依赖、精修、校验和适配状态 |
| Cursor Adapter | `adapters/cursor/create-subagent.md` | `/create-subagent` 薄入口；具体 model ID 和 Role Injection 留在 Cursor 层 |
| Cursor Renderer | `adapters/cursor/render_subagent.py` | 把通过公共 Validator 的 Agent Contract 渲染到 `.cursor/agents/` |
| Historical Reference | `commands/create-subagent.md` | P2 前的 Cursor 厚命令，保留设计史料，不再由 v1.2 manifest 安装 |
| Workflow Skill | `skills/create-command-workflow/` | 工具无关 Command Contract 流程；验证固定步骤、依赖闭包、Gate、失败恢复和最终验收 |
| Cursor Adapter | `adapters/cursor/create-command.md` | `/create-command` 薄入口；斜杠触发和 Role Injection 留在 Cursor 层 |
| Cursor Renderer | `adapters/cursor/render_command.py` | 把通过公共 Validator 的 Command Contract 渲染到 `.cursor/commands/` |
| Historical Reference | `commands/create-command.md` | P3 前的 Cursor 厚命令，保留设计史料，不再由 v1.3 manifest 安装 |
| Workflow Skill | `skills/create-rule-workflow/` | 工具无关 Rule 创建流程；校验薄契约并通过 Human Gate 登记到 `AGENTS.md` |
| Cursor Adapter | `adapters/cursor/create-rule.md` | `/create-rule` 薄入口；Cursor 激活模式留在 adapter |
| Cursor Renderer | `adapters/cursor/render_rule.py` | 从 `AGENTS.md` 受管 block 渲染 `.cursor/rules/<name>.mdc` |
| Public Skill | `skills/audit-agent-assets/` | 确定性准备审计包，由 Agent 按工具无关 rubric 返回证据化报告 |
| Triage Record | `LEGACY-TRIAGE.md` | 未安装 legacy 资产的事实依据、保留方式与后续入口 |

## 路由关系

```
用户需求
├── "按需执行的单一能力" → /create-skill
├── "必须常驻或条件生效的薄行为约束" → /create-rule
├── "需要推理/判断" → /create-subagent → 级联 /create-skill
└── "我想要一个命令" → /create-command → 级联 /create-skill + /create-subagent
```

## 组件依赖关系

```
/create-rule (Cursor 薄入口)
└── .agents/skills/create-rule-workflow
    ├── analyze → 三问类型判定 + activation / scope
    ├── scaffold/refine → 生成不超过 80 行的 Rule block draft
    ├── validate → 机器 Validator；拒绝厚流程与宿主格式泄漏
    ├── register → Human Gate 后登记到 AGENTS.md 唯一作者源
    ├── adapt → Cursor renderer 生成 .cursor/rules/<name>.mdc
    └── complete → 记录真实存在的宿主投影

/create-command (Cursor 薄入口)
└── .agents/skills/create-command-workflow
    ├── analyze → Human / Agent Gate，声明 Skill / Agent 依赖与风险
    ├── dependencies → 机器 Guard；缺失时走下层公共 Workflow
    ├── scaffold/refine → 生成并精修 .agents/commands/<name>.md
    ├── validate → 机器 Validator；固定 1–7 步且最后一步验证
    ├── adapt → Cursor renderer 生成斜杠入口和 Agent bindings
    └── complete → 记录已存在的 .cursor/commands/<name>.md

/create-subagent (Cursor 薄入口)
└── .agents/skills/create-subagent-workflow
    ├── analyze → Human / Agent Gate，声明 Skill 依赖与抽象 model_profile
    ├── dependencies → 机器 Guard；缺失时先走 create-skill-workflow
    ├── scaffold/refine → 生成并精修 .agents/agents/<name>.md
    ├── validate → 机器 Validator；拒绝宿主格式污染公共契约
    ├── adapt → Cursor renderer 选择当前真实 model ID
    └── complete → 记录已存在的 .cursor/agents/<name>.md

/create-skill (Cursor 薄入口)
├── 类型决策 → 非 Skill 时路由到上面两个命令
└── .agents/skills/create-skill-workflow
    ├── scaffold → 生成 .agents/skills/<name>/
    ├── refine → Human / Agent Gate
    ├── validate → 机器 Validator；失败可重试，超限 blocked
    ├── register → Human / Adapter Gate
    └── complete → 状态闭合

Inactive legacy（源文件保留，不安装）:
  commands/create-skill.md + create-subagent.md + create-command.md
  commands/create-project.md + commands/session-summary.md
  base-skill-engineer + base-skill-generator + base-rule-generator
  base-closure-validator + base-prompt-auditor + base-inventory-updater
  standards/skill-meta-standard.md
  └── 判决入口：LEGACY-TRIAGE.md
```

其中 `create-project.md` 已判为越界历史参考：完整 workspace bootstrap 由当前环境的用户级 `new-workspace` Skill 承接，不在 CG 重建同名能力。

`session-summary.md` 也保留为历史参考；工具无关的会话成果分诊机制已提炼到 `stable/atoms/skills/harvest-session/`，不回塞进资产创建工具箱。

## 安装方式

### 方式 A：通过 install-pack 脚本（推荐）

```powershell
python <cursor-genesis-path>/scripts/install-pack.py create-toolkit <target-project-path>
```

脚本读取 `install-manifest.yaml`：

- `audit-agent-assets` 和四个公共 Workflow 部署到目标项目 `.agents/skills/`；
- 四个 Cursor 薄命令和三个 renderer 部署到 `.cursor/`；
- 安装记录写入 `.agents/installed-packs.yaml`。

全新安装共 12 项。旧版本升级不会自动删除已经部署的 legacy 文件；installer 会把仍存在的旧副本记录为 `retained_unmanaged`，交由使用方人工分诊。

### 方式 B：手动复制

将以下文件复制到目标项目：

```
目标项目/
├── .agents/
│   ├── agents/                          # 运行 Workflow 后生成的 Agent Contract 作者层
│   ├── commands/                        # 运行 Workflow 后生成的 Command Contract 作者层
│   └── skills/
│       ├── create-skill-workflow/
│       ├── create-subagent-workflow/
│       ├── create-command-workflow/
│       ├── create-rule-workflow/
│       └── audit-agent-assets/
└── .cursor/
    ├── commands/
    │   ├── create-skill.md              # Cursor 薄入口
    │   ├── create-command.md             # Cursor 薄入口
    │   ├── create-subagent.md            # Cursor 薄入口
    │   └── create-rule.md                # Cursor 薄入口
    └── adapters/
        ├── create-subagent/
        │   └── render_subagent.py
        ├── create-command/
        │   └── render_command.py
        └── create-rule/
            └── render_rule.py
```

## 使用

安装完成后，Cursor 可以继续使用显式命令，Codex CLI 从 `.agents/skills/` 发现四个公共 Workflow 和审计 Skill。Claude Code 需要通过 `ai-runtime-compat/sync.ps1` 将选定 Skill 投影到 `.claude/skills/`；create-toolkit 当前不安装 Claude / Codex 原生命令入口，也不承诺跨宿主统一斜杠 ABI：

| 入口 | 场景 |
|:---|:---|
| `/create-skill` | 创建一个原子能力单元 |
| `/create-subagent` | 创建一个自主推理 Agent |
| `/create-command` | 创建一个用户可调用的 SOP 命令（自动级联） |
| `/create-rule` | 创建一个登记到 `AGENTS.md` 的薄行为契约，并按需投影 Cursor Rule |
| `audit-agent-assets` | 只读审计一个协作资产并返回证据化 PASS / WARN / FAIL |

### 认知元层

已退出 active manifest 的 legacy generator 曾使用以下认知元层分级。它只作为设计史保留，不等同于四个公共 Workflow 的当前契约或推荐规范：

| 分类标签 | 元数据级别 | 产出 |
|:---|:---|:---|
| executor | L0 | 仅增强 Frontmatter |
| analyzer / researcher | L1 | + `.meta/GUIDE.md` 修改指南 |
| generator / orchestrator | L2 | + `_meta/data/skill-meta/` 工厂记录 |

## 更新

重新运行 install-pack 脚本即可覆盖更新：

```powershell
python <cursor-genesis-path>/scripts/install-pack.py create-toolkit <target-project-path>
```
