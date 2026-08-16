#!/usr/bin/env python3
"""State Header Contract v1 机器验证器（契约见 ../CONTRACT.md）。

单文件或按登记表批量验证真相源机器头，输出 ok / stale / critical 三级判决。
stdlib-only，零依赖，可直接挂 CI / hook 当后置兜底。
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ("project", "status", "ball", "next", "updated")
STATUS_ENUM = ("\U0001f7e2", "\U0001f7e1", "\U0001f534", "⚪")  # 🟢 🟡 🔴 ⚪
DEFAULT_STALE_DAYS = 7


def read_header(path):
    """读文件顶部 front-matter 头。返回 (head dict | None, 错误说明 | None)。"""
    try:
        lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        return None, f"文件读不到: {exc}"
    if not lines or lines[0].strip() != "---":
        return None, "文件顶部没有 front-matter 机器头"
    head = {}
    for line in lines[1:]:
        if line.strip() == "---":
            if not head:
                return None, "机器头为空"
            return head, None
        if ":" in line:
            key, value = line.split(":", 1)  # ball 值含冒号(them:谁)，maxsplit=1 保住
            head[key.strip()] = value.strip()
    return None, "机器头没有用 --- 收尾"


def check(path, stale_days=DEFAULT_STALE_DAYS, today=None):
    """对单个真相源判级。critical 严格重于 stale（契约裁判语义）。"""
    today = today or datetime.date.today()
    head, err = read_header(path)
    if head is None:
        return {"file": str(path), "level": "critical", "age": None,
                "findings": [err], "head": None}

    findings = []
    for field in REQUIRED_FIELDS:
        if not head.get(field):
            findings.append(f"必填字段缺失或为空: {field}")

    status = head.get("status", "")
    if status and not status.startswith(STATUS_ENUM):
        findings.append(f"status 不以 🟢/🟡/🔴/⚪ 开头: {status!r}")

    ball = head.get("ball", "")
    if ball and ball != "me" and not (ball.startswith("them:") and len(ball) > len("them:")):
        findings.append(f"ball 必须是 'me' 或 'them:<谁>': {ball!r}")

    age = None
    updated = head.get("updated", "")
    if updated:
        try:
            age = (today - datetime.date.fromisoformat(updated)).days
        except ValueError:
            findings.append(f"updated 不是 ISO 日期 (YYYY-MM-DD): {updated!r}")

    limit = stale_days
    if head.get("stale_after"):
        try:
            limit = int(head["stale_after"])
        except ValueError:
            findings.append(f"stale_after 不是整数: {head['stale_after']!r}")

    if findings:
        level = "critical"
    elif age is not None and age > limit:
        level = "stale"
        findings.append(f"updated 距今 {age} 天，超过阈值 {limit} 天")
    else:
        level = "ok"

    return {"file": str(path), "level": level, "age": age, "findings": findings,
            "head": {k: head.get(k, "") for k in REQUIRED_FIELDS}}


def iter_registry(registry_path):
    """读登记表 JSON，产出 (显示名, 真相源路径)。路径相对登记表所在目录解析。"""
    base = Path(registry_path).parent
    data = json.loads(Path(registry_path).read_text(encoding="utf-8-sig"))
    for entry in data.get("projects", []):
        harness = entry.get("harness", "")
        path = Path(harness)
        if not path.is_absolute():
            path = base / path
        yield entry.get("name", "?"), path


def main(argv=None):
    parser = argparse.ArgumentParser(description="State Header Contract v1 验证器")
    parser.add_argument("files", nargs="*", help="要验证的真相源文件")
    parser.add_argument("--registry", help="登记表 JSON（{'projects': [{'name','harness'}]}）")
    parser.add_argument("--stale-days", type=int, default=DEFAULT_STALE_DAYS,
                        help=f"过期阈值天数（默认 {DEFAULT_STALE_DAYS}，可被文件内 stale_after 覆盖）")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args(argv)

    targets = [(None, Path(f)) for f in args.files]
    if args.registry:
        targets.extend(iter_registry(args.registry))
    if not targets:
        parser.error("需要至少一个文件或 --registry")

    results = []
    for name, path in targets:
        result = check(path, stale_days=args.stale_days)
        if name:
            result["name"] = name
        results.append(result)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            label = {"ok": "[OK]      ", "stale": "[STALE]   ", "critical": "[CRITICAL]"}[r["level"]]
            shown = r.get("name") or r["file"]
            detail = "; ".join(r["findings"]) if r["findings"] else f"updated={r['head']['updated']}"
            print(f"{label} {shown}  {detail}")

    return 0 if all(r["level"] == "ok" for r in results) else 1


if __name__ == "__main__":
    try:  # Windows 控制台默认 gbk，头里的 emoji 状态位会炸 print
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    sys.exit(main())
