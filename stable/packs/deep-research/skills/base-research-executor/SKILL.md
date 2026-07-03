---
name: base-research-executor
description: Executes research tasks with full persistence chain — brave search, URL fetch, raw data archival, and structured note generation. All artifacts are saved locally.
metadata:
  version: "2.0"
  freedom_level: medium
scope: base
package:
  id: base-research-executor
  version: "2.0.0"
  maturity: stable
  owner: "template-maintainers"
  tags: ["research", "search", "fetch", "persistence", "brave-search"]
platform:
  runtimes: ["cursor"]
dependencies:
  skills: []
  mcp: ["brave-search"]
io_contract:
  inputs:
    - name: task
      type: object
      required: true
      description: "单个调研任务，含 search queries、target sources、focus areas"
    - name: base_path
      type: string
      required: true
      description: "落盘根目录，如 docs/research/ai-trends-2026/"
    - name: task_index
      type: string
      required: true
      description: "任务序号，如 01、02，用于文件命名"
  outputs:
    - name: note_path
      type: string
      required: true
      description: "生成的 Research Note 文件路径"
    - name: raw_paths
      type: array
      required: true
      description: "保存的原始搜索结果文件路径列表"
    - name: fetched_paths
      type: array
      required: true
      description: "保存的抓取页面文件路径列表"
max_response_tokens: 4000
---

# Skill: Base Research Executor

## 目标

执行单个调研任务的完整闭环：**搜索 → 存储原始结果 → 抓取高价值页面 → 存储抓取内容 → 总结 → 落盘笔记**。

核心原则：**每一次 API 调用的结果都必须持久化到本地**，避免重复付费查询，确保调研过程可追溯。

## 输入

- **任务指令**：例如"搜索 Anthropic Constitutional AI 论文并总结核心观点"。
- **搜索关键词**：由 Planner 提供，可能包含多组 query。
- **关注点**：例如"只关注 RLHF 算法细节"。
- **base_path**：落盘根目录（如 `docs/research/constitutional-ai/`）。
- **task_index**：任务编号（如 `01`），用于文件命名。

## 工具链

本 Skill 依赖以下工具，executor agent 在执行时直接调用：

### 1. Brave Search MCP（搜索）

通过 Brave Search API 进行网络搜索，返回结构化的搜索结果。

**`brave_web_search`**（通用网络搜索）：
- 参数：`query`（搜索词，最长 400 字符 / 50 词）、`count`（结果数，1-20，默认 10）、`offset`（分页偏移，最大 9）
- 返回：搜索结果列表，每项包含标题、URL、摘要描述
- 适用于：技术文档、论文、博客、新闻等通用调研

**`brave_local_search`**（本地/地理搜索）：
- 参数：`query`（搜索词，如 "pizza near Central Park"）、`count`（结果数，1-20）
- 返回：商家名称、地址、评分、电话、营业时间等
- 适用于：涉及物理位置、商家、服务的调研
- 注意：无本地结果时自动回退为网络搜索

### 2. WebFetch（深度阅读）

抓取指定 URL 的页面内容并转换为可读 Markdown。

- 输入：完整 URL
- 返回：页面正文的 Markdown 格式
- 限制：不支持需要认证的页面、不支持 localhost / 内网地址
- 适用于：深入阅读搜索结果中高价值页面的全文

### 3. Write（本地持久化）

将内容写入本地文件。所有中间产物和最终笔记都通过此工具存储。

## 工作流（单个 Task 的执行步骤）

### Step 1: 搜索

根据任务中的搜索关键词，调用 `brave_web_search`。

- 如果一个 Task 有多组 query，逐个执行搜索
- 每次搜索建议 `count: 10`，确保覆盖面
- 对于地理相关调研，使用 `brave_local_search`

### Step 2: 存储原始搜索结果

**每次** `brave_web_search` / `brave_local_search` 调用的返回内容，**必须**立即写入本地文件。

文件路径：`{base_path}/raw/task-{NN}-search-{seq}.md`

文件格式：

```markdown
# 搜索原始结果

**Query**: "{搜索词}"
**时间**: {YYYY-MM-DD HH:mm}
**工具**: brave_web_search
**结果数**: {N}

---

## 结果 1
- **标题**: {title}
- **URL**: {url}
- **摘要**: {description}

## 结果 2
...
```

### Step 3: 评估并抓取高价值 URL

从搜索结果中筛选 **2-3 个最相关的 URL**（优先官方文档、权威来源、高信息密度页面），调用 `WebFetch` 抓取全文。

筛选标准：
- 优先：官方文档、学术论文、权威技术博客
- 次优：高质量社区问答（Stack Overflow, GitHub Discussions）
- 排除：无日期/无作者的碎片化内容、纯广告页面、paywall 页面

### Step 4: 存储抓取内容

**每次** `WebFetch` 返回的内容，**必须**立即写入本地文件。

文件路径：`{base_path}/fetched/task-{NN}-url-{seq}.md`

文件格式：

```markdown
# 页面抓取存档

**来源 URL**: {url}
**抓取时间**: {YYYY-MM-DD HH:mm}
**原始标题**: {从搜索结果中获取的标题}

---

{WebFetch 返回的 Markdown 正文}
```

如果 `WebFetch` 失败（404、需要认证等），记录失败原因并跳过，不要阻断整个 Task。

### Step 5: 信息过滤与交叉验证

- 根据任务的"关注点"筛选内容，丢弃无关噪音
- 如果多个来源说法不一致，记录冲突点（不强行统一）
- 区分"事实"与"观点"，标注信息置信度

### Step 6: 总结落盘（生成 Research Note）

综合搜索结果和抓取内容，生成结构化的调研笔记。

文件路径：`{base_path}/notes/task-{NN}.md`

## 输出（Research Note 模板）

```markdown
## 调研笔记：{Task Name}

**来源数量**: {N} 个搜索结果, {M} 个页面抓取
**时间**: {YYYY-MM-DD HH:mm}
**关注点**: {focus area}

### 核心发现
- Fact 1 [来源: Title](URL)
- Fact 2 [来源: Title](URL)
- ...

### 关键引用
> "原文摘录..." —— [Source Title](URL)

### 信息冲突（如有）
- Source A 认为 X，Source B 认为 Y。冲突原因可能是...

### 延伸线索（用于下一轮搜索）
- 发现新术语: "..."
- 未解问题: "..."
- 推荐后续查询: "..."

### 本地文件索引
- 原始搜索: `raw/task-{NN}-search-001.md`
- 抓取页面: `fetched/task-{NN}-url-001.md`, `fetched/task-{NN}-url-002.md`
```

## 约束

- **忠实原意**：不编造，必须基于搜索和抓取结果。
- **保留来源**：每一条关键结论都必须附带 URL。
- **必须落盘**：搜索结果（raw/）和抓取内容（fetched/）必须写入本地文件——这是硬性要求，不是可选步骤。MCP 调用有成本，原始数据丢失等于白花钱。
- **识别未知**：如果搜不到，明确返回"未找到信息"，而不是胡编。
- **容错处理**：单个 URL 抓取失败不影响整体 Task 执行，记录失败原因后继续。
- **文件命名一致性**：严格按 `task-{NN}-search-{seq}` / `task-{NN}-url-{seq}` / `task-{NN}` 格式命名，NN 为两位数字（01, 02...）。
