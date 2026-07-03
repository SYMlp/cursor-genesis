# Enterprise Pack

> 面向企业级多模块项目的完整 AI 协作治理套件

## 这个 Pack 解决什么问题

当项目规模扩展到 50+ 模块时，AI 协作的瓶颈不再是代码生成能力，而是**Agent 认知治理**：

- Agent 读取过多无关文件，上下文窗口被历史代码污染
- 没有约束时 Agent 从旧代码推断架构，导致架构漂移
- 模块数量多，无法为每个模块手写规则

**Enterprise Pack 的核心创新**：生成式规则系统（Meta-Rules）——用一套「创建规则的规则」驱动 Agent 为每个业务域自动生成专属规则，在整个项目生命周期内锁定架构认知。

## 已验证的效果

来自首个落地案例：一个大型全栈企业系统（50+ 模块，Spring Boot + Vue 3）

| 指标 | 结果 |
|:---|:---|
| 交付周期 | 零到验收 < 2 周 |
| Token 读取浪费 | 减少 60%（Design-Authority 规则生效） |
| 字段缺失率 | 从 35% 降至接近 0（ODD 驱动） |
| 生成的域规则数 | 16 条（由 4 条 Meta-Rules 驱动生成） |
| 覆盖模块 | 50+ |

## 核心组件

### 4 条 Meta-Rules（`stable/atoms/rules/enterprise/`）

| 规则 | 作用 |
|:---|:---|
| `design-authority.mdc` | 设计文档是唯一权威，禁止 Agent 从旧代码推断架构 |
| `routing-engine.mdc` | 意图路由表，将模糊自然语言映射为确定性文档读取路径 |
| `ontology-driven-dev.mdc` | 本体驱动开发，Agent 从领域本体而非代码推导字段和逻辑 |
| `rule-evolution.mdc` | 规则自演化，Agent 行为路径低效时触发规则优化记录 |

### Plan 模板（`stable/atoms/plan-templates/`，v1.1 新增）

工程化协作 plan 的可复用模板——把"plan 即协作契约"的设计原则固化为可复制的脚手架：

| 模板 | 适用 | 解决的问题 |
|:---|:---|:---|
| `engineered-multi-phase-plan.template.md` | 多 Phase + 多 sub-agent + 编译可验证的工程任务 | sub-agent clean context 启动时的"我以为它知道"协作缝隙 |

派生原则：`plan-as-collaboration-contract`（plan 形态必须随协作主体演化为契约）。
抽象自 soc 4 月 81 个工程化 plan（91% 完成率）的成熟形态。

### 工程实践 Skills（`stable/atoms/skills/`，v1.2 新增）

跨项目通用的工程实践方法论以独立 skill 形式承载，避免每个项目重复维护同一份运维经验：

| Skill | 适用 | 解决的问题 |
|:---|:---|:---|
| `java-backend-test-ops/SKILL.md` | Java + Maven + Spring Boot 3.x + Testcontainers + Docker Desktop | Testcontainers 留守容器累积导致 InnoDB EAGAIN（AIO 槽位耗尽）；Spring Boot 3.x MockMvc API @NonNull 注解告警扩散；共享测试基类变更传播失控 |

派生原则：`cross-project-workflow-belongs-to-leaf-node`（跨项目可复用方法论应抽离到叶子节点 cursor-genesis）。
抽象自 soc-test-ops §六 §九 通用化抽离（见 knowledge-graph rule_to_skill_distillation Phase 4）。

### ODD 方法论（`methodology/`）

领域本体的生成和维护方法论——从业务文档到形式化本体的可复制流程：

| 文件 | 回答的问题 |
|:---|:---|
| `ontology-extraction-rules.md` | 从哪里提取、如何不遗漏 |
| `ontology-document-guide.md` | 本体文档怎么写、分几级 |
| `ontology-validation-rules.md` | 本体如何校验（对齐/自洽/跨域） |
| `ontology-maintenance-guide.md` | 本体如何随项目演化持续维护 |

## 快速安装

```bash
git clone --filter=blob:none --sparse https://github.com/LSRabbit6/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set \
  stable/packs/enterprise \
  stable/atoms/rules/enterprise \
  stable/atoms/plan-templates \
  stable/atoms/skills/java-backend-test-ops
```

将 `stable/atoms/rules/enterprise/*.mdc` 复制到你项目的 `.cursor/rules/` 目录，然后按 `methodology/` 的流程为你的业务域建立本体。

复制 `stable/atoms/plan-templates/engineered-multi-phase-plan.template.md` 作为后续 plan 创建的脚手架（首次创建 plan 时复制并按 `<<< ... >>>` 占位符填空）。

如果你的项目用 Java + Spring Boot 3.x + Testcontainers，复制 `stable/atoms/skills/java-backend-test-ops/SKILL.md` 到 `.cursor/skills/java-backend-test-ops/SKILL.md`，让 Agent 在你跑集成测试遇到 EAGAIN 或 MockMvc 告警时主动召回。

## 适用场景

- 企业级多模块后端（20+ 模块起步有收益，50+ 模块效果显著）
- 有明确业务域划分的系统（DDD 风格，或监管驱动的领域划分）
- 使用设计文档驱动开发的团队（有需求规格、架构设计等文档资产）

## 与其他 Pack 的区别

| Pack | 定位 |
|:---|:---|
| `v1-talk` | 个人开发者，对话触发，无需配置 |
| `enterprise` | 企业项目，规则驱动，本体支撑，治理 Agent 认知 |
