# leaf-node 通用框架

**层级**: L2 模板层
**用途**: 叶子节点通用框架，任何想成为 knowledge-graph 叶子节点的项目都需要

---

## 概述

本目录包含成为 knowledge-graph 叶子节点所需的通用配置和机制。

任何想成为叶子节点的项目（如 vscode-genesis、jetbrains-genesis）都可以复用这套框架。

---

## 核心机制

### 1. 同步机制（sync）

**功能**：从 knowledge-graph 拉取推荐内容

**命令**：`/sync`

**实现要点**：
- 读取 knowledge-graph 的 `meta/recommendations.yaml`
- 使用 git sparse-checkout 拉取指定内容
- 放入 `pending/upstream/` 待审核
- 审核通过后合入 `stable/knowledge/`

### 2. 回流机制（backflow）

**功能**：接收下游项目的改进

**命令**：`/backflow`

**实现要点**：
- 监控 GitHub PR（标签：backflow）
- 拉取到 `backflow/pending/`
- 审核内容质量和可复用性
- 精炼后放入 `stable/knowledge/exports/`

### 3. 上报机制（export）

**功能**：向 knowledge-graph 上报精炼内容

**命令**：`/export`

**实现要点**：
- 检查 `stable/knowledge/exports/` 目录
- 生成上报清单
- 创建 PR 到 knowledge-graph
- 等待上游整合

---

## 目录结构

```
leaf-node/
├── README.md                    # 本文件
├── commands/
│   ├── sync.md                 # /sync - 从上游同步
│   ├── backflow.md             # /backflow - 处理下游回流
│   ├── export.md               # /export - 向上游上报
│   └── visualize.md            # /visualize - 叶子节点可视化
├── skills/
│   ├── node-sync.skill.yaml    # 节点同步技能
│   ├── node-backflow.skill.yaml # 节点回流技能
│   ├── node-export.skill.yaml  # 节点上报技能
│   └── node-visualize.skill.yaml # 可视化 skill
├── visualizer/                 # 可视化引擎模板（React + Vite）
│   ├── src/
│   ├── public/
│   │   └── config.yaml         # 示例配置，安装时替换为叶子节点自己的配置
│   └── package.json
├── subagents/
│   └── node-manager.yaml       # 节点管理子代理
└── rules/
    └── leaf-node.mdc           # 叶子节点规则
```

---

## 使用场景

### 场景 1：创建新的叶子节点

假设你想创建 `vscode-genesis`（VSCode 扩展开发的叶子节点）：

```bash
# 1. 创建项目
mkdir vscode-genesis
cd vscode-genesis

# 2. 拉取叶子节点框架
git clone --filter=blob:none --sparse --depth=1 \
  https://github.com/SYMlp/cursor-genesis.git .cursor-genesis-temp

cd .cursor-genesis-temp
git sparse-checkout set stable/packs/knowledge-manage/leaf-node

# 3. 复制到项目
cd ..
# 复制 Cursor 配置（commands, skills, rules 等）
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/leaf-node/commands .cursor/
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/leaf-node/skills .cursor/
# 复制可视化引擎到 .knowledge/
mkdir -p .knowledge
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/leaf-node/visualizer .knowledge/visualizer
cp .cursor-genesis-temp/stable/packs/knowledge-manage/leaf-node/visualizer/public/config.yaml .knowledge/visualizer.yaml
# 若有 rules、subagents 等也需复制
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/leaf-node/rules .cursor/ 2>/dev/null || true
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/leaf-node/subagents .cursor/ 2>/dev/null || true

rm -rf .cursor-genesis-temp

# 5. 定制化
# 编辑 .cursor/ 中的文件，添加 VSCode 特定的内容
```

### 场景 2：cursor-genesis 自己使用

cursor-genesis 本身就是一个叶子节点，所以它也使用这套框架：

```bash
cd d:/Project/cursor-genesis

# cursor-genesis 的 .cursor/ 目录就是基于这套框架定制的
# 添加了 Cursor 特定的 skills（kg-search、kg-assemble）
```

---

## 定制化指南

### 1. 保持核心机制

**必须保留**：
- `/sync` 命令 - 从上游同步
- `/backflow` 命令 - 处理下游回流
- `/export` 命令 - 向上游上报

这三个命令是叶子节点与 knowledge-graph 交互的核心。

### 2. 添加领域特定内容

