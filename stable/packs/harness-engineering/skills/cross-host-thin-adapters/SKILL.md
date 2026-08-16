---
name: cross-host-thin-adapters
description: >-
  三宿主（Cursor / Claude Code / Codex）跨宿主兼容层清单：公共作者层 vs 宿主薄适配层怎么切、
  哪些永不统一、中立运行时装哪、逐宿主验收状态。触发问法："三宿主薄适配的清单在哪"、
  "跨宿主哪些能统一哪些不能"、"AGENTS.md 三宿主怎么共用"、"中立运行时路径约定"。
  现行法清单——会随宿主版本漂，判断内核（两层划分律）在 kg。
---

# 跨宿主兼容层清单（三宿主 · 现行法）

> 迁自 kg `index/topics/ai-coding-harness-engineering.yaml` evidence
> 「跨宿主兼容层实证」（2026-08-12 跨仓迁移波；判-1 A 案 2026-08-11 已拍：判断内核留 kg，清单迁 cg）。
> 判断内核正本：kg `cross-host-author-layer-thin-adapters`——"一份资产喂多个运行时时按
> 公共作者层 + 宿主薄适配层两层治理；「同一路径」不等于「同一 ABI」；验收判据是行为级的"。
> 源件：toys `ai-runtime-compat/README.md` V0.1（本清单是它的验收快照）。

## ① 三个已验证能统一的（公共作者层）

- **项目规约**：AGENTS.md 单一作者源——Codex 原生读取 / Claude Code 薄导入 / Cursor 项目级原生读取。
- **已确认 Skill**：`.agents/skills/` 单向投影到各宿主的 skill 目录（单向，不做双向同步）。
- **UserPromptSubmit 路由数据**：共用中立路由器；找不到项目 route config 就**静默放行**
  （这条默认行为本身是薄适配层的设计要点——路由器不能因为项目没配就报错）。

## ② 永不统一的（宿主薄适配层）

登录态 / 权限 / sandbox · MCP 授权与信任 · 宿主 auto-memory · 宿主独有 hook 事件名与工具名。

机制原话：**"同一路径"不等于"同一 ABI"**。

## ③ 中立运行时路径约定

中立运行时装到宿主无关位置 `~/.agents/runtime/`，防止某一宿主（当时是 Claude）的私有路径
被误当公共层——否则两层的边界在第二次迁移时就化掉。本机路径约定，随 OS/宿主变。

## ④ 逐宿主验收状态（2026-07-27 时点读数，会漂）

- Claude Code：**全绿**（doctor/sync 实测 + 单 Skill 试点行为级通过）。
- Codex：待用户 /hooks 信任后补冒烟——**未验证**。
- Cursor CLI：运行时验收未执行——**未验证**。

∴ 判断的 experiential 效力以已实测部分（一宿主）为限；两个"未验证"如实标注，
不以文档推断代替——**文档层兼容不等于运行时通过**。

## ⑤ 实证场景

本机跨宿主兼容层 V0.1（2026-07-25~27，源件 toys `ai-runtime-compat/README.md`）；
单 Skill 试点跑在某数据安全公司的企业级项目上（脱敏口径 2026-08-11）。
