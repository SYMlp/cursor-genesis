# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **deep-research pack · synthesizer 溯源契约收紧**（2026-08-07）：Traceability 升为硬要求
  （*Key Findings* / *Analysis* 每条结论必须携带 inline `[Title](URL)`），
  **移除"可用 `(see notes/task-03.md)` 代替 URL"这个后门**——正是它导致 `notes/` 层攒下的
  2,234 个 URL 一个都没进入 report（引用 note 路径合法且更省事，于是永远被选中）；
  新增强制产出 `source-ledger.jsonl`、追不到源写 `[未溯源]` 显形。
  同步改动：`packs/deep-research/skills/base-research-synthesizer/SKILL.md`、
  `kg/.cursor/skill-library/research/base-research-synthesizer/SKILL.md`、
  `~/.claude/agents/base-research-synthesizer.md`（后者为 Claude Code 生效版，非本 pack 产物）。

### Added

- **`packs/deep-research/README.md` 新增「⚠ 副本地图」**：列明四处副本各自的宿主归属与生效路径，
  以及"改契约时哪几份必改"。防的是 2026-08-07 实际发生过的事故——
  只改了 Cursor 侧两份就宣布"已从源头修好"，而真正在跑的 Claude Code 版纹丝不动。
  判据沉淀为：**改任何契约前先确认谁在运行时读它，不要按目录名推断**。

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
