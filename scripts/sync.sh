#!/bin/bash
# /sync 命令实现
# 从 knowledge-graph 拉取知识

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 配置
UPSTREAM_PATH="../knowledge-graph"
META_FILE="meta.yaml"
PENDING_DIR=".knowledge/upstream/received"

# 打印帮助
print_help() {
    cat << EOF
/sync - 从 knowledge-graph 拉取知识

用法:
    ./sync.sh status              查看同步状态
    ./sync.sh pull                拉取 required + recommended（会询问是否查看 optional）
    ./sync.sh pull --required-only 仅拉取 required
    ./sync.sh pull --items <id>    拉取指定的 optional 项
    ./sync.sh pull --interactive   交互式选择
    ./sync.sh config              查看配置

状态说明:
    ✓  已拉取且是最新
    ↻  已拉取但有更新
    ○  未拉取
    ✗  上游不存在

示例:
    ./sync.sh status
    ./sync.sh pull
    ./sync.sh pull --items cognitive-psychology,software-architecture
    ./sync.sh pull --interactive

EOF
}

# 检查环境
check_environment() {
    if [ ! -f "$META_FILE" ]; then
        echo -e "${RED}错误: 找不到 meta.yaml${NC}"
        exit 1
    fi

    if [ ! -d "$UPSTREAM_PATH" ]; then
        echo -e "${RED}错误: 找不到 knowledge-graph 目录${NC}"
        echo "请确保 knowledge-graph 在 $UPSTREAM_PATH"
        exit 1
    fi
}

# 查看同步状态
sync_status() {
    echo -e "${GREEN}=== 同步状态 ===${NC}"
    echo ""

    # 读取 knowledge-graph 的推荐
    local rec_file="$UPSTREAM_PATH/meta/recommendations.yaml"

    if [ -f "$rec_file" ]; then
        echo -e "${YELLOW}knowledge-graph 推荐内容:${NC}"
        echo ""

        # 解析推荐文件，检查本地状态
        echo "【必须拉取】(required):"
        check_item "roots/cognitive-science.yaml" "根事实: 认知科学"
        check_item "roots/context-dependency.yaml" "根事实: 上下文依赖"
        check_item "meta/leaf-node-spec.md" "叶子节点规范"
        echo ""

        echo "【强烈推荐】(recommended):"
        check_item "index/topics/ai-collaboration.yaml" "AI 协作知识"
        check_item "index/topics/prompt-engineering.yaml" "提示词工程"
        echo ""

        echo "【可选清单】(optional) - AI 可浏览选择:"
        echo "  - cognitive-psychology: 认知心理学（设计能力分层时）"
        echo "  - software-architecture: 软件架构模式（重构架构时）"
        echo "  - knowledge-management: 知识管理方法论（完善知识结构时）"
        echo ""
    else
        echo -e "${YELLOW}未找到推荐清单，使用默认配置${NC}"
        echo ""
    fi

    echo ""
    echo "提示:"
    echo "  /sync pull                拉取 required + recommended"
    echo "  /sync pull --required-only 仅拉取 required"
    echo "  /sync pull --items <id>    拉取指定的 optional 项"
}

# 检查单个项的状态
check_item() {
    local upstream_path=$1
    local display_name=$2
    local local_path=".knowledge/upstream/received/${upstream_path##*/}"

    # 检查本地是否存在
    if [ -f "$local_path" ] || [ -d "$local_path" ]; then
        # 检查是否有更新
        if [ -f "$UPSTREAM_PATH/$upstream_path" ]; then
            local upstream_hash=$(md5sum "$UPSTREAM_PATH/$upstream_path" 2>/dev/null | cut -d' ' -f1)
            local local_hash=$(md5sum "$local_path" 2>/dev/null | cut -d' ' -f1)

            if [ "$upstream_hash" = "$local_hash" ]; then
                echo -e "  ${GREEN}✓${NC} $display_name (已是最新)"
            else
                echo -e "  ${YELLOW}↻${NC} $display_name (有更新)"
            fi
        else
            echo -e "  ${GREEN}✓${NC} $display_name (已拉取)"
        fi
    else
        # 检查上游是否存在
        if [ -f "$UPSTREAM_PATH/$upstream_path" ] || [ -d "$UPSTREAM_PATH/$upstream_path" ]; then
            echo -e "  ${YELLOW}○${NC} $display_name (未拉取)"
        else
            echo -e "  ${RED}✗${NC} $display_name (上游不存在)"
        fi
    fi
}

