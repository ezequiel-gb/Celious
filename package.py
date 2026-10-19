"""Build a source ZIP using an explicit allowlist and credential checks."""
import hashlib
import argparse
import json
import subprocess
from pathlib import Path
import re
import zipfile

BASE = Path(__file__).resolve().parent
FILES = ['LICENSE', 'README.md', 'TROUBLESHOOTING.md', 'SECURITY.md', 'PUBLISHING.md', 'VALIDATION.md',
         'SPREADSHEETS.md', 'WORKFLOWS.md', 'INSTALLATION-A-TO-Z.md', 'PROJECT-EXPLAINED.md', 'SECOND-BRAIN.md', 'PROJECT-MEMORY.md',
         '.gitignore', '.github/workflows/windows.yml', 'setup.py', 'upgrade.py', 'package.py', 'test_installation.py', 'test_package.py',
         'Install.cmd', 'Start-Celious.cmd', 'Diagnostics.cmd', 'CONSOLIDATION.md', 'DOCUMENTS.md', 'MAINTENANCE.md']
FILES += ['service/' + name for name in ['engine.py', 'server.py', 'spreadsheets.py', 'documents.py', 'test_spreadsheets.py', 'connect.py', 'tray_core.py',
          'tray.py', 'install_tray.py', 'review.py', 'test_service.py', 'test_tray.py',
          'requirements.txt', 'requirements.lock.txt', 'config.example.json',
          'second_brain.py', 'project_memory.py', 'memory_tools.py', 'test_second_brain.py', 'test_project_memory.py', 'test_memory_protocol.py',
          'operations_state.py', 'ingestion.py', 'workflows.py', 'workspace_tools.py', 'test_workflows.py', 'test_workspace_protocol.py',
          'authorization.py', 'diagnostics.py', 'connection_settings.py', 'test_stabilisation.py', 'test_documents.py']]
FILES += ['assets/celious-' + state + '.ico' for state in ['on', 'off', 'starting', 'error']]


def scan(name, data):
    if name.endswith('.ico'):
        return
    text = data.decode('utf-8-sig')
    checks = [
        (r'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}', 'Possible API secret'),
        (r'plugin_asdk_app_[a-z0-9]{20,}|org-[A-Za-z0-9]{16,}', 'Possible account identifier'),
        (r'(?i)[a-z]:[/\\]+Users[/\\]+[^/\\\s]+', 'Personal Windows profile path'),
        (r'(?i)\b[A-Z0-9_.+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', 'Email address requiring review'),
    ]
    for pattern, message in checks:
        if re.search(pattern, text):
            raise ValueError(message+' in '+name)
    if any(v != 'tunnel_'+'0'*32 for v in re.findall(r'tunnel_[a-z0-9]{32}', text)):
        raise ValueError('Account-specific tunnel in '+name)

def sources():
    result = {}
    for name in FILES:
        file = BASE / name
        if not file.is_file() or not file.resolve().is_relative_to(BASE):
            raise ValueError('Missing or linked source file: ' + name)
        for node in [file, *file.relative_to(BASE).parents]:
            # Parents from relative_to are relative paths; inspect using BASE.
            node = node if node.is_absolute() else BASE/node
            info = node.lstat()
            if node.is_symlink() or getattr(info, 'st_file_attributes', 0)&0x400 or (node.is_file() and info.st_nlink>1):
                raise ValueError('Linked source file: '+name)
        data = file.read_bytes()
        scan(name, data)
        result[name] = data
    return result

def tracked_check():
    tracked = subprocess.check_output(['git', '-c', 'safe.directory='+BASE.as_posix(),
                                       '-C', str(BASE), 'ls-files'], text=True).splitlines()
    if set(tracked) != set(FILES):
        raise ValueError('Tracked files differ from package allowlist; review before publication')

