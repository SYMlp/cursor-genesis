# 叶子节点规范

> D2 元认知：定义叶子节点的接入和交互规范

## 一、叶子节点定位

叶子节点是 knowledge-graph 的 L3 数据层，负责提供具体领域的知识和组件。

**职责边界**：

- ✅ 生产领域相关的组件和知识
- ✅ 接收下游项目的回流改进
- ✅ 暴露标准化索引供上层检索
- ✅ 定义与下游项目的交互规范
- ❌ 不负责跨领域知识关联（knowledge-graph 职责）
- ❌ 不负责根事实定义（knowledge-graph 职责）

## 二、信息流设计原则

### 2.1 契约 vs 内容

- **契约（格式/规范）**：上层定义，下层遵循
- **内容（传什么���**：下层决定，上层接收后自主处理

### 2.2 各层职责

```
knowledge-graph (认知层)
    │ 【定义】通用规范 + 注册时协商具体协议
    │ 【接收】叶子节点上报的内容
    │ 【处理】按自己的规则拆解、关联、存放
    ↓
叶子节点 (模板层，如 cursor-genesis)
    │ 【遵循】knowledge-graph 的规范和协议
    │ 【决定】上报什么内容（在协议范围内）
    │ 【定义】与下游项目���交互规范
    │ 【接收】下游项目的回流
    ↓
下游项目 (执行层，如 anfu_test)
    │ 【遵循】叶子节点的回流规范
    │ 【决定】回流什么内容
    │ 【产生】原始材料
```

### 2.3 传��通道

使用 Git 作为传输通道：

- 叶子节点通过 `stable/knowledge/exports/` 目录暴露给上层的内容
- knowledge-graph 通过 Git 稀疏检出拉取
- 各层自己维护上传/接收日志

## 三、必须提供的文件

### 3.1 meta.yaml（节点元信息）

```yaml
# 必填字段
id: <节点唯一标识>
name: <节点名称>
version: <版本号>
domain: <所属领域>
description: <节点描述>

# 职责声明
responsibilities:
  - <职责1>
  - <职责2>

out_of_scope:
  - <不负责的事项1>
  - <不负责的事项2>

# 生命周期
lifecycle:
  created: <创建日期>
  status: active | deprecated | archived
```

### 3.2 stable/knowledge/index.yaml（知识索引）

```yaml
domain: <领域>
description: <描述>

# 知识分类（供 knowledge-graph 检索）
categories:
  <category-id>:
    description: <分类描述>
    path: <相对路径>
    items:
      - id: <知识项ID>
        title: <标题>
        file: <文件名>
        solves: <能解决什么问题>  # 重要：必须说明能解决什么

# 关键词（供跨节点检索）
keywords:
  - <关键词1>
  - <关键词2>
```

### 3.3 stable/knowledge/exports/（上报目录）

专门存放要上报给 knowledge-graph 的精炼材料：

```
stable/knowledge/exports/
├── YYYY-MM-DD-<topic>.md    # 精炼后的知识文档
└── ...
```

### 3.4 docs/downstream-spec.md（下游项目规范）

定义与下游项目的交互方式（见第七节）。

## 四、注册流程

### 4.1 注册时协商

新叶子节点接入时，需要与 knowledge-graph 协商确定：

1. **上报内容范围**：哪些类型的知识需要上报
2. **上报格式**：具体的文档格式要求
3. **上报频率**：定期还是按需
4. **处理方式**：knowledge-graph 如何处理这些内容

### 4.2 协商结果记录

协商结果记录在 `knowledge-graph/index/nodes-registry.yaml` 的节点配置中：

