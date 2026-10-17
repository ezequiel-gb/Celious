"""Read-only, credential-free local diagnosis; explicit approval commands write state."""
import sys
sys.dont_write_bytecode = True
import argparse
import ast
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PureWindowsPath
import stat
import subprocess
import time
from connection_settings import tunnel_id

BASE = Path(__file__).resolve().parent


def identity(base):
    result = {'commit': None, 'dirty': None}
    try:
        command = ['git', '--no-optional-locks', '-C', str(base.parent)]
        # Do not accidentally identify a containing repository as this installation.
        top = subprocess.check_output(command + ['rev-parse', '--show-toplevel'], stderr=subprocess.DEVNULL, text=True).strip()
        if Path(top).resolve() == base.parent.resolve():
            result['commit'] = subprocess.check_output(command + ['rev-parse', 'HEAD'], text=True).strip()
            result['dirty'] = bool(subprocess.check_output(command + ['status', '--porcelain', '--untracked-files=no'], text=True))
    except (OSError, subprocess.SubprocessError):
        pass
    manifest = base.parent / 'BUILD-IDENTITY.json'
    if manifest.is_file():
        try:
            build = json.loads(manifest.read_text('utf-8'))
            matches = bool(build['files']) and all(not Path(name).is_absolute() and '..' not in Path(name).parts
                          and (base.parent / name).is_file() and hashlib.sha256((base.parent / name).read_bytes()).hexdigest() == digest
                          for name, digest in build['files'].items())
            matches = matches and build.get('source_digest') == hashlib.sha256(json.dumps(build['files'], sort_keys=True).encode()).hexdigest()
            result['packaged_commit'] = build.get('commit')
            result['build_matches'] = matches
            result['source_digest'] = build.get('source_digest')
        except (OSError, ValueError, KeyError, TypeError):
            result['build_matches'] = False
    return result


