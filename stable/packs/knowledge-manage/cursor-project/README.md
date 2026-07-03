# cursor-project 配置

**层级**: L1 执行层
**用途**: Cursor 真实项目使用的知识管理配置

---

## 概述

本目录包含 Cursor 真实项目（如 anfu_test）使用知识管理体系的配置，包括：

- 回流改进到 cursor-genesis
- 搜索 knowledge-graph 的知识
- 组装知识内容
- 安装 cursor-genesis 资源

---

## 目录结构

```
cursor-project/
├── README.md                    # 本文件
��── commands/
│   ├── backflow.md             # /backflow - 回流改进到 cursor-genesis
│   ├── kg-search.md            # /kg-search - 搜索知识图谱
│   └── kg-assemble.md          # /kg-assemble - 组装知识内容
├── skills/
│   ├── kg-search.skill.yaml    # 知识图谱搜索技能
│   ├── kg-assemble.skill.yaml  # 知识内容组装技能
│   ├── cg-install.skill.yaml   # cursor-genesis 安装技能
│   └── resources-catalog.yaml  # 资源目录
├── subagents/
│   └── knowledge-assistant.yaml # 知识助手子代理
└── rules/
    └── project-integration.mdc  # 项目集成规则
```

---

## 使用场景

### 场景 1：在 Cursor 项目中集成

假设你有一个 Cursor 项目 `anfu_test`：

```bash
cd d:/Project/work/anfu_test

# 1. 拉取知识管理配置和开发模板
git clone --filter=blob:none --sparse --depth=1 \
  https://github.com/SYMlp/cursor-genesis.git .cursor-genesis-temp

cd .cursor-genesis-temp
git sparse-checkout set \
  stable/packs/knowledge-manage/cursor-project \
  stable/packs/cursor-templates

# 2. 复制到项目
cd ..
mkdir -p .cursor
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/cursor-project/* .cursor/
cp -r .cursor-genesis-temp/stable/packs/cursor-templates/* .cursor/

# 3. 清理
rm -rf .cursor-genesis-temp
```

### 场景 2：使用知识管理功能

在 Cursor 中：

```
# 搜索知识
/kg-search AI 协作

# 组装知识内容
/kg-assemble prompt-engineering

# 回流改进
/backflow
```

---

## 命令详情

### /backflow

**用途**：回流改进到 cursor-genesis

**功能**：
- 创建回流目录结构
- 填写回流模板
- 提交 PR 到 cursor-genesis

**使用流程**：

1. **触发命令**：
   ```
   /backflow
   ```

2. **填写回流内容**：
   - 问题描述：遇到的问题
   - 解决方案：如何解决的
   - 适用场景：什么情况下适用
   - 测试验证：如何验证的
   - 边界和局限性：方案的边界

3. **提交 PR**：
   - Fork cursor-genesis 仓库
   - 创建分支 `backflow/{project}-{feature}`
   - 添加回流内容到 `backflow/pending/{project}/`
   - 提交 PR

**回流模板**：

```markdown
# 能力改进：{标题}

**来源项目**: anfu_test
**改进类型**: capability_change | refined_knowledge | solution_feedback
**日期**: 2026-02-27

## 问题描述

[描述遇到的问题]

## 解决方案

[描述解决方案]

## 适用场景

1. **场景1**: [描述]
2. **场景2**: [描述]

## 测试验证

[如何验证的]

## 边界和局限性

[方案的边界]
```

### /kg-search

**用途**：搜索 knowledge-graph 的知识

**参数**：
- `query`: 搜索关键词
- `--deep`: 深度搜索（包含文件内容）

**示例**：
```
/kg-search AI 协作
/kg-search prompt --deep
```

**功能**：
- 跨节点搜索知识内容
- 返回相关的知识项
- 显示 solves 和文件路径

**输出示例**：
```
找到 3 个相关结果：

1. [cursor-genesis] AI 协作基础
   - 文件: stable/knowledge/cursor-specs/ai-collaboration-basics.md
   - 解决: 如何设计有效的 AI 协作提示词
   - 相关度: 95%

2. [knowledge-graph] 提示词工程
   - 文件: index/topics/prompt-engineering.yaml
   - 解决: 提示词的不同组织形式
   - 相关度: 87%

3. [cursor-genesis] Cursor Rules 规范
   - 文件: stable/knowledge/cursor-specs/cursor-rules-spec.md
   - 解决: 如何正确编写和组织 Cursor Rules
   - 相关度: 76%
```

