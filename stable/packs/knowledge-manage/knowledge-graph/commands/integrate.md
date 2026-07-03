# /integrate - 整合叶子节点上报

## 功能

整合叶子节点（如 cursor-genesis）向 knowledge-graph 上报的内容。

## 使用

```
/integrate <node> <type>
```

**参数**：
- `node`: 叶子节点名称（如 cursor-genesis）
- `type`: 上报类型（capability_change | refined_knowledge | solution_feedback）

## 示例

```
/integrate cursor-genesis capability_change
```

## 工作流程

### 1. 检查上报内容

```bash
# 检查 data/cursor-genesis/exports/ 目录
ls -la data/cursor-genesis/exports/capability-changes/
```

### 2. 读取上报内容

```bash
# 读取每个上报文件
cat data/cursor-genesis/exports/capability-changes/2026-02-27-anfu_test-dialog-state-machine.md
```

### 3. 分析内容

- 内容质量：是否解决真实问题
- 可复用性：是否适用于其他项目
- 相关性：与哪些主题相关

### 4. 整合到主题索引

```yaml
# 更新 index/topics/ai-collaboration.yaml
items:
  - id: dialog-state-machine
    title: 多轮对话状态机
    source: cursor-genesis
    original_project: anfu_test
    file: data/cursor-genesis/exports/capability-changes/2026-02-27-anfu_test-dialog-state-machine.md
    solves: 如何管理多轮对话的状态
    keywords: [对话, 状态机, AI 协作]
```

### 5. 更新推荐清单

```yaml
# 更新 meta/recommendations.yaml
cursor-genesis:
  recommended:
    - id: dialog-state-machine
      type: capability_change
      files:
        - data/cursor-genesis/exports/capability-changes/2026-02-27-anfu_test-dialog-state-machine.md
      reason: 多轮对话状态机的实现模式
      solves: 如何管理多轮对话的状态
```

### 6. 记录推导过程

```markdown
# 创建 meta/derivation/2026-02-27-dialog-state-machine.md

# 推导记录：多轮对话状态机

**日期**: 2026-02-27
**来源**: cursor-genesis (原始项目: anfu_test)

## 推导起点

roots/context-dependency.yaml:
"提示词的效果依赖于模型对上下文的理解"

## 推导过程

1. 多轮对话需要维护上下文
2. 上下文可以用状态机建模
3. 状态机可以指导 AI 的响应

## 推导结果

index/topics/ai-collaboration.yaml:
"多轮对话状态机"
```

## 相关命令

- `/recommend` - 生成推荐清单
- `/derive` - 记录推导过程

## 相关文档

- [叶子节点规范](../../../meta/leaf-node-spec.md)
- [三层知识流动 PR 流程图](../../../docs/three-layer-pr-flow.md)
