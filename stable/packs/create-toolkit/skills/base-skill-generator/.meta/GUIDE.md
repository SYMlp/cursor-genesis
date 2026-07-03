# base-skill-generator 修改与优化指南

## 1. 架构速览 (Architecture at a Glance)

本 Skill 采用 **Hybrid Generation（混合生成）** 模式：脚本 `gen.py` 负责创建标准化的目录骨架（7 层结构），而 SKILL.md 中的 Progressive Workflow 指导 AI 在骨架基础上注入智能内容。

核心设计理念是"骨架与灵魂分离"——`gen.py` 保证结构一致性（可测试、可验证），`SKILL.md` 中的 Phase 1-3 流程保证内容质量（需要 AI 的创造性判断）。

这种分离使得：
- 结构变更只需改 `gen.py`，不影响内容指引
- 内容指引变更只需改 SKILL.md，不影响物理结构
- 两者可独立测试和演进

## 2. 修改地图 (Modification Map)

| 想要改的行为 | 应该修改的文件/位置 | 注意事项 |
|:-------------|:--------------------|:---------|
| 调整生成的目录结构（增减层） | `scripts/gen.py` 的 `dirs` 列表 | 需同步更新生成的 `test_gen.py` 中的 `required_dirs` |
| 修改生成的 SKILL.md 模板内容 | `scripts/gen.py` 的 `skill_md_content` 模板字符串 | 注意保持 Frontmatter YAML 语法正确 |
| 调整 CLI 参数（如新增 `--category`） | `scripts/gen.py` 底部的 `argparse` 定义 | 需同步更新 SKILL.md 第 3 节的参数表 |
| 修改创建前的知识库阅读清单 | `SKILL.md` 的 Phase 1 → Step 1 "Read Knowledge Base" | Tier 优先级排列很重要，修改时考虑依赖关系 |
| 新增设计模式/参考文档 | `assets/docs/` 目录中新增 `.md` 文件 | 需在 SKILL.md Phase 1 的 Tier 列表中注册 |
| 修改 Scope 前缀逻辑 | `scripts/gen.py` 的 `full_name` 拼接逻辑 | 影响所有下游用户的命名 |
| 让生成过程支持元数据（Meta Layer） | `scripts/gen.py` 中增加 `.meta/` 目录和 GUIDE.md 模板生成 | 这是当前最重要的演进方向 |

## 3. 优化方向 (Optimization Roadmap)

| 方向 | 描述 | 优先级 | 发现时间 |
|:-----|:-----|:-------|:---------|
| Meta Layer 集成 | `gen.py` 应在生成骨架时自动创建 `.meta/GUIDE.md`，并根据 `--category` 参数决定是否创建 L2 工厂记录目录 | 高 | 2026-03-02 |
| 学习型工厂 | 创建新 Skill 前应自动检索同 category 的已有 Skill 元数据，作为 few-shot 范例注入 | 高 | 2026-03-02 |
| Frontmatter 增强 | 生成的 SKILL.md 模板应包含 `category`、`meta_level`、`maturity`、`tags` 字段 | 高 | 2026-03-02 |
| 模板可配置化 | `skill_md_content` 目前硬编码在 gen.py 中，应提取为 Jinja2 模板放到 `assets/templates/` | 中 | 2026-03-02 |
| 创建后验证 | 生成完成后应自动运行 `test_gen.py` 验证结构完整性 | 低 | 2026-03-02 |
| 多语言支持 | 生成的 SKILL.md 和 README 目前全英文，可考虑支持中文模板 | 低 | 2026-03-02 |

## 4. 不可动区域 (Invariants)

- **SKILL.md 的 Frontmatter `name` 字段**：值必须为 `base-skill-generator`。与目录名绑定，被 inventory updater 索引。
- **`scripts/gen.py` 的 `create_skill()` 函数签名**：`(name, scope, description, target_dir)`——被 `create-skill` Command 直接调用，改签名会导致 Command 失效。
- **`scripts/gen.py` 的 CLI 参数 `--name`**：必须保持 required=True，这是 Skill 创建的最基本输入。
- **7 层目录中的 `scripts/` 和 `SKILL.md`**：这两层是 Anthropic 标准的核心，不可移除。
- **Phase 1 → Phase 2 → Phase 3 的三阶段流程**：这是 Hybrid Generation 模式的核心，顺序不可打乱。
