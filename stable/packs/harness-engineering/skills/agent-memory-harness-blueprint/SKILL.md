---
name: agent-memory-harness-blueprint
description: >-
  Agent 记忆 harness 约束蓝图（37 条，六章：定位/准入/存储状态/运行/代谢验证/执行面）。
  触发问法："agent 记忆的约束蓝图在哪"、"harness 约束条件取出来给壳子用"、
  "自研 agent 记忆系统该守哪些约束"、"记忆系统准入/代谢规则"、
  "无人值守 agent 的围栏/熔断/注入面约束"。
  给不带上下文的新会话或自研 harness 壳子提供可直接消费的约束集；
  配套 export.py 取件 + 验鲜（--check）+ 条号索引（--toc）。
---

# Agent 记忆 harness 约束蓝图 · 取用入口

**是什么**：一套经真实系统淬炼的 agent 记忆 harness 约束集（37 条，C-01~C-37），
每条〔约束/为什么/失效边界/溯源〕四要素。**全 37 条已转 candidate**（C-01~33 2026-08-12 用户拍板，
依据两轮零上下文消费：验收 28/33 零背景可执行 + 真实审计 33/33 全判 0 质疑 0 读不懂；
第六章 C-34~37（执行面：围栏/互斥/熔断/注入信任级）同日晚随转手桥首活三发闭环升 candidate，
含 C-34 判据修订"执行期是否有人在环"）。
方法层资产——慢变、可开源；资源池/本机配置等快变敏感件**不在此**（归 harness-environment）。

**用法**：

```bash
python export.py            # 取件（输出约束集）
python export.py --check    # 只验鲜（对照祝福时点 commit，检查 kg 源文件是否漂移）
python export.py --toc      # 只出章节+条号清单（审计/评审先拿这张表）
```

- 正文：[blueprint.md](blueprint.md)（六章 37 条 + 逐条溯源附录 + 术语表 + 开头"库/壳/环"路由表）
- 验鲜依赖 kg 仓（`D:\Project\knowledge-graph`）在盘；脱仓时优雅降级为只取件不验鲜。
- 蓝图是**投影非正本**：与 kg 宪法/特别法冲突时蓝图让位；祝福时点 commit 锚在 export.py 头部，
  与 blueprint.md 附录两处须同步改。

## 附录 · 参数化收割机三层分账（2026-08-12 随迁移波并入，源 kg ai-collaboration topic 甲-10）

自动沉淀（收割）机制设计的三层分账——own-system 定义半边，判断内核仍在 kg：

- **机制层**：生命周期钩子，跨人跨场景同一套（定位事件即时留痕 / 收尾查漏 / 归档）；
- **判据层**：「什么值得留」从**使用者画像**加载——机制层不写死任何个人偏好；
- **场景层**：案卷/任务 FRAME 注入（谁用、什么性格偏好、什么场景 → 决定沉淀什么）。

对应蓝图第四章运行约束（收割/回流环节）的实现拆分建议。判断内核
（"判据从画像加载、机制不写死偏好"）正本：kg `index/topics/ai-collaboration.yaml`
`parameterized-harvester-three-layer-split`。

## 家谱

- 淬炼源：kg 宪法（meta/constitution.md）+ 特别法 + 机制清单（遮名泛化，判断内容不外泄）
- 设计正本：kg `meta/derivation/dispatch-layer-design-2026-08-12.md`（决策点 A-E + §7 验收记录）
- kg 侧壳：`workbench/harness-export/README.md`（2026-08-12 迁移波后指向此处）
- 消费者：dispatch-kernel（toys）等自研壳；终检 = 真实 harness 项目首次消费（读数回填 kg derivation §7）
