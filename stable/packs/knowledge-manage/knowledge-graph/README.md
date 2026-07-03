# knowledge-graph 配置

**层级**: L3 认知层
**用途**: knowledge-graph 项目自己使用的 Cursor 配置

---

## 概述

本目录包含 knowledge-graph 项目在 Cursor 中操作时使用的配置，包括：

- 整合叶子节点上报的内容
- 生成推荐清单给叶子节点
- 记录推导过程
- 管理节点注册表

---

## 目录结构

```
knowledge-graph/
├── README.md                    # 本文件
├── commands/
│   ├── integrate.md            # /integrate - 整合叶子节点上报
│   ├── recommend.md            # /recommend - 生成推荐清单
│   └── derive.md               # /derive - 记录推导过程
├── skills/
│   ├── kg-manage.skill.yaml    # 知识图谱管理技能
│   └── node-registry.skill.yaml # 节点注册技能
├── subagents/
│   └── knowledge-integrator.yaml # 知识整合子代理
└── rules/
    └── knowledge-graph.mdc     # knowledge-graph 规则
```

---

## 使用场景

### 1. 整合叶子节点上报

当叶子节点（如 cursor-genesis）向 knowledge-graph 提交 PR 上报内容时：

```
/integrate
```

功能：
- 拉取叶子节点的 `exports/` 目录
- 分析上报内容的类型和质量
- 整合到对应的主题索引
- 更新推荐清单
- 记录推导过程

### 2. 生成推荐清单

为叶子节点生成推荐内容：

```
/recommend cursor-genesis
```

功能：
- 分析叶子节点的 `solves` 领域
- 从 knowledge-graph 中检索相关内容
- 生成分级推荐清单（required/recommended/optional）
- 更新 `meta/recommendations.yaml`

### 3. 记录推导过程

记录从第一性原理到具体知识的推导：

```
/derive
```

功能：
- 记录推导的起点（第一性原理）
- 记录推导的过程（逻辑链条）
- 记录推导的结果（具体知识）
- 存储到 `meta/derivation/`

---

## 安装

### 在 knowledge-graph 项目中安装

```bash
cd d:/Project/knowledge-graph

# 稀疏克隆 cursor-genesis
git clone --filter=blob:none --sparse --depth=1 \
  https://github.com/SYMlp/cursor-genesis.git .cursor-genesis-temp

cd .cursor-genesis-temp
git sparse-checkout set stable/packs/knowledge-manage/knowledge-graph

# 复制到 .cursor/
cd ..
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/knowledge-graph/* .cursor/

# 清理
rm -rf .cursor-genesis-temp
```

---

## 命令详情

### /integrate

**用途**：整合叶子节点上报的内容

**参数**：
- `node`: 叶子节点名称（如 cursor-genesis）
- `type`: 上报类型（capability_change/refined_knowledge/solution_feedback）

**示例**：
```
/integrate cursor-genesis capability_change
```

**流程**：
1. 检查 `data/{node}/exports/{type}/` 目录
2. 读取上报内容
3. 分析内容质量和相关性
4. 整合到 `index/topics/` 对应主题
5. 更新 `meta/recommendations.yaml`
6. 记录到 `meta/derivation/`

### /recommend

**用途**：为叶子节点生成推荐清单

**参数**：
- `node`: 叶子节点名称

**示例**：
```
/recommend cursor-genesis
```

**流程**：
1. 读取节点的 `solves` 领域
2. 从 `roots/` 和 `index/topics/` 检索相关内容
3. 分级推荐（required/recommended/optional）
4. 更新 `meta/recommendations.yaml`

### /derive

**用途**：记录推导过程

**参数**：
- `topic`: 主题名称
- `from`: 起点（第一性原理）
- `to`: 终点（具体知识）

**示例**：
```
/derive prompt-engineering context-dependency cursor-rules
```

**流程**：
1. 记录推导起点（roots/context-dependency.yaml）
2. 记录推导过程（逻辑链条）
3. 记录推导结果（index/topics/prompt-engineering.yaml）
4. 存储到 `meta/derivation/{date}-{topic}.md`

---

## 技能详情

### kg-manage.skill.yaml

知识图谱管理技能，包括：
- 节点注册和管理
- 主题索引维护
- 关联关系管理
- 推荐清单生成

### node-registry.skill.yaml

节点注册表管理技能，包括：
- 新节点注册
- 节点状态更新
- 节点能力查询
- 节点关系维护

---

## 子代理详情

### knowledge-integrator.yaml

知识整合子代理，负责：
- 自动检测叶子节点上报
- 分析上报内容质量
- 建议整合方案
- 执行整合操作

---

## 规则详情

### knowledge-graph.mdc

knowledge-graph 项目的 Cursor 规则，包括：
- 文件组织规范
- 命名约定
- YAML 格式要求
- 推导记录格式

---

## 相关文档

- [知识管理体系配置](../README.md)
- [Cursor 集成设计方案](../../../../knowledge-graph/docs/cursor-integration-design.md)
- [系统初始化配置指南](../../../../knowledge-graph/docs/system-initialization.md)
