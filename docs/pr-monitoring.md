# PR 自动监控系统

## 概述

每天零点，Claude Code 自动检查 GitHub 上的回流 PR，拉取到本地临时区，生成待处理清单。

## 工作流程

```
GitHub PR (anfu_test 提交)
    ↓
定时任务 (每天 00:00)
    ↓
pr-monitor.sh 脚本
    ↓
1. 检查 GitHub PR (gh CLI)
2. 拉取 PR 内容到 pending/pr-review/
3. 分析 PR 类型和内容
4. 生成待处理清单 pending/pr-summary-{date}.md
    ↓
用户查看清单
    ↓
手动审核和处理
```

## 目录结构

```
cursor-genesis/
├── scripts/
│   └── pr-monitor.sh           # PR 监控脚本
├── pending/
│   ├── pr-review/              # PR 临时审核区
│   │   ├── pr-123/            # PR #123 的内容
│   │   │   ├── metadata.json  # PR 元数据
│   │   │   ├── diff.patch     # PR diff
│   │   │   └── {files}/       # PR 修改的文件
│   │   └── pr-124/
│   └── pr-summary-2026-02-26.md  # 每日待处理清单
└── backflow/
    ├── pending/                # 待审核（来自 PR）
    ├── processing/             # 处理中
    └── stable/                 # 已完成
```

## 安装配置

### 1. 安装 GitHub CLI

```bash
# Windows (使用 winget)
winget install --id GitHub.cli

# 或下载安装包
# https://cli.github.com/

# 验证安装
gh --version
```

### 2. 认证 GitHub

```bash
# 登录 GitHub
gh auth login

# 选择：
# - GitHub.com
# - HTTPS
# - Login with a web browser
```

### 3. 配置定时任务

#### Windows (任务计划程序)

```powershell
# 创建定时任务（每天零点运行）
$action = New-ScheduledTaskAction -Execute "bash" -Argument "d:/Project/cursor-genesis/scripts/pr-monitor.sh"
$trigger = New-ScheduledTaskTrigger -Daily -At 00:00
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "cursor-genesis-pr-monitor" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "每天零点检查 cursor-genesis 的回流 PR"
```

#### Linux/Mac (cron)

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天零点运行）
0 0 * * * cd /path/to/cursor-genesis && ./scripts/pr-monitor.sh >> logs/pr-monitor.log 2>&1
```

## 使用方式

### 自动运行（定时任务）

每天零点自动运行，无需手动操作。

### 手动运行

```bash
cd d:/Project/cursor-genesis
./scripts/pr-monitor.sh
```

### 查看结果

```bash
# 查看最新的待处理清单
cat pending/pr-summary-$(date +%Y-%m-%d).md

# 或在 VSCode 中打开
code pending/pr-summary-$(date +%Y-%m-%d).md
```

## 待处理清单示例

```markdown
# 回流 PR 待处理清单

**生成时间**: 2026-02-26 00:00:15
**检查仓库**: SYMlp/cursor-genesis

---

## 待处理 PR 列表

## 🔧 能力变更 (2)

### PR #123: anfu_test 改进 - 多轮对话状态机

- **作者**: @user123
- **提交时间**: 2026-02-25
- **文件数量**: 3
- **本地路径**: `pending/pr-review/pr-123`
- **GitHub 链接**: https://github.com/SYMlp/cursor-genesis/pull/123

**操作建议**:
1. 审核内容质量和格式规范
2. 验证是否可复用
3. 如果通过，移动到 `backflow/processing/`
4. 精炼后放入 `stable/knowledge/exports/`

---

### PR #124: anfu_test 改进 - 错误处理模式

- **作者**: @user456
- **提交时间**: 2026-02-25
- **文件数量**: 2
- **本地路径**: `pending/pr-review/pr-124`
- **GitHub 链接**: https://github.com/SYMlp/cursor-genesis/pull/124

**操作建议**:
1. 审核内容质量和格式规范
2. 验证是否可复用
3. 如果通过，移动到 `backflow/processing/`
4. 精炼后放入 `stable/knowledge/exports/`

---

## 快速操作指南

### 审核 PR

```bash
# 查看 PR 详情
gh pr view {PR_NUMBER}

# 查看 PR diff
gh pr diff {PR_NUMBER}

# 在浏览器中打开
gh pr view {PR_NUMBER} --web
```

### 处理通过的 PR

```bash
# 1. 合并 PR
gh pr merge {PR_NUMBER} --squash

# 2. 移动到 processing（记录到 backflow.yaml）
# 内容保留在 pending/ 但状态更新为 processing

# 3. 精炼后放入 exports
cp .knowledge/downstream/pending/{project}/{item} .knowledge/upstream/exports/capability-changes/

# 4. 提交
git add .knowledge/
git commit -m "backflow: 处理 PR #{PR_NUMBER}"
git push
```
```

## 审核流程

### 1. 查看待处理清单

```bash
# 每天早上查看昨晚生成的清单
cat pending/pr-summary-$(date +%Y-%m-%d).md
```

### 2. 审核单个 PR

```bash
# 在浏览器中打开 PR
gh pr view 123 --web

