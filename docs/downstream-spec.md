# 下游项目集成规范 (Downstream Integration Specification)

> **版本**: 1.0.0
> **更新日期**: 2026-02-26
> **适用对象**: 使用 cursor-genesis 的下游项目（如 anfu_test）

## 1. 集成方式 (Integration Methods)

### 1.1 选择性克隆（推荐）

使用 Git Sparse Checkout 只获取需要的部分，减少仓库体积。

#### 场景 A: 只需要规则和能力（最常见）

```bash
# 初始化稀疏检出
git clone --filter=blob:none --sparse https://github.com/your-org/cursor-genesis.git .cursor-genesis
cd .cursor-genesis

# 选择需要的路径
git sparse-checkout set stable/atoms/rules stable/atoms/capabilities

# 可选：添加特定包
git sparse-checkout add stable/packs/v1-talk
```

#### 场景 B: 需要完整的 v1-talk 包

```bash
git clone --filter=blob:none --sparse https://github.com/your-org/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set stable/packs/v1-talk stable/atoms/rules stable/atoms/capabilities stable/atoms/patterns
```

#### 场景 C: 需要代码模板

```bash
git sparse-checkout add stable/atoms/code-templates
```

### 1.2 完整克隆

适用于需要访问所有内容（包括知识库、文档）的场景。

```bash
git clone https://github.com/your-org/cursor-genesis.git .cursor-genesis
```

### 1.3 版本固定（强烈推荐）

为确保稳定性，建议固定到特定版本或 commit：

```bash
cd .cursor-genesis
# 使用 tag
git checkout v1.0.0

# 或使用 commit hash
git checkout abc1234
```

**版本选择建议**：
- **生产项目**: 使用稳定的 tag 版本（如 v1.0.0）
- **实验项目**: 可以使用 main 分支的最新版本
- **关键项目**: 固定到特定 commit hash，避免意外更新

## 2. 可用资源 (Available Resources)

### 2.1 Atoms 层（原子组件）

#### Rules（规则文件，.mdc 格式）

位置：`stable/atoms/rules/`

| 文件 | 用途 | 使用方式 |
|:---|:---|:---|
| `production-safety.mdc` | 生产安全规则 | 复制到项目 `.cursor/rules/` |
| `project-rules.mdc` | 项目通用规则 | 复制到项目 `.cursor/rules/` |
| `playbook.mdc` | 工作手册 | 复制到项目 `.cursor/rules/` |
| `user-preferences.mdc` | 用户偏好 | 复制到项目 `.cursor/rules/` |
| `teams/*.mdc` | 团队协作规则 | 按需复制到 `.cursor/rules/teams/` |

**使用示例**：
```bash
# 在你的项目中
mkdir -p .cursor/rules/teams
cp .cursor-genesis/stable/atoms/rules/production-safety.mdc .cursor/rules/
cp .cursor-genesis/stable/atoms/rules/teams/strategic-research-team.mdc .cursor/rules/teams/
```

#### Capabilities（能力定义）

位置：`stable/atoms/capabilities/`

四层认知能力：
- `01_insight/`: 洞察与定义（需求分析、市场洞察）
- `02_architecture/`: 结构与设计（架构设计、技术评估）
- `03_engineering/`: 实现与执行（代码编写、工程落地）
- `04_quality/`: 质量与风控（逻辑审计、验收标准）

**使用方式**：作为提示词模板参考，根据项目需求调整后使用。

#### Standalone（独立角色）

位置：`stable/atoms/standalone/`

独立的、完整的角色定义，可直接使用。

#### Code Templates（代码模板）

位置：`stable/atoms/code-templates/`

包含：
- DDD 领域驱动设计模板
- Java Spring Boot 项目模板
- Vue Admin 管理后台模板

**使用方式**：复制到项目中作为脚手架，根据需求修改。

### 2.2 Packs 层（场景包）

#### v1-talk（对话场景包）

位置：`stable/packs/v1-talk/`

