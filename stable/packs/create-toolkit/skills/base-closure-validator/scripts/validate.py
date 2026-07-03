#!/usr/bin/env python3
"""
Base Closure Validator - 闭环检验脚本

Checks:
1. Inventory Consistency: v2-asset-inventory.md vs disk
2. Reference Integrity: Paths in Rules/Skills/Commands/docs point to existing files

Configuration: assets/default_config.json (scan_dirs, exclude_dirs, exclude_path_contains)
"""
import os
import re
import json
import argparse
import sys


def _find_project_root():
    """Find project root by walking up until we see _meta/ or .cursor/."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current = script_dir
    for _ in range(6):
        if os.path.exists(os.path.join(current, "_meta")) or os.path.exists(os.path.join(current, ".cursor")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # Fallback: core/x/scripts -> 3 levels up; .cursor/skills/base/x/scripts -> 5 levels up
    return os.path.normpath(os.path.join(script_dir, "..", "..", ".."))


def _parse_inventory_ids(inventory_path):
    """Extract asset IDs from inventory markdown. Returns dict: {agents: set, skills: set, commands: set}"""
    result = {"agents": set(), "skills": set(), "commands": set()}
    if not os.path.exists(inventory_path):
        return result

    with open(inventory_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match table rows: | `id` | ...
    pattern = re.compile(r"\|\s*`([^`]+)`\s*\|")
    current_section = None

    for line in content.split("\n"):
        if "## 1. Agents" in line:
            current_section = "agents"
        elif "## 2. Skills" in line:
            current_section = "skills"
        elif "## 3. Commands" in line:
            current_section = "commands"
        elif current_section and line.strip().startswith("|") and "---" not in line:
            match = pattern.search(line)
            if match:
                result[current_section].add(match.group(1))

    return result


def _get_disk_agents(root):
    agents_dir = os.path.join(root, ".cursor", "agents")
    if not os.path.exists(agents_dir):
        return set()
    return {f.replace(".md", "") for f in os.listdir(agents_dir) if f.endswith(".md")}


def _get_disk_skills(root):
    seen = set()
    # core/
    core_dir = os.path.join(root, "core")
    if os.path.exists(core_dir):
        for d in os.listdir(core_dir):
            skill_path = os.path.join(core_dir, d, "SKILL.md")
            if os.path.isdir(os.path.join(core_dir, d)) and os.path.exists(skill_path):
                seen.add(d)
    # .cursor/skills/ recursive
    skills_dir = os.path.join(root, ".cursor", "skills")
    if os.path.exists(skills_dir):
        for r, dirs, files in os.walk(skills_dir):
            if "SKILL.md" in files:
                skill_id = os.path.basename(r)
                if skill_id not in seen:
                    seen.add(skill_id)
    return seen


def _get_disk_commands(root):
    cmd_dir = os.path.join(root, ".cursor", "commands")
    if not os.path.exists(cmd_dir):
        return set()
    return {f.replace(".md", "") for f in os.listdir(cmd_dir) if f.endswith(".md")}


def check_inventory(root, inventory_path):
    """Compare inventory with disk. Returns (issues: list, ok: bool)"""
    inv = _parse_inventory_ids(inventory_path)
    disk_agents = _get_disk_agents(root)
    disk_skills = _get_disk_skills(root)
    disk_commands = _get_disk_commands(root)

    issues = []

    # Stale: in inventory but not on disk
    for aid in inv["agents"] - disk_agents:
        issues.append(("stale", "Agent", aid, "Listed in inventory but file missing"))
    for sid in inv["skills"] - disk_skills:
        issues.append(("stale", "Skill", sid, "Listed in inventory but SKILL.md missing"))
    for cid in inv["commands"] - disk_commands:
        issues.append(("stale", "Command", cid, "Listed in inventory but file missing"))

    # Missing: on disk but not in inventory
    for aid in disk_agents - inv["agents"]:
        issues.append(("missing", "Agent", aid, "Exists on disk but not in inventory"))
    for sid in disk_skills - inv["skills"]:
        issues.append(("missing", "Skill", sid, "Exists on disk but not in inventory"))
    for cid in disk_commands - inv["commands"]:
        issues.append(("missing", "Command", cid, "Exists on disk but not in inventory"))

    return issues


def _extract_path_refs(content, file_path=None):
    """Extract path-like references from content. Returns list of (path, line_num).

    Context-aware: skips YAML body blocks and markdown code blocks to avoid
    false positives from example/template paths that only exist in product projects.
    """
    refs = []
    is_yaml = file_path and file_path.endswith((".yaml", ".yml"))
    in_yaml_body = False
    yaml_body_indent = 0
    in_code_block = False

    # Match: ](path), `path`, core/xxx, _meta/xxx, .cursor/xxx, prompts-library/xxx
    patterns_with_group = [
        (r'\]\(([^)]+)\)', 1),
        (r'`([a-zA-Z0-9_\-./]+(?:\.md|\.mdc|\.yaml|\.json)?)`', 1),
    ]
    patterns_no_group = [
        r'(?:core|_meta|\.cursor|prompts-library)/[a-zA-Z0-9_\-./]+',
    ]
    for i, line in enumerate(content.split("\n"), 1):
        stripped = line.lstrip()

        # --- YAML body detection ---
        if is_yaml and not in_code_block:
            if re.match(r'^\s*body:\s*\|', line):
                in_yaml_body = True
                yaml_body_indent = len(line) - len(stripped) + 2  # content indented further
                continue
            if in_yaml_body:
                current_indent = len(line) - len(stripped) if stripped else yaml_body_indent
                if stripped and current_indent < yaml_body_indent:
                    in_yaml_body = False  # body block ended
                else:
                    continue  # still inside body, skip

        # --- Markdown code block detection ---
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for pattern, g in patterns_with_group:
            for m in re.finditer(pattern, line):
                path = m.group(g)
                if path and not path.startswith("http"):
                    refs.append((path.strip(), i))
        for pattern in patterns_no_group:
            for m in re.finditer(pattern, line):
                path = m.group(0)
                if path:
                    refs.append((path.strip(), i))
    return refs


def _resolve_path(root, ref):
    """Resolve ref to absolute path. Handles relative paths from project root."""
    ref = ref.strip()
    if ref.startswith("/"):
        return None
    # Normalize: remove leading ./
    if ref.startswith("./"):
        ref = ref[2:]
    full = os.path.normpath(os.path.join(root, ref))
    if full.startswith(root):
        return full
    return None


def _is_path_like(ref):
    """Heuristic: ref looks like a file path (has / or ends with .md/.mdc/.yaml).

    Filters out bare extensions (.md, .mdc) and generic short names without path separators.
    """
    if not ref or len(ref) < 3:
        return False
    if ref.startswith("--"):
        return False
    # Bare extensions like `.md`, `.mdc`, `.py` are not paths
    if ref.startswith(".") and "/" not in ref and ref.count(".") == 1:
        return False
    if "/" in ref:
        return True
    if ref.endswith((".md", ".mdc", ".yaml", ".json", ".py")):
        # Must have a meaningful stem (not just extension)
        stem = ref.rsplit(".", 1)[0]
        if len(stem) < 2:
            return False
        return True
    # Single words in backticks are usually not paths (JPA, order, api, etc.)
    return False


def _load_config(root, config_path=None):
    """Load config. config_path overrides default location. Returns dict with defaults."""
    default = {
        "reference_check": {
            "scan_dirs": ["_meta", ".cursor", "prompts-library"],
            "exclude_dirs": ["archive", "legacy", "legacy_roles", "__pycache__", "node_modules", ".git"],
            "exclude_path_contains": ["_meta/archive/", "_meta/legacy/", "node_modules/"],
            "include_extensions": [".md", ".mdc", ".yaml", ".json"],
            "exclude_ref_prefixes": [],
        }
    }
    to_try = []
    if config_path:
        to_try.append(config_path if os.path.isabs(config_path) else os.path.join(root, config_path))
    to_try.extend([
        os.path.join(root, "core", "base-closure-validator", "assets", "default_config.json"),
        os.path.join(root, ".cursor", "skills", "base", "base-closure-validator", "assets", "default_config.json"),
    ])
    for p in to_try:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    rc = loaded.get("reference_check", {})
                    default["reference_check"] = {
                        "scan_dirs": rc.get("scan_dirs", default["reference_check"]["scan_dirs"]),
                        "exclude_dirs": rc.get("exclude_dirs", default["reference_check"]["exclude_dirs"]),
                        "exclude_path_contains": rc.get("exclude_path_contains", default["reference_check"]["exclude_path_contains"]),
                        "include_extensions": rc.get("include_extensions", default["reference_check"]["include_extensions"]),
                        "exclude_ref_prefixes": rc.get("exclude_ref_prefixes", default["reference_check"]["exclude_ref_prefixes"]),
                    }
                    break
            except Exception:
                pass
    return default


def check_references(root, config_path=None, scan_dirs=None, exclude_dirs=None, exclude_path_contains=None, include_extensions=None):
    """Scan files for path references and verify targets exist. Returns list of (file, ref, line, ok)."""
    config = _load_config(root, config_path)
    rc = config["reference_check"]
    scan_dirs = scan_dirs or rc["scan_dirs"]
    exclude_dirs = set(exclude_dirs or rc["exclude_dirs"])
    exclude_path_contains = exclude_path_contains or rc["exclude_path_contains"]
    include_extensions = include_extensions or rc["include_extensions"]
    exclude_ref_prefixes = rc.get("exclude_ref_prefixes", [])

    issues = []
    for scan_dir in scan_dirs:
        base = os.path.join(root, scan_dir)
        if not os.path.exists(base):
            continue
        for r, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext not in include_extensions:
                    continue
                path = os.path.join(r, f)
                rel_path = os.path.relpath(path, root).replace("\\", "/")
                if any(exc in rel_path for exc in exclude_path_contains):
                    continue
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()
                except Exception:
                    continue
                file_dir = os.path.dirname(path)
                for ref, line in _extract_path_refs(content, file_path=rel_path):
                    if not _is_path_like(ref):
                        continue
                    if ref in ("...", ".", "..", "-", "|"):
                        continue
                    # Skip refs matching exclude_ref_prefixes (product-only paths)
                    if exclude_ref_prefixes and any(ref.startswith(p) for p in exclude_ref_prefixes):
                        continue
                    # Strip leading @ (Cursor skill reference syntax)
                    clean_ref = ref.lstrip("@") if ref.startswith("@") else ref
                    if "#" in clean_ref:
                        clean_ref = clean_ref.split("#")[0]
                    # Try resolve relative to file's directory first
                    local_path = os.path.normpath(os.path.join(file_dir, clean_ref))
                    if os.path.exists(local_path) or os.path.isdir(local_path):
                        continue
                    if os.path.exists(local_path + ".md"):
                        continue
                    # Then try resolve relative to project root
                    resolved = _resolve_path(root, clean_ref)
                    if resolved:
                        if os.path.exists(resolved):
                            continue
                        if os.path.exists(resolved + ".md"):
                            continue
                        if os.path.isdir(resolved):
                            continue
                        issues.append((rel_path, ref, line, "Broken reference"))
    return issues


def main():
    parser = argparse.ArgumentParser(description="Base Closure Validator - 闭环检验")
    parser.add_argument("--mode", choices=["inventory", "references", "full"], default="full",
                        help="Check mode. Default: full")
    parser.add_argument("--inventory", default="_meta/docs/v2-asset-inventory.md",
                        help="Path to inventory file")
    parser.add_argument("--root", default=None, help="Project root (default: auto-detect)")
    parser.add_argument("--config", default=None, help="Path to config JSON (overrides assets/default_config.json)")
    parser.add_argument("--strict", action="store_true",
                        help="Strict mode: reference warnings also cause exit 1 (default: only inventory errors)")
    args = parser.parse_args()

    root = args.root or _find_project_root()
    inventory_path = os.path.join(root, args.inventory) if not os.path.isabs(args.inventory) else args.inventory

    all_issues = []
    inventory_error = False
    has_ref_warnings = False

    if args.mode in ("inventory", "full"):
        inv_issues = check_inventory(root, inventory_path)
        if inv_issues:
            inventory_error = True
            all_issues.extend(("inventory", i) for i in inv_issues)

    if args.mode in ("references", "full"):
        ref_issues = check_references(root, config_path=args.config)
        if ref_issues:
            has_ref_warnings = True
            all_issues.extend(("reference", i) for i in ref_issues)

    # Report
    print("=== Base Closure Validator Report ===\n")
    if args.mode in ("inventory", "full"):
        inv_items = [x for x in all_issues if x[0] == "inventory"]
        if inv_items:
            print("## Inventory Inconsistencies [ERROR]\n")
            for _, (typ, asset_type, aid, msg) in inv_items:
                print(f"  - [{typ.upper()}] {asset_type} `{aid}`: {msg}")
            print()
        else:
            print("## Inventory: OK\n")

    if args.mode in ("references", "full"):
        ref_items = [x for x in all_issues if x[0] == "reference"]
        if ref_items:
            label = "[ERROR]" if args.strict else "[WARNING]"
            print(f"## Reference Warnings {label} ({len(ref_items)} issues)\n")
            seen = set()
            for _, (file, ref, line, msg) in ref_items[:20]:  # Limit output
                key = (file, ref, line)
                if key not in seen:
                    seen.add(key)
                    print(f"  - {file}:{line} -> `{ref}` ({msg})")
            if len(ref_items) > 20:
                print(f"  ... and {len(ref_items) - 20} more")
            print()
        else:
            print("## References: OK (no obvious broken links)\n")

    # Exit code: inventory errors always fail; reference warnings only fail with --strict
    if inventory_error:
        sys.exit(1)
    if has_ref_warnings and args.strict:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
