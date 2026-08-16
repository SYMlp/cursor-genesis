---
name: harness-engineering-fieldbook
description: >-
  Harness Engineering 实战规程手册：把工程环境（尤其 Java 微服务这类远程依赖重的项目）
  改造为 AI Coding 友好状态。触发问法："harness 规程在哪"、"最小可运行子集怎么判"、
  "怎么让 AI 在本地闭环验证"、"微服务项目 AI 跑不起来怎么改造"。
  含优先级阶梯、最小可运行子集判别、脚本化、分层验证、JVM 诊断 CLI 化等 6 条规程。
---

# Harness Engineering 实战规程手册

> 迁自 kg `index/topics/ai-coding-harness-engineering.yaml`（2026-08-12 跨仓迁移波，批 2 片 1 甲-5 判决
> "规程出口 = cg harness skill"）。判断内核 3 条（归因矫正 / replace-not-mock / AI-codability 入 -ility 清单）
> 留 kg 判断层；本手册是操作规程正本。原始来源：kg `meta/archives/2026-05-21-harness-engineering-dachang-article.md`。

## 0. 定义与优先级阶梯

**Harness Engineering** = 把工程环境改造为 AI Coding 友好状态的方法论。它跟 Context Engineering
（写 CLAUDE.md / lint / 规则）互补——前者解决"AI 能不能跑、跑完能不能验证"，后者解决"AI 知不知道该怎么写"。

社区谈 Harness 时常聚焦写规则文档、配验证脚本，但 Java 微服务有更基础的瓶颈：项目在本地能跑起来吗？
CLAUDE.md 写得再好，AI 连编译都验不了，后面的一切都是空谈。

**优先级阶梯：可运行 > 可测试 > 可观测 > 工具 AI 化 > 隔离性。**

## 1. 最小可运行子集（设计起点）

找到核心链路（如 接收请求 → 调 LLM → 执行 Tool → 返回结果），只把这条链路必需的依赖搬到本地。
监控 / 链路追踪 / 服务发现这些非核心的，能排除就排除。

不要陷入"要本地化就把所有东西本地化"的完美主义——目标不是复刻线上，是让 AI 能验证核心修改。

**判别问句：删掉这个依赖，AI 改完代码后能否仍然验证修改的正确性？** 能 → 排除；不能 → 必须替代。

## 2. 真实替代，不是 mock（判断内核在 kg，此处存规程上下文）

本地替代必须用"真实可运行的替代品"：H2 不是模拟 MySQL，它就是真数据库；ProcessBuilder 不是模拟沙箱，
它就是真 bash。mock 只返回预设数据，掩盖真实问题；真实替代会暴露真实问题（SQL 语法错误 H2 也会报错）。
→ 判断内核正本：kg `ai-coding-harness-engineering.replace-not-mock`。

## 3. 脚本化一切人工操作

任何需要人登录管理台 / 复制配置 / 点击按钮的步骤，都应该有对应的脚本。**脚本就是 AI 的手**，
没有脚本 AI 就是残废的。GUI 操作对 AI 不可见，只要某步是 GUI-only，AI 就被卡死在那一步。

脚本不仅仅是为了 AI——它同时使流程可审计 / 可重放 / 可被 CI 调用。
例：fetch-switch-config.sh 替代"登录管理台 → 找配置 → 复制"；start-local.sh 替代"先编译再设环境变量再启动"。

## 4. 分层隔离、逐层验证

**编译 → 启动 → 接口可调通 → 端到端**，每层配对自动化验证手段与修复策略：

| 层 | 验证手段 | 失败时的修复方向 |
|:--|:--|:--|
| 编译 | mvn compile | 语法 / import |
| 启动 | health endpoint | 配置 / Profile |
| 接口 | API 冒烟 | 路由 / Bean 装配 |
| 端到端 | Playwright E2E | 业务逻辑 |

AI 排查问题时也需要分层定位，否则只看到"端到端失败"但不知道是哪一层错了。

## 5. JVM 诊断能力 CLI/Skill 化（成熟度下一阶）

JVM 诊断（jstack / Arthas watch / trace / tt）应通过 Skill 封装为 AI 可调用、异常以 JSON 输出，
让 AI 直接定位到代码行。成熟度阶梯：可运行 → 可测试 → **可诊断** → 可自愈。

## 6. 验证脚本 > Checklist 文档

同样的检查项，写成 Markdown checklist 还是写成 `set -e` 的 bash 脚本，对 AI 价值差一个量级——
前者 AI 只能"读到"，后者 AI 能直接执行并解析输出。技术文档里的"验收标准"若希望 AI 自主验证，
必须有可执行配对（脚本 / 测试 / lint 规则）。
→ 判断本体（约束强度四档阶梯）正本：kg `ai-collaboration.constraint-enforcement-strength-ladder`。

## 附 · Checklist 与改造对照表

原文含五类 15 项检查表（可运行/可测试/可观测/工具 AI 化/隔离性）+ 9 项"线上依赖 → 本地替代"对照表
（OSS → java.nio.file，TDDL → H2，远程沙箱 → ProcessBuilder 等）：
kg `meta/archives/2026-05-21-harness-engineering-dachang-article.md` §6 / §9.7。