### /kg-assemble

**用途**：组装知识内容

**参数**：
- `topic`: 主题名称
- `--pretty`: 美化输出

**示例**：
```
/kg-assemble prompt-engineering --pretty
```

**功能**：
- 根据主题索引组装结构化内容
- 包含标题、概述、章节、参考文献
- 可导出为 Markdown 或 PPT

**输出示例**：
```markdown
# 提示词工程

## 概述

提示词工程是设计和优化 AI 提示词的方法论...

## 核心概念

### 1. 上下文依赖性

提示词的效果依赖于模型对上下文的理解...

### 2. 提示词本质

一切 AI 交互工具本质上都是提示词...

## 最佳实践

1. 明确任务目标
2. 提供充分上下文
3. 使用结构化格式
...

## 参考文献

- [Cursor Rules 规范](...)
- [AI 协作基础](...)
```

---

## 技能详情

### kg-search.skill.yaml

知识图谱搜索技能，包括：
- 跨节点搜索
- 关键词匹配
- 相关度排序
- 结果展示

**技术实现**：
- 调用 knowledge-graph 的 `tools/search.py`
- 支持浅层搜索（文件名、标题）
- 支持深度搜索（文件内容）

### kg-assemble.skill.yaml

知识内容组装技能，包括：
- 主题索引解析
- 内容结构化组装
- 格式美化
- 导出功能

**技术实现**：
- 调用 knowledge-graph 的 `tools/assemble.py`
- 支持 Markdown 输出
- 支持 PPT 生成（通过 /pptx skill）

### cg-install.skill.yaml

cursor-genesis 安装技能，包括：
- 稀疏检出指导
- 目录结构说明
- 安装验证
- 使用示例

### resources-catalog.yaml

资源目录，包括：
- cursor-genesis 可用资源列表
- 每个资源的用途说明
- 拉取路径
- 使用示例

---

## 子代理详情

### knowledge-assistant.yaml

知识助手子代理，负责：
- 自动推荐相关知识
- 监控可回流的改进
- 提醒知识更新
- 生成学习报告

---

## 规则详情

### project-integration.mdc

项目集成规则，包括：
- 如何组织 .cursor/ 目录
- 如何使用知识管理命令
- 如何回流改进
- 最佳实践

---

## 回流流程

```
anfu_test (真实项目)
    ↓ 产生改进
    ↓ /backflow 命令
    ↓ 填写回流模板
    ↓ 提交 PR
    ↓
cursor-genesis (叶子节点)
    ↓ 接收 PR
    ↓ 审核内容
    ↓ 精炼到 exports/
    ↓ 提交 PR
    ↓
knowledge-graph (上游)
    ↓ 整合到 index/topics/
    ↓ 更新推荐清单
```

---

## 与 cursor-templates 的配合

**cursor-project/**（本目录）：
- 知识管理相关
- 回流、搜索、组装

**cursor-templates/**：
- 开发模板
- teams、规则、最佳实践

**配合使用**：
```bash
# 同时拉取两者
git sparse-checkout set \
  stable/packs/knowledge-manage/cursor-project \
  stable/packs/cursor-templates

# 复制到项目
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/cursor-project/* .cursor/
cp -r .cursor-genesis-temp/stable/packs/cursor-templates/* .cursor/
```

---

## 快速开始

### 1. 安装

```bash
cd your-cursor-project
git clone --filter=blob:none --sparse --depth=1 \
  https://github.com/SYMlp/cursor-genesis.git .cursor-genesis-temp
cd .cursor-genesis-temp
git sparse-checkout set \
  stable/packs/knowledge-manage/cursor-project \
  stable/packs/cursor-templates
cd ..
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/cursor-project/* .cursor/
cp -r .cursor-genesis-temp/stable/packs/cursor-templates/* .cursor/
rm -rf .cursor-genesis-temp
```

### 2. 验证

在 Cursor 中：
```
/kg-search test
```

如果能搜索到结果，说明安装成功。

### 3. 使用

- 开发时使用 cursor-templates 的 teams 和规则
- 遇到可复用的改进时使用 `/backflow`
- 需要查找知识时使用 `/kg-search`

---

## 相关文档

- [知识管理体系配置](../README.md)
- [Cursor 集成设计方案](../../../../knowledge-graph/docs/cursor-integration-design.md)
- [下游集成规范](../../../docs/downstream-spec.md)
- [回流工作流程](../../../../BACKFLOW-WORKFLOW.md)
