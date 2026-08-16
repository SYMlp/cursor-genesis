---
name: create-rule-workflow
description: 创建、恢复或重试一个跨宿主项目 Rule 时使用；把薄行为契约生成并校验为 AGENTS.md 受管 block，限制规则长度、指令强度、激活边界和宿主格式泄漏，再由 Cursor 等宿主 adapter 投影自身激活格式。
---

# Create Rule Workflow

把稳定、薄且需要常驻或条件生效的行为约束写入项目 `AGENTS.md`。不要建立第二份公共 Rule 作者库；Workflow 中的 draft 只是登记前状态，登记后的 `AGENTS.md` block 才是唯一公共来源。

## 类型边界

先回答三问：

1. 不读这条约束会造成严重错误，还是只让流程不够顺？
2. 它必须每轮生效，还是只在路径、意图或显式调用下生效？
3. 它是否包含多步 SOP、模板或复杂决策表？

只有薄行为契约进入 Rule。多步 SOP 创建 Command / Workflow；需要自主判断创建 Agent；按需操作知识创建 Skill。

## 状态流

```text
analyze → scaffold → refine → validate → register → adapt → complete
```

1. 初始化：

   ```powershell
   python <skill-dir>/scripts/workflow.py init `
     --state docs/state/create-rule/safe-edit.json `
     --project-root . `
     --name safe-edit `
     --description "Bound risky file changes"
   ```

2. 通过分析 Gate：

   ```powershell
   python <skill-dir>/scripts/workflow.py resume `
     --state docs/state/create-rule/safe-edit.json `
     --event analyzed `
     --activation paths `
     --path "src/critical/**" `
     --trigger "When changing critical source files" `
     --rationale "A missed constraint can cause irreversible regressions" `
     --note "Thin behavioral contract confirmed"
   ```

3. 运行 scaffold，精修 draft，确认后运行 Validator：

   ```powershell
   python <skill-dir>/scripts/workflow.py run --state docs/state/create-rule/safe-edit.json
   python <skill-dir>/scripts/workflow.py resume --state docs/state/create-rule/safe-edit.json --event refined --note "Rule completed"
   python <skill-dir>/scripts/workflow.py run --state docs/state/create-rule/safe-edit.json
   ```

4. 在 Human Gate 后登记到 `AGENTS.md`：

   ```powershell
   python <skill-dir>/scripts/register_rule.py `
     --project-root . `
     --rule-file docs/state/create-rule/drafts/safe-edit.md `
     --agents-file AGENTS.md `
     --confirm-id safe-edit

   python <skill-dir>/scripts/workflow.py resume `
     --state docs/state/create-rule/safe-edit.json `
     --event registered `
     --note "Registered after diff review"
   ```

5. 生成需要的宿主 adapter，再用 `adapted` 记录真实产物；没有额外 adapter 时用 `adaptation-not-required` 并说明原因。

退出码：`0` 推进或完成，`2` 等待 Gate，`3` 可重试校验失败，`4` 阻塞或输入非法。

## Rule block 不变量

- 受管标记为 `cg-rule-contract:<id>:start/end`，ID 使用 kebab-case。
- `Activation` 只能是 `always`、`paths`、`intent`、`manual`。
- 行为指令为 1–7 条，并以 `MUST`、`MUST NOT`、`SHOULD` 或 `MAY` 开头。
- 整个 block 不超过 80 行；厚流程必须迁到 Skill / Workflow。
- 公共 block 不包含 `.cursor`、`.mdc`、`globs`、`alwaysApply`、具体模型或宿主调用语法。
- draft、已登记 block 和宿主产物均不覆盖已有文件或同名规则。

## 当前实现边界

- Validator 和 register 脚本是确定性现货。
- 公共登记目标是根或子目录 `AGENTS.md`；Claude 继续通过薄 `CLAUDE.md` 加载，Codex 原生读取。
- Cursor renderer 是独立 adapter；其他宿主的路径/意图激活 ABI 尚未实现，不能写成现货。

## 验证

```powershell
python -B -m unittest discover -s <skill-dir>/tests -q
```
