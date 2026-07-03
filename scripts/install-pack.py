#!/usr/bin/env python3
"""
install-pack: cursor-genesis Pack 通用安装脚本

将 cursor-genesis 的 Pack 部署到目标项目的 .cursor/ 目录下。
支持首次安装和覆盖更新。

用法:
    python install-pack.py <pack-name> <target-project-path> [--source <cursor-genesis-path>]

示例:
    python install-pack.py deep-research d:/Project/knowledge-graph
    python install-pack.py deep-research . --source d:/Project/cursor-genesis
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def load_yaml_simple(filepath: Path) -> dict:
    """简易 YAML 解析（不依赖 pyyaml 时的 fallback）"""
    if HAS_YAML:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    result = {'mappings': [], 'dependencies': {'mcp': []}}
    current_section = None
    current_item = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('#') or not stripped:
                continue
            if stripped.startswith('pack:'):
                result['pack'] = stripped.split(':', 1)[1].strip()
            elif stripped.startswith('version:'):
                if 'pack' in result and 'version' not in result:
                    result['version'] = stripped.split(':', 1)[1].strip()
            elif stripped.startswith('description:'):
                if 'description' not in result:
                    result['description'] = stripped.split(':', 1)[1].strip()
            elif stripped == 'mappings:':
                current_section = 'mappings'
            elif stripped == 'dependencies:':
                current_section = 'dependencies'
            elif current_section == 'mappings':
                if stripped.startswith('- source:'):
                    if current_item.get('source'):
                        result['mappings'].append(current_item)
                    current_item = {'source': stripped.split(':', 1)[1].strip()}
                elif stripped.startswith('target:'):
                    current_item['target'] = stripped.split(':', 1)[1].strip()
                elif stripped.startswith('type:'):
                    current_item['type'] = stripped.split(':', 1)[1].strip()

        if current_item.get('source'):
            result['mappings'].append(current_item)

    return result


def dump_yaml_simple(data: dict, filepath: Path):
    """写入 YAML 文件"""
    if HAS_YAML:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# cursor-genesis Pack 安装记录\n")
        f.write("# 由 install-pack.py 自动生成，请勿手动编辑\n\n")
        f.write("installed:\n")
        for pack_name, info in data.get('installed', {}).items():
            f.write(f"  {pack_name}:\n")
            for k, v in info.items():
                if isinstance(v, list):
                    f.write(f"    {k}:\n")
                    for item in v:
                        f.write(f"      - {item}\n")
                else:
                    f.write(f"    {k}: {v}\n")


def find_cursor_genesis_root(script_path: Path) -> Path:
    """从脚本自身位置推断 cursor-genesis 根目录"""
    return script_path.parent.parent


def install_pack(pack_name: str, target_path: Path, source_path: Path):
    pack_dir = source_path / 'stable' / 'packs' / pack_name
    manifest_file = pack_dir / 'install-manifest.yaml'

    if not pack_dir.exists():
        print(f"[ERROR] Pack '{pack_name}' not found at: {pack_dir}")
        print(f"  Available packs:")
        packs_dir = source_path / 'stable' / 'packs'
        if packs_dir.exists():
            for p in packs_dir.iterdir():
                if p.is_dir() and (p / 'install-manifest.yaml').exists():
                    print(f"    - {p.name}")
        sys.exit(1)

    if not manifest_file.exists():
        print(f"[ERROR] No install-manifest.yaml found in: {pack_dir}")
        sys.exit(1)

    manifest = load_yaml_simple(manifest_file)
    pack_version = manifest.get('version', 'unknown')
    print(f"[INFO] Installing pack: {pack_name} v{pack_version}")
    print(f"  Source: {pack_dir}")
    print(f"  Target: {target_path}")

    cursor_dir = target_path / '.cursor'
    installed_files = []
    errors = []

    for mapping in manifest.get('mappings', []):
        src = pack_dir / mapping['source']
        tgt = cursor_dir / mapping['target']
        is_dir = mapping.get('type') == 'directory'

        if not src.exists():
            errors.append(f"Source not found: {src}")
            continue

        tgt.parent.mkdir(parents=True, exist_ok=True)

        if is_dir:
            if tgt.exists():
                shutil.rmtree(tgt)
            shutil.copytree(src, tgt)
            installed_files.append(f"{mapping['target']}/")
            print(f"  [DIR]  {mapping['source']} -> .cursor/{mapping['target']}/")
        else:
            shutil.copy2(src, tgt)
            installed_files.append(mapping['target'])
            print(f"  [FILE] {mapping['source']} -> .cursor/{mapping['target']}")

    if errors:
        print(f"\n[WARN] {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")

    record_file = cursor_dir / 'installed-packs.yaml'
    record = {}
    if record_file.exists():
        try:
            record = load_yaml_simple(record_file)
        except Exception:
            record = {}

    if 'installed' not in record:
        record['installed'] = {}

    record['installed'][pack_name] = {
        'version': pack_version,
        'installed_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'source': str(source_path),
        'files': installed_files,
    }

    dump_yaml_simple(record, record_file)

    deps = manifest.get('dependencies', {})
    mcp_deps = deps.get('mcp', [])
    if mcp_deps:
        print(f"\n[NOTICE] MCP dependencies required:")
        for dep in mcp_deps:
            name = dep.get('name', dep) if isinstance(dep, dict) else dep
            required = dep.get('required', True) if isinstance(dep, dict) else True
            info = dep.get('info', '') if isinstance(dep, dict) else ''
            status = "REQUIRED" if required else "optional"
            print(f"  - {name} ({status})")
            if info:
                print(f"    Details: {pack_dir / info}")

    file_count = len(installed_files)
    error_count = len(errors)
    print(f"\n[DONE] Pack '{pack_name}' installed: {file_count} items deployed, {error_count} error(s)")
    print(f"  Record saved to: {record_file}")


def uninstall_pack(pack_name: str, target_path: Path):
    cursor_dir = target_path / '.cursor'
    record_file = cursor_dir / 'installed-packs.yaml'

    if not record_file.exists():
        print(f"[ERROR] No installed-packs.yaml found. Nothing to uninstall.")
        sys.exit(1)

    record = load_yaml_simple(record_file)
    installed = record.get('installed', {})

    if pack_name not in installed:
        print(f"[ERROR] Pack '{pack_name}' is not installed.")
        sys.exit(1)

    files = installed[pack_name].get('files', [])
    print(f"[INFO] Uninstalling pack: {pack_name}")

    for f in files:
        fpath = cursor_dir / f
        if fpath.is_dir():
            shutil.rmtree(fpath, ignore_errors=True)
            print(f"  [DEL DIR]  .cursor/{f}")
        elif fpath.exists():
            fpath.unlink()
            print(f"  [DEL FILE] .cursor/{f}")

    del installed[pack_name]
    record['installed'] = installed
    dump_yaml_simple(record, record_file)

    print(f"\n[DONE] Pack '{pack_name}' uninstalled.")


def list_packs(source_path: Path):
    packs_dir = source_path / 'stable' / 'packs'
    if not packs_dir.exists():
        print("[INFO] No packs directory found.")
        return

    print("Available packs:")
    for p in sorted(packs_dir.iterdir()):
        manifest = p / 'install-manifest.yaml'
        if p.is_dir() and manifest.exists():
            data = load_yaml_simple(manifest)
            desc = data.get('description', '')
            ver = data.get('version', '?')
            print(f"  - {p.name} (v{ver}): {desc}")


def register_in_workspace(target_path: Path, workspace_file: Path):
    """将项目路径注册到 .code-workspace 文件"""
    if not workspace_file.exists():
        print(f"[WARN] Workspace file not found: {workspace_file}")
        return False

    try:
        with open(workspace_file, 'r', encoding='utf-8') as f:
            ws = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[WARN] Failed to parse workspace file: {e}")
        return False

    folders = ws.get('folders', [])
    ws_dir = workspace_file.parent.resolve()

    try:
        rel = os.path.relpath(target_path.resolve(), ws_dir).replace('\\', '/')
    except ValueError:
        rel = str(target_path.resolve()).replace('\\', '/')

    existing_paths = []
    for f in folders:
        p = f.get('path', '')
        abs_p = (ws_dir / p).resolve()
        existing_paths.append(abs_p)

    if target_path.resolve() in existing_paths:
        print(f"[INFO] Project already registered in workspace: {target_path.name}")
        return True

    folders.append({"path": rel})
    ws['folders'] = folders

    with open(workspace_file, 'w', encoding='utf-8') as f:
        json.dump(ws, f, indent='\t', ensure_ascii=False)
        f.write('\n')

    print(f"[INFO] Registered in workspace: {rel}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='cursor-genesis Pack installer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install-pack.py deep-research .
  python install-pack.py deep-research d:/Project/my-project
  python install-pack.py deep-research . --source d:/Project/cursor-genesis
  python install-pack.py deep-research . --workspace path/to/file.code-workspace
  python install-pack.py --list
  python install-pack.py --uninstall deep-research .
        """,
    )
    parser.add_argument('pack', nargs='?', help='Pack name to install')
    parser.add_argument('target', nargs='?', default='.', help='Target project path (default: current directory)')
    parser.add_argument('--source', help='cursor-genesis root path (auto-detected if not specified)')
    parser.add_argument('--list', action='store_true', help='List available packs')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall the specified pack')
    parser.add_argument('--workspace', help='Register target project in the specified .code-workspace file')

    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    source_path = Path(args.source) if args.source else find_cursor_genesis_root(script_path)
    source_path = source_path.resolve()

    if args.list:
        list_packs(source_path)
        return

    if not args.pack:
        parser.print_help()
        sys.exit(1)

    target_path = Path(args.target).resolve()

    if not target_path.exists():
        print(f"[ERROR] Target path does not exist: {target_path}")
        sys.exit(1)

    if args.uninstall:
        uninstall_pack(args.pack, target_path)
    else:
        install_pack(args.pack, target_path, source_path)

        if args.workspace:
            register_in_workspace(target_path, Path(args.workspace).resolve())


if __name__ == '__main__':
    main()
