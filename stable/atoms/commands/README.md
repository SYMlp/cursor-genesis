# Commands 命令目录

Cursor slash commands，通过 `/命令名` 触发。

## 目录结构

```
commands/
├── internal/    # 认知系统体系内部命令
└── public/      # 提供给真实项目的命令
```

## internal/ - 内部命令

知识图谱体系内的协作命令，用户是"叶子节点维护者"。

| 命令 | 用途 |
|:---|:---|
| /sync | 从 knowledge-graph 拉取知识 |
| /backflow | 向 knowledge-graph 回流内容 |

## public/ - 公开命令

cursor-genesis 产品对外暴露的命令，用户是"下游项目开发者"。

| 命令 | 用途 |
|:---|:---|
| /cg-install | 安装 cursor-genesis 资产到项目 |
