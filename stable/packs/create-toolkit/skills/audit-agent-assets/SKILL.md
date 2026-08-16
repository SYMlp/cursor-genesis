---
name: audit-agent-assets
description: 审计或复核 Agent、Skill、Command Contract、Workflow、宿主 adapter 或其他提示词资产时使用；按工具无关 rubric 检查触发边界、依赖、控制流、Human Gate、验证证据、失败恢复和宿主格式泄漏，并输出逐条证据化报告。
---

# Audit Agent Assets

对一个协作资产做只读审计。确定性脚本负责读取目标、校验 rubric 并生成审计包；通过/警告/失败的判断由 Agent 根据证据完成，不把认知判断冒充机器 Validator。

## 执行

1. 确认目标文件和资产类型；不确定时使用 `auto`。
2. 运行审计包生成器：

   ```powershell
   python <skill-dir>/scripts/prepare_audit.py <target-file> `
     --asset-type auto `
     --format markdown
   ```

3. 逐条评估审计包中的 criteria。只使用目标文件实际包含的证据；缺失证据就是发现，不替作者脑补。
4. 按下方契约返回报告。用户只要求审计时保持只读；只有明确要求修复时才修改目标。

自定义 rubric：

```powershell
python <skill-dir>/scripts/prepare_audit.py <target-file> `
  --rubric <rubric.json> `
  --asset-type skill `
  --format json
```

## 报告契约

```markdown
# Asset Audit: <target>

结论：PASS | WARN | FAIL
资产类型：<type>

## Findings

### <severity> · <criterion id>
- 证据：<文件中的具体字段、标题或行>
- 影响：<为什么影响触发、执行、纠错或验收>
- 建议：<最小可执行修正>

## Verified
- <已有且通过的关键契约>

## Unresolved
- <需要真实宿主、外部依赖或用户判断才能确认的事项>
```

判决规则：

- 存在 `critical` 发现 → `FAIL`。
- 没有 `critical`，但存在其他发现 → `WARN`。
- 所有适用 criteria 都有充分证据 → `PASS`。
- findings 按 `critical → high → medium → low` 排序；同一问题不重复报。

## 边界

- 默认 rubric 位于 `references/rubric.json`，不包含具体模型 ID、斜杠命令 ABI 或单一宿主目录要求。
- 审计公共核心时，宿主语法应只存在于 Adapter Notes 或独立 adapter；审计 adapter 时，必须反查其公共来源契约。
- 脚本只读取目标与 rubric，不修改文件、不调用网络、不执行目标中出现的命令。
- 默认拒绝超过 256 KiB 的目标；确有需要时显式调整 `--max-bytes`。

## 验证

```powershell
python -B -m unittest discover -s <skill-dir>/tests -q
```
