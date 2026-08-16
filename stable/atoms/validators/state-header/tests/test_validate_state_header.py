"""State Header Contract v1 验证器行为测试。跑法：python -m pytest tests/ -q"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from validate_state_header import check, iter_registry, main  # noqa: E402

TODAY = datetime.date(2026, 8, 17)


def write(tmp_path, text, name="STATE.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def good_header(updated="2026-08-15", extra=""):
    return (f"---\nproject: demo\nstatus: 🟢\nball: me\n"
            f"next: 下一步\nupdated: {updated}\n{extra}---\n\n# 正文\n")


def test_ok(tmp_path):
    r = check(write(tmp_path, good_header()), today=TODAY)
    assert r["level"] == "ok" and r["age"] == 2


def test_stale_over_default_threshold(tmp_path):
    r = check(write(tmp_path, good_header(updated="2026-08-01")), today=TODAY)
    assert r["level"] == "stale" and r["age"] == 16


def test_stale_after_overrides_threshold(tmp_path):
    r = check(write(tmp_path, good_header(updated="2026-08-01", extra="stale_after: 30\n")),
              today=TODAY)
    assert r["level"] == "ok"


def test_missing_header_is_critical(tmp_path):
    r = check(write(tmp_path, "# 没有头的文件\n"), today=TODAY)
    assert r["level"] == "critical" and r["head"] is None


def test_unreadable_file_is_critical(tmp_path):
    r = check(tmp_path / "not-exist.md", today=TODAY)
    assert r["level"] == "critical"


def test_bad_updated_is_critical_not_stale(tmp_path):
    r = check(write(tmp_path, good_header(updated="08/15/2026")), today=TODAY)
    assert r["level"] == "critical"


def test_missing_field_is_critical(tmp_path):
    text = "---\nproject: demo\nstatus: 🟢\nupdated: 2026-08-15\n---\n"
    r = check(write(tmp_path, text), today=TODAY)
    assert r["level"] == "critical"
    assert any("ball" in f for f in r["findings"])
    assert any("next" in f for f in r["findings"])


def test_ball_them_keeps_who(tmp_path):
    r = check(write(tmp_path, good_header().replace("ball: me", "ball: them:张三")), today=TODAY)
    assert r["level"] == "ok" and r["head"]["ball"] == "them:张三"


def test_ball_bare_them_is_critical(tmp_path):
    r = check(write(tmp_path, good_header().replace("ball: me", "ball: them:")), today=TODAY)
    assert r["level"] == "critical"


def test_status_enum_enforced_when_present(tmp_path):
    r = check(write(tmp_path, good_header().replace("status: 🟢", "status: green")), today=TODAY)
    assert r["level"] == "critical"


def test_status_optional_since_v1_1(tmp_path):
    # v1.1：status 缺失不再 critical——机器可观测态归探针，头只硬性承载判断态
    r = check(write(tmp_path, good_header().replace("status: 🟢\n", "")), today=TODAY)
    assert r["level"] == "ok"


def test_status_allows_suffix(tmp_path):
    r = check(write(tmp_path, good_header().replace("status: 🟢", "status: 🟡有卡点")), today=TODAY)
    assert r["level"] == "ok"


def test_bom_tolerated(tmp_path):
    p = tmp_path / "BOM.md"
    p.write_bytes(b"\xef\xbb\xbf" + good_header().encode("utf-8"))
    assert check(p, today=TODAY)["level"] == "ok"


def test_unclosed_header_is_critical(tmp_path):
    r = check(write(tmp_path, "---\nproject: demo\n"), today=TODAY)
    assert r["level"] == "critical"


def test_registry_resolves_relative_paths(tmp_path):
    write(tmp_path, good_header(), name="A.md")
    reg = tmp_path / "projects.json"
    reg.write_text(json.dumps({"projects": [{"name": "A", "harness": "A.md"}]}),
                   encoding="utf-8")
    items = list(iter_registry(reg))
    assert items[0][0] == "A" and items[0][1] == tmp_path / "A.md"


def test_main_exit_codes(tmp_path, capsys):
    # main() 用真实 today，这里动态生成今天的日期，测试不随时间过期
    ok = write(tmp_path, good_header(updated=datetime.date.today().isoformat()), name="ok.md")
    assert main([str(ok), "--json"]) == 0
    dead = write(tmp_path, "# 没头\n", name="dead.md")
    assert main([str(ok), str(dead)]) == 1
    out = capsys.readouterr().out
    assert "[CRITICAL]" in out
