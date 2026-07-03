# 精炼知识上报：目录结构重组洞察

> 来源：cursor-genesis 叶子节点实践经验
> 日期：2026-02-28
> 类型：refined_knowledge
> 知识分类：methodology
> 验证程度：2（single_validated —— 在 cursor-genesis 项目中验证过一次）

## 问题域

在叶子节点（如 cursor-genesis）的目录结构设计中，如何在保持流程完整性的同时，让用户面对的目录结构不至于"发蒙"。

## 原始知识

"在叶子节点中，选择先在当前的基础上走通上下游流程，之后重新调整目录结构，按照一些维度把相关内容放在一起，方便用户使用时候不用看见很多同级的目录发蒙"

## 解决方案摘要

### 核心方法

1. **先打通再收缩**：在现有基础上先跑通上下游完整流程（同步、回流、上报），确保机制可用
2. **按维度重组**：流程走通后，按照使用场景的维度把相关内容归拢到一起
3. **减少同级暴露**：通过分组/嵌套减少用户在同一层级看到的目录数量

### 背后的认知

- 同级目录过多会让用户产生"选择困难"
- 相关内容放在一起后，用户只需要关注当前场景对应的一个目录
- 先打通是为了理解"什么和什么是相关的"——这个判断来自实际使用，不是理论推导

## 适用场景

- 知识管理系统的目录设计
- 任何需要兼顾"流程完整"和"用户友好"的信息架构设计
- 叶子节点接入 knowledge-graph 后的结构优化

## 具体案例：knowledge-graph 主线 vs cursor-genesis 变体

### knowledge-graph 下发的主线（sync-and-backflow-spec.md §2.5 + leaf-node-spec.md）

按**内容状态**组织目录——stable/pending/draft 各管各的：

```
<leaf-node>/
├── stable/
│   └── knowledge/
│       └── exports/          # 待上报
├── pending/
│   ├── backflow/             # 下游回流待审批
│   └── upstream/             # 上游更新待合入
├── draft/
└── .sync-status.yaml
```

组织维度：**内容生命周期**（stable → pending → draft）

### cursor-genesis 的实际变体

按**交互方向**组织目录——跟谁交互的东西放一起：

```
.knowledge/
├── upstream/                 # 跟上游有关的全部放一起
│   ├── exports/              # 待上报（主线放 stable/knowledge/exports/）
│   │   ├── capability-changes/
│   │   ├── refined-knowledge/
│   │   └── feedback/
│   ├── received/             # 上游下发的内容（主线放 pending/upstream/）
│   │   ├── roots/
│   │   ├── topics/
│   │   └── specs/
│   └── sync.yaml             # 同步配置
│
├── downstream/               # 跟下游有关的全部放一起
│   ├── pending/              # 下游回流待审批（主线放 pending/backflow/）
│   │   ├── README.md
│   │   └── TEMPLATE.md
│   └── backflow.yaml         # 回流配置
│
└── meta.yaml                 # 节点元信息
```

组织维度：**交互方向**（upstream / downstream）

### 变体的动机

主线的 status-based 组织有一个问题：**处理一个方向的交互时，需要在多个顶级目录之间跳转**。

例如做一次上游同步：
- 主线结构下：先去 `stable/knowledge/exports/` 准备上报 → 再去 `pending/upstream/` 看待合入 → 再去 `.sync-status.yaml` 查状态
- 变体结构下：全部在 `.knowledge/upstream/` 下完成

这正是"按维度把相关内容放在一起"的实践——cursor-genesis 选择的维度是"交互方向"，因为这更匹配实际使用场景的心理上下文。

### 主线没有被违反

cursor-genesis 的变体并没有违反主线定义的**约束**：
- ✅ 依然有 exports 目录（只是换了位置）
- ✅ 依然有接收上游更新的机制（received/）
- ✅ 依然有下游回流的入口（downstream/pending/）
- ✅ 依然有同步状态记录（sync.yaml + backflow.yaml）

变的是**内部组织方式**，不变的是**必须存在的功能**。

### 这说明了什么

1. **主线是边界验证器**：knowledge-graph 定义了"你必须有什么功能"，不规定"你怎么组织这些功能"
2. **变体来自实践反馈**："交互方向"这个维度不是理论推出来的，是跑过流程后才发现的——这就是"先打通再收缩"的由来
3. **柔性治理**：knowledge-graph 作为总控，控制方向（什么功能必须有），不控制内容（功能怎么放）。每个叶子节点根据自己的领域特性做易用性调整，然后通过回流把调整反馈给上游

## 待上游处理

此知识包含多层含义，建议 knowledge-graph 做第一性拆解：

1. "同级目录多导致用户迷茫" → 可能匹配 cognitive-limits 根事实，也可能指向新的根事实（认知切换成本）
2. "先打通再收缩" → 可能匹配 model-implementation-gap 根事实（通用主线+场景变体）
3. "按维度归拢" → 可能匹配 context-dependency 根事实（按问题域组织）
4. DDD 限界上下文的思想可能与此有关联
5. "控制方向不控制内容"的柔性治理模式 → 可能是 model-implementation-gap 的新推论
