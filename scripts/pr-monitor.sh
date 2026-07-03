#!/bin/bash
# PR 监控脚本 - 每天零点运行
# 检查 GitHub 上的回流 PR，自动拉取到临时区并生成待处理清单

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
REPO_OWNER="SYMlp"
REPO_NAME="cursor-genesis"
TEMP_DIR="pending/pr-review"
SUMMARY_FILE="pending/pr-summary-$(date +%Y-%m-%d).md"

# 打印日志
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查依赖
check_dependencies() {
    log "检查依赖..."

    if ! command -v gh &> /dev/null; then
        log_error "gh CLI 未安装，请安装: https://cli.github.com/"
        exit 1
    fi

    if ! gh auth status &> /dev/null; then
        log_error "gh CLI 未认证，请运行: gh auth login"
        exit 1
    fi

    log_success "依赖检查通过"
}

# 获取待处理的 PR 列表
get_pending_prs() {
    log "获取待处理的 PR 列表..."

    # 获取所有 open 状态的 PR，标签包含 "backflow"
    gh pr list \
        --repo "$REPO_OWNER/$REPO_NAME" \
        --state open \
        --label backflow \
        --json number,title,author,createdAt,headRefName,body \
        --jq '.[] | "\(.number)|\(.title)|\(.author.login)|\(.createdAt)|\(.headRefName)"'
}

# 拉取单个 PR 到临时区
pull_pr_to_temp() {
    local pr_number=$1
    local pr_title=$2
    local pr_author=$3
    local pr_branch=$4

    log "拉取 PR #$pr_number: $pr_title"

    # 创建临时目录
    local pr_temp_dir="$TEMP_DIR/pr-$pr_number"
    mkdir -p "$pr_temp_dir"

    # 获取 PR 的文件变更
    gh pr diff "$pr_number" --repo "$REPO_OWNER/$REPO_NAME" > "$pr_temp_dir/diff.patch"

    # 获取 PR 详情
    gh pr view "$pr_number" --repo "$REPO_OWNER/$REPO_NAME" --json title,body,author,createdAt,files > "$pr_temp_dir/metadata.json"

    # 检出 PR 分支到临时目录
    local temp_clone="$pr_temp_dir/files"
    git clone --depth=1 --branch "$pr_branch" "https://github.com/$REPO_OWNER/$REPO_NAME.git" "$temp_clone" 2>/dev/null || {
        log_warning "无法克隆分支 $pr_branch，尝试从 fork 拉取"
        # 如果是 fork 的 PR，需要从作者的仓库拉取
        git clone --depth=1 "https://github.com/$pr_author/$REPO_NAME.git" "$temp_clone" 2>/dev/null || {
            log_error "无法拉取 PR #$pr_number 的文件"
            return 1
        }
    }

    # 只保留 backflow 相关的文件
    if [ -d "$temp_clone/backflow/pending" ]; then
        cp -r "$temp_clone/backflow/pending/"* "$pr_temp_dir/" 2>/dev/null || true
    fi

    # 清理 git 目录
    rm -rf "$temp_clone"

    log_success "PR #$pr_number 已拉取到 $pr_temp_dir"

    echo "$pr_temp_dir"
}

# 分析 PR 内容
analyze_pr_content() {
    local pr_dir=$1
    local pr_number=$2

    log "分析 PR #$pr_number 的内容..."

    # 读取 metadata
    local metadata_file="$pr_dir/metadata.json"
    if [ ! -f "$metadata_file" ]; then
        log_warning "未找到 metadata.json"
        return 1
    fi

    # 提取关键信息
    local title=$(jq -r '.title' "$metadata_file")
    local author=$(jq -r '.author.login' "$metadata_file")
    local created_at=$(jq -r '.createdAt' "$metadata_file")
    local body=$(jq -r '.body' "$metadata_file")

    # 检测回流类型
    local backflow_type="unknown"
    if echo "$body" | grep -q "capability_change"; then
        backflow_type="capability_change"
    elif echo "$body" | grep -q "refined_knowledge"; then
        backflow_type="refined_knowledge"
    elif echo "$body" | grep -q "solution_feedback"; then
        backflow_type="solution_feedback"
    fi

    # 统计文件数量
    local file_count=$(jq '.files | length' "$metadata_file")

    # 返回分析结果（JSON 格式）
    cat <<EOF
{
  "pr_number": $pr_number,
  "title": "$title",
  "author": "$author",
  "created_at": "$created_at",
  "backflow_type": "$backflow_type",
  "file_count": $file_count,
  "pr_dir": "$pr_dir"
}
EOF
}

