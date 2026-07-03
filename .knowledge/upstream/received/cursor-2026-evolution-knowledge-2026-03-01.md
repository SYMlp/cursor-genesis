# 上游下达：Cursor 2026 能力演进知识包

> 来源：knowledge-graph 推导
> 推导记录：meta/derivation/cursor-2026-capability-evolution-2026-03-01.md
> 原始资料：meta/archives/cursor-2026-latest-research-raw-2026-03-01.md
> 下达时间：2026-03-01
> 状态：待 cursor-genesis 消化处理

---

## 一、核心发现：Cursor 工具能力边界已质变

cursor-genesis v1.x 基于 2025 年初的 Cursor 特性设计（仅有 Rules 和 Prompts）。
截至 2026-03，Cursor 已经引入了**全新的组件类型和执行模型**。

### 1.1 新增组件类型（cursor-genesis 需要管理的新资产类型）

| 组件类型 | Cursor 引入版本 | 作用 | 对 cursor-genesis 的影响 |
|:---|:---|:---|:---|
| **Skills** | 2.4 (2026-01) | 领域知识+工作流+脚本的可复用包 | 需要新增 Skills 模板和最佳实践 |
| **Commands** | 1.6 (2025-08) | 可复用 prompt 快捷方式（`/` 触发） | 需要建立 Commands 库 |
| **Hooks** | 1.7 (2025-09) | Agent 生命周期扩展（afterFileEdit/stop） | 需要管理 Hooks 脚本模板 |
| **Plugins** | 2.5 (2026-02) | Skills+Rules+Hooks+MCP+Subagents 打包 | Packs 层可直接对齐 Plugin 格式 |

### 1.2 新增执行模型

| 执行模型 | 引入时间 | 特点 |
|:---|:---|:---|
| **Async Subagents** | 2.5 (2026-02) | 子 Agent 异步执行，可生成子子 Agent 树 |
| **Cloud Agents** | 2.4 (2026-01) | VM 隔离，可 build/test/demo，通过 Web/Slack/Mobile 触发 |
| **Long-running Agents** | 2026-02-12 | 运行数小时，先规划后执行（Ultra/Teams/Enterprise） |
| **Git Worktree 并行** | 2.5 (2026-02) | 每个 Agent 独立 worktree，物理隔离 |
| **多模型竞跑** | 2.5 (2026-02) | 同一 prompt 发给多模型，比较结果 |

### 1.3 新增交互模式

| 模式 | 特点 |
|:---|:---|
| **Plan Mode** | Shift+Tab 切换，生成可编辑 Markdown 计划，保存到 `.cursor/plans/` |
| **Debug Mode** | 证据驱动调试：复现→采集→假设→修复 |
| **Browser Control** | Agent 控制浏览器：截图、DOM、控制台、网络请求 |
| **Composer 模型** | Cursor 自有编码模型，2x Sonnet 速度，质量持平顶级 |

---

## 二、提炼认知（从根事实推导）

### 2.1 上下文加载时机梯度

**核心洞察**：Rules/Skills/Commands 的三分法本质是**上下文加载时机的梯度**。

```
Rules (Always/Auto)  →  Skills (Agent-detected)  →  Commands (Manual only)
     高置信度                 中置信度                    低置信度
   "总是相关"              "可能相关"                "只在触发时"
   始终占用上下文          按需占用上下文             触发时才占用
```

**根事实支撑**：`cognitive-limits`（上下文窗口有限 → 按相关性置信度排序加载）

**对 cursor-genesis 的指导**：
- 框架/包/语言等通用约定 → Rules（Always Apply）
- 领域工作流/复杂操作指南 → Skills（Agent Requested + `/` 调用）
- 重复性 prompt → Commands
- 不确定分类时，从 Command 开始，需要参考资料/脚本/自动检测时升级为 Skill

### 2.2 Agent 自主性连续谱

**核心洞察**：应根据任务特征匹配 Agent 自主性级别。

```
Tab 补全 → Inline Edit → Agent Chat → Plan Mode → Background Agent → Long-running Agent → Cloud Agent
最低自主性                                                                              最高自主性
```

| 自主性级别 | 适合场景 | 人的角色 |
|:---|:---|:---|
| Tab/Inline | 小函数、已知模式、格式化 | 逐字符/逐行控制 |
| Agent Chat | 单文件修改、明确需求 | 对话式指导 |
| Plan Mode | 大功能、重构、跨文件 | 审批计划后放手 |
| Background/Cloud | 文档、测试生成、依赖升级 | 只审查结果 |
| Long-running | 复杂多文件特性、大型 PR | 定义目标后离开 |

**根事实支撑**：
- `cognitive-limits` → 自主性越高，人的认知负担越低（但审查负担越高）
- `model-implementation-gap` → 自主性越高，偏离风险越高
- `subjective-irreducibility` → 价值/方向/取舍判断只能由人做

### 2.3 Plugins = Packs 的产品化

**核心洞察**：Cursor 2.5 Plugin = Skills + Rules + Hooks + MCP + Subagents 打包。
这与 cursor-genesis 的 Packs 层概念**完全同构**。