# 或在命令行查看
gh pr view 123
gh pr diff 123

# 查看本地拉取的文件
ls -la pending/pr-review/pr-123/
cat pending/pr-review/pr-123/metadata.json
```

### 3. 审核标准

- **内容质量**: 是否解决真实问题，描述是否清晰
- **可复用性**: 是否适用于其他项目，不是项目特定的
- **格式规范**: 是否符合 .knowledge/downstream/TEMPLATE.md 的格式
- **测试验证**: 是否提供了测试验证
- **边界说明**: 是否说明了适用场景和局限性

### 4. 处理通过的 PR

```bash
# 合并 PR
gh pr merge 123 --squash --body "审核通过，感谢贡献！"

# 移动到 processing（更新 backflow.yaml 状态）
# 内容保留在 pending/ 但状态更新

# 精炼内容
# 编辑文件，提炼关键信息

# 放入 exports
cp .knowledge/downstream/pending/anfu_test/user123/abc123/improvement.md \
   .knowledge/upstream/exports/capability-changes/2026-02-26-anfu_test-dialog-state-machine.md

# 更新索引
vim stable/knowledge/index.yaml

# 提交
git add .knowledge/ stable/knowledge/index.yaml
git commit -m "backflow: 处理 PR #123 - anfu_test 多轮对话状态机"
git push
```

### 5. 拒绝 PR

```bash
# 添加评论说明原因
gh pr comment 123 --body "感谢提交！但这个改进过于项目特定，不适合作为通用能力。建议..."

# 关闭 PR
gh pr close 123
```

## Claude Code 集成

### 使用 Claude Code 辅助审核

当定时任务生成待处理清单后，可以使用 Claude Code 辅助审核：

```
# 在 Claude Code 中
请帮我审核今天的回流 PR，清单在 pending/pr-summary-2026-02-26.md

# Claude Code 会：
1. 读取待处理清单
2. 逐个查看 PR 内容
3. 分析内容质量和可复用性
4. 给出审核建议（通过/拒绝/需要修改）
5. 如果通过，帮助精炼内容并放入 exports/
```

### 自动化审核（未来）

可以进一步自动化：

```bash
# 使用 Claude Code API 自动审核
./scripts/pr-auto-review.sh

# 流程：
# 1. 读取待处理清单
# 2. 调用 Claude Code API 分析每个 PR
# 3. 生成审核报告
# 4. 对于明显通过/拒绝的，自动处理
# 5. 对于需要人工判断的，标记并通知
```

## 监控和日志

### 查看运行日志

```bash
# Windows 任务计划程序
# 打开任务计划程序 → 找到 cursor-genesis-pr-monitor → 查看历史记录

# Linux/Mac
tail -f logs/pr-monitor.log
```

### 监控指标

- 每日 PR 数量
- 处理时间
- 通过率/拒绝率
- 平均审核时长

## 故障排查

### 脚本运行失败

```bash
# 检查 gh CLI 是否认证
gh auth status

# 检查网络连接
gh repo view SYMlp/cursor-genesis

# 手动运行脚本查看错误
cd d:/Project/cursor-genesis
bash -x ./scripts/pr-monitor.sh
```

### 定时任务未运行

```bash
# Windows: 检查任务计划程序
# 确保任务状态为"就绪"
# 查看上次运行结果

# Linux/Mac: 检查 cron 日志
grep CRON /var/log/syslog
```

## 安全注意事项

1. **GitHub Token**: gh CLI 的 token 存储在本地，确保机器安全
2. **PR 内容**: 拉取的 PR 内容可能包含恶意代码，审核时注意
3. **自动合并**: 不建议完全自动合并，至少需要人工确认
4. **权限控制**: 确保只有授权用户可以提交回流 PR

## 扩展功能

### 1. 邮件通知

```bash
# 在 pr-monitor.sh 末尾添加
if [ ${#pr_analyses[@]} -gt 0 ]; then
    echo "发现 ${#pr_analyses[@]} 个待处理 PR" | mail -s "cursor-genesis PR 通知" your@email.com
fi
```

### 2. Slack 通知

```bash
# 使用 Slack webhook
curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"发现 ${#pr_analyses[@]} 个待处理 PR\"}" \
    YOUR_SLACK_WEBHOOK_URL
```

### 3. 自动标签

```bash
# 根据 PR 内容自动添加标签
gh pr edit 123 --add-label "capability-change"
gh pr edit 124 --add-label "needs-review"
```

## 总结

这个 PR 监控系统实现了：

1. ✓ 自动检查 GitHub PR（每天零点）
2. ✓ 拉取 PR 内容到本地临时区
3. ✓ 分析 PR 类型和内容
4. ✓ 生成结构化的待处理清单
5. ✓ 提供快速操作指南
6. ✓ 支持 Claude Code 辅助审核

下一步可以：
- 集成 Claude Code API 实现自动审核
- 添加通知机制（邮件/Slack）
- 实现审核指标统计和可视化
