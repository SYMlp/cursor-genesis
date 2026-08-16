#!/usr/bin/env python3
"""
install-pack: cursor-genesis Pack 通用安装脚本

将 cursor-genesis 的 Pack 部署到目标项目的公共作者层或宿主适配层。
manifest 未声明 target_root 时保持兼容，默认部署到 .cursor/。
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


ALLOWED_TARGET_ROOTS = {".agents", ".cursor"}


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
            elif stripped.startswith('record_root:'):
                result['record_root'] = stripped.split(':', 1)[1].strip()
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
                elif stripped.startswith('target_root:'):
                    current_item['target_root'] = stripped.split(':', 1)[1].strip()
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


def _validated_relative_path(value: str, field: str) -> Path:
    path = Path(value)
    if not value.strip() or path == Path("."):
        raise ValueError(f"{field} must not be empty or '.': {value}")
    if path.is_absolute() or path.anchor or path.drive or ".." in path.parts:
        raise ValueError(f"{field} must be an unanchored relative path without '..': {value}")
    return path


def _mapping_destination(target_path: Path, mapping: dict) -> tuple[str, Path]:
    target_root = mapping.get("target_root", ".cursor")
    if target_root not in ALLOWED_TARGET_ROOTS:
        raise ValueError(
            f"Unsupported target_root '{target_root}'. Allowed: {', '.join(sorted(ALLOWED_TARGET_ROOTS))}"
        )
    relative_target = _validated_relative_path(mapping["target"], "mapping.target")
    return target_root, target_path / target_root / relative_target


def _record_path(target_path: Path, record_root: str) -> Path:
    if record_root not in ALLOWED_TARGET_ROOTS:
        raise ValueError(
            f"Unsupported record_root '{record_root}'. Allowed: {', '.join(sorted(ALLOWED_TARGET_ROOTS))}"
        )
    return target_path / record_root / "installed-packs.yaml"


def _remove_legacy_record_entry(
    pack_name: str,
    target_path: Path,
    current_record_file: Path,
) -> dict | None:
    """升级 record_root 后移除旧 .cursor 记录中的同名 Pack，保留其他条目。"""
    legacy_record_file = target_path / ".cursor" / "installed-packs.yaml"
    if legacy_record_file == current_record_file or not legacy_record_file.exists():
        return None

    try:
        legacy_record = load_yaml_simple(legacy_record_file)
    except Exception:
        return None

    installed = legacy_record.get("installed", {})
    if pack_name not in installed:
        return None

    removed_entry = installed.pop(pack_name)
    legacy_record["installed"] = installed
    dump_yaml_simple(legacy_record, legacy_record_file)
    return removed_entry


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

    record_root = manifest.get("record_root", ".cursor")
    record_file = _record_path(target_path, record_root)
    installed_files = []
    errors = []

    for mapping in manifest.get('mappings', []):
        try:
            relative_source = _validated_relative_path(mapping["source"], "mapping.source")
            src = pack_dir / relative_source
            target_root, tgt = _mapping_destination(target_path, mapping)
        except (KeyError, ValueError) as error:
            errors.append(f"Invalid mapping {mapping!r}: {error}")
            continue
        is_dir = mapping.get('type') == 'directory'

        if not src.exists():
            errors.append(f"Source not found: {src}")
            continue

        tgt.parent.mkdir(parents=True, exist_ok=True)

        if is_dir:
            if tgt.exists():
                shutil.rmtree(tgt)
            shutil.copytree(src, tgt)
            installed_files.append(f"{target_root}/{mapping['target']}/")
            print(f"  [DIR]  {mapping['source']} -> {target_root}/{mapping['target']}/")
        else:
            shutil.copy2(src, tgt)
            installed_files.append(f"{target_root}/{mapping['target']}")
            print(f"  [FILE] {mapping['source']} -> {target_root}/{mapping['target']}")

    if errors:
        print(f"\n[WARN] {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")

    record = {}
    if record_file.exists():
        try:
            record = load_yaml_simple(record_file)
        except Exception:
            record = {}

    if 'installed' not in record:
        record['installed'] = {}
    previous_entry = record['installed'].get(pack_name, {})
    legacy_entry = (
        _remove_legacy_record_entry(pack_name, target_path, record_file)
        if not errors
        else None
    )
    retained_candidates = set(previous_entry.get('retained_unmanaged', []))
    if not errors:
        retained_candidates.update(previous_entry.get('files', []))
        if legacy_entry:
            retained_candidates.update(legacy_entry.get('retained_unmanaged', []))
            retained_candidates.update(legacy_entry.get('files', []))
    active_paths = {
        _installed_entry_path(target_path, entry).resolve()
        for entry in installed_files
    }
    retained_unmanaged = {
        entry
        for entry in retained_candidates
        if _installed_entry_path(target_path, entry).exists()
        and _installed_entry_path(target_path, entry).resolve() not in active_paths
    }

    current_entry = {
        'version': pack_version,
        'installed_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'source': str(source_path),
        'files': installed_files,
    }
    if retained_unmanaged:
        current_entry['retained_unmanaged'] = sorted(retained_unmanaged)
    record['installed'][pack_name] = current_entry

    record_file.parent.mkdir(parents=True, exist_ok=True)
    dump_yaml_simple(record, record_file)
    if legacy_entry:
        print("  [RECORD] Migrated legacy .cursor install record")
    if retained_unmanaged:
        print(
            f"  [NOTICE] Retained {len(retained_unmanaged)} unmanaged legacy item(s); "
            "no files were deleted"
        )

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


def _find_install_record(pack_name: str, target_path: Path) -> tuple[Path | None, dict]:
    for root in (".agents", ".cursor"):
        record_file = target_path / root / "installed-packs.yaml"
        if not record_file.exists():
            continue
        record = load_yaml_simple(record_file)
        if pack_name in record.get("installed", {}):
            return record_file, record
    return None, {}


def _installed_entry_path(target_path: Path, entry: str) -> Path:
    normalized = entry.rstrip("/\\")
    entry_path = _validated_relative_path(normalized, "installed file entry")
    if entry_path.parts and entry_path.parts[0] in ALLOWED_TARGET_ROOTS:
        return target_path / entry_path
    # Backward compatibility: old records stored paths relative to .cursor/.
    return target_path / ".cursor" / entry_path


def uninstall_pack(pack_name: str, target_path: Path):
    record_file, record = _find_install_record(pack_name, target_path)

    if record_file is None:
        print(f"[ERROR] No installed-packs.yaml found. Nothing to uninstall.")
        sys.exit(1)

    installed = record.get('installed', {})

    if pack_name not in installed:
        print(f"[ERROR] Pack '{pack_name}' is not installed.")
        sys.exit(1)

    files = installed[pack_name].get('files', [])
    print(f"[INFO] Uninstalling pack: {pack_name}")

    for f in files:
        fpath = _installed_entry_path(target_path, f)
        if fpath.is_dir():
            shutil.rmtree(fpath, ignore_errors=True)
            print(f"  [DEL DIR]  {f}")
        elif fpath.exists():
            fpath.unlink()
            print(f"  [DEL FILE] {f}")

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