def tool_names(base, memory):
    names = []
    for module in ['server.py', 'spreadsheets.py', 'workspace_tools.py'] + (['memory_tools.py'] if memory else []):
        for node in ast.walk(ast.parse((base / module).read_text('utf-8-sig'))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(
                    isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == 'tool'
                    for d in node.decorator_list):
                names.append(node.name)
    return sorted(names)


def status(base=BASE):
    """Never import Files/Workspace, probe the network, create a lock, or append logs."""
    result = {'diagnostic_contract': 'read-only; local evidence, not authenticated MCP acceptance',
              'python': {'version': sys.version.split()[0], 'executable': sys.executable,
                         'prefix': sys.prefix, 'base_prefix': sys.base_prefix,
                         'isolated_environment': sys.prefix != sys.base_prefix},
              'build': identity(base), 'errors': []}
    try:
        tree = ast.parse((base / 'server.py').read_text('utf-8-sig'))
        result['version'] = next(k.value.value for n in ast.walk(tree) if isinstance(n, ast.Call)
                                 and isinstance(n.func, ast.Name) and n.func.id == 'MCPServer'
                                 for k in n.keywords if k.arg == 'version' and isinstance(k.value, ast.Constant))
    except (OSError, SyntaxError, StopIteration):
        result['errors'].append('server_source_unreadable')
    config = {}
    try:
        config = json.loads((base / 'config.json').read_text('utf-8-sig'))
        if not isinstance(config, dict) or not isinstance(config.get('roots'), dict) or not config['roots']:
            raise ValueError()
        for root in config['roots'].values():
            p = Path(root['path'])
            if not p.is_absolute() or not p.is_dir() or not isinstance(root.get('writable', False), bool):
                raise ValueError()
            for node in [p, *p.parents]:
                info = node.lstat()
                if node.is_symlink() or getattr(info, 'st_file_attributes', 0) & 0x400:
                    raise ValueError()
        if config.get('approval_mode', 'client') not in {'local', 'client'}:
            raise ValueError()
        for key in ['read_only', 'direct_operations']:
            if key in config and not isinstance(config[key], bool):
                raise ValueError()
        spec = config.get('second_brain')
        if spec is not None:
            if not isinstance(spec, dict) or spec.get('root', 'Projects') not in config['roots']:
                raise ValueError()
            relative = spec.get('path', 'Celious/Second Brain')
            if not isinstance(relative, str) or not relative or PureWindowsPath(relative).drive or relative.startswith(('/', '\\')) or ':' in relative:
                raise ValueError()
            if any(p == '..' or p.startswith('.') for p in relative.replace('\\', '/').split('/')):
                raise ValueError()
        result['configuration'] = {'valid': True, 'roots': len(config['roots']),
                                   'memory_configured': bool(config.get('second_brain')),
                                   'approval_mode': config.get('approval_mode', 'client'),
                                   'legacy_client_approval': 'approval_mode' not in config}
    except (OSError, ValueError, TypeError, KeyError):
        config = {}
        result['configuration'] = {'valid': False}
        result['errors'].append('configuration_invalid_or_missing')
    try:
        profile = base / '.runtime/profiles/celious.yaml'
        resolved = tunnel_id(config, profile)
        result['connection_configuration'] = {'identity_valid': True, 'source': 'config' if 'tunnel_id' in config else 'legacy_profile'}
        if profile.is_file():
            result['connection_configuration']['profile_identity_matches'] = tunnel_id({}, profile) == resolved
    except (OSError, ValueError):
        result['connection_configuration'] = {'identity_valid': False}
    try:
        result['tools'] = {'names': tool_names(base, bool(config.get('second_brain'))),
                           'evidence': 'static registration inventory; live discovery still required'}
        result['tools']['count'] = len(result['tools']['names'])
    except (OSError, SyntaxError):
        result['errors'].append('tool_source_unreadable')
    dependencies = []
    lock = base / 'requirements.lock.txt'
    if lock.is_file():
        for line in lock.read_text('utf-8-sig').splitlines():
            if '==' not in line or line.lstrip().startswith('#'):
                continue
            name, expected = line.split('==', 1)
            try:
                actual = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                actual = None
            dependencies.append(dict(name=name, expected=expected, actual=actual, matches=actual == expected))
    result['dependencies'] = {'lock_present': lock.is_file(), 'versions': dependencies,
                               'matches': bool(dependencies) and all(d['matches'] for d in dependencies)}
    cfg = Path(sys.prefix) / 'pyvenv.cfg'
    result['python']['inherits_site_packages'] = cfg.is_file() and 'include-system-site-packages = true' in cfg.read_text().lower()
    runtime = base / '.runtime'
    try:
        tray = json.loads((runtime / 'tray-status.json').read_text('utf-8'))
        result['connection'] = {'reported_state': tray.get('state'), 'busy': tray.get('busy'),
                                'status_age_seconds': round(time.time() - (runtime / 'tray-status.json').stat().st_mtime),
                                'authenticated_acceptance': 'not probed'}
    except (OSError, ValueError):
        result['connection'] = {'reported_state': 'unknown', 'authenticated_acceptance': 'not probed'}
    pending = 0
    for node in (runtime / 'second-brain').glob('journal-*.json'):
        try:
            pending += json.loads(node.read_text('utf-8')).get('status') in {'prepared', 'applying', 'recovery_required'}
        except (OSError, ValueError):
            result['errors'].append('unreadable_memory_journal')
    result['recovery'] = {'pending_memory_journals': pending,
                          'overwrite_records': len(list((runtime / 'backups').glob('*/record.json'))),
                          'trash_records': len(list((runtime / 'trash').glob('*/record.json'))),
                          'full_backup_verified': False, 'note': 'Inventory only; verify checkpoint separately'}
    result['logs'] = {'audit_exists': (runtime / 'audit.jsonl').is_file(),
                      'connection_log_exists': (runtime / 'tray-connection.log').is_file(),
                      'startup_error_log_exists': (runtime / 'tray-error.log').is_file(),
                      'contents': 'not disclosed; inspect locally after a failure'}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'approve', 'revoke'], nargs='?', default='status')
    parser.add_argument('--root')
    parser.add_argument('--path', default='')
    parser.add_argument('--minutes', type=int, default=15)
    parser.add_argument('--yes', action='store_true', help='Owner confirms the displayed scope locally')
    args = parser.parse_args()
    if args.action == 'status':
        print(json.dumps(status(), indent=2))
        return
    from engine import Files
    from authorization import grant, revoke
    if args.action == 'approve':
        if not args.root:
            parser.error('--root is required')
        if not args.yes:
            print(json.dumps(dict(root=args.root, relative_scope=args.path, minutes=args.minutes)))
            answer = input('Allow ALL permitted direct mutations inside the selected directory scope for this session window? Type APPROVE: ')
            if answer != 'APPROVE':
                parser.error('Not approved; no grant written')
        result = grant(Files(), args.root, args.path, args.minutes)
    else:
        result = revoke(Files())
    print(json.dumps(result))


if __name__ == '__main__':
    main()
