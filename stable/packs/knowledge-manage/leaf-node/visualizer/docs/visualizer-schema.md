# visualizer.yaml Schema

叶子节点可视化配置文件格式说明。

## 顶层结构

```yaml
engine:
  version: "1.0.0"    # 可选，引擎版本

project:
  name: string        # 必填，项目名称
  description: string # 必填，项目描述
  version: string     # 可选，项目版本

dimensions:           # 必填（或使用 perspectives 旧格式）
  - ...               # 维度配置数组

flows:                # 必填，信息流定义
  - ...

annotations:          # 可选，目录注解
  "path/": ...

structure:            # 可选，目录结构（开发时用，生产由扫描器生成）
  - ...
```

## 维度类型 (dimensions[].type)

### highlight-groups

可切换的路径高亮分组，适用于"使用者视角"等场景。

```yaml
- id: perspectives
  type: highlight-groups
  name: 使用者视角
  description: 可选描述
  groups:
    - id: producer
      name: 知识生产者
      description: 可选
      highlight: [.knowledge/upstream/exports/, stable/knowledge/]
      flow_direction: outbound  # inbound | outbound | bidirectional
      color: "#10b981"
```

### layer-stack

分层堆叠视图，适用于"架构分层"等场景。

```yaml
- id: architecture
  type: layer-stack
  name: 认知架构分层
  layers:
    - id: knowledge
      name: 知识层
      paths: [stable/knowledge/]
      description: 可选
      color: "#10b981"
```

### flow-sequence

顺序流程视图，适用于"生命周期"等场景。

```yaml
- id: lifecycle
  type: flow-sequence
  name: 知识生命周期
  stages:
    - id: receive
      name: 接收回流
      paths: [.knowledge/downstream/pending/]
      description: 可选
      color: "#f59e0b"
```

### tag-map

标签分类视图，适用于"按标签分组"等场景。

```yaml
- id: tags
  type: tag-map
  name: 内容分类
  tags:
    - id: rules
      name: 规则类
      paths: [stable/atoms/rules/]
      color: "#6366f1"
```

## 向后兼容

支持旧版 `perspectives` 格式，会自动转换为 `highlight-groups` 维度。