# 拉取更新
sync_pull() {
    local mode="${1:-default}"  # default, required-only, items, interactive
    local items="${2:-}"

    echo -e "${GREEN}=== 从 knowledge-graph 拉取更新 ===${NC}"
    echo ""

    # 创建 pending 目录
    mkdir -p "$PENDING_DIR"

    case "$mode" in
        --required-only)
            echo "模式: 仅拉取必须项 (required)"
            pull_required
            ;;
        --items)
            echo "模式: 拉取指定项 ($items)"
            pull_required
            pull_items "$items"
            ;;
        --interactive)
            echo "模式: 交互式选择"
            pull_interactive
            ;;
        *)
            echo "模式: 拉取 required + recommended"
            pull_required
            pull_recommended

            # 询问是否查看 optional
            echo ""
            echo -e "${YELLOW}是否查看可选项 (optional)? [y/N]${NC}"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                show_optional_and_select
            fi
            ;;
    esac

    echo ""
    echo -e "${GREEN}✓ 拉取完成${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 查看 $PENDING_DIR/ 中的内容"
    echo "  2. 审批后移动到 stable/ 目录"
    echo "  3. 更新 meta.yaml 中的 last_sync 时间"
}

# 显示可选项并让用户选择
show_optional_and_select() {
    echo ""
    echo -e "${YELLOW}可选项清单:${NC}"
    echo ""
    echo "1. cognitive-psychology"
    echo "   解决: 如何设计符合认知规律的规则和能力"
    echo "   适用: 设计复杂的团队编排或能力分层时"
    echo ""
    echo "2. software-architecture"
    echo "   解决: 如何组织 rules/capabilities/patterns 的结构"
    echo "   适用: 重构或扩展 cursor-genesis 架构时"
    echo ""
    echo "3. knowledge-management"
    echo "   解决: 如何管理和索引知识内容"
    echo "   适用: 完善 stable/knowledge/ 结构时"
    echo ""
    echo "请输入要拉取的项（逗号分隔，如 1,3）或按回车跳过:"
    read -r selection

    if [ -n "$selection" ]; then
        # 转换数字到 ID
        local items=""
        IFS=',' read -ra NUMS <<< "$selection"
        for num in "${NUMS[@]}"; do
            case "$num" in
                1) items="${items}cognitive-psychology," ;;
                2) items="${items}software-architecture," ;;
                3) items="${items}knowledge-management," ;;
            esac
        done
        items="${items%,}"  # 移除末尾逗号

        if [ -n "$items" ]; then
            echo ""
            pull_items "$items"
        fi
    fi
}

# 交互式拉取
pull_interactive() {
    echo "请选择要拉取的内容:"
    echo ""
    echo "1. 仅必须项 (required)"
    echo "2. 必须项 + 推荐项 (required + recommended)"
    echo "3. 全部 (required + recommended + 自选 optional)"
    echo ""
    echo "请输入选项 [1-3]:"
    read -r choice

    case "$choice" in
        1)
            pull_required
            ;;
        2)
            pull_required
            pull_recommended
            ;;
        3)
            pull_required
            pull_recommended
            show_optional_and_select
            ;;
        *)
            echo "无效选项，默认拉取 required + recommended"
            pull_required
            pull_recommended
            ;;
    esac
}

# 拉取必须项
pull_required() {
    echo -e "${YELLOW}[Required] 拉取必须项...${NC}"

    # 拉取根事实库
    pull_file_if_needed "roots/cognitive-science.yaml" "根事实: 认知科学"
    pull_file_if_needed "roots/context-dependency.yaml" "根事实: 上下文依赖"

    # 拉取叶子节点规范
    pull_file_if_needed "meta/leaf-node-spec.md" "叶子节点规范"
}

