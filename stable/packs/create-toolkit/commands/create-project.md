# 历史参考：创建项目 (Create Project)

> **状态：historical_reference。** 本文件不在 active manifest 中，不是 CG 当前项目创建能力，也不能按下文直接承诺执行。当前工作环境中的完整 workspace bootstrap 由用户级 `new-workspace` Skill 承接；CG 只提供其中可复用的协作资产与 Pack 注入机制。

<!--
WHY（2026-07-26）：旧命令把目录、代码模板、Pack、Cursor 规则、个人 workspace 登记和 KG 自动接入捆成 CG 的“一步创建项目”能力。
参照系：CG 是人—Agent 协作机制 Provider；AGENTS.md / .agents 公共作者层由 new-workspace 与 cursor-to-codex-migration 流程编排，个人工作台布局不属于 CG。
本次决定：将 create-project 定性为越界历史参考，不在 CG 重建同名 Workflow；可复用的 Pack、Rule 与注入机制继续由 CG 单独发布。
排除项：不把用户级 new-workspace 冒充 CG 现货，不新增 workspace schema，不修改 KG / cursor-workspaces，也不删除、移动或重写下方历史正文。
-->

以下内容保留为 2026-03 时期的 Cursor-first 设计样本：

## 概述

在 knowledge-graph 认知运行时工作空间中创建一个新的工作项目，一步完成：目录结构 → 模板部署 → Pack 安装 → 规则生成 → workspace 注册。

## 参数

| 参数 | 必填 | 说明 | 示例 |
|:---|:---|:---|:---|
| `name` | 是 | 项目名称（英文短横线格式） | `security-mgmt-center` |
| `path` | 否 | 项目路径，默认 `D:/Project/{name}/` | `D:/Project/security-mgmt-center` |
| `stack` | 否 | 技术栈预设，默认 `custom` | `full-stack-java-vue` |
| `packs` | 否 | 额外部署的 Pack 列表 | `deep-research` |
| `workspace` | 否 | .code-workspace 文件路径 | 自动检测当前 workspace |

### 技术栈预设 (stack)

| 预设 | 部署的模板 | 部署的 Pack/规则 |
|:---|:---|:---|
| `full-stack-java-vue` | ddd + java + vue | DDD 团队规则 |
| `frontend-react` | _(不部署模板)_ | _(按需)_ |
| `frontend-vue` | vue | _(按需)_ |
| `custom` | _(手动指定)_ | _(手动指定)_ |

## 执行步骤

### Step 1: 确认项目信息

与用户确认以下信息（未提供的需要询问）：

- 项目名称和路径
- 技术栈选择
- 是否需要额外的 Pack（如 deep-research）
- 业务领域简述（用于生成项目专属规则）

### Step 2: 创建目录结构

```powershell
# 创建项目根目录
mkdir -p <project-path>

# 创建标准子目录
mkdir -p <project-path>/.cursor/rules
mkdir -p <project-path>/docs/research
mkdir -p <project-path>/docs/architecture
mkdir -p <project-path>/docs/domain
mkdir -p <project-path>/src
```

对于 `full-stack-java-vue` 预设，额外创建：
```
mkdir -p <project-path>/docs/research/compliance
mkdir -p <project-path>/docs/research/competitors
mkdir -p <project-path>/docs/research/technology
mkdir -p <project-path>/backend
mkdir -p <project-path>/frontend
```

### Step 3: 部署代码模板

根据 `stack` 参数调用 `use-template.ps1`：

```powershell
# cursor-genesis 的 code-templates 路径
$templateRoot = "<cursor-genesis-path>/stable/atoms/code-templates"

# full-stack-java-vue 预设：
& "$templateRoot/use-template.ps1" -Name ddd    # → docs/domain/
& "$templateRoot/use-template.ps1" -Name java -Target backend
& "$templateRoot/use-template.ps1" -Name vue  -Target frontend
```

如果 Agent 无法直接执行 PowerShell（如在非 Windows 环境），改为手动复制：
- `code-templates/design/ddd-structure/*` → `docs/domain/`
- `code-templates/backend/java-spring-boot/*` → `backend/`
- `code-templates/frontend/vue-admin/*` → `frontend/`

### Step 4: 部署 Pack

调用 `install-pack.py` 部署指定的 Pack：

```bash
python <cursor-genesis-path>/scripts/install-pack.py <pack-name> <project-path>
```

默认部署 deep-research（如果用户同意）。额外 Pack 按 `packs` 参数逐个部署。

### Step 5: 生成项目专属规则

在 `<project-path>/.cursor/rules/` 下生成两个规则文件：

**domain-context.mdc** — 业务领域上下文：
- globs 限定到项目目录
- 包含业务领域术语、核心概念、关键约束
- 内容基于 Step 1 中用户提供的业务领域简述生成

**project-conventions.mdc** — 项目技术规范：
- globs 限定到项目的 src/ 或 backend/frontend/ 目录
- 包含技术栈约定、编码规范、框架使用约定
- 内容基于 `stack` 参数生成

规则的 globs 格式：
```
globs: <project-path>/**
```

### Step 6: 注册到 workspace

将项目路径追加到 `.code-workspace` 文件的 `folders` 数组中：

```bash
python <cursor-genesis-path>/scripts/install-pack.py <any-pack> <project-path> --workspace <workspace-file>
```

或由 Agent 直接编辑 `.code-workspace` JSON 文件，在 `folders` 数组中新增：
```json
{
  "path": "../../../<project-name>"
}
```

### Step 7: 生成 README

在项目根目录生成 `README.md`，包含：
- 项目名称和简述
- 目录结构说明
- 已安装的模板和 Pack 列表
- 开发工作流（调研 → 业务边界 → 技术架构 → DDD → 开发）
- knowledge-graph 认知介入点

### Step 8: 验证

检查以下条件是否满足：
- [ ] 项目目录已创建且结构完整
- [ ] 模板已部署到正确位置
- [ ] .cursor/rules/ 已生成且 globs 正确
- [ ] Pack 已安装（.cursor/installed-packs.yaml 存在）
- [ ] workspace 文件已更新
- [ ] README.md 已生成

## 与 knowledge-graph 的关系

创建的项目会自动成为 knowledge-graph 认知运行时的一部分：
- knowledge-graph 的 always-apply 规则（GM、操作范式）自动覆盖
- Agent 在项目中工作时可直接读取 knowledge-graph 的 roots/、topics/
- 涌现的方法论认知可通过 ingestion 流程回流 knowledge-graph

项目本身不需要注册为叶子节点（除非后续发展为长期知识生产领域）。
