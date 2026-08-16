# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`packs/deep-research/README.md` 新增「⚠ 副本地图」**（2026-08-07/08 场）：列明四处副本各自的宿主归属与生效路径，
  以及"改契约时哪几份必改"。防的是 2026-08-07 实际发生过的事故——
  只改了 Cursor 侧两份就宣布"已从源头修好"，而真正在跑的 Claude Code 版纹丝不动。
  判据沉淀为：**改任何契约前先确认谁在运行时读它，不要按目录名推断**。

- `create-toolkit` v1.1 的首个工具无关状态型 Workflow：持久化 scaffold/refine/validate/register/complete、Human/Agent Gate、机器 Validator 与有界重试。
- `.agents/skills/create-skill-workflow` 公共作者层和 `/create-skill` Cursor 薄适配。
- `create-toolkit` v1.2 的工具无关 `create-subagent-workflow`：持久化能力分析、Skill 依赖检查、Agent Contract、机器 Validator 和宿主适配 Gate。
- Cursor `create-subagent` 薄入口与确定性 renderer；具体 model ID 和 Role Injection 不再进入公共 Agent Contract。
- `create-toolkit` v1.3 的工具无关 `create-command-workflow`：持久化 SOP 分析、Skill/Agent 依赖 Guard、Command Contract、机器 Validator 和宿主适配 Gate。
- Cursor `create-command` 薄入口与确定性 renderer；斜杠格式和 Agent Role Injection bindings 不再进入公共 Command Contract。
- `create-toolkit/LEGACY-TRIAGE.md`：逐项记录旧厚命令、Cursor 工厂/校验器和旧认知元层规范的冻结、隔离或后续迁移判决。
- `create-toolkit` v1.5 的工具无关 `audit-agent-assets`：确定性准备审计包，按公共 rubric 审计 Skill、Agent、Command、Workflow、adapter 和 prompt。
- `create-toolkit` v1.6 的工具无关 `create-rule-workflow`：将薄行为契约校验并登记为项目 `AGENTS.md` 受管 block，保留 Human Gate、持久化状态和有界重试。
- Cursor `create-rule` 薄入口与确定性 renderer；`.mdc` 路径和激活 frontmatter 不进入公共 Rule Contract。
- `stable/atoms/skills/harvest-session`：工具无关的会话成果分诊 Skill，将定位 why、项目状态、跨项目候选与环境约定送入已有容器并明确负空间。
- `stable/atoms/validators/` 新原子类目及首个条目 `state-header`：真相源 5 字段机器头契约 v1.0 + 死存根裁判验证器（stdlib-only，单文件/登记表批量，退出码可挂 CI/hook）。机制自 my-desk 驾驶舱现役实现回流提炼；Desk 为首个登记消费方——CG"可替换插件供给"路径的第一个完整闭环（回流→提炼→版本化→登记→消费）。

### Changed

- `install-pack.py` 支持 manifest 逐项声明 `.agents` / `.cursor` 目标根，并兼容旧 `.cursor` 安装记录。
- `create-toolkit` v1.4 默认只安装 3 个公共 Workflow、3 个 Cursor 薄入口和 2 个 renderer；升级时不删除旧副本，而是记录为 `retained_unmanaged`。
- `base-prompt-auditor` 保留为迁移前历史样本，不恢复默认安装；旧 Cursor / model-specific rubric 不进入公共审计核心。
- `base-rule-generator` 保留为迁移前历史样本，不恢复默认安装；旧 meta-rule 模板、Cursor `.mdc` 工厂和未经验证的多 glob 语法不进入公共核心。
- `create-project` 定性为越界历史参考，不在 CG 重建同名 Workflow；完整 workspace bootstrap 由用户级工作区编排能力承接，CG 继续提供可复用的 Pack、Rule 与注入机制。
- `session-summary` 保留为早期描述性聊天纪要样本，不恢复默认安装；其通用分诊机制进入 `harvest-session` 核心 Skill，用户级 `session-harvest` 保留个人 KG 与容器适配。
- **deep-research pack · synthesizer 溯源契约收紧**（2026-08-07/08 场）：Traceability 升为硬要求
  （*Key Findings* / *Analysis* 每条结论必须携带 inline `[Title](URL)`），
  **移除"可用 `(see notes/task-03.md)` 代替 URL"这个后门**——正是它导致 `notes/` 层攒下的
  2,234 个 URL 一个都没进入 report（引用 note 路径合法且更省事，于是永远被选中）；
  新增强制产出 `source-ledger.jsonl`、追不到源写 `[未溯源]` 显形。
  同步改动：`packs/deep-research/skills/base-research-synthesizer/SKILL.md`、
  `kg/.cursor/skill-library/research/base-research-synthesizer/SKILL.md`、
  `~/.claude/agents/base-research-synthesizer.md`（后者为 Claude Code 生效版，非本 pack 产物）。

## [1.0.0] - 2026-02-25

### Added
- 初始目录结构创建
- meta.yaml 节点元信息
- stable/ 发布目录结构
  - atoms/: rules, capabilities, standalone, code-templates
  - packs/v1-talk/: 简化版套装
  - knowledge/: 知识索引结构
- backflow/ 回流目录结构
- workspace/ 本地工作台（.gitignore）
- scripts/ 自动化脚本目录

### Migration
- 待从 personal_knowlegy/v1-rules控制cursor精华/ 迁移内容
