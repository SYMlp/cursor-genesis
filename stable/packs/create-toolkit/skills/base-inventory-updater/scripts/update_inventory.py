import os
import argparse
import re
from typing import Any, Dict, List, Tuple

def _split_inline_list(raw: str) -> List[str]:
    s = raw.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return []
    inner = s[1:-1].strip()
    if not inner:
        return []
    # naive CSV split; good enough for tags/runtimes
    parts = [p.strip() for p in inner.split(",")]
    out: List[str] = []
    for p in parts:
        p = p.strip().strip('"').strip("'")
        if p:
            out.append(p)
    return out


def _parse_scalar(raw: str) -> Any:
    s = raw.strip()
    if not s:
        return ""
    if s.startswith("[") and s.endswith("]"):
        return _split_inline_list(s)
    # keep as string (we only need a few string/list fields)
    return s.strip().strip('"').strip("'")


def _parse_yaml_frontmatter_subset(text: str) -> Dict[str, Any]:
    """
    A tiny YAML subset parser for our SKILL.md frontmatter.
    Supports:
    - key: value
    - key:            (nested map or list inferred by next non-empty line)
    - key: [a, b]
    - key:
        sub: value
    - key:
        - item
    Notes:
    - Tabs are treated as 2 spaces.
    - Everything is parsed as string or list of strings.
    """
    lines = text.replace("\t", "  ").splitlines()
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Any]] = [(-1, root)]  # (indent, container)

    def current_container() -> Any:
        return stack[-1][1]

    def unwind(target_indent: int) -> None:
        while len(stack) > 1 and target_indent <= stack[-1][0]:
            stack.pop()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(line) - len(line.lstrip(" "))
        unwind(indent)
        container = current_container()

        if stripped.startswith("- "):
            if isinstance(container, list):
                container.append(_parse_scalar(stripped[2:]))
            i += 1
            continue

        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", stripped)
        if not m:
            i += 1
            continue

        key = m.group(1)
        raw_val = m.group(2)

        if raw_val == "":
            # infer nested container type from next meaningful line
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#")):
                j += 1
            nested: Any = {}
            if j < len(lines):
                next_line = lines[j].replace("\t", "  ")
                next_stripped = next_line.strip()
                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent > indent and next_stripped.startswith("- "):
                    nested = []
                elif next_indent > indent:
                    nested = {}
                else:
                    nested = {}
            if isinstance(container, dict):
                container[key] = nested
                stack.append((indent, nested))
            i += 1
            continue

        val = _parse_scalar(raw_val)
        if isinstance(container, dict):
            container[key] = val

        i += 1

    return root


def get_frontmatter(file_path: str) -> Dict[str, Any]:
    """Extract YAML frontmatter as dict (best-effort)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return {}
        return _parse_yaml_frontmatter_subset(match.group(1))
    except Exception:
        return {}


def get_description(file_path):
    """
    Attempts to extract a description from a markdown file.
    Looks for a line starting with 'description:' in YAML frontmatter 
    or the first non-header line.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Try finding YAML frontmatter block (prefer parsed dict)
        fm = get_frontmatter(file_path)
        if isinstance(fm, dict):
            desc = fm.get("description")
            if isinstance(desc, str) and desc.strip():
                return desc.strip()
            
        # Try finding a description in the text (simple heuristic)
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('---') and len(line) > 5:
                return line.strip()[:100] # Limit length
                
        return "No description found"
    except Exception:
        return "Error reading file"

def scan_agents(root_dir):
    agents_dir = os.path.join(root_dir, '.cursor', 'agents')
    if not os.path.exists(agents_dir):
        return []
    
    agents = []
    for f in os.listdir(agents_dir):
        if f.endswith('.md'):
            path = os.path.join(agents_dir, f)
            desc = get_description(path)
            agents.append({'id': f.replace('.md', ''), 'scope': 'Agent', 'desc': desc})
    return agents

def scan_skills(root_dir):
    """
    Scans for skills in:
    1. core/ (Base Skills Source)
    2. .cursor/skills/ (Runtime Skills, including nested base/lib/meta)
    """
    skills = []
    seen_ids = set()

    def _skill_meta(skill_md_path: str) -> Dict[str, Any]:
        fm = get_frontmatter(skill_md_path)
        if not isinstance(fm, dict):
            fm = {}

        scope = fm.get("scope") if isinstance(fm.get("scope"), str) else ""
        pkg = fm.get("package") if isinstance(fm.get("package"), dict) else {}
        maturity = pkg.get("maturity") if isinstance(pkg.get("maturity"), str) else ""
        owner = pkg.get("owner") if isinstance(pkg.get("owner"), str) else ""
        tags_val = pkg.get("tags")
        if isinstance(tags_val, list):
            tags = ", ".join(str(x) for x in tags_val if str(x).strip())
        elif isinstance(tags_val, str):
            tags = tags_val
        else:
            tags = ""

        platform = fm.get("platform") if isinstance(fm.get("platform"), dict) else {}
        runtimes_val = platform.get("runtimes")
        if isinstance(runtimes_val, list):
            runtimes = ", ".join(str(x) for x in runtimes_val if str(x).strip())
        elif isinstance(runtimes_val, str):
            runtimes = runtimes_val
        else:
            runtimes = ""

        return {
            "package_scope": scope,
            "maturity": maturity,
            "owner": owner,
            "runtimes": runtimes,
            "tags": tags,
        }

    # 1. Scan core/
    core_dir = os.path.join(root_dir, 'core')
    if os.path.exists(core_dir):
        for d in os.listdir(core_dir):
            skill_path = os.path.join(core_dir, d, 'SKILL.md')
            if os.path.isdir(os.path.join(core_dir, d)) and os.path.exists(skill_path):
                if d not in seen_ids:
                    desc = get_description(skill_path)
                    meta = _skill_meta(skill_path)
                    skills.append({'id': d, 'scope': 'Skill (Core)', 'desc': desc, **meta})
                    seen_ids.add(d)

    # 2. Scan .cursor/skills/ (Recursive)
    skills_dir = os.path.join(root_dir, '.cursor', 'skills')
    if os.path.exists(skills_dir):
        for root, dirs, files in os.walk(skills_dir):
            if 'SKILL.md' in files:
                skill_id = os.path.basename(root)
                # Skip if already found in core (Core is source of truth)
                if skill_id not in seen_ids:
                    skill_path = os.path.join(root, 'SKILL.md')
                    desc = get_description(skill_path)
                    meta = _skill_meta(skill_path)
                    skills.append({'id': skill_id, 'scope': 'Skill (Runtime)', 'desc': desc, **meta})
                    seen_ids.add(skill_id)
    
    # Sort by ID for consistency
    skills.sort(key=lambda x: x['id'])
    return skills

