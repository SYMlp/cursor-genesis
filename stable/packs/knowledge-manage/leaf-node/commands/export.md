# /export - 向上游上报精炼内容

## 功能

向 knowledge-graph 上报精炼的知识内容。

## 使用

```
/export status      # 查看待上报内容
/export prepare     # 准备上报清单
/export submit      # 提交 PR 到上游
```

## 工作流程

### 1. 查看待上报内容

```bash
/export status
```

**输出示例**：

```
待上报内容：

能力变更 (capability-changes/)：
  - 2026-02-26-anfu_test-dialog-state-machine.md
  - 2026-02-27-anfu_test-error-handling.md

精炼知识 (refined-knowledge/)：
  - 2026-02-26-prompt-engineering-summary.md

方案反馈 (feedback/)：
  - 2026-02-27-cursor-rules-feedback.md

总计：4 个待上报项
```

### 2. 准备上报清单

```bash
/export prepare
```

**功能**：
- 检查 `.knowledge/upstream/exports/` 目录
- 生成上报清单
- 验证格式规范
- 生成 PR 描述

**输出示例**：

```markdown
## 上报内容

**来源节点**: cursor-genesis
**上报类型**: 混合（capability_change + refined_knowledge + feedback）
**日期**: 2026-02-27

### 能力变更清单

- [x] 2026-02-26-anfu_test-dialog-state-machine.md
- [x] 2026-02-27-anfu_test-error-handling.md

### 精炼知识清单

- [x] 2026-02-26-prompt-engineering-summary.md

### 方案反馈清单

- [x] 2026-02-27-cursor-rules-feedback.md

### 来源追溯

- **原始项目**: anfu_test
- **回流路径**: anfu_test → cursor-genesis → knowledge-graph
- **验证状态**: 已在 anfu_test 中验证

### 建议处理

- 建议整合到 `index/topics/ai-collaboration.yaml`
- 建议添加到推荐清单（recommended 级别）
```

### 3. 提交 PR 到上游

```bash
/export submit
```

**功能**：
- 创建分支 `exports/{date}`
- 提交所有 exports/ 内容
- 推送到 GitHub
- 创建 PR 到 knowledge-graph

**流程**：

```bash
# 1. 创建分支
git checkout -b exports/2026-02-27

# 2. 提交内容
git add .knowledge/upstream/exports/
git commit -m "exports: 上报能力变更和精炼知识"

# 3. 推送
git push origin exports/2026-02-27

# 4. 创建 PR
gh pr create \
  --repo SYMlp/knowledge-graph \
  --title "[cursor-genesis] 能力变更上报 - 2026-02-27" \
  --body "$(cat pr-description.md)"
```

## 上报类型

### capability_change

**路径**: `stable/knowledge/exports/capability-changes/`

**内容**：
- 新增或改进的能力
- 来自下游项目的回流
- 已验证的解决方案

**示例**：
- 多轮对话状态机
- 错误处理模式
- 数据可视化组件

### refined_knowledge

**路径**: `stable/knowledge/exports/refined-knowledge/`

**内容**：
- 精炼的知识总结
- 跨项目的共性提炼
- 最佳实践归纳

**示例**：
- 提示词工程总结
- AI 协作模式归纳
- Cursor 使用技巧

### solution_feedback

**路径**: `stable/knowledge/exports/feedback/`

**内容**：
- 对上游方案的反馈
- 使用中发现的问题
- 改进建议

**示例**：
- Cursor Rules 规范反馈
- 推荐清单使用反馈
- 同步机制改进建议

## 格式要求

### 文件命名

```
{date}-{source}-{title}.md

示例：
2026-02-27-anfu_test-dialog-state-machine.md
2026-02-27-prompt-engineering-summary.md
```

### 文件内容

```markdown
# {标题}

**来源**: {项目名称}
**类型**: {capability_change | refined_knowledge | solution_feedback}
**日期**: {YYYY-MM-DD}

## 概述

[简要描述]

## 详细内容

[详细内容]

## 适用场景

[适用场景]

## 验证状态

[验证状态]
```

## 审核标准

knowledge-graph 审核时会检查：

1. **内容质量**：
   - 是否解决真实问题
   - 描述是否清晰
   - 是否有验证

2. **可复用性**：
   - 是否适用于其他项目
   - 不是项目特定的
   - 有明确的适用场景

3. **格式规范**：
   - 文件命名正确
   - 内容结构完整
   - Markdown 格式正确

4. **来源追溯**：
   - 能追溯到原始项目
   - 有回流路径
   - 有验证状态

## 上报频率

建议：
- **每周一次**：积累一周的改进后统一上报
- **重大改进**：立即上报
- **批量上报**：多个改进一起上报

## 示例

### 示例 1：单个能力变更

```bash
# 1. 查看
/export status

# 输出：
# 能力变更 (capability-changes/)：
#   - 2026-02-27-anfu_test-dialog-state-machine.md

# 2. 准备
/export prepare

# 3. 提交
/export submit
```

### 示例 2：批量上报

```bash
# 1. 查看
/export status

# 输出：
# 能力变更 (capability-changes/)：
#   - 2026-02-26-anfu_test-dialog-state-machine.md
#   - 2026-02-27-anfu_test-error-handling.md
# 精炼知识 (refined-knowledge/)：
#   - 2026-02-26-prompt-engineering-summary.md

# 2. 准备
/export prepare

# 3. 提交
/export submit
```

## 相关命令

- `/sync` - 从上游同步推荐内容
- `/backflow` - 处理下游项目回流

## 相关文档

- [叶子节点规范](../../../../knowledge-graph/meta/leaf-node-spec.md)
- [三层知识流动 PR 流程图](../../../../knowledge-graph/docs/three-layer-pr-flow.md)