**推导**：cursor-genesis v2 的 Packs 应考虑直接输出为 Cursor Plugin 格式。

### 2.4 上下文管理最佳实践

从官方和社区提炼的**已验证**上下文管理策略：

1. **新开对话 vs 续聊判断**：
   - 下一个 prompt 依赖当前对话历史 → 续聊
   - 不依赖 → 新开（避免上下文污染）

2. **精准 `@` 引用**：积极使用 `@Files`/`@Code`/`@Branch`/`@Past Chats`

3. **上下文窗口管理**：
   - 关注 Cursor 的上下文使用量指示器
   - 达到上限前用 `/summarize` 压缩
   - 每个逻辑任务新开会话

4. **Plan Mode 作为上下文压缩器**：
   - 计划 = 把大量需求组块化(chunking)为结构化清单
   - 不是所有任务都需要 Plan Mode（小任务直接 Agent Chat）

5. **小步提交**：频繁 commit → 更清晰 diff → 更安全回滚 → 更好 Agent 对齐

### 2.5 代码审查三层体系

Cursor 2026 提供了三个层次的代码审查：

1. **生成时审查**：观察 Agent 工作，Escape 中断
2. **Agent Review**：完成后 Review → Find Issues 逐行分析
3. **Bugbot**：PR 级别自动审查 + Autofix（35% 合并率）

---

## 三、对 cursor-genesis 改造的具体建议

### 3.1 短期（可立即执行）

1. **新增 Cursor 2026 能力全景文档**
   - 位置建议：`stable/knowledge/cursor-specs/cursor-2026-capability-landscape.md`
   - 内容：版本演进、功能定位、使用场景

2. **新增 Rules/Skills/Commands 决策指南**
   - 位置建议：`stable/knowledge/cursor-specs/component-type-decision-guide.md`
   - 内容：选择矩阵、最佳实践、反模式

3. **新增上下文管理指南**
   - 位置建议：`stable/knowledge/cursor-specs/context-management-guide.md`
   - 内容：新开vs续聊、@引用、Plan Mode 使用时机

4. **新增 Agent 自主性选择指南**
   - 位置建议：`stable/knowledge/cursor-specs/agent-autonomy-guide.md`
   - 内容：连续谱、场景匹配表、风险提示

### 3.2 中期（需要设计）

5. **Commands 库建设**
   - 新增目录：`stable/atoms/commands/`
   - 预置常用 Commands：`/pr`、`/review`、`/update-deps`、`/fix-issue`

6. **Skills 模板扩展**
   - 已有的 skill 体系需要完善：添加模板 SKILL.md 样例
   - 参考 Cursor 官方规范

7. **Hooks 模板库**
   - 新增目录：`stable/atoms/hooks/`
   - 预置模板：`afterFileEdit/format.sh`、`stop/grind.ts`

### 3.3 远期（需要评估）

8. **Packs → Plugin 格式对齐**
   - 调研 Cursor Marketplace 的 Plugin 打包规范
   - 评估 cursor-genesis Packs 转换为 Plugin 的可行性

9. **v2 版本划分**
   - 建议以"支持 Skills + Commands + Hooks"为 v2 标志
   - v1 = Rules + Prompts/Capabilities（对话触发）
   - v2 = 全组件类型 + 多执行模型支持

---

## 四、Ultra 计划使用策略

作为 Ultra 会员，以下功能可以充分利用：

### 4.1 Long-running Agents
- **最佳场景**：大型重构、多文件特性开发、复杂 bug 修复
- **使用方式**：在 cursor.com/agents 启动，定义清晰目标后让 Agent 自主运行
- **注意**：确保 Rules 和 Skills 完备，减少 Agent 偏离

### 4.2 Cloud Agents
- **最佳场景**：文档更新、测试生成、依赖升级、代码审查
- **优势**：VM 隔离（零上下文泄漏）、可从手机/Slack 触发
- **技巧**：用于"离开后稍后审查"模式

### 4.3 20x 用量
- **策略**：不再犹豫使用高级模型，可以大胆尝试多模型竞跑
- **注意**：即使用量充足，仍应关注上下文质量（不是越多越好）

### 4.4 优先功能访问
- **策略**：关注 Cursor changelog，第一时间测试新功能
- **回流**：新功能的使用经验应回流到 cursor-genesis 知识库

---

## 五、参考资料索引

| # | 内容 | 位置 |
|:---|:---|:---|
| 1 | 完整原始资料 | knowledge-graph/meta/archives/cursor-2026-latest-research-raw-2026-03-01.md |
| 2 | 推导记录 | knowledge-graph/meta/derivation/cursor-2026-capability-evolution-2026-03-01.md |
| 3 | 官方最佳实践 | cursor.com/blog/agent-best-practices |
| 4 | 官方 Changelog | cursor.com/changelog |
| 5 | Rules/Skills/Commands 对比 | ibuildwith.ai/blog/cursor-rules-skills-and-commands |