# 生成待处理清单
generate_summary() {
    local pr_analyses=("$@")

    log "生成待处理清单..."

    cat > "$SUMMARY_FILE" <<'HEADER'
# 回流 PR 待处理清单

**生成时间**: DATE_PLACEHOLDER
**检查仓库**: REPO_PLACEHOLDER

---

## 待处理 PR 列表

HEADER

    # 替换占位符
    sed -i "s/DATE_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/g" "$SUMMARY_FILE"
    sed -i "s|REPO_PLACEHOLDER|$REPO_OWNER/$REPO_NAME|g" "$SUMMARY_FILE"

    # 如果没有 PR
    if [ ${#pr_analyses[@]} -eq 0 ]; then
        echo "" >> "$SUMMARY_FILE"
        echo "✓ 当前没有待处理的回流 PR" >> "$SUMMARY_FILE"
        log_success "没有待处理的 PR"
        return 0
    fi

    # 按类型分组
    local capability_prs=()
    local knowledge_prs=()
    local feedback_prs=()
    local unknown_prs=()

    for analysis in "${pr_analyses[@]}"; do
        local pr_number=$(echo "$analysis" | jq -r '.pr_number')
        local title=$(echo "$analysis" | jq -r '.title')
        local author=$(echo "$analysis" | jq -r '.author')
        local created_at=$(echo "$analysis" | jq -r '.created_at' | cut -d'T' -f1)
        local backflow_type=$(echo "$analysis" | jq -r '.backflow_type')
        local file_count=$(echo "$analysis" | jq -r '.file_count')
        local pr_dir=$(echo "$analysis" | jq -r '.pr_dir')

        local pr_item="### PR #$pr_number: $title

- **作者**: @$author
- **提交时间**: $created_at
- **文件数量**: $file_count
- **本地路径**: \`$pr_dir\`
- **GitHub 链接**: https://github.com/$REPO_OWNER/$REPO_NAME/pull/$pr_number

**操作建议**:
1. 审核内容质量和格式规范
2. 验证是否可复用
3. 如果通过，移动到 \`backflow/processing/\`
4. 精炼后放入 \`stable/knowledge/exports/\`

---
"

        case "$backflow_type" in
            capability_change)
                capability_prs+=("$pr_item")
                ;;
            refined_knowledge)
                knowledge_prs+=("$pr_item")
                ;;
            solution_feedback)
                feedback_prs+=("$pr_item")
                ;;
            *)
                unknown_prs+=("$pr_item")
                ;;
        esac
    done

    # 写入分类的 PR
    if [ ${#capability_prs[@]} -gt 0 ]; then
        echo "" >> "$SUMMARY_FILE"
        echo "## 🔧 能力变更 (${#capability_prs[@]})" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        for pr in "${capability_prs[@]}"; do
            echo "$pr" >> "$SUMMARY_FILE"
        done
    fi

    if [ ${#knowledge_prs[@]} -gt 0 ]; then
        echo "" >> "$SUMMARY_FILE"
        echo "## 📚 精炼知识 (${#knowledge_prs[@]})" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        for pr in "${knowledge_prs[@]}"; do
            echo "$pr" >> "$SUMMARY_FILE"
        done
    fi

    if [ ${#feedback_prs[@]} -gt 0 ]; then
        echo "" >> "$SUMMARY_FILE"
        echo "## 💬 方案反馈 (${#feedback_prs[@]})" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        for pr in "${feedback_prs[@]}"; do
            echo "$pr" >> "$SUMMARY_FILE"
        done
    fi

    if [ ${#unknown_prs[@]} -gt 0 ]; then
        echo "" >> "$SUMMARY_FILE"
        echo "## ❓ 未分类 (${#unknown_prs[@]})" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        for pr in "${unknown_prs[@]}"; do
            echo "$pr" >> "$SUMMARY_FILE"
        done
    fi

    # 添加快速操作指南
    cat >> "$SUMMARY_FILE" <<'FOOTER'

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

# 2. 移动到 processing
git mv backflow/pending/{project}/{item} backflow/processing/

# 3. 精炼后放入 exports
cp backflow/processing/{item} stable/knowledge/exports/capability-changes/

# 4. 提交
git add backflow/ stable/knowledge/exports/
git commit -m "backflow: 处理 PR #{PR_NUMBER}"
git push
```

### 拒绝 PR

```bash
# 添加评论说明原因
gh pr comment {PR_NUMBER} --body "拒绝原因..."

# 关闭 PR
gh pr close {PR_NUMBER}
```

FOOTER

    log_success "待处理清单已生成: $SUMMARY_FILE"
}

# 主函数
main() {
    echo ""
    log "=========================================="
    log "  cursor-genesis PR 监控"
    log "=========================================="
    echo ""

    # 检查依赖
    check_dependencies

    # 创建临时目录
    mkdir -p "$TEMP_DIR"

    # 获取 PR 列表
    local pr_list=$(get_pending_prs)

    if [ -z "$pr_list" ]; then
        log_success "没有待处理的回流 PR"
        generate_summary
        exit 0
    fi

    # 处理每个 PR
    local pr_analyses=()
    while IFS='|' read -r pr_number pr_title pr_author pr_created pr_branch; do
        log "处理 PR #$pr_number..."

        # 拉取 PR 到临时区
        local pr_dir=$(pull_pr_to_temp "$pr_number" "$pr_title" "$pr_author" "$pr_branch")

        if [ -n "$pr_dir" ]; then
            # 分析 PR 内容
            local analysis=$(analyze_pr_content "$pr_dir" "$pr_number")
            pr_analyses+=("$analysis")
        fi

        echo ""
    done <<< "$pr_list"

    # 生成待处理清单
    generate_summary "${pr_analyses[@]}"

    echo ""
    log "=========================================="
    log_success "PR 监控完成"
    log "待处理清单: $SUMMARY_FILE"
    log "临时文件: $TEMP_DIR"
    log "=========================================="
    echo ""
}

# 运行
main "$@"
