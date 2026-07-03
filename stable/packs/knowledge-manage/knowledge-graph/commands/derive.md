# /derive - 记录推导过程

## 功能

记录从第一性原理到具体知识的推导过程。

## 使用

```
/derive <topic> <from> <to>
```

**参数**：
- `topic`: 主题名称
- `from`: 推导起点（第一性原理）
- `to`: 推导终点（具体知识）

## 示例

```
/derive prompt-engineering context-dependency cursor-rules
```

## 工作流程

### 1. 确定推导起点

```yaml
# 从 roots/ 读取第一性原理
# roots/context-dependency.yaml
principle: "提示词的效果依赖于模型对上下文的理解"
```

### 2. 记录推导过程

```markdown
# 推导记录：Cursor Rules 设计

**日期**: 2026-02-27
**主题**: prompt-engineering
**起点**: roots/context-dependency.yaml
**终点**: cursor-genesis/stable/atoms/rules/

## 推导起点

**第一性原理**: 上下文依赖性

"提示词的效果依赖于模型对上下文的理解"

## 推导过程

### 步骤 1：理解上下文的作用

- 模型需要理解当前任务的上下文
- 上下文包括：项目背景、代码风格、技术栈
- 上下文越丰富，提示词可以越简洁

### 步骤 2：设计上下文的组织形式

- 需要一种方式持久化上下文
- 需要一种方式让模型自动加载上下文
- Cursor Rules 是一种解决方案

### 步骤 3：定义 Cursor Rules 的结构

- 使用 .mdc 文件格式
- 包含元数据和内容
- 支持分层和组合

### 步骤 4：实现 Cursor Rules

- 创建 stable/atoms/rules/ 目录
- 定义规则的编写规范
- 提供示例和模板

## 推导结果

**具体知识**: cursor-genesis/stable/atoms/rules/

- Cursor Rules 规范
- 规则编写指南
- 示例规则库

## 验证

- 在 anfu_test 项目中使用
- 验证上下文加载效果
- 收集反馈和改进

## 关联

- **根事实**: roots/context-dependency.yaml
- **主题索引**: index/topics/prompt-engineering.yaml
- **具体实现**: cursor-genesis/stable/atoms/rules/
```

### 3. 存储推导记录

```bash
# 保存到 meta/derivation/
meta/derivation/2026-02-27-cursor-rules-design.md
```

### 4. 更新主题索引

```yaml
# 在 index/topics/prompt-engineering.yaml 中添加
derivations:
  - file: meta/derivation/2026-02-27-cursor-rules-design.md
    from: roots/context-dependency.yaml
    to: cursor-genesis/stable/atoms/rules/
    date: 2026-02-27
```

## 推导模板

```markdown
# 推导记录：{标题}

**日期**: {YYYY-MM-DD}
**主题**: {主题名称}
**起点**: {第一性原理路径}
**终点**: {具体知识路径}

## 推导起点

**第一性原理**: {原理名称}

"{原理描述}"

## 推导过程

### 步骤 1：{步骤标题}

{步骤内容}

### 步骤 2：{步骤标题}

{步骤内容}

...

## 推导结果

**具体知识**: {结果路径}

{结果描述}

## 验证

{如何验证的}

## 关联

- **根事实**: {根事实路径}
- **主题索引**: {主题索引路径}
- **具体实现**: {实现路径}
```

## 推导类型

### 1. 从原理到实现

**起点**: roots/
**终点**: 叶子节点的具体实现

**示例**：
- context-dependency → cursor-rules
- cognitive-load → capability-layers

### 2. 从实践到原理

**起点**: 叶子节点的实践经验
**终点**: roots/

**示例**：
- cursor-rules 使用经验 → prompt-essence
- teams 协作模式 → tool-adaptation

### 3. 跨领域关联

**起点**: 一个领域的知识
**终点**: 另一个领域的应用

**示例**：
- cognitive-science → ai-collaboration
- software-architecture → knowledge-management

## 相关命令

- `/integrate` - 整合叶子节点上报
- `/recommend` - 生成推荐清单

## 相关文档

- [推导记录目录](../../../meta/derivation/)
- [第一性原理](../../../roots/)
