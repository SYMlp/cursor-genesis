# Skills 目录

本目录包含 cursor-genesis 提供的 skills，用于增强 Cursor/Claude Code 的能力。

## 什么是 Skill

Skill 是对工具或命令的封装，提供：

- 清晰的参数定义
- 使用场景说明
- 故障排查指南
- 相关工具链接

## 可用 Skills

### Knowledge Management

| Skill | 描述 | 使用示例 |
|:---|:---|:---|
| [kg-search](kg-search.skill.yaml) | 搜索 knowledge-graph 中的知识 | `/kg-search cursor --deep` |
| [kg-assemble](kg-assemble.skill.yaml) | 组装主题内容 | `/kg-assemble ai-collaboration --pretty` |

### Engineering Practices（v1.2 新增）

| Skill | 描述 | 触发场景 |
|:---|:---|:---|
| [java-backend-test-ops](java-backend-test-ops/SKILL.md) | Java 后端测试运维方法论：Testcontainers 资源治理 + Spring Boot 3.x Null-Safety 规范 + 共享测试基类变更传播 | Testcontainers 报 EAGAIN / MockMvc @NonNull 告警 / 改测试基类前评估影响 |

> 注：Engineering Practices 类 skill 用 SKILL.md 目录格式（YAML frontmatter + Markdown 主体），与 `.skill.yaml` 命令封装格式分开承载——前者是方法论参考，后者是命令操作。

## 使用方式

### 方式 1: 在 knowledge-graph 项目中使用

```bash
# 1. 在 knowledge-graph 项目根目录
cd knowledge-graph

# 2. 添加 cursor-genesis 为 submodule（如果还没有）
git submodule add https://github.com/your-org/cursor-genesis.git .cursor-genesis

# 3. 配置 sparse checkout
cd .cursor-genesis
git sparse-checkout init --cone
git sparse-checkout set stable/atoms/skills stable/atoms/rules
cd ..

# 4. 创建 .cursor 目录并链接 skills
mkdir -p .cursor
ln -s ../.cursor-genesis/stable/atoms/skills .cursor/skills

# 5. 现在可以使用 skills
# 在 Cursor/Claude Code 中输入 /kg-search
```

### 方式 2: 在其他项目中使用

```bash
# 1. 克隆 cursor-genesis（稀疏检出）
git clone --filter=blob:none --sparse https://github.com/your-org/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set stable/atoms/skills

# 2. 复制需要的 skills
mkdir -p ../.cursor/skills
cp stable/atoms/skills/kg-*.skill.yaml ../.cursor/skills/
```

## Skill 文件格式

每个 skill 文件包含：

```yaml
name: skill-name
version: 1.0.0
description: Skill 描述
category: 分类

command: 实际执行的命令

parameters:
  param1:
    type: string
    required: true
    description: 参数说明

use_cases:
  - scenario: 使用场景
    example: 示例命令

troubleshooting:
  - issue: 问题描述
    solution: 解决方案
```

## 设计原则

1. **声明式**：Skill 只声明"如何使用"，不包含实现
2. **自文档化**：包含完整的使用说明和故障排查
3. **可组合**：Skills 之间可以组合使用
4. **工具无关**：Skill 可以封装任何命令行工具

## 扩展 Skills

如果你创建了新的 skill：

1. 遵循现有的 YAML 格式
2. 提供完整的文档和示例
3. 通过回流机制贡献回 cursor-genesis

参考：[backflow/README.md](../../../backflow/README.md)

## 相关资源

- [Tools Registry](../../../../knowledge-graph/meta/tools-registry.yaml) - 工具能力注册表
- [Downstream Spec](../../../docs/downstream-spec.md) - 下游集成规范
- [Backflow Guide](../../../backflow/README.md) - 回流指南
