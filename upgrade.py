"""Reviewed local source upgrade; preserves roots, profiles, credentials and notes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

BASE = Path(__file__).resolve().parent
MODULES = ['engine.py', 'server.py', 'second_brain.py', 'project_memory.py', 'memory_tools.py', 'spreadsheets.py']
TESTS = ['test_service.py', 'test_tray.py', 'test_second_brain.py', 'test_project_memory.py',
         'test_memory_protocol.py', 'test_spreadsheets.py']
GUIDES = ['SPREADSHEETS.md', 'LICENSE', 'README.md', 'PROJECT-MEMORY.md', 'SECOND-BRAIN.md', 'INSTALLATION-A-TO-Z.md',
          'PROJECT-EXPLAINED.md', 'VALIDATION.md', 'SECURITY.md', 'PUBLISHING.md', 'TROUBLESHOOTING.md']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def checked(path):
    for node in [path, *path.parents]:
        if node.exists():
            info = node.lstat()
            if node.is_symlink() or getattr(info, 'st_file_attributes', 0) & 0x400 or (node.is_file() and info.st_nlink > 1):
                raise ValueError('Linked paths are not supported')
    return path

def replace(path, data):
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    with os.fdopen(fd, 'wb') as output:
        output.write(data)
    os.replace(temporary, path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installation', type=Path, required=True)
    parser.add_argument('--backup-dir', type=Path, required=True)
    parser.add_argument('--enable-memory', action='store_true')
    parser.add_argument('--apply', action='store_true', help='Apply reviewed file/config overlay, never migrate notes')
    parser.add_argument('--connection-off', action='store_true', help='Operator confirms all clients for this installation are OFF')
    args = parser.parse_args()
    live = checked(args.installation.absolute())
    backup = checked(args.backup_dir.absolute())
    if live == BASE or live.is_relative_to(BASE) or BASE.is_relative_to(live):
        parser.error('Use a separate source folder and existing installation')
    config_path = checked(live/'service/config.json')
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes.decode('utf-8-sig'))
    excluded = [live, BASE, *(Path(r['path']).absolute() for r in config['roots'].values())]
    if any(backup.is_relative_to(p) or p.is_relative_to(backup) for p in excluded):
        parser.error('Backup folder must be outside the installation and authorized roots')
    changes = {'service/'+name: checked(BASE/'service'/name).read_bytes() for name in MODULES+TESTS}
    lock = checked(live/'service/requirements.lock.txt')
    if not lock.is_file():
        parser.error('Dependency lock missing; review the existing environment separately before this source-only overlay')
    if lock.read_text('utf-8-sig').splitlines() != (BASE/'service/requirements.lock.txt').read_text('utf-8-sig').splitlines():
        parser.error('Dependency lock differs; use a reviewed environment upgrade before this source-only overlay')
    changes.update({name: checked(BASE/name).read_bytes() for name in GUIDES})
    if args.enable_memory and 'second_brain' not in config:
        config['second_brain'] = dict(root='Projects', path='Archives', flat_projects=True)
        changes['service/config.json'] = (json.dumps(config, indent=2)+'\n').encode()
    for name in changes:
        checked(live/name)
    status_path = live/'service/.runtime/tray-status.json'
    if status_path.exists():
        status = json.loads(status_path.read_text('utf-8'))
        if status.get('state') != 'off' or status.get('busy'):
            parser.error('Switch this installation OFF before upgrade; do not edit status files')
    print(json.dumps(dict(changes={n:sha(d) for n,d in changes.items()}, memory_enabled='second_brain' in config,
                         migration='not performed', applied=False), indent=2))
    if not args.apply:
        return
    if not args.connection_off:
        parser.error('--apply requires --connection-off after stopping the actual clients')
    # This overlay checkpoint supplements the operator's verified full backup.
    folder = backup/('source-upgrade-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    folder.mkdir(parents=True, exist_ok=False)
    originals = {n:(live/n).read_bytes() if (live/n).exists() else None for n in changes}
    files = {n:d for n,d in originals.items() if d is not None}
    files['service/config.json'] = config_bytes
    archive = folder/'overlay-before.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for n,d in files.items(): output.writestr(n,d)
    with zipfile.ZipFile(archive) as verify:
        assert verify.testzip() is None
        assert all(verify.read(n)==d for n,d in files.items())
    manifest = dict(scope='overlay files and original configuration; NOT a full installation/data backup',
                    absent_before=[n for n,d in originals.items() if d is None],
                    files={n:sha(d) for n,d in files.items()}, archive_sha256=sha(archive.read_bytes()))
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2),'utf-8')
    try:
        for n,d in changes.items(): replace(live/n,d)
        assert all((live/n).read_bytes()==d for n,d in changes.items())
    except Exception:
        for n,d in originals.items():
            if d is not None: replace(live/n,d)
            elif (live/n).exists():
                target=folder/'failed-new-files'/n
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.move(str(live/n),str(target))
        raise
    print(json.dumps(dict(applied=True, checkpoint=str(folder), migration='not performed',
                          roots_preserved=True, profile_preserved=True)))

if __name__ == '__main__':
    main()
