# knowledge-manage - 知识管理体系配置

**版本**: 1.0.0
**日期**: 2026-02-27

---

## 概述

本目录包含知识管理体系在 Cursor 中的配置，分为三个子目录，对应三层架构：

```
knowledge-manage/
├── knowledge-graph/     # L3 认知层配置
├── leaf-node/          # L2 模板层配置（叶子节点通用）
└── cursor-project/     # L1 执行层配置（Cursor 真实项目）
```

---

## 三层对应关系

### L3: knowledge-graph/

**用途**：knowledge-graph 项目自己使用的 Cursor 配置

**适用场景**：
- 在 knowledge-graph 项目中操作
- 整合叶子节点上报的内容
- 生成推荐清单给叶子节点
- 记录推导过程

**拉取方式**：
```bash
cd your-knowledge-graph-project
git sparse-checkout set stable/packs/knowledge-manage/knowledge-graph
```

### L2: leaf-node/

**用途**：叶子节点通用框架

**适用场景**：
- 创建新的叶子节点（如 vscode-genesis、jetbrains-genesis）
- 需要实现与 knowledge-graph 的交互
- 需要处理下游项目的回流

**核心机制**：
- **sync**：从上游同步推荐内容
- **backflow**：处理下游项目回流
- **export**：向上游上报精炼内容

**拉取方式**：
```bash
cd your-new-leaf-node
git sparse-checkout set stable/packs/knowledge-manage/leaf-node
```

### L1: cursor-project/

**用途**：Cursor 真实项目使用的知识管理配置

**适用场景**：
- 在 Cursor 真实项目中使用（如 anfu_test）
- 回流改进到 cursor-genesis
- 搜索 knowledge-graph 的知识
- 组装知识内容

**拉取方式**：
```bash
cd your-cursor-project
git sparse-checkout set \
  stable/packs/knowledge-manage/cursor-project \
  stable/packs/cursor-templates
```

---

## 与 cursor-templates 的区别

| 类别 | 用途 | 是否参与知识管理 |
|------|------|-----------------|
| **knowledge-manage/** | 知识管理体系配置 | ✓ 是 |
| **cursor-templates/** | Cursor 开发模板 | ✗ 否 |

**knowledge-manage/**：
- 服务于知识管理体系的运作
- 包含回流、同步、上报等机制
- 三层架构对应的配置

**cursor-templates/**：
- 纯粹的 Cursor 开发模板
- teams 协作模式、代码风格、最佳实践
- 与知识管理无关

---

## 快速开始

### 场景 1：我是 knowledge-graph 项目

```bash
cd d:/Project/knowledge-graph
git clone --filter=blob:none --sparse https://github.com/SYMlp/cursor-genesis.git .cursor-genesis-temp
cd .cursor-genesis-temp
git sparse-checkout set stable/packs/knowledge-manage/knowledge-graph
cd ..
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/knowledge-graph/* .cursor/
rm -rf .cursor-genesis-temp
```

### 场景 2：我想创建新的叶子节点

```bash
cd your-new-leaf-node
git clone --filter=blob:none --sparse https://github.com/SYMlp/cursor-genesis.git .cursor-genesis-temp
cd .cursor-genesis-temp
git sparse-checkout set stable/packs/knowledge-manage/leaf-node
cd ..
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/leaf-node/* .cursor/
rm -rf .cursor-genesis-temp
```

### 场景 3：我是 Cursor 真实项目

```bash
cd your-cursor-project
git clone --filter=blob:none --sparse https://github.com/SYMlp/cursor-genesis.git .cursor-genesis-temp
cd .cursor-genesis-temp
git sparse-checkout set \
  stable/packs/knowledge-manage/cursor-project \
  stable/packs/cursor-templates
cd ..
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/cursor-project/* .cursor/
cp -r .cursor-genesis-temp/stable/packs/cursor-templates/* .cursor/
rm -rf .cursor-genesis-temp
```

---

## 相关文档

- [Cursor 集成设计方案](../../../knowledge-graph/docs/cursor-integration-design.md)
- [系统初始化配置指南](../../../knowledge-graph/docs/system-initialization.md)
- [三层知识流动 PR 流程图](../../../knowledge-graph/docs/three-layer-pr-flow.md)

---

## 目录详情

- [knowledge-graph/](./knowledge-graph/) - L3 认知层配置
- [leaf-node/](./leaf-node/) - L2 模板层配置
- [cursor-project/](./cursor-project/) - L1 执行层配置
