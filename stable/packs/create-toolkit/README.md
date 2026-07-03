# Create Toolkit Pack

资产创建三件套，通过 `/create-skill`、`/create-command`、`/create-subagent` 三个互相路由的命令，实现 Cursor 项目中 Skill / Command / Subagent 的完整创建闭环。

## 组件清单

| 类型 | 文件 | 说明 |
|:---|:---|:---|
| Command | `commands/create-skill.md` | 创建原子 Skill（含分类标签 + 学习型工厂检索） |
| Command | `commands/create-command.md` | 创建 Command（最高层入口，自动级联创建 Skill + Subagent） |
| Command | `commands/create-subagent.md` | 创建 Subagent（含能力拆分分析，级联创建 Skill） |
| Command | `commands/session-summary.md` | 会话沉淀：根据对话上下文生成复盘式记录 |
| Agent | `agents/base-skill-engineer.md` | Skill 工厂工程师（三命令共享） |
| Skill | `skills/base-skill-generator/` | 脚手架生成器（含 9 篇知识库文档） |
| Skill | `skills/base-closure-validator/` | 引用完整性校验（`/create-command` 依赖） |
| Skill | `skills/base-prompt-auditor/` | 质量审查工具（可选） |
| Skill | `skills/base-inventory-updater/` | 资产清单更新工具（可选） |
| Standard | `standards/skill-meta-standard.md` | 认知元层规范 V1.0 |

## 路由关系

```
用户需求
├── "单一确定性动作" → /create-skill
├── "需要推理/判断" → /create-subagent → 级联 /create-skill
└── "我想要一个命令" → /create-command → 级联 /create-skill + /create-subagent
```

## 组件依赖关系

```
/create-command (最高层入口)
├── 架构分析 → 判断需要哪些 Skill + Subagent
├── 级联调用 /create-skill
├── 级联调用 /create-subagent
├── 验证: base-closure-validator
└── 注册: base-inventory-updater (可选)

/create-subagent (中间层)
├── 能力拆分 → 判断需要哪些 Skill
├── 级联调用 /create-skill
├── 创建 Agent 定义 (读取 standard-subagent.md + model-selection-guide.md)
└── 注册: base-inventory-updater (可选)

/create-skill (最底层)
├── 类型决策钩子 → 路由到上面两个命令
├── 分类标签判断 (executor/generator/analyzer/orchestrator/researcher)
├── 学习型工厂检索 (同 category 的已有 Skill 作为 few-shot)
├── 调用 base-skill-engineer Agent
│   └── 执行 base-skill-generator/scripts/gen.py
└── 注册: base-inventory-updater (可选)

共享:
  base-skill-engineer ← 三命令共用
  base-skill-generator/assets/docs/ ← Agent 知识库 (9 篇)
  skill-meta-standard.md ← 认知元层规范
```

## 安装方式

### 方式 A：通过 install-pack 脚本（推荐）

```powershell
python <cursor-genesis-path>/scripts/install-pack.py create-toolkit <target-project-path>
```

脚本读取 `install-manifest.yaml`，自动将文件部署到目标项目的 `.cursor/` 目录下。

### 方式 B：手动复制

将以下文件复制到目标项目：

```
目标项目/
├── .cursor/
│   ├── commands/
│   │   ├── create-skill.md
│   │   ├── create-command.md
│   │   └── create-subagent.md
│   ├── agents/
│   │   └── base-skill-engineer.md
│   ├── skills/
│   │   ├── base-skill-generator/    (含 scripts/, assets/docs/, .meta/)
│   │   ├── base-closure-validator/  (含 scripts/, assets/)
│   │   ├── base-prompt-auditor/     (可选)
│   │   └── base-inventory-updater/  (可选)
│   └── standards/
│       └── skill-meta-standard.md
```

## 使用

安装完成后，在 Cursor 中使用以下命令：

| 命令 | 场景 |
|:---|:---|
| `/create-skill` | 创建一个原子能力单元 |
| `/create-subagent` | 创建一个自主推理 Agent |
| `/create-command` | 创建一个用户可调用的 SOP 命令（自动级联） |

### 认知元层

Pack 内置认知元层支持，创建的资产会根据复杂度自动分级：

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
