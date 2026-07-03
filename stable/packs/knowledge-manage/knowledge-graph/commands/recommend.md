# /recommend - 生成推荐清单

## 功能

为叶子节点生成推荐内容清单。

## 使用

```
/recommend <node>
```

**参数**：
- `node`: 叶子节点名称（如 cursor-genesis）

## 示例

```
/recommend cursor-genesis
```

## 工作流程

### 1. 读取节点信息

```yaml
# 从 index/nodes-registry.yaml 读取
nodes:
  cursor-genesis:
    solves:
      - Cursor AI 协作的规则和能力定义
      - 提示词工程的最佳实践
      - AI 辅助开发的工作流模式
    domain: ai-collaboration
```

### 2. 检索相关内容

从以下位置检索：
- `roots/` - 第一性原理
- `index/topics/` - 主题索引

匹配条件：
- domain 匹配
- solves 相关
- keywords 重叠

### 3. 分级推荐

**required**（必须拉取）：
- 设计推导依赖的根事实
- 治理框架规范

**recommended**（强烈推荐）：
- 领域相关的通用知识
- 解决核心问题的内容

**optional**（可选）：
- 扩展知识
- 相关但非核心的内容

### 4. 生成推荐清单

```yaml
# 更新 meta/recommendations.yaml
recommendations:
  cursor-genesis:
    required:
      - id: root-facts-cognitive
        type: root_facts
        files:
          - roots/cognitive-science.yaml
          - roots/context-dependency.yaml
        reason: cursor-genesis 的设计推导依赖这些根事实
        priority: high
        size: small

    recommended:
      - id: ai-collaboration
        type: ai_general_knowledge
        files:
          - index/topics/ai-collaboration.yaml
        reason: 提示词设计的理论基础
        solves: 如何设计有效的 AI 协作提示词
        priority: medium
        size: medium

    optional:
      - id: cognitive-psychology
        type: root_facts
        files:
          - roots/miller-7plus2.yaml
        reason: 理解认知限制，优化信息组织
        when_needed: 设计复杂的团队编排时
        priority: low
        size: small
```

## 推荐策略

### 1. 必须推荐（required）

**条件**：
- 叶子节点的设计推导依赖
- 治理框架规范
- 核心交互协议

**特点**：
- 数量少（2-3 个）
- 体积小
- 优先级高

### 2. 强烈推荐（recommended）

**条件**：
- 领域高度相关
- 解决核心问题
- 通用性强

**特点**：
- 数量适中（3-5 个）
- 体积中等
- 优先级中

### 3. 可选推荐（optional）

**条件**：
- 扩展知识
- 特定场景需要
- 相关但非核心

**特点**：
- 数量较多（5-10 个）
- 体积不限
- 优先级低

## 相关命令

- `/integrate` - 整合叶子节点上报
- `/derive` - 记录推导过程

## 相关文档

- [节点注册表](../../../index/nodes-registry.yaml)
- [推荐清单](../../../meta/recommendations.yaml)
