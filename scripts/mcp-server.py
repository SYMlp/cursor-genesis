#!/usr/bin/env python3
"""
cursor-genesis MCP Server

向外部调用方（如 knowledge-graph）暴露 cursor-genesis 的能力目录。
解决的问题：调用方无需扫描文件系统即可发现和使用 cursor-genesis 的资产。

配置方式（全局 ~/.cursor/mcp.json）:
{
  "mcpServers": {
    "cursor-genesis": {
      "command": "python",
      "args": ["d:/Project/cursor-genesis/scripts/mcp-server.py"]
    }
  }
}
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("Error: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from mcp.server.fastmcp import FastMCP

CG_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = CG_ROOT / "stable" / "atoms" / "skills" / "resources-catalog.yaml"

mcp = FastMCP(
    "cursor-genesis",
    instructions=(
        "cursor-genesis 是 Cursor AI 协作领域的资产库，"
        "提供 Rules、Capabilities、Patterns、Skills、Code Templates、Packs 等可复用组件。"
        "使用 list_capabilities 浏览可用资产，用 install_pack 部署到目标项目。"
    ),
)


def _load_catalog() -> dict:
    if not CATALOG_PATH.exists():
        return {}
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _flatten_capabilities(catalog: dict) -> list[dict]:
    """将 resources-catalog.yaml 的嵌套结构展平为统一列表"""
    results = []
    resources = catalog.get("resources", {})

    # Rules
    rules = resources.get("rules", {})
    for name, info in rules.get("items", {}).items():
        results.append({
            "name": name,
            "category": "rules",
            "description": info.get("description", ""),
            "path": f"{rules.get('path', '')}/{info.get('file', '')}",
            "recommended": info.get("recommended", False),
        })
    teams = rules.get("teams", {})
    for name, info in teams.get("items", {}).items():
        results.append({
            "name": name,
            "category": "rules/teams",
            "description": info.get("description", ""),
            "path": f"{teams.get('path', '')}/{info.get('file', '')}",
            "use_case": info.get("use_case", ""),
        })

    # Capabilities
    caps = resources.get("capabilities", {})
    for layer_name, layer in caps.get("layers", {}).items():
        results.append({
            "name": f"capabilities/{layer_name}",
            "category": "capabilities",
            "description": layer.get("description", ""),
            "path": layer.get("path", ""),
            "count": layer.get("count", 0),
        })

    # Patterns
    patterns = resources.get("patterns", {})
    if patterns:
        results.append({
            "name": "patterns",
            "category": "patterns",
            "description": patterns.get("description", ""),
            "path": patterns.get("path", ""),
            "count": patterns.get("count", 0),
        })

    # Skills
    skills = resources.get("skills", {})
    for name, info in skills.get("items", {}).items():
        results.append({
            "name": name,
            "category": "skills",
            "description": info.get("description", ""),
            "path": f"{skills.get('path', '')}/{info.get('file', '')}",
        })

    # Code Templates
    templates = resources.get("code-templates", {})
    for name, info in templates.get("items", {}).items():
        results.append({
            "name": name,
            "category": "code-templates",
            "description": info.get("description", ""),
            "path": info.get("path", ""),
            "language": info.get("language", ""),
        })

    # Packs
    packs = resources.get("packs", {})
    for name, info in packs.get("items", {}).items():
        entry = {
            "name": name,
            "category": "packs",
            "description": info.get("description", ""),
            "path": info.get("path", ""),
            "includes": info.get("includes", []),
        }
        if info.get("dependencies"):
            entry["dependencies"] = info["dependencies"]
        results.append(entry)

    return results


@mcp.tool()
def list_capabilities(category: Optional[str] = None) -> list[dict]:
    """列出 cursor-genesis 所有可用资产。

    可选 category 过滤:
      rules, rules/teams, capabilities, patterns, skills, code-templates, packs

    返回每个资产的 name、category、description、path 等信息。
    """
    catalog = _load_catalog()
    items = _flatten_capabilities(catalog)
    if category:
        items = [i for i in items if i["category"] == category]
    return items


@mcp.tool()
def get_capability_details(name: str) -> dict:
    """获取某个资产的详细信息。

    name 示例: "deep-research", "ddd", "domain-driven-design", "kg-search"
    """
    catalog = _load_catalog()
    items = _flatten_capabilities(catalog)
    for item in items:
        if item["name"] == name:
            return item
    return {"error": f"Capability '{name}' not found", "available": [i["name"] for i in items]}


@mcp.tool()
def search_capabilities(query: str) -> list[dict]:
    """按关键词搜索资产（匹配 name、description、use_case）。"""
    catalog = _load_catalog()
    items = _flatten_capabilities(catalog)
    query_lower = query.lower()
    results = []
    for item in items:
        searchable = " ".join([
            item.get("name", ""),
            item.get("description", ""),
            item.get("use_case", ""),
            item.get("language", ""),
        ]).lower()
        if query_lower in searchable:
            results.append(item)
    return results


@mcp.tool()
def list_recommended_combinations() -> list[dict]:
    """列出预设的推荐组合（minimal/standard/full-stack/research/knowledge-management）。

    每个组合说明适用场景和包含的资产。
    """
    catalog = _load_catalog()
    combos = catalog.get("recommended_combinations", {})
    return [
        {
            "id": combo_id,
            "name": info.get("name", ""),
            "description": info.get("description", ""),
            "use_case": info.get("use_case", ""),
            "includes": info.get("includes", []),
        }
        for combo_id, info in combos.items()
    ]


@mcp.tool()
def install_pack(pack_name: str, target_path: str) -> str:
    """将指定 Pack 安装到目标项目。

    调用 cursor-genesis 的 install-pack.py 脚本执行实际部署。

    Args:
        pack_name: Pack 名称（如 deep-research, create-toolkit）
        target_path: 目标项目的绝对路径
    """
    script = CG_ROOT / "scripts" / "install-pack.py"
    if not script.exists():
        return f"Error: install-pack.py not found at {script}"

    target = Path(target_path)
    if not target.exists():
        return f"Error: Target path does not exist: {target_path}"

    try:
        result = subprocess.run(
            [sys.executable, str(script), pack_name, str(target), "--source", str(CG_ROOT)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout
        if result.returncode != 0:
            output += f"\n[STDERR] {result.stderr}" if result.stderr else ""
        return output
    except subprocess.TimeoutExpired:
        return "Error: Installation timed out after 60 seconds"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_packs_detailed() -> list[dict]:
    """列出所有可安装的 Pack 及其详细信息（从 install-manifest.yaml 读取）。

    比 list_capabilities(category='packs') 更详细，包含具体的文件映射和依赖。
    """
    packs_dir = CG_ROOT / "stable" / "packs"
    if not packs_dir.exists():
        return []

    results = []
    for pack_path in sorted(packs_dir.iterdir()):
        manifest = pack_path / "install-manifest.yaml"
        if not pack_path.is_dir() or not manifest.exists():
            continue
        try:
            with open(manifest, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            results.append({
                "name": data.get("pack", pack_path.name),
                "version": data.get("version", "unknown"),
                "description": data.get("description", ""),
                "mappings_count": len(data.get("mappings", [])),
                "dependencies": data.get("dependencies", {}),
            })
        except Exception:
            results.append({"name": pack_path.name, "error": "Failed to parse manifest"})

    return results


if __name__ == "__main__":
    mcp.run()
