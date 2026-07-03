#!/bin/bash
# cursor-genesis 资源安装脚本
# 用法: ./install.sh [preset] [options]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 默认配置
PRESET="standard"
USE_LINK=true
UPDATE=false
CG_REPO="https://github.com/your-org/cursor-genesis.git"

# 打印帮助
print_help() {
    cat << EOF
cursor-genesis 资源安装工具

用法:
    ./install.sh [preset] [options]

预设配置:
    minimal              最小化配置（基础规则）
    standard             标准配置（默认）
    full-stack           全栈配置
    research             研究配置
    knowledge-management 知识管理配置

选项:
    --copy              使用复制而非符号链接
    --update            更新已有资源
    --help              显示此帮助信息

示例:
    ./install.sh                    # 使用标准配置
    ./install.sh minimal            # 使用最小化配置
    ./install.sh --update           # 更新已有资源
    ./install.sh full-stack --copy  # 全栈配置，使用复制

EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        minimal|standard|full-stack|research|knowledge-management)
            PRESET="$1"
            shift
            ;;
        --copy)
            USE_LINK=false
            shift
            ;;
        --update)
            UPDATE=true
            shift
            ;;
        --help)
            print_help
            exit 0
            ;;
        *)
            echo -e "${RED}未知参数: $1${NC}"
            print_help
            exit 1
            ;;
    esac
done

# 检查是否在 git 仓库中
if [ ! -d ".git" ]; then
    echo -e "${RED}错误: 当前目录不是 git 仓库${NC}"
    echo "请先运行: git init"
    exit 1
fi

echo -e "${GREEN}=== cursor-genesis 资源安装 ===${NC}"
echo "预设配置: $PRESET"
echo "使用链接: $USE_LINK"
echo ""

# Step 1: 检查或添加 submodule
if [ ! -d ".cursor-genesis" ]; then
    echo -e "${YELLOW}[1/5] 添加 cursor-genesis submodule...${NC}"
    git submodule add "$CG_REPO" .cursor-genesis
else
    echo -e "${YELLOW}[1/5] cursor-genesis 已存在${NC}"
    if [ "$UPDATE" = true ]; then
        echo "更新 submodule..."
        cd .cursor-genesis
        git pull origin main
        cd ..
    fi
fi

# Step 2: 配置 sparse checkout
echo -e "${YELLOW}[2/5] 配置 sparse checkout...${NC}"
cd .cursor-genesis

if [ ! -f ".git/info/sparse-checkout" ]; then
    git sparse-checkout init --cone
fi

# 根据预设配置设置 sparse checkout 路径
case $PRESET in
    minimal)
        git sparse-checkout set stable/atoms/rules/production-safety.mdc stable/atoms/rules/project-rules.mdc stable/atoms/skills
        ;;
    standard)
        git sparse-checkout set stable/atoms/rules stable/atoms/skills
        ;;
    full-stack)
        git sparse-checkout set stable/atoms/rules stable/atoms/capabilities/03_engineering stable/atoms/code-templates stable/atoms/skills
        ;;
    research)
        git sparse-checkout set stable/atoms/rules/teams stable/atoms/capabilities/01_insight stable/atoms/skills
        ;;
    knowledge-management)
        git sparse-checkout set stable/atoms/rules/teams/knowledge-system-team.mdc stable/atoms/skills stable/atoms/capabilities/02_architecture
        ;;
esac

cd ..

# Step 3: 创建目录结构
echo -e "${YELLOW}[3/5] 创建 .cursor 目录结构...${NC}"
mkdir -p .cursor/rules/teams .cursor/skills

# Step 4: 安装资源
echo -e "${YELLOW}[4/5] 安装资源...${NC}"

install_resource() {
    local source=$1
    local target=$2

    if [ "$USE_LINK" = true ]; then
        # 使用符号链接
        if [ -e "$target" ] && [ "$UPDATE" = false ]; then
            echo "  跳过 $target (已存在)"
        else
            ln -sf "../.cursor-genesis/$source" "$target"
            echo "  链接 $target"
        fi
    else
        # 复制文件
        if [ -e "$target" ] && [ "$UPDATE" = false ]; then
            echo "  跳过 $target (已存在)"
        else
            cp -r ".cursor-genesis/$source" "$target"
            echo "  复制 $target"
        fi
    fi
}

# 根据预设安装资源
case $PRESET in
    minimal)
        install_resource "stable/atoms/rules/production-safety.mdc" ".cursor/rules/production-safety.mdc"
        install_resource "stable/atoms/rules/project-rules.mdc" ".cursor/rules/project-rules.mdc"
        install_resource "stable/atoms/skills" ".cursor/skills"
        ;;
    standard)
        install_resource "stable/atoms/rules/production-safety.mdc" ".cursor/rules/production-safety.mdc"
        install_resource "stable/atoms/rules/project-rules.mdc" ".cursor/rules/project-rules.mdc"
        install_resource "stable/atoms/rules/teams/strategic-research-team.mdc" ".cursor/rules/teams/strategic-research-team.mdc"
        install_resource "stable/atoms/rules/teams/domain-driven-design.mdc" ".cursor/rules/teams/domain-driven-design.mdc"
        install_resource "stable/atoms/skills" ".cursor/skills"
        ;;
    full-stack)
        install_resource "stable/atoms/rules" ".cursor/rules"
        install_resource "stable/atoms/skills" ".cursor/skills"
        ;;
    research)
        install_resource "stable/atoms/rules/teams/topic-research-team.mdc" ".cursor/rules/teams/topic-research-team.mdc"
        install_resource "stable/atoms/rules/teams/strategic-research-team.mdc" ".cursor/rules/teams/strategic-research-team.mdc"
        install_resource "stable/atoms/skills" ".cursor/skills"
        ;;
    knowledge-management)
        install_resource "stable/atoms/rules/teams/knowledge-system-team.mdc" ".cursor/rules/teams/knowledge-system-team.mdc"
        install_resource "stable/atoms/skills" ".cursor/skills"
        ;;
esac

# Step 5: 验证安装
echo -e "${YELLOW}[5/5] 验证安装...${NC}"

check_file() {
    if [ -e "$1" ]; then
        echo -e "  ${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1"
        return 1
    fi
}

ALL_OK=true

if ! check_file ".cursor/rules"; then ALL_OK=false; fi
if ! check_file ".cursor/skills"; then ALL_OK=false; fi

# 根据预设检查特定文件
case $PRESET in
    minimal|standard)
        if ! check_file ".cursor/rules/production-safety.mdc"; then ALL_OK=false; fi
        if ! check_file ".cursor/rules/project-rules.mdc"; then ALL_OK=false; fi
        ;;
esac

echo ""
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✓ 安装成功！${NC}"
    echo ""
    echo "已安装的资源:"
    echo "  - .cursor/rules/     规则文件"
    echo "  - .cursor/skills/    技能定义"
    echo ""
    echo "下一步:"
    echo "  1. 在 Cursor/Claude Code 中打开项目"
    echo "  2. 使用 /kg-search 等 skills"
    echo "  3. 查看 .cursor-genesis/stable/atoms/skills/README.md 了解更多"
else
    echo -e "${RED}✗ 安装过程中出现错误${NC}"
    exit 1
fi
