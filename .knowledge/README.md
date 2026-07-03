# .knowledge/ 目录说明

## 用途

存放知识管理相关的元数据和配置，不干扰日常使用。

## 目录结构

```
.knowledge/
├── meta.yaml                # 叶子节点元信息
├── upstream/                # 与上游 knowledge-graph 的交互
│   ├── sync.yaml           # 同步配置和记录
│   ├── exports/            # 待上报内容
│   │   ├── capability-changes/
│   │   ├── refined-knowledge/
│   │   └── feedback/
│   └── received/           # 上游推荐内容
│       ├── roots/          # 根事实
│       ├── topics/         # 主题索引
│       └── specs/          # 规范文档
└── downstream/              # 与下游项目的交互
    ├── backflow.yaml       # 回流配置和记录
    ├── pending/            # 待处理回流
    └── processing/         # 处理中回流
```

## 核心文件说明

### meta.yaml

叶子节点元信息，遵循 knowledge-graph 的 leaf-node-spec.md 规范。

包含：
- 节点 ID 和名称
- 版本信息
- 上游连接配置
- 知识索引路径

### upstream/sync.yaml

记录与上游 knowledge-graph 的同步状态：
- 上次同步时间
- 已同步的推荐清单
- 同步范围配置
- 同步历史

### upstream/received/

存放从上游 knowledge-graph 拉取的推荐内容：
- `roots/` - 根事实（认知科学、计算理论等）
- `topics/` - 主题索引（AI 协作、提示词工程等）
- `specs/` - 规范文档（叶子节点规范等）

### upstream/exports/

存放待上报到 knowledge-graph 的精炼内容：
- `capability-changes/` - 能力变更
- `refined-knowledge/` - 精炼知识
- `feedback/` - 方案反馈

### downstream/backflow.yaml

记录与下游项目的回流状态：
- 回流来源项目
- 待审核的回流
- 处理中的回流
- 已完成的回流

### downstream/pending/

存放来自下游项目的待处理回流内容。

## 使用场景

### 场景 1: 从上游同步推荐

```bash
# 使用 /sync 命令
# 会更新 upstream/sync.yaml 记录
```

### 场景 2: 向上游上报内容

```bash
# 1. 将精炼内容放入 upstream/exports/
# 2. 使用 /export 命令
# 3. 创建 PR 到 knowledge-graph
```

### 场景 3: 处理下游回流

```bash
# 1. 下游项目提交 PR 到 downstream/pending/
# 2. 使用 /backflow 命令审核
# 3. 更新 downstream/backflow.yaml 记录
```

## 相关文档

- [叶子节点规范](../knowledge-graph/meta/leaf-node-spec.md)
- [下游集成规范](../docs/downstream-spec.md)
- [架构设计文档](../docs/architecture.md)