**适用场景**：只需要与 AI 对话协作，不涉及复杂工程。

**包含内容**：
- 6 个团队协作模式（战略研判、虚拟 Streamlit 团队、课题研究等）
- 相关的 rules 和 capabilities 引用

**使用方式**：
```bash
# 查看包的 manifest
cat .cursor-genesis/stable/packs/v1-talk/manifest.yaml

# 按照 manifest 中的引用，复制需要的 atoms
```

### 2.3 Knowledge 层（知识库）

位置：`stable/knowledge/`

**访问方式**：
1. 查看知识索引：`stable/knowledge/index.yaml`
2. 根据索引中的 `solves` 字段找到解决你问题的知识项
3. 阅读对应的 markdown 文件

**主要类别**：
- `cursor-specs/`: Cursor 使用规范和最佳实践
- `architecture-decisions/`: 架构决策记录
- `learnings/`: 经验沉淀
- `knowledge-system/`: 知识体系设计文档

## 3. 回流规范 (Backflow Specification)

当你在下游项目中发现改进点或创建了新的有价值内容时，可以回流到 cursor-genesis。

### 3.1 回流内容类型

**适合回流的内容**：
- 新的原子能力（Capability）
- 改进的规则文件（Rule）
- 新的团队协作模式（Pattern）
- 经验总结和最佳实践
- Bug 修复和优化建议

**不适合回流的内容**：
- 项目特定的业务逻辑
- 敏感信息或私有数据
- 未经验证的实验性内容

### 3.2 回流目录结构

```
.knowledge/downstream/pending/<project-hash>/<contributor-name>/<commit-id>/
├── SUBMISSION.md          # 使用 .knowledge/downstream/TEMPLATE.md 填写
├── content/               # 回流的内容
│   ├── rules/            # 如果是规则文件
│   ├── capabilities/     # 如果是能力定义
│   └── ...
└── tests/                 # 可选：测试验证材料
```

**project-hash**: 你的项目标识（如 `anfu-test-a3f2`）
**contributor-name**: 贡献者名称（如 `zhangsan`）
**commit-id**: 本次提交的简短 ID（如 `20260226-001`）

### 3.3 回流提交流程

1. **Fork 仓库**
   ```bash
   # 在 GitHub 上 fork cursor-genesis
   git clone https://github.com/your-username/cursor-genesis.git
   cd cursor-genesis
   ```

2. **创建回流分支**
   ```bash
   git checkout -b backflow/my-improvement
   ```

3. **准备回流内容**
   ```bash
   # 创建回流目录
   mkdir -p .knowledge/downstream/pending/anfu-test-a3f2/zhangsan/20260226-001
   cd .knowledge/downstream/pending/anfu-test-a3f2/zhangsan/20260226-001

   # 复制 TEMPLATE.md 并填写
   cp ../../../TEMPLATE.md SUBMISSION.md
   # 编辑 SUBMISSION.md，填写必填字段

   # 添加回流内容
   mkdir content
   cp /path/to/your/improved-rule.mdc content/
   ```

4. **提交并创建 PR**
   ```bash
   git add .
   git commit -m "backflow: 改进的战略研判团队规则"
   git push origin backflow/my-improvement

   # 在 GitHub 上创建 Pull Request
   ```

### 3.4 审核标准

回流内容将根据以下标准审核：

- **内容质量**: 是否清晰、完整、可复用
- **一致性**: 是否符合 cursor-genesis 的现有风格和结构
- **价值**: 是否解决真实问题，有实际应用场景
- **验证**: 是否经过测试验证，有使用案例

### 3.5 审核时间预期

- **简单改进**（Bug 修复、文档优化）: 1-3 天
- **新增内容**（新能力、新模式）: 3-7 天
- **重大变更**（架构调整）: 7-14 天

审核通过后，内容将记录到 `.knowledge/downstream/backflow.yaml` 的 processing 状态，最终合并到 `stable/` 目录或上报到上游。

## 4. 使用示例

