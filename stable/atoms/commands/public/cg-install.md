# /cg-install - 安装 cursor-genesis 资产

> 提供给下游项目的命令，用于安装 cursor-genesis 资产

## 用途

下游项目（如 anfu_test）从 cursor-genesis 安装：
- Rules（.mdc 规则文件）
- Capabilities（原子能力）
- Patterns（团队编排模式）
- Packs（预组合套装）

## 子命令

### /cg-install list

列出可安装的资产。

**输出示例**：
```
可安装的套装 (packs):
- v1-talk: 对话模式套装（6 个团队模式）

可安装的规则 (rules):
- 01-project-rules.mdc: 项目宪法
- 02-project-playbook.mdc: 项目剧本
- ...

可安装的能力 (capabilities):
- 01_insight/: 洞察分析能力
- 02_architecture/: 架构设计能力
- ...
```

### /cg-install <pack>

安装指定套装。

**示例**：
```
/cg-install v1-talk
```

**流程**：
1. 执行 git sparse-checkout 拉取套装内容
2. 复制到项目的 `.cursor/rules/` 目录
3. 更新项目的 `.cursor/config.yaml`

### /cg-install --custom

自定义安装，选择具体的 atoms。

**流程**：
1. 列出所有可选的 atoms
2. 用户选择需要的组件
3. 生成 sparse-checkout 配置
4. 执行安装

## 配置

在下游项目中创建 `.cursor/cg-config.yaml`：

```yaml
# cursor-genesis 安装配置
source:
  repo: https://github.com/SYMlp/cursor-genesis
  branch: main

installed:
  pack: v1-talk
  version: 1.0.0
  date: 2026-02-26

# 自定义安装的组件
custom_atoms:
  - stable/atoms/rules/01-project-rules.mdc
  - stable/atoms/capabilities/01_insight/
```

## 底层实现

基于 Git sparse-checkout：

```bash
# 初始化 sparse-checkout
git clone --filter=blob:none --sparse https://github.com/SYMlp/cursor-genesis.git .cursor-genesis
cd .cursor-genesis

# 安装 v1-talk 套装
git sparse-checkout set stable/packs/v1-talk stable/atoms/rules stable/atoms/capabilities

# 复制到项目
cp -r stable/packs/v1-talk/* ../.cursor/rules/
```

## 更新资产

### /cg-install update

检查并更新已安装的资产。

**流程**：
1. 读取 `.cursor/cg-config.yaml` 中的安装记录
2. 检查 cursor-genesis 是否有更新
3. 提示用户确认更新
4. 执行 git pull 和复制

## 与内部命令的区别

| 命令 | 用户 | 方向 | 用途 |
|:---|:---|:---|:---|
| /cg-install | 下游项目开发者 | cursor-genesis → 下游 | 安装资产 |
| /sync | 叶子节点维护者 | knowledge-graph → 叶子节点 | 拉取知识 |
| /backflow | 下游项目开发者 | 下游 → cursor-genesis | 回流经验 |

## 注意事项

1. **版本兼容**：检查 Cursor 版本是否支持安装的功能
2. **冲突处理**：如果项目已有同名规则，提示用户选择覆盖或跳过
3. **依赖关系**：某些 patterns 依赖特定的 capabilities，自动安装依赖
