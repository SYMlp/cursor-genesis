# /backflow - 向 cursor-genesis 回流经验

> 提供给下游项目的命令，用于向 cursor-genesis 回流实践经验

## 用途

下游项目（如 anfu_test）向 cursor-genesis 回流：
- 更好的实践方式
- 通用问题的解决方案
- 值得分享的经验

## 子命令

### /backflow status

查看回流状态。

**输出示例**：
```
本地待回流：
- .cursor/learnings/2026-02-25-dynamic-list-width.md

已提交 PR：
- #42: backflow: anfu_test - 动态列宽方案 (审核中)
```

### /backflow prepare

AI 辅助整理待回流内容。

**流程**：
1. 扫描 `.cursor/learnings/` 目录
2. 识别值得回流的内容
3. 按 cursor-genesis 格式整理
4. 生成回流清单供确认

### /backflow submit

通过 GitHub PR 提交回流。

**流程**：
1. Fork cursor-genesis 仓库（如果还没有）
2. 创建 backflow 分支
3. 将内容放到 `backflow/pending/<project>/`
4. 创建 PR

## 配置

在项目中创建 `.cursor/backflow.yaml`：

```yaml
role: downstream

upstream:
  name: cursor-genesis
  repo: https://github.com/SYMlp/cursor-genesis

learnings_path: .cursor/learnings/
project_id: <your-project-name>
```

## 回流格式要求

```yaml
# backflow/pending/<project>/<date>-<topic>.md

problem_domain: <问题域>
problem_description: <具体问题>
solution_summary: <解决方案摘要>
applicable_scenario: <适用场景>

# 可选
code_example: |
  <通用代码示例，不要项目特定代码>

related_resources:
  - <相关资源链接>
```

## 什么值得回流？

**值得回流**：
- 通用的解决方案（不只适用于你的项目）
- 对 cursor-genesis 现有组件的改进
- 新的使用模式或最佳实践
- Bug 修复或边界情况处理

**不值得回流**：
- 项目特定的配置
- 临时的 workaround
- 包含敏感信息的内容
- 未经验证的想法

## 与内部命令的区别

| 层级 | 命令 | 方向 |
|:---|:---|:---|
| 下游 → cursor-genesis | /backflow (public) | 回流实践经验 |
| cursor-genesis → knowledge-graph | /backflow (internal) | 上报精炼知识 |

两个 /backflow 是不同层级的回流：
- public 版：下游项目的原始经验 → cursor-genesis
- internal 版：cursor-genesis 整理后的知识 → knowledge-graph

## 注意事项

1. **脱敏**：确保不包含项目敏感信息
2. **通用性**：确保方案对其他项目也有价值
3. **格式**：遵循 cursor-genesis 的格式要求
4. **描述**：清晰说明问题和解决方案
