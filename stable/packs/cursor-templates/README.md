# cursor-templates - Cursor 开发模板

**版本**: 1.0.0（原 v1-talk）
**日期**: 2026-02-27

---

## 概述

本目录包含 Cursor 项目开发的模板和最佳实践，与知识管理体系无关。

任何 Cursor 项目都可以使用这些模板，无需参与知识管理体系。

---

## 与 knowledge-manage 的区别

| 类别 | 用途 | 是否参与知识管理 |
|------|------|-----------------|
| **knowledge-manage/** | 知识管理体系配置 | ✓ 是 |
| **cursor-templates/** | Cursor 开发模板 | ✗ 否 |

**cursor-templates/**（本目录）：
- 纯粹的 Cursor 开发模板
- teams 协作模式、代码风格、最佳实践
- 与知识管理无关
- 任何 Cursor 项目都可以使用

**knowledge-manage/**：
- 服务于知识管理体系的运作
- 包含回流、同步、上报等机制
- 三层架构对应的配置
- 需要参与知识管理体系

---

## 目录结构

```
cursor-templates/
├── README.md                    # 本文件
├── commands/
│   └── (开发相关的命令)
├── skills/
│   └── (开发相关的技能)
├── subagents/
│   └── (开发相关的子代理)
└── rules/
    ├── teams/                  # 团队协作模式
    │   ├── frontend-backend/
    │   │   ├── frontend.mdc
    │   │   └── backend.mdc
    │   ├── fullstack/
    │   │   └── fullstack.mdc
    │   └── data-analysis/
    │       ├── analyst.mdc
    │       └── engineer.mdc
    ├── code-style.mdc          # 代码风格
    ├── best-practices.mdc      # 最佳实践
    └── error-handling.mdc      # 错误处理
```

---

## 包含的团队模式

### 1. frontend-backend/

**用途**：前后端分离开发

**团队成员**：
- `frontend.mdc` - 前端开发者
- `backend.mdc` - 后端开发者

**适用场景**：
- Web 应用开发
- 前后端分离架构
- API 驱动的项目

**触发方式**：
```
"帮我做一个前后端分离的项目"
"前端用 React，后端用 Node.js"
```

### 2. fullstack/

**用途**：全栈开发

**团队成员**：
- `fullstack.mdc` - 全栈开发者

**适用场景**：
- 快速原型开发
- 个人项目
- 小型应用

**触发方式**：
```
"帮我做一个全栈应用"
"用 Next.js 做一个项目"
```

### 3. data-analysis/

**用途**：数据分析和可视化

**团队成员**：
- `analyst.mdc` - 数据分析师
- `engineer.mdc` - 数据工程师

**适用场景**：
- 数据分析项目
- 数据可视化
- BI 报表

**触发方式**：
```
"帮我分析这个数据集"
"做一个数据看板"
```

---

## 规则文件

### code-style.mdc

**内容**：
- 命名约定
- 代码格式
- 注释规范
- 文件组织

### best-practices.mdc

**内容**：
- 错误处理
- 性能优化
- 安全实践
- 测试策略

### error-handling.mdc

**内容**：
- 异常捕获
- 错误日志
- 用户提示
- 降级策略

---

## 使用方式

### 场景 1：只用开发模板（不参与知识管理）

```bash
cd your-cursor-project

# 只拉取开发模板
git clone --filter=blob:none --sparse --depth=1 \
  https://github.com/SYMlp/cursor-genesis.git .cursor-genesis-temp

cd .cursor-genesis-temp
git sparse-checkout set stable/packs/cursor-templates

# 复制到项目
cd ..
cp -r .cursor-genesis-temp/stable/packs/cursor-templates/* .cursor/
rm -rf .cursor-genesis-temp
```

### 场景 2：同时使用开发模板和知识管理

```bash
cd your-cursor-project

# 同时拉取两者
git clone --filter=blob:none --sparse --depth=1 \
  https://github.com/SYMlp/cursor-genesis.git .cursor-genesis-temp

cd .cursor-genesis-temp
git sparse-checkout set \
  stable/packs/knowledge-manage/cursor-project \
  stable/packs/cursor-templates

# 复制到项目
cd ..
cp -r .cursor-genesis-temp/stable/packs/knowledge-manage/cursor-project/* .cursor/
cp -r .cursor-genesis-temp/stable/packs/cursor-templates/* .cursor/
rm -rf .cursor-genesis-temp
```

---

## 触发方式

### 自动触发

直接用自然语言对话，AI 会自动识别意图并激活对应团队。

**示例**：
- "我有个新想法..." → Strategic Research Team
- "帮我做个数据看板" → Data Analysis Team
- "前后端分离开发" → Frontend-Backend Team

### 手动指定

在对话中明确指定团队：

```
使用 fullstack 团队，帮我做一个博客系统
```

---

## 适用场景

### ✓ 适合使用 cursor-templates

- 个人开发者
- 快速原型开发
- 不想学习复杂配置的用户
- 只需要开发模板，不需要知识管理

### ✓ 适合同时使用 cursor-templates + knowledge-manage

- 参与知识管理体系的项目
- 需要回流改进到 cursor-genesis
- 需要搜索 knowledge-graph 的知识
- 既要开发模板，又要知识管理

---

## 版本历史

### v1.0.0（2026-02-27）

- 从 v1-talk 重命名为 cursor-templates
- 明确与 knowledge-manage 的区别
- 保持原有的 teams 和规则内容

### v1-talk（历史版本）

- 原始版本
- 包含 teams 协作模式
- only talk，对话触发

---

## 相关文档

- [知识管理体系配置](../knowledge-manage/README.md)
- [Cursor 集成设计方案](../../../knowledge-graph/docs/cursor-integration-design.md)
- [下游集成规范](../../docs/downstream-spec.md)

---

## 未来计划

### v2-advanced（计划中）

面向专业用户的高级模板：
- 更复杂的团队编排
- 更细粒度的能力分层
- 更丰富的代码模板
- 更强大的自动化

---

## 贡献指南

如果你有好的 teams 模式或规则，欢迎贡献：

1. Fork cursor-genesis 仓库
2. 添加你的 teams 或规则到 `stable/packs/cursor-templates/`
3. 提交 PR
4. 等待审核和合并

**注意**：
- cursor-templates 只接受纯开发模板
- 与知识管理相关的内容应该提交到 knowledge-manage
