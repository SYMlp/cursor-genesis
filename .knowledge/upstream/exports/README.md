# Exports 目录

此目录用于向 knowledge-graph 上报内容。

## 目录结构

```
exports/
├── capability-changes/    # 能力变更（必须）
├── refined-knowledge/     # 精炼知识（可选）
└── feedback/              # 方案反馈（可选）
```

## 上报流程

1. **准备内容**：在对应目录下创建 markdown 文件
2. **格式要求**：参考 knowledge-graph/index/nodes-registry.yaml 中的 format 定义
3. **提交 PR**：提交到 cursor-genesis 仓库
4. **上游拉取**：knowledge-graph 通过稀疏检出拉取此目录

## 文件命名规范

- `capability-changes/YYYY-MM-DD-{capability-name}.md`
- `refined-knowledge/YYYY-MM-DD-{topic}.md`
- `feedback/YYYY-MM-DD-{feedback-type}.md`

## 示例

参考 `capability-changes/2026-02-26-commands-layer.md`
