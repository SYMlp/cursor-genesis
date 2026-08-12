---
name: agent-memory-harness-blueprint
description: >-
  Agent 记忆 harness 约束蓝图（33 条，五章：定位/准入/存储状态/运行/代谢验证）。
  触发问法："agent 记忆的约束蓝图在哪"、"harness 约束条件取出来给壳子用"、
  "自研 agent 记忆系统该守哪些约束"、"记忆系统准入/代谢规则"。
  给不带上下文的新会话或自研 harness 壳子提供可直接消费的约束集；
  配套 export.py 取件 + 验鲜（--check）。
---

# Agent 记忆 harness 约束蓝图 · 取用入口

**是什么**：一套经真实系统淬炼的 agent 记忆 harness 约束集（33 条，C-01~C-33），
每条〔约束/为什么/失效边界/溯源〕四要素。已通过零上下文验收（28/33 条零背景可执行；
10 条骨架决定全部可从蓝图内推出）。方法层资产——慢变、可开源；
资源池/本机配置等快变敏感件**不在此**（归 harness-environment）。

**用法**：

```bash
python export.py            # 取件（输出约束集）
python export.py --check    # 只验鲜（对照祝福时点 commit，检查 kg 源文件是否漂移）
```

- 正文：[blueprint.md](blueprint.md)（五章 33 条 + 逐条溯源附录 + 术语表）
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
