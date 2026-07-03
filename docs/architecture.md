# cursor-genesis 架构设计文档

> 创建日期：2026-02-25
> 状态：已实现

---

## 一、项目定位

### 1.1 在知识体系中的位置

```
knowledge-graph/（上层，待建）
    │ 索引、关联、治理
    ↓
cursor-genesis/（叶子节点，已建）  ← 我们在这里
    │ 生产内容
    ↓
具体项目（使用方）
```

### 1.2 职责边界

| 职责 | 归属 |
|:---|:---|
| 内容生产 | cursor-genesis（我们生产，别人用） |
| 知识治理 | knowledge-graph 上层（定义我们是谁） |
| 回流审批 | cursor-genesis（我们决定接不接受） |

**不负责**：
- 跨领域知识关联（上层职责）
- 治理框架设计（leaf-node-framework 职责）
- 知识体系定位（上层 domains.yaml 定义）

---

## 二、核心设计决策

### 2.1 单仓库 vs 多仓库

**决策**：采用单仓库

**理由**：
- 单一仓库 = 单一真理源
- 稀疏检出已解决"按需获取"问题
- 组件和知识有强关联，原子提交更方便

**废弃方案**：三仓库（cursor-genesis + cursor-components + cursor-knowledge）

### 2.2 stable/ vs scripts/ 分离

**决策**：提示词资产和维护工具分开

| 目录 | 定位 | 内容 |
|:---|:---|:---|
| `stable/` | 提示词资产 | Prometheus 产出，可被外部稀疏检出使用 |
| `scripts/` | 维护工具 | 辅助管理提示词的脚本，不混入资产 |

**理由**：
- 提示词是 Prometheus 角色写的，是记录下来的资产
- 脚本是维护边上的东西，不跟提示词本身混淆

### 2.3 atoms + packs 两层架构

**决策**：原子层 + 套装层

| 层级 | 目录 | 定位 |
|:---|:---|:---|
| atoms | `stable/atoms/` | 最小可复用单元，细粒度 |
| packs | `stable/packs/` | 场景化组合，面向用户 |

**设计原则**：
- 原子不感知场景（一个 prompt 不知道自己会被哪个 pack 用）
- 套装面向用户（用户只需选 pack，不需要了解原子细节）

---

## 三、目录结构

```
cursor-genesis/
├── .knowledge/               # 【知识管理元数据】
│   ├── meta.yaml            # 节点元信息
│   ├── upstream/            # 与上游 knowledge-graph 的交互
│   │   ├── sync.yaml       # 同步配置和记录
│   │   └── exports/        # 待上报内容
│   └── downstream/          # 与下游项目的交互
│       ├── backflow.yaml   # 回流配置和记录
│       └── pending/        # 待处理回流
│
├── README.md
├── CHANGELOG.md
├── .gitignore
│
├── stable/                   # 【提示词资产】可被外部稀疏检出
│   ├── atoms/               # 原子层
│   │   ├── rules/          # 10 个规则文件（→ .cursor/rules/）
│   │   ├── capabilities/   # 20 个原子角色（四层认知）
│   │   ├── patterns/       # 5 个团队编排
│   │   ├── standalone/     # 12 个独立角色
│   │   └── code-templates/ # DDD/Java/Vue 脚手架
│   │
│   ├── packs/               # 套装层
│   │   ├── knowledge-manage/  # 知识管理配置
│   │   └── cursor-templates/  # 开发模板
│   │
│   └── knowledge/           # 知识层（可被上层索引）
│       ├── index.yaml      # 知识索引
│       ├── cursor-specs/   # 8 份使用手册
│       ├── architecture-decisions/ # 9 份 ADR
│       └── learnings/      # 2 份经验沉淀
│
├── workspace/                # 【本地工作台】.gitignore，不开源
│
├── scripts/                  # 【维护工具】
│   ├── legacy_scanner.py
│   └── legacy_scanner_requirements.txt
│
└── docs/                     # 【设计文档】
    └── architecture.md      # 本文件
```

---

## 四、回流机制

### 4.1 目录结构

