# /visualize - 叶子节点可视化

**用途**：管理叶子节点的可视化配置，支持多种理解维度（视角、架构、生命周期等）。

## 架构说明

可视化系统分为两部分：

- **引擎**：`leaf-visualizer` 独立项目，构建后部署到叶子节点
- **配置**：`.knowledge/visualizer/skeleton.yaml`，定义维度、流向、骨架结构

## 子命令

### /visualize init

初始化可视化配置目录。

**流程**：

1. 创建 `.knowledge/visualizer/` 目录
2. 扫描项目结构，生成 `skeleton.yaml` 模板
3. 提示用户编辑配置

**示例**：

```bash
/visualize init
```

### /visualize add <idea>

根据用户想法添加新的理解维度。

**流程**：

1. 读取现有 `.knowledge/visualizer/skeleton.yaml`
2. 理解用户想法，选择合适的维度类型（highlight-groups、layer-stack、flow-sequence、tag-map）
3. 分析目录结构，确定 paths/groups/layers/stages/tags
4. 生成新维度配置，追加到 dimensions 数组
5. 写回配置文件

**示例**：

```bash
/visualize add 从认知架构分层理解
/visualize add 知识从产生到上报的生命周期
/visualize add 按内容类型分类（规则、能力、知识）
```

### /visualize edit

编辑现有维度的配置。可指定维度 id 或通过对话确定要修改的维度。

### /visualize deploy

部署可视化引擎到当前叶子节点。

**前置条件**：

- `leaf-visualizer` 引擎项目存在（默认 `../leaf-visualizer` 或 `$LEAF_VISUALIZER_PATH`）
- 已有 `.knowledge/visualizer/skeleton.yaml` 配置

**执行**：

```bash
cd $LEAF_VISUALIZER_PATH
npm run deploy -- --target <当前叶子节点路径>
```

### /visualize update

更新可视化引擎到最新版本。

**执行**：

```bash
cd $LEAF_VISUALIZER_PATH
git pull origin main
npm run deploy -- --target <当前叶子节点路径>
```

### /visualize open

在浏览器中打开可视化页面。

**执行**：

```bash
# Windows
start .knowledge/visualizer/engine/index.html

# macOS/Linux
open .knowledge/visualizer/engine/index.html
```

### /visualize dev

启动开发服务器（用于引擎开发调试）。

**执行**：

```bash
cd $LEAF_VISUALIZER_PATH
npm run dev
```

开发模式下，引擎从 `public/skeleton.yaml` 加载配置，需要先复制：

```bash
cp .knowledge/visualizer/skeleton.yaml $LEAF_VISUALIZER_PATH/public/skeleton.yaml
```

### /visualize status

查看当前可视化配置状态。

**输出示例**：

```text
可视化状态：
- 引擎版本: 0.1.0
- 配置文件: skeleton.yaml ✓
- 维度数量: 2 (perspectives, architecture)
- 流向数量: 3
- 最后部署: 2026-02-27 21:28
```

## 目录结构

```text
.knowledge/visualizer/
├── skeleton.yaml      # 骨架配置（固定目录 + 维度定义）
├── perspectives/      # 动态视角配置（预留）
└── engine/            # 引擎构建产物
    ├── index.html
    └── assets/
```

## 配置文件

### skeleton.yaml

定义：

- project: 项目基本信息
- dimensions: 维度视角（highlight-groups、layer-stack、flow-sequence、tag-map）
- flows: 信息流向
- annotations: 目录注解
- structure.skeleton: 固定目录结构（scan:true 标记动态扫描）

## 相关资源

- [leaf-visualizer](../../../leaf-visualizer/README.md) - 引擎源码
- [visualizer.md](.cursor/commands/internal/visualizer.md) - 内部命令详情
