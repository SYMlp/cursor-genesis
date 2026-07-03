# cursor-genesis 可视化配置

本目录包含 cursor-genesis 叶子节点的可视化引擎实例。

## 目录结构

```text
visualizer/
├── skeleton.yaml      # 骨架配置（固定目录结构 + 维度定义）
├── perspectives/      # 动态视角配置（预留，由 skill 生成）
└── engine/            # 引擎构建产物（从 leaf-visualizer 部署）
    ├── index.html
    └── assets/
```

## 查看

直接在浏览器打开 `engine/index.html`

## 配置说明

### skeleton.yaml

定义项目的：

- 基本信息（project）
- 维度视角（dimensions）：highlight-groups、layer-stack 等
- 信息流向（flows）
- 目录注解（annotations）
- 骨架结构（structure.skeleton）：固定目录 + scan:true 标记动态扫描

### 更新引擎

引擎源码位于 `D:\Project\leaf-visualizer`，更新方式：

```bash
cd D:\Project\leaf-visualizer
npm run deploy:cursor-genesis
```

## 相关项目

- [leaf-visualizer](../../../leaf-visualizer/README.md) - 可视化引擎源码
