# 能力变更：Commands 层

**日期**: 2026-02-26
**类型**: capability_change
**状态**: 待审批

## 问题域

如何让 AI Agent 和用户能够方便地调用 knowledge-graph 的工具能力（search、assemble 等）。

## 解决方案摘要

新增 Commands 层，提供声明式的命令定义：
- **internal commands**: 体系内部命令（/sync、/backflow）
- **public commands**: 对外提供命令（/cg-install）
- 结合 Skills 层（.yaml）提供技术实现细节

## 适用场景

1. **知识检索场景**：用户需要搜索 knowledge-graph 中的知识
   - 使用 `/kg-search {query}` 命令
   - Agent 读取 skill 定义，自动执行 search.py

2. **内容组装场景**：用户需要组装特定主题的内容
   - 使用 `/kg-assemble {topic}` 命令
   - Agent 读取 skill 定义，自动执行 assemble.py

3. **资源安装场景**：下游项目需要安装 cursor-genesis 资源
   - 使用 `/cg-install {preset}` 命令
   - Agent 执行 git submodule + sparse checkout

## 实现形式

- **Commands**: `.cursor/commands/*.md` - Cursor 识别的 slash 命令
- **Skills**: `stable/atoms/skills/*.yaml` - 技术实现细节（参数、命令模板）
- **Tools Registry**: `knowledge-graph/meta/tools-registry.yaml` - 工具能力声明

## 边界

- 仅适用于 Cursor/Claude Code 环境
- 需要底层工具支持（如 Python 脚本）
- 命令定义与实现分离，便于维护

## 局限性

- 命令执行依赖 Agent 的理解能力
- 复杂命令可能需要多轮交互
- 错误处理需要人工介入

## 相关资源

- [Commands README](../../../stable/atoms/commands/README.md)
- [Skills README](../../../stable/atoms/skills/README.md)
- [Tools Registry](../../../../knowledge-graph/meta/tools-registry.yaml)
