# Skills 目录

本目录包含 cursor-genesis 提供的工具无关 Skill 作者资产；宿主发现路径和调用入口由安装或适配层处理。

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

### Human–Agent Collaboration

| Skill | 描述 | 触发场景 |
|:---|:---|:---|
| [harvest-session](harvest-session/SKILL.md) | 将会话成果分诊到定位 why、项目状态、提炼候选和环境约定 | 会话收尾、交接、总结阶段成果、判断“这场值得留什么” |

> 注：方法论与协作机制使用 `SKILL.md` 目录格式（YAML frontmatter + Markdown 主体）；旧 `.skill.yaml` 仅保留命令封装型资产。

## 使用方式

### 方法论与协作机制型 `SKILL.md`

`stable/atoms/skills/<name>/` 是 CG 作者资产。消费项目应选择需要的单个 Skill，部署到 `.agents/skills/<name>/`；Claude 等宿主的镜像由各自适配层生成，不把 `.cursor/skills` 当公共作者源。

本仓尚未为 atom 级 Skill 提供通用安装器；有 Pack 映射时优先走 Pack，没有时由消费项目明确记录注入来源和版本。

### 旧命令封装型 `.skill.yaml` · Cursor 参考方式

```bash
# 1. 在 knowledge-graph 项目根目录
cd knowledge-graph

# 2. 添加 cursor-genesis 为 submodule（如果还没有）
git submodule add https://github.com/LSRabbit6/cursor-genesis.git .cursor-genesis

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

在其他 Cursor 项目中的旧参考方式：

```bash
# 1. 克隆 cursor-genesis（稀疏检出）
git clone --filter=blob:none --sparse https://github.com/LSRabbit6/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set stable/atoms/skills

# 2. 复制需要的 skills
mkdir -p ../.cursor/skills
cp stable/atoms/skills/kg-*.skill.yaml ../.cursor/skills/
```

## 旧 `.skill.yaml` 命令封装格式

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

1. 可复用方法与协作机制使用 `<name>/SKILL.md`；
2. 仅封装已有命令时，存量资产可继续使用 `.skill.yaml`，新资产应先评估是否应迁为 `SKILL.md`；
3. 只添加执行所需文件，并通过回流机制贡献回 cursor-genesis。

参考：[backflow/README.md](../../../backflow/README.md)

## 相关资源

- [Tools Registry](../../../../knowledge-graph/meta/tools-registry.yaml) - 工具能力注册表
- [Downstream Spec](../../../docs/downstream-spec.md) - 下游集成规范
- [Backflow Guide](../../../backflow/README.md) - 回流指南
