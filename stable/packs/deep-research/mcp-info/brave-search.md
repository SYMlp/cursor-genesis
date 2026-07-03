# MCP 依赖：Brave Search

## 概述

`deep-research` 命令的 **Executor** 阶段依赖 Brave Search MCP 进行网络搜索。
这是唯一的外部 MCP 依赖。

## 服务信息

- **Server Identifier**: `user-brave-search`
- **Server Name**: `brave-search`
- **来源**: Cursor MCP 市场 / 用户自行配置

## 提供的工具

### `brave_web_search`
- **用途**: 通用网络搜索
- **参数**:
  - `query` (string, required): 搜索词，最长 400 字符 / 50 词
  - `count` (number, optional): 结果数，1-20，默认 10
  - `offset` (number, optional): 分页偏移，最大 9
- **返回**: 搜索结果列表（标题、URL、摘要）

### `brave_local_search`
- **用途**: 本地/地理相关搜索
- **参数**:
  - `query` (string, required): 搜索词
  - `count` (number, optional): 结果数，1-20
- **返回**: 商家信息（名称、地址、评分等）
- **注意**: 无本地结果时自动回退为网络搜索

## 迁移配置步骤

1. 在目标项目的 Cursor Settings → MCP 中添加 `brave-search`
2. 需要 Brave Search API Key（从 https://brave.com/search/api/ 获取）
3. 配置格式参考 Cursor MCP 文档

## 替代方案

如果不想使用 Brave Search MCP，可以：
- 使用 Cursor 内置的 `WebSearch` 工具替代（修改 Executor agent/skill 中的搜索调用）
- 使用其他搜索 MCP（如 Google Search MCP）
- 注意：需同步修改 Executor skill 中的工具链描述