```yaml
nodes:
  <node-id>:
    # ... 基本信息 ...

    # 【注册时协商确定】上报协议
    export_protocol:
      # 上报内容范围
      scope:
        - type: capability_change    # 能力变更（必须）
          required: true
        - type: refined_knowledge    # 精炼知识（可选）
          required: false
        - type: relation_discovery   # 关联发现（可选）
          required: false

      # 上报格式要求
      format:
        must_include:
          - problem_domain           # 问题域
          - solution_summary         # 解决方案摘要
          - applicable_scenario      # 适用场景
        must_not_include:
          - project_specific_code    # 不要项目特定代码
          - temporary_workaround     # 不要临时方案

      # 上报方式
      method: git_sparse_checkout    # 通过 Git 稀疏检出
      export_path: stable/knowledge/exports/
```

## 五、向上汇报规范

### 5.1 汇报内容（在协议范围内由叶子节点决定）

叶子节点根据注册时协商的协议，决定上报什么：

1. **能力声明**（通常必须）：我能解决什么问题
2. **精炼知识**（通常可选）：整理后的解决方案文档
3. **关联发现**（通常可选）：发现了与其他节点的关联

### 5.2 汇报方式

1. 将精炼材料放到 `stable/knowledge/exports/`
2. 更新 `stable/knowledge/index.yaml`
3. knowledge-graph 通过 Git 拉取时自动获取

### 5.3 叶子节点内部管理

叶子节点应维护自己的上报记录：

```
<leaf-node>/
├── internal/                    # 内部管理（可 .gitignore）
│   ├── export-log.yaml         # 上报记录
│   └── pending-export/         # 待上报的内容
└── stable/knowledge/exports/   # 已上报的内容
```

## 六、knowledge-graph 的处理

knowledge-graph 收到叶子节点上报的内容后，按自己的规则处理：

1. **第一性拆解**：用根事实库拆解知识
2. **建立关联**：与其他知识建立 D1 关联
3. **存放位置**：放到合适的 topics/ 或其他位置
4. **记录来源**：在 derivation/ 记录知识来源

这些处理逻辑由 knowledge-graph 自主决定，叶子节点不需要关心。

## 七、与下游项目的交互规范

### 7.1 必须定义的内容

叶子节点需要在 `docs/downstream-spec.md` 中定义：

1. **可使用的资产**：下游项目可以使用什么
2. **使用方式**：如何引入和使用
3. **回流规范**：下游项目如何提交改进

### 7.2 回流规范模板

```markdown
# 下游项目回流规范

## 回流内容格式

每次回流需要包含：

- 问题描述：遇到了什么问题
- 解决方案：如何解决的
- 代码样例：具体实现（如有）
- 适用场景：什么情况下适用

## 回流提交方式

1. Fork 本仓库
2. 在 backflow/pending/<project-hash>/<your-name>/ 下创建文件
3. 提交 PR

## 回流审批流程

pending → processing → stable
```

### 7.3 下游项目的职责

- 产生原始材料
- 决定哪些值得回流（人+AI辅助判断）
- 按叶子节点定义的格式提交

## 八、推导记录要求

叶子节点的设计决策需要在 knowledge-graph 的 `meta/derivation/<node-id>.md` 中记录推导过程。

### 8.1 推导记录格式

```markdown
# <节点名称> 推导记录

## 根事实（推导起点）

引用 knowledge-graph/roots/*.yaml 中的根事实

## 推导链

从根事实逐层推导到设计决策

## 外部约束

工具限制、技术约束等

## 产出

最终的设计决策和结构
```

## 九、版本管理

- 遵循语义化版本（SemVer）
- 重大变更需要在 CHANGELOG.md 记录
- 破坏性变更需要提前通知下游项目

## 十、检查清单

新叶子节点接入前的检查：

- [ ] meta.yaml 符合规范
- [ ] stable/knowledge/index.yaml 符合规范
- [ ] stable/knowledge/exports/ 目录已创建
- [ ] 每个知识项都有 `solves` 字段
- [ ] keywords 覆盖主要能力
- [ ] docs/downstream-spec.md 已创建
- [ ] 与 knowledge-graph 协商了上报协议
- [ ] 协议已记录到 nodes-registry.yaml
- [ ] 推导记录已提交到 knowledge-graph