### 示例 1: anfu_test 项目集成

**需求**：anfu_test 需要使用战略研判团队和 DDD 领域建模能力。

**步骤**：

```bash
# 1. 在 anfu_test 项目根目录
cd D:/Project/work/anfu_test

# 2. 克隆 cursor-genesis（稀疏检出）
git clone --filter=blob:none --sparse https://github.com/your-org/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set stable/atoms/rules stable/atoms/capabilities stable/atoms/patterns
git checkout v1.0.0  # 固定版本

# 3. 复制需要的规则
cd ..
mkdir -p .cursor/rules/teams
cp .cursor-genesis/stable/atoms/rules/teams/strategic-research-team.mdc .cursor/rules/teams/
cp .cursor-genesis/stable/atoms/rules/teams/domain-driven-design.mdc .cursor/rules/teams/

# 4. 参考能力定义
# 查看 .cursor-genesis/stable/atoms/capabilities/01_insight/concept-decoder.md
# 根据项目需求调整提示词

# 5. 在 .gitignore 中添加
echo ".cursor-genesis/" >> .gitignore
```

### 示例 2: 快速原型项目

**需求**：快速验证想法，只需要基础规则和 Streamlit 专家能力。

```bash
# 1. 最小化集成
git clone --filter=blob:none --sparse https://github.com/your-org/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set stable/atoms/rules/production-safety.mdc stable/atoms/capabilities/03_engineering/streamlit-expert.md

# 2. 复制规则
mkdir -p .cursor/rules
cp stable/atoms/rules/production-safety.mdc ../.cursor/rules/

# 3. 参考 Streamlit 专家能力定义编写提示词
```

### 示例 3: 企业级项目

**需求**：完整的工程能力，包括 DDD 模板、完整的团队协作模式。

```bash
# 1. 完整克隆
git clone https://github.com/your-org/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git checkout v1.0.0

# 2. 使用 DDD 代码模板
cp -r .cursor-genesis/stable/atoms/code-templates/ddd/* ./

# 3. 配置完整的团队规则
cp -r .cursor-genesis/stable/atoms/rules/teams/* .cursor/rules/teams/

# 4. 定期更新
# 每月检查新版本，评估是否升级
```

## 5. 常见问题 (FAQ)

### Q1: 如何更新 cursor-genesis 到新版本？

```bash
cd .cursor-genesis
git fetch origin
git checkout v1.1.0  # 切换到新版本
```

**注意**：更新前请查看 CHANGELOG.md，了解破坏性变更。

### Q2: 可以修改 cursor-genesis 中的内容吗？

**不建议直接修改**。如果需要定制：
1. 复制到你的项目中
2. 在项目中修改
3. 如果改进有通用价值，通过回流机制贡献回来

### Q3: 如何知道哪些内容适合我的项目？

1. 查看 `stable/knowledge/index.yaml` 的 `solves` 字段
2. 找到解决你问题的知识项
3. 阅读对应文档，了解相关的 atoms 和 packs

### Q4: 回流的内容会被接受吗？

只要符合审核标准（质量、一致性、价值、验证），就有很大概率被接受。建议在提交前：
- 在你的项目中充分验证
- 提供清晰的使用案例
- 遵循现有的文件结构和命名规范

### Q5: 可以只使用部分内容吗？

**完全可以**。cursor-genesis 采用原子化设计，每个 atom 都是独立的，可以按需选择。

## 6. 版本兼容性

| cursor-genesis 版本 | 最低 Cursor 版本 | 破坏性变更 |
|:---|:---|:---|
| v1.0.0 | 0.30.0 | - |
| v1.1.0 | 0.30.0 | 无（新增下游规范） |

## 7. 支持与反馈

- **问题反馈**: 在 cursor-genesis 仓库提交 Issue
- **改进建议**: 通过回流机制提交 PR
- **使用咨询**: 查看 `stable/knowledge/` 中的文档

---

**最后更新**: 2026-02-26
**维护者**: cursor-genesis 团队