# 拉取推荐项
pull_recommended() {
    echo -e "${YELLOW}[Recommended] 拉取推荐项...${NC}"

    # 拉取 AI 协作主题
    pull_file_if_needed "index/topics/ai-collaboration.yaml" "AI 协作知识"

    # 拉取提示词工程
    pull_file_if_needed "index/topics/prompt-engineering.yaml" "提示词工程"
}

# 智能拉取文件（检查是否需要）
pull_file_if_needed() {
    local upstream_path=$1
    local display_name=$2
    local upstream_file="$UPSTREAM_PATH/$upstream_path"
    local local_file="$PENDING_DIR/${upstream_path##*/}"

    # 检查上游文件是否存在
    if [ ! -f "$upstream_file" ]; then
        echo -e "  ${RED}✗${NC} $display_name (上游不存在)"
        return
    fi

    # 检查本地是否已有且是最新
    if [ -f "$local_file" ]; then
        local upstream_hash=$(md5sum "$upstream_file" 2>/dev/null | cut -d' ' -f1)
        local local_hash=$(md5sum "$local_file" 2>/dev/null | cut -d' ' -f1)

        if [ "$upstream_hash" = "$local_hash" ]; then
            echo -e "  ${GREEN}✓${NC} $display_name (已是最新，跳过)"
            return
        else
            echo -e "  ${YELLOW}↻${NC} $display_name (有更新，拉取)"
        fi
    else
        echo -e "  ${YELLOW}+${NC} $display_name (新增，拉取)"
    fi

    # 创建目录并复制
    local target_dir=$(dirname "$local_file")
    mkdir -p "$target_dir"
    cp "$upstream_file" "$local_file"
}

# 拉取指定项
pull_items() {
    local items=$1
    echo -e "${YELLOW}[Optional] 拉取指定项: $items${NC}"

    IFS=',' read -ra ITEM_ARRAY <<< "$items"
    for item in "${ITEM_ARRAY[@]}"; do
        case "$item" in
            cognitive-psychology)
                if [ -d "$UPSTREAM_PATH/roots" ]; then
                    mkdir -p "$PENDING_DIR/roots"
                    cp "$UPSTREAM_PATH/roots/miller-7plus2.yaml" "$PENDING_DIR/roots/" 2>/dev/null || true
                    cp "$UPSTREAM_PATH/roots/ebbinghaus-forgetting.yaml" "$PENDING_DIR/roots/" 2>/dev/null || true
                    echo "  ✓ cognitive-psychology"
                fi
                ;;
            software-architecture)
                if [ -f "$UPSTREAM_PATH/index/topics/architecture-patterns.yaml" ]; then
                    mkdir -p "$PENDING_DIR/topics"
                    cp "$UPSTREAM_PATH/index/topics/architecture-patterns.yaml" "$PENDING_DIR/topics/"
                    echo "  ✓ software-architecture"
                fi
                ;;
            knowledge-management)
                if [ -f "$UPSTREAM_PATH/index/topics/knowledge-organization.yaml" ]; then
                    mkdir -p "$PENDING_DIR/topics"
                    cp "$UPSTREAM_PATH/index/topics/knowledge-organization.yaml" "$PENDING_DIR/topics/"
                    echo "  ✓ knowledge-management"
                fi
                ;;
            *)
                echo "  ✗ 未知项: $item"
                ;;
        esac
    done
}

# 查看配置
sync_config() {
    echo -e "${GREEN}=== 同步配置 ===${NC}"
    echo ""
    echo "配置文件: $META_FILE"
    echo ""
    echo "receives_from_upper:"
    grep -A 20 "receives_from_upper:" "$META_FILE" | head -20
}

# 主函数
main() {
    check_environment

    case "${1:-status}" in
        status)
            sync_status
            ;;
        pull)
            sync_pull "$2" "$3"
            ;;
        config)
            sync_config
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
