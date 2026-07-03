# Creation Failure Post-Mortem (创建失败根因追溯)

> **用途**：当通过 `base-skill-generator` 创建的 Skill、Subagent 或 Command 存在问题时，按本文档的优先级逐层排查，定位并修复根因。
> **原则**：规范是稳定的，轻易不动。修复源头应始终是"负责创建的 Skill"本身。

## 1. 追溯优先级（从近到远，不可跳级）

### 第一层：检查负责创建的 Skill 本身

**最优先排查对象**：`base-skill-generator` 的以下组件——

- **参考文档** (`assets/docs/`)：是否覆盖了出错场景？例如 `standard-subagent.md` 是否包含 `model` 字段的要求？`model-selection-guide.md` 是否列出了所有可用模型？
- **脚本模板** (`scripts/gen.py`)：生成的骨架是否包含必要字段？例如 Frontmatter 是否默认包含 `model` 占位符？
- **SKILL.md 必读清单**：Phase 1 的 Tier 列表是否引用了所有相关参考文档？

**修复方式**：直接更新 `base-skill-generator` 文件空间内的对应文件。

### 第二层：检查 Skill 引用的参考文档

如果第一层没有问题（参考文档存在，但内容不够详细或有遗漏）：

- 补充 `assets/docs/` 下对应的参考文档内容。
- 例如：`standard-subagent.md` 存在但模板中 `model` 字段写的是 `[fast | slow]` 而非具体模型 ID → 更新该文档。

**修复方式**：仍然是更新 `base-skill-generator` 文件空间内的参考文档。

### 第三层：提交规范迭代申请（极少情况）

只有在以下条件**全部满足**时，才考虑修改全局规范（`_meta/docs/standards/`）：

1. 第一层和第二层都已检查且无法解决问题；
2. 发现了**新的认知**（如 Cursor 平台新增了元数据字段、架构拓扑需要新增实体类型）；
3. 确认这是一个**系统性缺陷**，而非单次遗漏。

**修复方式**：通过 Workflow A (Fix/Update) 路由到 `meta-architect`，由其评估并修改规范。Skill 本身**不直接修改规范**。

## 2. 专门角色原则

系统中的创建和修改应由专门角色统一负责，确保产出质量一致：

| 创建对象 | 负责角色/Skill | 职责 |
| :------- | :------------- | :--- |
| 提示词 (Prompt) | `base-prompt-engineer` | 统一编写和优化所有 System Prompt |
| Skill / Subagent / Command | `base-skill-generator` | 统一生成骨架和注入逻辑 |
| 质量审计 | `base-prompt-auditor` | 统一检验产出是否符合工程标准 |

**不允许**绕过专门角色直接手写资产文件（紧急修补除外，但事后必须回溯更新负责 Skill）。

## 3. 自检清单

创建失败时，按以下顺序逐项检查：

- [ ] `base-skill-generator` 的 SKILL.md Phase 1 必读清单是否完整？
- [ ] 对应的参考文档（`standard-subagent.md`、`model-selection-guide.md` 等）是否覆盖了出错字段？
- [ ] `gen.py` 生成的骨架是否包含必要的 Frontmatter 字段？
- [ ] 若以上都完整 → 是否属于全局规范需要迭代的新认知？