def scan_commands(root_dir):
    commands_dir = os.path.join(root_dir, '.cursor', 'commands')
    if not os.path.exists(commands_dir):
        return []
        
    commands = []
    for f in os.listdir(commands_dir):
        if f.endswith('.md'):
            path = os.path.join(commands_dir, f)
            desc = get_description(path)
            commands.append({'id': f.replace('.md', ''), 'scope': 'Command', 'desc': desc})
    return commands

def generate_table(items, table_type: str = "simple"):
    if not items:
        return "\nNo items found.\n"

    if table_type == "skills":
        header = (
            "| ID | Scope | Description | scope | maturity | owner | runtimes | tags | Dependencies | Status |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        )
    else:
        header = "| ID | Scope | Description | Dependencies | Status |\n| :--- | :--- | :--- | :--- | :--- |"
    rows = []
    for item in items:
        # Sanitize description to avoid breaking table
        desc = item['desc'].replace('|', '\\|').replace('\n', ' ')
        if table_type == "skills":
            pkg_scope = (item.get("package_scope") or "").replace("|", "\\|")
            maturity = (item.get("maturity") or "").replace("|", "\\|")
            owner = (item.get("owner") or "").replace("|", "\\|")
            runtimes = (item.get("runtimes") or "").replace("|", "\\|")
            tags = (item.get("tags") or "").replace("|", "\\|")
            row = (
                f"| `{item['id']}` | {item['scope']} | {desc} | {pkg_scope} | {maturity} | {owner} | {runtimes} | {tags} | - | Active |"
            )
        else:
            row = f"| `{item['id']}` | {item['scope']} | {desc} | - | Active |"
        rows.append(row)
    
    return header + "\n" + "\n".join(rows) + "\n"

def update_file(target_file, agents, skills, commands):
    if not os.path.exists(target_file):
        print(f"Target file {target_file} does not exist. Creating it.")
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write("# Project Asset Inventory\n\n## 1. Agents (.cursor/agents/)\n\n## 2. Skills (.cursor/skills/)\n\n## 3. Commands (.cursor/commands/)\n")
            
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Helper to replace section
    # 工作原理：
    # 1. 使用正则表达式匹配：标题 + 标题下的所有内容 + 下一个标题（或文件结尾）
    # 2. 模式结构：({header_regex})(.*?)(\n## |$)
    #    - group(1): 匹配到的标题（完整标题行）
    #    - group(2): 标题下的所有内容（.*? 非贪婪匹配，直到下一个 ## 或文件结尾）
    #    - group(3): 下一个标题的换行符和 ##，或文件结尾 $
    # 3. 替换策略：保留标题和下一个标题，只替换中间的内容部分
    def replace_section(content, header_regex, new_table):
        # 构建正则模式：匹配标题 + 内容 + 下一个标题/文件结尾
        # re.DOTALL 让 . 匹配换行符
        pattern = re.compile(f"({header_regex})(.*?)(\n## |$)", re.DOTALL)
        match = pattern.search(content)
        if match:
            start_header = match.group(1)  # 原始标题（如 "## 1. Agents (.cursor/agents/)"）
            next_header = match.group(3)   # 下一个标题的换行和 ##，或文件结尾
            # 替换整个匹配区域：标题 + 新表格 + 下一个标题
            return content.replace(match.group(0), f"{start_header}\n\n{new_table}\n{next_header}")
        else:
            # 如果找不到匹配的标题，追加到文件末尾（fallback）
            cleaned_header = header_regex.replace("\\", "")
            return content + f"\n\n{cleaned_header}\n\n{new_table}"

    # 使用正则表达式匹配标题，支持括号中的路径信息
    # r"## 1\. Agents \(.*?\)" 可以匹配：
    #   - "## 1. Agents (.cursor/agents/)"
    #   - "## 1\. Agents \(.*?\)" (转义版本)
    content = replace_section(content, r"## 1\. Agents \(.*?\)", generate_table(agents, table_type="simple"))
    content = replace_section(content, r"## 2\. Skills \(.*?\)", generate_table(skills, table_type="skills"))
    content = replace_section(content, r"## 3\. Commands \(.*?\)", generate_table(commands, table_type="simple"))
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {target_file}")

def main():
    parser = argparse.ArgumentParser(description='Update Asset Inventory')
    parser.add_argument('--target', required=True, help='Path to the target markdown file')
    args = parser.parse_args()
    
    root_dir = os.getcwd()
    
    agents = scan_agents(root_dir)
    skills = scan_skills(root_dir)
    commands = scan_commands(root_dir)
    
    update_file(args.target, agents, skills, commands)

if __name__ == "__main__":
    main()