def history_check(baseline):
    git=['git','-c','safe.directory='+BASE.as_posix(),'-C',str(BASE)]
    subprocess.run(git+['merge-base','--is-ancestor',baseline,'HEAD'],check=True)
    commits=subprocess.check_output(git+['rev-list',baseline+'..HEAD'],text=True).splitlines()
    for commit in commits:
        names=subprocess.check_output(git+['ls-tree','-r','--name-only',commit],text=True).splitlines()
        for name in names:
            if name not in FILES:
                raise ValueError('Historical file outside current allowlist; review: '+name)
            scan(name,subprocess.check_output(git+['show',commit+':'+name]))
    print('Privacy checked '+str(len(commits))+' commit trees after the pinned baseline.')

def verify(archive, data):
    prefix='celious-files/'
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None or set(bundle.namelist()) != {prefix+n for n in data}|{prefix+'PACKAGE-MANIFEST.json', prefix+'BUILD-IDENTITY.json'} or len(bundle.namelist()) != len(data)+2:
            raise ValueError('Package membership or CRC mismatch')
        manifest=json.loads(bundle.read(prefix+'PACKAGE-MANIFEST.json'))
        expected={n:hashlib.sha256(d).hexdigest() for n,d in data.items()}
        if manifest != expected:
            raise ValueError('Package manifest differs from current source')
        build = json.loads(bundle.read(prefix+'BUILD-IDENTITY.json'))
        if build.get('files') != expected or build.get('source_digest') != hashlib.sha256(json.dumps(expected, sort_keys=True).encode()).hexdigest():
            raise ValueError('Build identity differs from source')
        for n,d in data.items():
            actual=bundle.read(prefix+n)
            scan(n,actual)
            if actual != d:
                raise ValueError('Package source mismatch: '+n)
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    if (archive.parent/'SHA256SUMS.txt').read_text('ascii') != digest+'  '+archive.name+'\n':
        raise ValueError('Package checksum mismatch')
    return digest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Check existing ZIP against source and checksums')
    parser.add_argument('--check-tracked', action='store_true', help='Require Git tracked paths to equal the public allowlist')
    parser.add_argument('--check-history', metavar='BASELINE', help='Scan every subsequent commit tree before publication')
    args=parser.parse_args()
    if args.check_tracked: tracked_check()
    if args.check_history: history_check(args.check_history)
    data=sources()
    destination = BASE / 'dist'
    archive = destination / 'celious-files-source.zip'
    if not args.verify:
        destination.mkdir(exist_ok=True)
        entries=dict(data)
        entries['PACKAGE-MANIFEST.json']=json.dumps({n:hashlib.sha256(d).hexdigest() for n,d in data.items()},sort_keys=True,indent=2).encode()
        hashes = {n:hashlib.sha256(d).hexdigest() for n,d in data.items()}
        commit, dirty = None, None
        try:
            git = ['git', '--no-optional-locks', '-C', str(BASE)]
            if Path(subprocess.check_output(git+['rev-parse','--show-toplevel'], stderr=subprocess.DEVNULL, text=True).strip()).resolve() == BASE:
                commit = subprocess.check_output(git+['rev-parse','HEAD'], text=True).strip()
                dirty = bool(subprocess.check_output(git+['status','--porcelain','--untracked-files=no'], text=True))
        except (OSError, subprocess.SubprocessError):
            previous = BASE/'BUILD-IDENTITY.json'
            if previous.is_file():
                build = json.loads(previous.read_text('utf-8'))
                if build.get('files') == hashes:
                    commit, dirty = build.get('commit'), build.get('dirty')
        entries['BUILD-IDENTITY.json'] = json.dumps(dict(commit=commit, dirty=dirty, files=hashes,
            source_digest=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()),sort_keys=True,indent=2).encode()
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
            for name,content in sorted(entries.items()):
                info=zipfile.ZipInfo('celious-files/'+name, date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o100644<<16
                output.writestr(info,content)
        digest=hashlib.sha256(archive.read_bytes()).hexdigest()
        (destination/'SHA256SUMS.txt').write_text(digest+'  '+archive.name+'\n','ascii')
    digest=verify(archive,data)
    print(f'Verified {len(FILES)} allowlisted source files plus generated manifest and build identity.')
    print(archive)
    print('SHA256: ' + digest)


if __name__ == '__main__':
    main()
