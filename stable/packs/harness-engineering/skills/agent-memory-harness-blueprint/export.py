#!/usr/bin/env python3
"""agent 记忆 harness 约束蓝图 · 取用入口（薄脚本：取件 + 验鲜，不做泛化）

用法:
    python export.py            # 取件：蓝图全文 → stdout；鲜度报告 → stderr
    python export.py --check    # 只验鲜，不取件
    python export.py --toc      # 只出章节+条号清单（快速索引/引用用）

设计约束（调度层设计场 2026-08-12，决策点 A/D）:
- 泛化是判断不是拼接——本脚本永远不现场生成蓝图，只搬运人审过的静态蓝图。
- 鲜度以"祝福时点 commit"为锚（同 lint 祝福基线模式）：源文件此后变更 = 过期信号，
  刷新蓝图须人批准；本脚本只报信号，不自动跟随。
- 脱离源仓运行（蓝图被拷去别的 harness 项目）时验鲜优雅降级：只取件 + 声明验鲜不可用。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BLUEPRINT = HERE / "blueprint.md"

# 祝福时点：人批准蓝图内容时的源仓 commit。刷新蓝图时一并更新（人批准，不自动）。
# 注：v0.2（2026-08-12 用户拍板转正+终检修订）是消费读数驱动的蓝图修订，非源文件跟随——
# 源文件状态自 6e5d539 未变，锚不动。
BLESSED_COMMIT = "6e5d539"
BLESSED_DATE = "2026-08-12"

# 验鲜范围 = 蓝图"附·源文件清单"（相对源仓根）。两处必须同步改。
SOURCE_FILES = [
    "meta/constitution.md",
    "meta/spec.md",
    "meta/operating-paradigm.md",
    "workbench/kg-redesign/judgment-admission-card-draft-2026-08-11.md",
    ".cursor/prompts/knowledge-ingestion.md",
    "index/root-gaps.yaml",
    "meta/derivation/memory-governance-phase4-design-2026-08-03.md",
    "workbench/health-check/health-check-2026-08-03.md",
    "meta/mechanisms-registry.md",
]


def find_source_repo() -> Path | None:
    """向上找 kg 源仓（本 skill 迁入 cg 后，HERE 所在 git 仓不再是验鲜锚定的源仓；
    cg 作为 kg submodule 挂载时，沿父目录可找回源仓——找不到即优雅降级）。"""
    for p in HERE.parents:
        if (p / "meta" / "constitution.md").is_file() and (p / ".git").exists():
            return p
    return None


def freshness_report() -> str:
    """对比祝福时点与 HEAD 的源文件差异。返回人读报告。"""
    repo = find_source_repo()
    if repo is None:
        return f"[验鲜不可用] 未找到约束源仓（脱离源仓运行）。蓝图按祝福时点 {BLESSED_COMMIT} 内容交付。"
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", f"{BLESSED_COMMIT}..HEAD", "--", *SOURCE_FILES],
            capture_output=True, text=True, cwd=repo, timeout=30, check=True,
        ).stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
        return f"[验鲜不可用] 不在源仓库或 git 不可用（{e.__class__.__name__}）。蓝图按祝福时点 {BLESSED_COMMIT} 内容交付。"
    if not out:
        return f"[鲜] 源文件自祝福时点 {BLESSED_COMMIT}（{BLESSED_DATE}）起无变更，蓝图与权威源一致。"
    changed = out.splitlines()
    lines = "\n".join(f"  - {p}" for p in changed)
    return (
        f"[过期信号] 以下 {len(changed)} 个源文件在祝福时点 {BLESSED_COMMIT}（{BLESSED_DATE}）之后有变更：\n{lines}\n"
        "蓝图内容仍可用（约束慢变），但引用受影响条目前建议回源核对；刷新蓝图须人批准。"
    )


def print_toc(text: str) -> None:
    """--toc：只出章节标题与条号行（终检消费者反馈：审计/评审类消费第一件事就是自造这张表）。"""
    for line in text.splitlines():
        if line.startswith("## ") or line.startswith("### C-"):
            print(line.lstrip("# ").strip())


def main() -> int:
    args = sys.argv[1:]
    check_only = "--check" in args
    toc_only = "--toc" in args
    print(freshness_report(), file=sys.stderr)
    if check_only:
        return 0
    if not BLUEPRINT.is_file():
        print(f"[错误] 蓝图文件缺失: {BLUEPRINT}", file=sys.stderr)
        return 1
    sys.stdout.reconfigure(encoding="utf-8")
    text = BLUEPRINT.read_text(encoding="utf-8")
    if toc_only:
        print_toc(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