```
.knowledge/downstream/
├── backflow.yaml             # 回流配置和记录
└── pending/                  # 待审批（PR 提交到这里）
    └── {project-hash}/
        └── {contributor}/
            └── {commit-id}/
                └── content.md
```

### 4.2 流转路径

```
PR 提交到 .knowledge/downstream/pending/
    ↓ 审批通过
记录到 .knowledge/downstream/backflow.yaml (processing)
    ↓ 处理完成
合并到 stable/ 或 .knowledge/upstream/exports/
```

### 4.3 回流内容限制

- 必须是实际应用中使用过的
- PR 提交时不需要知道最终目录
- 是否有价值、放哪里由项目自治决定

---

## 五、v1-talk 套装

### 5.1 定位

only talk，最简洁，对话触发，不用 skill 等复杂特性

### 5.2 包含的团队（5个）

| 团队 | 用途 |
|:---|:---|
| Virtual Streamlit Team | Python/Streamlit 小工具开发 |
| Strategic Research Team | 新概念/新方向的可行性研判 |
| Topic Research Team | 学术/技术课题深度调研 |
| Domain Driven Design | DDD 领域建模 |
| AI Migration Team | 遗留项目接管 |

### 5.3 核心机制

- **动态路由**：rules/teams/*.mdc 通过决策矩阵（Signal → Pattern → Role）自动分发
- **认知协议**：Think-First 法则 + 强制 `<thinking>` 块

---

## 六、与上层的关系

### 6.1 上层缺失的能力（cursor-genesis 不负责）

| 能力 | 说明 | 归属 |
|:---|:---|:---|
| 跨节点主题索引 | "AI协作"涉及哪些节点的哪些内容 | knowledge-graph |
| 查询和组装引擎 | 根据问题找到相关内容并组织 | knowledge-graph |
| 输出生成器 | 把组装好的内容变成 PPT/文档 | knowledge-graph |

### 6.2 cursor-genesis 暴露的接口

**上层链接目录**：`stable/knowledge/`

上层 knowledge-graph 通过符号链接引用本节点时，应链接到 `stable/knowledge/` 目录，而非整个仓库。

```bash
# knowledge-graph/data/nodes/ 下的符号链接（已完成接入）
cursor-genesis -> ../../../cursor-genesis/stable/knowledge
```

**原因**：
- `stable/atoms/`、`stable/packs/` 是给项目稀疏检出用的，不是给上层索引的
- `scripts/`、`.knowledge/` 是内部维护用的
- 只有 `stable/knowledge/` 是认知内容，需要被上层索引和提炼

**暴露的文件**：
- `stable/knowledge/index.yaml` - 知识索引，供上层检索
- `.knowledge/meta.yaml` - 节点元信息，遵循 leaf-node-framework 规范

---

## 七、实施路线图

```
                    ┌─────────────────────────┐
                    │   knowledge-graph       │  ← 最后建（需要多个叶子节点才有意义）
                    │   (上层索引/关联)        │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   cursor-genesis        │  ← 现在在这里 ✅
                    │   (叶子节点/提示词资产)   │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
   新项目初始化            回流流程验证              开源发布
   (scripts/init)         (.knowledge/)            (双仓库?)
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   实际项目使用           │  ← 验证整个体系
                    └─────────────────────────┘
```

### 7.1 当前状态

- [x] 目录结构创建
- [x] v1 内容迁移
- [ ] git init 初始化仓库
- [ ] 在真实项目中试用（验证稀疏检出）
- [ ] 验证回流机制
- [ ] 决定开源方案
- [ ] 建立 knowledge-graph 上层

### 7.2 建议的下一步

**先做最小闭环验证**：
1. git init cursor-genesis
2. 在一个真实小项目里试用（稀疏检出 v1-talk 套装）
3. 用起来发现问题 → 回流 → 验证回流机制

**不要在没有实际使用的情况下继续设计**，否则会越想越乱。

---

## 八、版本记录

| 版本 | 日期 | 变更 |
|:---|:---|:---|
| v1.0 | 2026-02-25 | 初始设计，从 personal_knowlegy/v1 迁移 |
