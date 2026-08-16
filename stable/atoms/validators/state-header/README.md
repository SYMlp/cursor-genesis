# state-header · 真相源机器头契约 + 死存根裁判

第一个进入 `stable/atoms/validators/` 类目的机器 Validator 原子：一份 5 字段的真相源状态头契约（[CONTRACT.md](CONTRACT.md)），加一个零依赖、可独立运行的验证器（[scripts/validate_state_header.py](scripts/validate_state_header.py)）。

它解决的问题：多项目并行时，各项目状态文件是"死存根"（头不更新 / 没有头）→ 任何聚合视图（驾驶舱、看板、HOME 导航）失明，人脑也串不起来。契约把每个项目的义务压缩到 5 行填空，裁判用机器兜底"谁没喂头"。

<!--
WHY（2026-08-17，资产升入 + 新类目开设）：
触发事件：CG 定位对齐至 kg 登记的"催化剂节点"（2026-08-07 改判）后，用户拍板"CG=给工作台供可替换插件的五金供应商"（A 读法），并选定死存根裁判作为第一个跑完整圈（回流→提炼→版本化→登记→消费）的插件。
参照系：my-desk 驾驶舱现役实现（server.py 死存根裁判，2026-08 上线，工作台第一条可执行不变量）+ context-shell/harness-template 的 5 行机器头契约；备货判据取 kg scaffold-vs-body 洞察——只上架"作用域主语是使用者体系而非 harness 产品"的机制件。
排除项：不把 Desk 个人偏好（UI/画像/入口布局）收进 CG；不建中央 runtime 让消费方在线调用（催化剂拿走反应仍发生）；不制造第二契约权威——个人侧 harness-template 保留为参考实现并加指针回本契约。
-->

## 内容

| 文件 | 作用 |
|:---|:---|
| `CONTRACT.md` | 契约正文 v1.0：字段规范、解析规则、裁判语义 |
| `scripts/validate_state_header.py` | 机器验证器：单文件 / 登记表批量，stdlib-only |
| `tests/test_validate_state_header.py` | 行为测试 |

## 用法

```bash
# 验证单个真相源
python scripts/validate_state_header.py path/to/PROJECT-STATE.md

# 按登记表横扫全部项目（驾驶舱模式）
python scripts/validate_state_header.py --registry projects.json

# 调整过期阈值 / 机器可读输出
python scripts/validate_state_header.py --stale-days 14 --json FILE...
```

退出码：全部 `ok` 为 0；存在 `stale` 或 `critical` 为 1（可直接挂 CI / hook 当后置兜底）。

## 溯源与消费登记

- **机制来源**：my-desk 驾驶舱（`toys/my-desk/server.py`）的现役实现回流提炼；个人侧模板 `toys/context-shell/harness-template/` 是本契约的参考实现。
- **首个消费方**：my-desk（工作台），以自有实现符合本契约 v1.0；关系已登记 kg `index/relations.yaml`。
- **可替换性**：消费方按 contract_version 钉版本；换掉本验证器不影响契约，换掉契约需出 v2 并保留 v1 语义说明。
