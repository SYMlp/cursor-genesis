# Deep Research Pack

系统化深度调研能力，通过 **Plan → Execute → Synthesize** 三阶段流程，将模糊的调研需求转化为结构化的研究报告。

## ⚠ 副本地图（改契约前必读）

同一份 synthesizer / executor 契约在四处存在。**它们不是一个宿主的镜像，是两条已经分家的演进线**——
Cursor 线（pack，Gemini 模型、`@.cursor/skills/` 引用、Brave MCP）与 Claude Code 线（后来单独演进，
带 `tools:` / `model:` frontmatter、Glob/tavily、subagent 返回契约）。

| # | 路径 | 宿主 / 角色 | 改契约时 |
|:--|:---|:---|:---|
| 1 | `~/.claude/agents/base-research-{planner,executor,synthesizer}.md` | **Claude Code 实际读取的生效版** | **必改** |
| 2 | `kg/.cursor/skill-library/research/base-research-*/SKILL.md` | Cursor skill 库（宿主中性） | 必改 |
| 3 | `packs/deep-research/skills/base-research-*/SKILL.md` | 本 pack 分发件 → 目标项目 `.cursor/skills/` | 必改 |
| 4 | `packs/deep-research/agents/base-research-*-agent.md` | 本 pack 分发的 Cursor agent 壳，**只引用 #3、不含契约正文** | 一般不动 |

**#1 不是本 pack 的安装产物**（`install-manifest.yaml` 只部署到 `.cursor/`），手改它安全，
不会被 `install-pack.py` 覆盖；反过来说，**改本 pack 也不会让 Claude Code 那边生效**。

> **2026-08-07 教训**：溯源契约的修复第一次只改了 #2 #3 就宣布"已从源头修好"，
> 而实际在跑 deep research 的 #1 纹丝不动。起因是按目录直觉找文件、没验证"谁在运行时读它"。
> 判据：**改任何契约前先确认生效路径，而不是按目录名推断**。
> 推导与实证见 toys `self-analysis/2026-08-07-验证器装在准入而非流程-观测件.md` §同日更正。

## 组件清单

| 类型 | 文件 | 说明 |
|:---|:---|:---|
| Command | `commands/deep-research.md` | 命令入口，编排三阶段流程 |
| Agent | `agents/base-research-planner-agent.md` | 调研规划师：需求提炼 → 计划生成 |
| Agent | `agents/base-research-executor-agent.md` | 调研执行者：搜索 → 抓取 → 落盘 |
| Agent | `agents/base-research-synthesizer-agent.md` | 报告合成师：笔记 → 研究报告 |
| Agent | `agents/base-research-analyst-agent.md` | 战略分析师（可选）：洞察 → SWOT → 创意方案 |
| Skill | `skills/base-research-planner/` | Planner 的核心能力定义 |
| Skill | `skills/base-research-executor/` | Executor 的核心能力定义 |
| Skill | `skills/base-research-synthesizer/` | Synthesizer 的核心能力定义 |

## 组件依赖关系

```
/deep-research (Command 入口)
│
├─→ Phase 1: base-research-planner-agent
│   └── reads: .cursor/skills/base-research-planner/SKILL.md
│   └── output: docs/research/{slug}/brief.md 或 plan.md
│
├─→ Phase 2: base-research-executor-agent
│   └── reads: .cursor/skills/base-research-executor/SKILL.md
│   └── calls: brave_web_search (MCP), WebFetch (内置)
│   └── output: docs/research/{slug}/raw/*, fetched/*, notes/*
│
├─→ Phase 3: base-research-synthesizer-agent
│   └── reads: .cursor/skills/base-research-synthesizer/SKILL.md
│   └── output: docs/research/{slug}/report.md
│
└─→ (可选) base-research-analyst-agent
    └── 用于对调研结果的二次分析和战略洞察
```

## 外部依赖

| 依赖 | 必需性 | 说明 |
|:---|:---|:---|
| Brave Search MCP | **必需** | Executor 的搜索功能依赖此 MCP，详见 `mcp-info/brave-search.md` |

## 安装方式

### 方式 A：通过 install-pack 脚本（推荐）

```powershell
# PowerShell (Windows)
# 假设 cursor-genesis 在 .cursor-genesis/ 或已知路径
python <cursor-genesis-path>/scripts/install-pack.py deep-research <target-project-path>
```

脚本会读取 `install-manifest.yaml`，自动将文件部署到目标项目的 `.cursor/` 目录下。

### 方式 B：手动复制

将以下文件复制到目标项目：

```
目标项目/
├── .cursor/
│   ├── commands/
│   │   └── deep-research.md
│   ├── agents/
│   │   ├── base-research-planner-agent.md
│   │   ├── base-research-executor-agent.md
│   │   ├── base-research-synthesizer-agent.md
│   │   └── base-research-analyst-agent.md
│   └── skills/
│       ├── base-research-planner/SKILL.md
│       ├── base-research-executor/SKILL.md
│       └── base-research-synthesizer/SKILL.md
```

### 安装后配置

在目标项目的 Cursor Settings → MCP 中添加 **Brave Search**，参考 `mcp-info/brave-search.md`。

## 使用

安装完成后，在 Cursor 中输入 `/deep-research` 触发命令，按提示输入调研主题即可。

### 调研产物结构

```
docs/research/{topic-slug}/
├── brief.md          # 调研简报（模糊输入时生成）
├── plan.md           # 调研计划
├── raw/              # 原始搜索结果
│   └── task-01-search-001.md
├── fetched/          # 抓取的页面全文
│   └── task-01-url-001.md
├── notes/            # 结构化调研笔记
│   └── task-01.md
└── report.md         # 最终研究报告
```

## 更新

重新运行 install-pack 脚本即可覆盖更新：

```powershell
python <cursor-genesis-path>/scripts/install-pack.py deep-research <target-project-path>
```
