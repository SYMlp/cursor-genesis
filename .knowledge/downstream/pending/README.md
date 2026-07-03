# pending/ 目录说明

## 用途

存放来自下游项目的待处理回流内容。

## 目录结构

```
pending/
└── {project-hash}/
    └── {contributor-name}/
        └── {commit-id}/
            ├── metadata.yaml      # 回流元数据
            ├── content/          # 回流内容
            └── verification/     # 验证材料
```

## 使用流程

1. 下游项目通过 Fork + PR 提交回流
2. 使用 `/backflow status` 查看待处理回流
3. 使用 `/backflow review` 审核回流内容
4. 使用 `/backflow accept` 接受并精炼

## 回流格式要求

详见 `docs/downstream-spec.md` 中的回流规范。

## 审核标准

- 内容质量：是否解决真实问题
- 可复用性：是否适用于其他项目
- 格式规范：是否符合模板
- 测试验证：是否有验证结果
