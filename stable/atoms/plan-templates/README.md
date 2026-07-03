# Plan Templates

工程化 plan 模板集合——把"plan 即协作契约"的设计原则固化为可复用的模板。

## 设计基础

- **派生原则**：`plan-as-collaboration-contract`（plan 形态必须随协作主体演化为契约，避免"我以为它知道"的协作缝隙）
- **承载规则**：`plan-execution-guide.mdc` 6 条硬约束（H-1 ~ H-6）+ `plan-architecture-navigation.mdc` 三段契约要素（0.1/0.2/0.3）
- **演化证据**：knowledge-graph 4 个月 301 个 plan 的实证演化轨迹

## 何时使用本模板

适用场景：
- 多 Phase 工程任务（≥ 3 Phase 或 ≥ 10 TODO）
- 计划中含 sub-agent 调用（任意 TODO 需要派发给 Task 工具）
- 涉及编译/测试可机器验证的产物
- 跨域影响（修改可能波及多个模块/字段/枚举）

不适用场景：
- 单步操作（"修个 typo"不需要模板）
- 纯讨论性 plan（不落代码改动）
- 一次性脚本任务（< 3 个文件改动）

## 可用模板

| 模板 ID | 适用场景 | 文件 |
|:---|:---|:---|
| `engineered-multi-phase` | 多 Phase + 多 sub-agent 协作的工程化 plan | `engineered-multi-phase-plan.template.md` |

> 后续按需扩充：单 Phase 简化版、纯前端版、纯后端版等。

## 使用步骤

### 方式 1：复制后填空

1. 复制目标模板到 `~/.cursor/plans/{your-plan-name}.plan.md`
2. 按文件内 `<<< ... >>>` 占位符填空
3. 删除 `<!-- TEMPLATE-NOTE: ... -->` 模板说明注释
4. 在 Cursor Plan mode 中通过 `CreatePlan` 工具落盘（首次创建必走 CreatePlan，参见 plan-tool-interface-split derivation）

### 方式 2：sparse checkout 后引用

```bash
cd your-project
git clone --filter=blob:none --sparse https://github.com/your-org/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set stable/atoms/plan-templates
cd ..
cp .cursor-genesis/stable/atoms/plan-templates/engineered-multi-phase-plan.template.md ~/.cursor/plans/draft.plan.md
```

## 模板结构骨架

每个模板都遵循统一 6 段结构（来自 plan-architecture-navigation 三段契约要素 + plan-execution-guide 6 条硬约束）：

```text
Frontmatter
├── name / overview
└── todos[]  ← TODO 数据结构含 4 项必标注：类型 / 模型 / 前置 / ⚠️首读

Body
├── 一、目标与现状基线   ← G1/G2/... 多目标矩阵
├── 二、契约级规格        ← plan-architecture-navigation 行为 0.1
├── 三、影响范围           ← 行为 0.2（含 grep 自检 0.2.b）
├── 四、设计文档指向        ← 行为 0.3
├── 五、Phase 流程图        ← 可选 mermaid
└── 六、回滚策略           ← 失败时如何撤回
```

## 模板演化

如果你在使用模板时发现了缺失的章节、不合理的结构、可改进的标注方式：

1. 把改进先在自己项目的 plan 中验证 ≥ 3 次
2. 通过 cursor-genesis 的 backflow 机制提交改进
3. 在 backflow PR 中说明：本次改进解决了什么"plan 协作缝隙"问题

## 相关资源

- [plan-execution-guide.mdc](https://github.com/your-org/knowledge-graph/blob/main/.cursor/rules/plan-execution-guide.mdc)
- [plan-architecture-navigation.mdc](https://github.com/your-org/knowledge-graph/blob/main/.cursor/rules/plan-architecture-navigation.mdc)
- [plan-as-collaboration-contract.yaml](https://github.com/your-org/knowledge-graph/blob/main/roots/plan-as-collaboration-contract.yaml)（派生原则）
- [plan-evolution-2026-04-18.md](https://github.com/your-org/knowledge-graph/blob/main/meta/derivation/plan-evolution-2026-04-18.md)（演化推导）
