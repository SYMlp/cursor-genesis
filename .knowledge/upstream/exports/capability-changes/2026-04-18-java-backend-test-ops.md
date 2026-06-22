# 能力变更：java-backend-test-ops Skill（Engineering Practices 类）

**日期**: 2026-04-18
**类型**: capability_change
**状态**: 待审批
**来源**: knowledge-graph rule_to_skill_distillation Phase 4

## 问题域

跨项目可复用的"Java 后端测试运维方法论"在 cursor-genesis 之前没有承载形式：

- 项目 A 在 soc-test-ops §六 §九 中沉淀了 Testcontainers 资源治理 + Spring Boot 3.x Null-Safety 规范两段方法论
- 项目 B / C / ... 后续如果用 Java + Spring Boot + Testcontainers，会重新踩同一类坑（InnoDB EAGAIN / MockMvc @NonNull 告警扩散）
- 派生原则 `cross-project-workflow-belongs-to-leaf-node` 要求：跨项目通用方法论应抽离到叶子节点，避免每个项目维护一份

## 解决方案摘要

新增 `stable/atoms/skills/java-backend-test-ops/SKILL.md`（方法论型 skill，YAML frontmatter + Markdown 主体，约 159 行）：

- **§一 Spring Boot 3.x Null-Safety 规范**：Spring Framework 6.1 / Boot 3.2+ 给 MockMvc API 加 @NonNull 后的应对（`MediaType.APPLICATION_JSON_VALUE` vs `MediaType.APPLICATION_JSON` + 类级 `@SuppressWarnings("null")`）
- **§二 Testcontainers 资源治理**：留守容器累积导致 InnoDB AIO 槽位耗尽（EAGAIN）的根因 + PowerShell `Clear-Testcontainers` 函数 + Bash 等价示例 + 替代方案对比 + 何时必须执行 / 不触发情况
- **§三 共享测试基类变更传播**：grep 全部继承者 + 常量/方法签名/注解全量传播 + 代码生成器模板同步
- **§四 故障案例**：EAGAIN 实战复盘 + Null-Safety 扩散事故复盘
- **§五 来源回链**：明确指向 soc-test-ops + 派生原则

## 适用场景

1. **Java 后端开发者首次遇到 Testcontainers EAGAIN**：直接召回 §二 + §四.1，避免乱用 `docker container prune -a` 误删主开发库
2. **Spring Boot 3.x 升级后 MockMvc 告警扩散**：召回 §一，30 秒修复 + 理解原理
3. **改测试基类常量前评估影响**：召回 §三，先 grep 后改
4. **任何 Java + Maven + Spring Boot 3.x + Testcontainers + Docker Desktop 项目**：作为通用工程实践参考资料

## 实现形式

- **承载文件**：`stable/atoms/skills/java-backend-test-ops/SKILL.md`（Anthropic Agent Skills 风格的 SKILL.md，目录形式）
- **资产清单引用**：
    - `stable/atoms/skills/resources-catalog.yaml` v1.2.0 → items 增加 `java-backend-test-ops`，format=methodology
    - `stable/atoms/skills/README.md` → 新增 "Engineering Practices" 段
- **pack 引用**：`stable/packs/enterprise/manifest.yaml` v1.2.0 → atoms 段引入 `skills:` 子段
- **pack 引导**：`stable/packs/enterprise/README.md` → 新增 "工程实践 Skills（v1.2 新增）" 段
- **上层检索**：`stable/knowledge/index.yaml` → 新增 `engineering-practices` category

## 边界

- **适用版本**：Java 17+ / Maven / Spring Boot 3.2 ~ 3.x / Testcontainers / Docker Desktop（Windows / macOS / Linux）
- **不适用**：纯 JUnit 单元测试（无 Spring 上下文）、纯前端测试、Docker 不在 Desktop 模式（如 CI 远程 daemon）
- **本 skill 在 cursor-genesis 仓没有配套薄触发器**——这是设计意图（叶子节点不绑定下游 globs），下游消费时由其本地 `.cursor/rules/*.mdc` 触发器承接

## 局限性

- PowerShell `Clear-Testcontainers` 函数在 macOS / Linux 用户需用 §2.4 的 Bash 等价示例
- Spring Boot 4.x 启用包级 `@NonNullApi` 后，§一规范可能简化（需重新评估）
- 项目特异性内容（`AbstractCrudControllerTest` / `BaseIntegrationTest` 等命名 / 40+ 子类规模 / 具体测试类名）保留在 `soc-test-ops`，本 skill 不重复

## 与现有资产的边界

| 已有 cursor-genesis skill | 与本 skill 的关系 |
|:---|:---|
| `cg-install.skill.yaml` / `kg-search.skill.yaml` / `kg-assemble.skill.yaml` | 命令封装型（`.skill.yaml`），主题完全不同 |
| `packs/deep-research/skills/base-research-*/SKILL.md` | 方法论型（SKILL.md），管 deep research，主题完全不同 |
| `packs/create-toolkit/skills/base-*/SKILL.md` | 方法论型，管 skill/rule/command 创建，主题完全不同 |
| 项目特化版 `soc-test-ops`（在 enterprise-soc 仓）| 本 skill 是其通用化抽离版，两者并存 |

## 派生原则

- `cross-project-workflow-belongs-to-leaf-node`（跨项目可复用方法论应抽离到叶子节点 cursor-genesis）
- `behavioral-contract-vs-workflow`（厚工作流下沉到 skill，薄触发器留 .mdc——本 skill 在叶子节点仓只承载工作流，薄触发器由下游自建）

## 相关资源

- [SKILL.md 主体](../../../stable/atoms/skills/java-backend-test-ops/SKILL.md)
- [enterprise pack manifest v1.2.0](../../../stable/packs/enterprise/manifest.yaml)
- [knowledge-graph 抽离评估 PROBE](../../../../knowledge-graph/docs/learnings/rule-skill-phase4-extraction-assessment.md)
- [knowledge-graph Phase 4 GATE 报告](../../../../knowledge-graph/docs/learnings/rule-skill-distillation-phase4-regression.md)
- [knowledge-graph 推导记录](../../../../knowledge-graph/meta/derivation/rule-to-skill-distillation-2026-04-17.md)
- [knowledge-graph changelog 2026-04 Phase 4 段](../../../../knowledge-graph/meta/changelog/2026-04.md)
