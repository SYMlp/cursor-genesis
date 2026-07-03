#!/bin/bash
# /backflow 命令实现
# 向 knowledge-graph 上报内容

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 配置
EXPORTS_DIR=".knowledge/upstream/exports"
META_FILE="meta.yaml"

# 打印帮助
print_help() {
    cat << EOF
/backflow - 向 knowledge-graph 上报内容

用法:
    ./backflow.sh status              查看待上报内容
    ./backflow.sh prepare <type>      准备上报内容
    ./backflow.sh submit              提交上报（创建 PR）

类型:
    capability    能力变更
    knowledge     精炼知识
    feedback      方案反馈

EOF
}

# 查看待上报内容
backflow_status() {
    echo -e "${GREEN}=== 待上报内容 ===${NC}"
    echo ""

    # 检查 capability-changes
    echo "能力变更 (capability-changes/):"
    if [ -d "$EXPORTS_DIR/capability-changes" ]; then
        local count=$(find "$EXPORTS_DIR/capability-changes" -name "*.md" 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            find "$EXPORTS_DIR/capability-changes" -name "*.md" -exec basename {} \; | sed 's/^/  - /'
        else
            echo "  (无)"
        fi
    else
        echo "  (目录不存在)"
    fi
    echo ""

    # 检查 refined-knowledge
    echo "精炼知识 (refined-knowledge/):"
    if [ -d "$EXPORTS_DIR/refined-knowledge" ]; then
        local count=$(find "$EXPORTS_DIR/refined-knowledge" -name "*.md" 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            find "$EXPORTS_DIR/refined-knowledge" -name "*.md" -exec basename {} \; | sed 's/^/  - /'
        else
            echo "  (无)"
        fi
    else
        echo "  (目录不存在)"
    fi
    echo ""

    # 检查 feedback
    echo "方案反馈 (feedback/):"
    if [ -d "$EXPORTS_DIR/feedback" ]; then
        local count=$(find "$EXPORTS_DIR/feedback" -name "*.md" 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            find "$EXPORTS_DIR/feedback" -name "*.md" -exec basename {} \; | sed 's/^/  - /'
        else
            echo "  (无)"
        fi
    else
        echo "  (目录不存在)"
    fi
}

# 准备上报内容
backflow_prepare() {
    local type=$1
    local date=$(date +%Y-%m-%d)

    case "$type" in
        capability)
            local dir="$EXPORTS_DIR/capability-changes"
            local file="$dir/$date-new-capability.md"
            ;;
        knowledge)
            local dir="$EXPORTS_DIR/refined-knowledge"
            local file="$dir/$date-new-knowledge.md"
            ;;
        feedback)
            local dir="$EXPORTS_DIR/feedback"
            local file="$dir/$date-feedback.md"
            ;;
        *)
            echo -e "${RED}错误: 未知类型 $type${NC}"
            echo "支持的类型: capability, knowledge, feedback"
            exit 1
            ;;
    esac

    mkdir -p "$dir"

    # 创建模板文件
    cat > "$file" << 'EOF'
# 标题

**日期**: DATE
**类型**: TYPE
**状态**: 待审批

## 问题域

[描述要解决的问题]

## 解决方案摘要

[简要描述解决方案]

## 适用场景

1. **场景1**: [描述]
2. **场景2**: [描述]

## 实现形式

[如何实现的]

## 边界

[方案的边界]

## 局限性

[已知的局限性]

## 相关资源

- [链接1]
- [链接2]
EOF

    # 替换占位符
    sed -i "s/DATE/$date/g" "$file"
    sed -i "s/TYPE/$type/g" "$file"

    echo -e "${GREEN}✓ 已创建模板文件${NC}"
    echo "  $file"
    echo ""
    echo "下一步:"
    echo "  1. 编辑文件填写内容"
    echo "  2. 运行 ./backflow.sh submit 提交"
}

# 提交上报
backflow_submit() {
    echo -e "${GREEN}=== 提交上报 ===${NC}"
    echo ""

    # 检查是否有待上报内容
    local total=0
    total=$((total + $(find "$EXPORTS_DIR/capability-changes" -name "*.md" 2>/dev/null | wc -l)))
    total=$((total + $(find "$EXPORTS_DIR/refined-knowledge" -name "*.md" 2>/dev/null | wc -l)))
    total=$((total + $(find "$EXPORTS_DIR/feedback" -name "*.md" 2>/dev/null | wc -l)))

    if [ "$total" -eq 0 ]; then
        echo -e "${YELLOW}没有待上报内容${NC}"
        exit 0
    fi

    echo "待上报内容: $total 个文件"
    echo ""

    # Git 操作
    echo -e "${YELLOW}[1/3] 添加文件到 Git...${NC}"
    git add "$EXPORTS_DIR"

    echo -e "${YELLOW}[2/3] 创建提交...${NC}"
    local commit_msg="backflow: 上报内容到 knowledge-graph

包含:
- capability-changes: $(find "$EXPORTS_DIR/capability-changes" -name "*.md" 2>/dev/null | wc -l) 个
- refined-knowledge: $(find "$EXPORTS_DIR/refined-knowledge" -name "*.md" 2>/dev/null | wc -l) 个
- feedback: $(find "$EXPORTS_DIR/feedback" -name "*.md" 2>/dev/null | wc -l) 个
"
    git commit -m "$commit_msg"

    echo -e "${YELLOW}[3/3] 推送到远程...${NC}"
    git push origin main

    echo ""
    echo -e "${GREEN}✓ 提交完成${NC}"
    echo ""
    echo "下一步:"
    echo "  1. knowledge-graph 会通过稀疏检出拉取 exports/ 目录"
    echo "  2. 等待上游审批和处理"
}

# 主函数
main() {
    case "${1:-status}" in
        status)
            backflow_status
            ;;
        prepare)
            if [ -z "$2" ]; then
                echo -e "${RED}错误: 缺少类型参数${NC}"
                print_help
                exit 1
            fi
            backflow_prepare "$2"
            ;;
        submit)
            backflow_submit
            ;;
        --help|-h)
            print_help
            ;;
        *)
            echo -e "${RED}未知命令: $1${NC}"
            print_help
            exit 1
            ;;
    esac
}

main "$@"