**可以添加**：
- 领域特定的 skills（如 cursor-genesis 的 kg-search）
- 领域特定的 commands（如 cursor-genesis 的 /cg-install）
- 领域特定的 rules（如 cursor-genesis 的 Cursor 规则）

### 3. 示例：cursor-genesis 的定制化

```
cursor-genesis/.cursor/
├── commands/
│   ├── sync.md              # 保留（核心机制）
│   ├── backflow.md          # 保留（核心机制）
│   ├── export.md            # 保留（核心机制）
│   ├── kg-search.md         # 添加（Cursor 特定）
│   └── kg-assemble.md       # 添加（Cursor 特定）
├── skills/
│   ├── node-sync.skill.yaml     # 保留（核心机制）
│   ├── node-backflow.skill.yaml # 保留（核心机制）
│   ├── node-export.skill.yaml   # 保留（核心机制）
│   ├── kg-search.skill.yaml     # 添加（Cursor 特定）
│   └── kg-assemble.skill.yaml   # 添加（Cursor 特定）
└── rules/
    ├── leaf-node.mdc        # 保留（核心机制）
    └── cursor-specific.mdc  # 添加（Cursor 特定）
```

---

## 命令详情

### /sync

**用途**：从 knowledge-graph 拉取推荐内容

**子命令**：
- `/sync pull` - 拉取推荐内容
- `/sync status` - 查看同步状态
- `/sync list` - 列出可用推荐

**流程**：
1. 读取 knowledge-graph 的 `meta/recommendations.yaml`
2. 找到针对本节点的推荐清单
3. 使用 git sparse-checkout 拉取
4. 放入 `pending/upstream/` 待审核
5. 审核通过后合入 `stable/knowledge/`

### /backflow

**用途**：处理下游项目的回流

**子命令**：
- `/backflow status` - 查看待处理回流
- `/backflow review` - 审核回流内容
- `/backflow accept` - 接受并精炼

**流程**：
1. 监控 GitHub PR（标签：backflow）
2. 拉取 PR 内容到 `backflow/pending/`
3. 审核内容质量、可复用性、格式规范
4. 通过后移动到 `backflow/processing/`
5. 精炼后放入 `stable/knowledge/exports/`

### /export

**用途**：向 knowledge-graph 上报精炼内容

**子命令**：
- `/export status` - 查看待上报内容
- `/export prepare` - 准备上报清单
- `/export submit` - 提交 PR 到上游

**流程**：
1. 检查 `stable/knowledge/exports/` 目录
2. 生成上报清单（类型、数量、摘要）
3. 创建 PR 到 knowledge-graph
4. 等待上游审核和整合

---

## 技能详情

### node-sync.skill.yaml

节点同步技能，包括：
- 读取上游推荐清单
- 执行 git sparse-checkout
- 管理 pending/upstream/ 目录
- 审核和合入流程

### node-backflow.skill.yaml

节点回流技能，包括：
- 监控 GitHub PR
- 拉取 PR 内容
- 审核回流质量
- 精炼和导出

### node-export.skill.yaml

节点上报技能，包括：
- 检查 exports/ 目录
- 生成上报清单
- 创建 PR
- 跟踪上报状态

---

## 子代理详情

### node-manager.yaml

节点管理子代理，负责：
- 自动执行同步任务
- 监控回流 PR
- 提醒待处理事项
- 生成统计报告

---

## 规则详情

### leaf-node.mdc

叶子节点通用规则，包括：
- 目录结构规范
- 文件命名约定
- 回流格式要求
- 上报格式要求

---

## 与 knowledge-graph 的交互

```
knowledge-graph (上游)
    ↓ 推荐清单
    ↓ meta/recommendations.yaml
    ↓
Leaf Node (本节点)
    ↓ 拉取 (/sync)
    ↓ pending/upstream/
    ↓ 审核合入
    ↓ stable/knowledge/
    ↓
    ↓ 接收回流 (/backflow)
    ↓ backflow/pending/
    ↓ 审核精炼
    ↓ stable/knowledge/exports/
    ↓
    ↓ 上报 (/export)
    ↓ 创建 PR
    ↓
knowledge-graph (上游)
    ↓ 整合
    ↓ index/topics/
```

---

## 相关文档

- [知识管理体系配置](../README.md)
- [Cursor 集成设计方案](../../../../knowledge-graph/docs/cursor-integration-design.md)
- [叶子节点规范](../../../../knowledge-graph/meta/leaf-node-spec.md)
