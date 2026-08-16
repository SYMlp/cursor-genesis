# v1-talk 套装

> only talk，最简洁，对话触发

## 适用场景

- 个人开发者
- 快速原型开发
- 不想学习复杂配置的用户

## 包含的团队

| 团队 | 用途 |
|:---|:---|
| Virtual Streamlit Team | Python/Streamlit 全栈开发 |
| Strategic Research Team | 新概念/新方向的可行性研判 |
| Topic Research Team | 学术/技术课题深度调研 |
| Domain Driven Design | DDD 领域建模 |
| AI Migration Team | 遗留项目接管 |

## 使用方式

```bash
# 稀疏检出到你的项目
git clone --filter=blob:none --sparse https://github.com/LSRabbit6/cursor-genesis.git .cursor-genesis
cd .cursor-genesis
git sparse-checkout set stable/packs/v1-talk stable/atoms/rules stable/atoms/capabilities
```

## 触发方式

直接用自然语言对话，AI 会自动识别意图并激活对应团队。

示例：
- "我有个新想法..." → Strategic Research Team
- "帮我做个数据看板" → Virtual Streamlit Team
- "分析一下这个课题" → Topic Research Team
