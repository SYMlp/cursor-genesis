---
name: sse-stream-parsing
description: >-
  SSE/NDJSON 流式解析规程：逻辑帧与 TCP 传输帧不对齐 → 按行分割必须 carry buffer。
  触发问法："SSE 按行分割那个 carry buffer 规程"、"流式输出偶发解析失败/内部 JSON 泄漏到界面"、
  "OpenAI 兼容流客户端怎么写行分割"。含三个叠加缺陷与修复模式。
---

# SSE 流式解析 · carry buffer 规程

> 迁自 kg `index/topics/ai-engineering.yaml` `sse-stream-carry-buffer`（2026-08-12 跨仓迁移波，
> 批 2 片 1 判决"专业操作规程出 kg，出口 = skill / 项目仓"）。
> 推导正本（溯源）：kg `meta/derivation/sse-stream-parsing-buffer-boundary-2026-03-17.md`。

## 问题

流式文本协议（SSE/NDJSON）的**逻辑帧（\n 行）与 TCP 传输帧（缓冲区）不对齐**：
`ReadableStream.read()` 按 TCP 缓冲区边界返回数据，`split('\n')` 后最后一段可能是不完整行，
`JSON.parse` 必然失败。如果 catch 块把失败数据拼入输出，系统内部协议数据（如 usage 统计 JSON）
就会泄漏到用户界面。

## 三个叠加缺陷

1. 无 carry buffer（跨缓冲区残行被当完整行解析）
2. catch 泄漏（解析失败的数据拼进用户输出）
3. fallback 字段链过宽（拿到什么都往外吐）

## 修复模式

```js
buffer += chunk;
const lines = buffer.split('\n');
buffer = lines.pop();          // ① 最后一段留作 carry，下轮拼接
for (const line of lines) {
  try { handle(JSON.parse(stripPrefix(line))); }
  catch { /* ② 丢弃，绝不拼入输出 */ }
}
// ③ 每个 fallback 字段做 typeof 守卫再取用
```

适用于所有消费 OpenAI 兼容 SSE 流的客户端。抽象内核（协议逻辑帧与传输帧不对齐时
须显式持有跨帧残留状态）是计算机基础知识，不入判断层。
