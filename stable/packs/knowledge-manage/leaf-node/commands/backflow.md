# /backflow - 向上游回流内容

> 认知系统体系内部命令，用于叶子节点向 knowledge-graph 回流知识

## 用途

叶子节点（如 cursor-genesis）向 knowledge-graph 上报：
- capability_change：新增或变更的能力
- refined_knowledge：从实践中整理的通用解决方案
- solution_feedback：对方案边界/局限性的新发现

## 实际执行

```bash
# 在 cursor-genesis 项目根目录
./scripts/backflow.sh status              # 查看待上报内容
./scripts/backflow.sh prepare capability  # 准备能力变更
./scripts/backflow.sh prepare knowledge   # 准备精炼知识
./scripts/backflow.sh prepare feedback    # 准备方案反馈
./scripts/backflow.sh submit              # 提交上报
```

## 子命令

### /backflow status

查看回流状态。

**输出示例**：
```
待上报内容：
- exports/pending.yaml: 11 项待上报

已上报历史：
- 2026-02-20: four-layer-cognition (已合入)
- 2026-02-15: cognitive-model-3plus2 (审核中)
```

### /backflow prepare

AI 辅助整理待上报内容。

**流程**：
1. 扫描 `stable/` 目录的变更
2. 对比 `exports/pending.yaml` 和 `local-only.yaml`
3. 识别新增的、值得上报的内容
4. 按上报格式整理到 `exports/pending.yaml`

### /backflow submit

提交上报内容到 knowledge-graph。

**流程**：
1. 读取 `exports/pending.yaml`
2. 按 `nodes-registry.yaml` 中的 `export_protocol` 格式化
3. 手动复制到 knowledge-graph（因为 knowledge-graph 是私有仓库）
4. 更新本地状态

### /backflow review

（在 knowledge-graph 侧执行）审批叶子节点的上报内容。

### /backflow process

（在 knowledge-graph 侧执行）处理已审批的内容：
- 用根事实库拆解知识
- 与其他知识建立 D1 关联
- 归入相关 topics/

## 配置位置

`meta.yaml` 中的 `reports_to_upper`：

```yaml
reports_to_upper:
  - type: capability_change
    required: true
    format: 问题域 + 解决方案摘要 + 适用场景

  - type: refined_knowledge
    required: false
    format: 问题描述 + 解决思路 + 适用场景

  - type: solution_feedback
    required: false
    format: 发现内容 + 影响范围 + 建议
```

## 上报格式要求

来自 `knowledge-graph/meta/sync-and-backflow-spec.md`：

```yaml
# exports/pending.yaml 中的每一项
- id: <唯一标识>
  title: <标题>
  source: <来源文件>
  type: capability_change | refined_knowledge | solution_feedback
  content_status: stable
  knowledge_type: fundamental | methodology | application | tool_specific
  validation_level: 1-5
  problem_domain: <问题域>
  solution_summary: <解决方案摘要>
  applicable_scenario: <适用场景>
```

## 与 /sync 的关系

```
knowledge-graph
      ↑ /backflow submit (上报)
      │
      ↓ /sync pull (拉取)
cursor-genesis
```

- `/backflow`：向上游回流内容（上报）
- `/sync`：拉取上游知识（下达）

## 可见性处理

因为 knowledge-graph 是私有仓库，cursor-genesis 是公开仓库：
- 不能直接 PR
- 采用手动同步方式
- 在 `exports/` 目录准备好内容
- knowledge-graph 维护者手动拉取并合入
