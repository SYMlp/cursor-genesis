# /sync - 从上游拉取知识

> 认知系统体系内部命令，用于叶子节点从 knowledge-graph 拉取知识

## 用途

叶子节点（如 cursor-genesis）从 knowledge-graph 拉取：
- 根事实（roots/*.yaml）
- 叶子节点规范（meta/leaf-node-spec.md）
- 相关主题索引（index/topics/*.yaml）

## Agent 执行方式

当用户输入 `/sync <subcommand>` 时，Agent 应该：

1. **理解用户意图**：查看同步状态、拉取更新、查看配置
2. **调用实际脚本**：`./scripts/sync.sh <subcommand>`
3. **解释输出**：向用户说明拉取了什么、有什么更新

## 子命令

### /sync status

查看与上游的同步状态。

**Agent 执行**：
```bash
./scripts/sync.sh status
```

**输出说明**：
- ✓ 已拉取且是最新
- ↻ 已拉取但有更新
- ○ 未拉取
- ✗ 上游不存在

**Agent 应该告诉用户**：
- 哪些是必须拉取的（required）
- 哪些是推荐的（recommended）
- 哪些是可选的（optional）
- 当前本地状态如何

### /sync pull

从上游拉取更新。

**Agent 执行**：
```bash
# 默认：拉取 required + recommended，询问是否查看 optional
./scripts/sync.sh pull

# 仅拉取必须项
./scripts/sync.sh pull --required-only

# 拉取指定的 optional 项
./scripts/sync.sh pull --items cognitive-psychology,software-architecture

# 交互式选择
./scripts/sync.sh pull --interactive
```

**Agent 的决策逻辑**：
1. 如果用户明确说"只拉必须的"，使用 `--required-only`
2. 如果用户说"我需要认知心理学相关的"，使用 `--items cognitive-psychology`
3. 如果用户说"帮我选择"，使用 `--interactive`
4. 默认情况，使用无参数的 `pull`（会询问用户是否查看 optional）

**流程**：
1. 检查每个文件是否已存在、是否有更新
2. 只拉取缺失或有更新的文件
3. 将内容放入 `pending/upstream/` 待审批
4. 提示用户审批后合入 `stable/`

### /sync config

查看拉取配置。

**Agent 执行**：
```bash
./scripts/sync.sh config
```

**输出**：显示 `meta.yaml` 中的 `receives_from_upper` 配置

## 前置条件

- 当前项目是 knowledge-graph 的叶子节点
- knowledge-graph 在 `../knowledge-graph` 或配置的路径
- `meta.yaml` 中有 `receives_from_upper` 配置

## 推荐机制

knowledge-graph 通过 `meta/recommendations.yaml` 主动推荐内容：

- **required**：必须拉取（如根事实、叶子节点规范）
- **recommended**：强烈推荐（如 AI 协作知识、提示词工程）
- **optional**：可选清单，Agent 根据当前任务决定是否拉取

**Agent 选择 optional 的逻辑**：
1. 查看 optional 项的 `solves` 字段
2. 判断是否与当前任务相关
3. 查看 `when_needed` 条件是否满足
4. 考虑 `size`（优先选择 small/medium）
5. 向用户确认或自主决定

## 与 /backflow 的关系

```
knowledge-graph
      ↑ /backflow (上报)
      │
      ↓ /sync (拉取)
cursor-genesis
```

- `/sync`：拉取上游知识（下达）
- `/backflow`：向上游回流内容（上报）
