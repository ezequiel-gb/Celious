"""Real disposable fresh installers and upgrades from pinned v0.2/v0.3 source."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

BASE=Path(__file__).resolve().parent
PUBLIC_BASELINE='1181f82fd6df5802cf5cc4317dd35ce3f42799b0'
MEMORY_BASELINE='a1cb1890cc0ee93c46dd979d2c79a44ccf9a141f'

def run(*args):
    subprocess.run([str(a) for a in args],check=True)

def verify_service_tests(service, python):
    from upgrade import TESTS
    for name in TESTS:
        assert (service/name).read_bytes()==(BASE/'service'/name).read_bytes(), 'Stale installed service test: '+name
    config_path=service/'config.json'
    original=config_path.read_bytes()
    try:
        # A standalone test must not read or mutate the installation's roots.
        config_path.write_text(json.dumps(dict(roots={'Unavailable':dict(path=str(service/'nonexistent-root'),writable=False)})), 'utf-8')
        run(python,service/'test_service.py')
    finally:
        config_path.write_bytes(original)
    assert config_path.read_bytes()==original
    print('Installed service tests match source; file protocol ignores installed roots/configuration.',flush=True)

def verify_legacy_launcher(service, python):
    config_path=service/'config.json'
    original=config_path.read_bytes()
    config=json.loads(original)
    config.pop('tunnel_id',None);config.pop('plugin_url',None)
    try:
        config_path.write_text(json.dumps(config),'utf-8')
        legacy=config_path.read_bytes()
        profile=service/'.runtime/profiles/celious.yaml';profile_bytes=profile.read_bytes()
        run(python,service/'connect.py','--check')
        run(python,'-c',"import sys;sys.path.insert(0,sys.argv[1]);import tray;assert tray.PLUGIN=='https://chatgpt.com/plugins'",service)
        assert config_path.read_bytes()==legacy and profile.read_bytes()==profile_bytes
    finally:
        config_path.write_bytes(original)
    print('Legacy profile identity supports launcher check and tray import without config/profile mutation.',flush=True)

async def seed_v03(service, manifest):
    sys.path.insert(0,str(service))
    from mcp import Client
    from mcp.client.stdio import StdioServerParameters
    from engine import Files
    from second_brain import Brain,digest
    async with Client(StdioServerParameters(command=sys.executable,args=[str(service/'server.py')])) as client:
        assert len((await client.list_tools()).tools)==19
        def unpack(result):
            assert not result.is_error,str(result)
            return json.loads(next(c.text for c in result.content if getattr(c,'type',None)=='text'))
        text='User: Preserve existing memory.\r\n'
        claims=[dict(type='requirement',title='Existing memory',topic='Upgrade',key='preserve',value='memory',
                     evidence='Preserve existing memory.',epistemic='accepted',uncertainty='Synthetic v0.3 fixture')]
        plan=unpack(await client.call_tool('memory_archive_preview',dict(title='Existing v0.3 source',text=text,
                    source_ref='synthetic v0.3 fixture',completeness='excerpt',claims_json=json.dumps(claims))))
        unpack(await client.call_tool('memory_commit',dict(plan_id=plan['plan_id'],approved_sha256=plan['plan_sha256'])))
        assert not unpack(await client.call_tool('memory_inspect',{}))['issues']
    config=json.loads((service/'config.json').read_text())
    brain=Brain(Files(config,service/'.runtime'),prefix=config['second_brain']['path'])
    manifest.write_text(json.dumps({r['meta']['id']:digest(brain.path(r['path']).read_bytes()) for r in brain.records()}))
    brain.path('WORKFLOW.md').write_bytes(b'# Existing workflow\r\nPreserve this.\r\n')

async def probe(service, initialize, legacy, count, cli=False, expected_records=None):
    sys.path.insert(0,str(service))
    from mcp import Client
    from mcp.client.stdio import StdioServerParameters
    from engine import Files
    from second_brain import Brain, digest
    from project_memory import ProjectBrain
    config=json.loads((service/'config.json').read_text('utf-8'))
    files=Files(config,service/'.runtime')
    memory=config.get('second_brain',dict(path='Archives'))
    prefix=Path(config['roots']['Projects']['path'])/memory['path']
    original=json.loads(expected_records.read_text()) if expected_records else {}
    if legacy:
        old=Brain(files,prefix=memory['path'])
        evidence='User: Use portable Markdown.\r\n'
        plan=old.plan_archive('Synthetic legacy evidence',evidence,'synthetic public fixture','excerpt',[
            dict(type='requirement',title='Portable memory',topic='Memory',key='format',value='Markdown',
                 evidence='Use portable Markdown.',epistemic='accepted',uncertainty='Synthetic upgrade fixture')])
        old.commit(plan['plan_id'],plan['plan_sha256'])
        original={r['meta']['id']:digest(old.path(r['path']).read_bytes()) for r in old.records()}
        old.path('WORKFLOW.md').write_bytes(b'# Existing workflow\r\nPreserve this.\r\n')
    def unpack(result):
        assert not result.is_error,str(result)
        return json.loads(next(c.text for c in result.content if getattr(c,'type',None)=='text'))
    if initialize and cli:
        assert not (prefix/'LAYOUT.md').exists()
        command=[sys.executable,str(service/'second_brain.py')]
        plan=json.loads(subprocess.check_output(command+['plan-migrate'],text=True))
        run(*command,'commit',plan['plan_id'],plan['plan_sha256'])
        inspection=json.loads(subprocess.check_output(command+['inspect'],text=True))
        assert not inspection['issues'] and (prefix/'WORKFLOW.md').is_file()
    async with Client(StdioServerParameters(command=sys.executable,args=[str(service/'server.py')])) as client:
        assert len((await client.list_tools()).tools)==count
        if initialize:
            if not cli:
                assert not (prefix/'LAYOUT.md').exists(), 'Installer must not silently initialize'
                plan=unpack(await client.call_tool('memory_migrate_preview',{}))
                unpack(await client.call_tool('memory_commit',dict(plan_id=plan['plan_id'],approved_sha256=plan['plan_sha256'])))
            inspected=unpack(await client.call_tool('memory_inspect',{}))
            assert not inspected['issues'] and inspected['layout']=='project-v4'
            assert (prefix/'WORKFLOW.md').is_file()
            if legacy or expected_records:
                brain=ProjectBrain(files,prefix=memory['path'])
                assert {r['meta']['id']:digest(brain.path(r['path']).read_bytes()) for r in brain.records()}==original
                assert (prefix/'WORKFLOW.md').read_bytes()==b'# Existing workflow\r\nPreserve this.\r\n'
                hits=unpack(await client.call_tool('memory_search',dict(query='memory' if expected_records else 'portable Markdown')))['hits']
                assert hits and hits[0]['provenance_valid']
            else: assert inspected['notes']==0
        assert not (await client.call_tool('read_document',dict(root='Vault',path='INDEX.md'))).is_error
    print(json.dumps(dict(probe=True,tools=count,initialized=initialize,legacy_preserved=legacy)),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe',type=Path)
    parser.add_argument('--initialize',action='store_true')
    parser.add_argument('--legacy',action='store_true')
    parser.add_argument('--count',type=int,default=33)
    parser.add_argument('--cli',action='store_true')
    parser.add_argument('--seed-v03',type=Path)
    parser.add_argument('--expected-records',type=Path)
    args=parser.parse_args()
    if args.probe:
        if args.seed_v03:
            asyncio.run(seed_v03(args.probe,args.seed_v03));return
        asyncio.run(probe(args.probe,args.initialize,args.legacy,args.count,args.cli,args.expected_records));return
    from package import FILES
    with tempfile.TemporaryDirectory(prefix='celious release acceptance ') as tmp:
        workspace=Path(tmp)
        fresh=workspace/'fresh source with spaces';fresh.mkdir()
        for name in FILES:
            target=fresh/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/name,target)
        run(sys.executable,fresh/'setup.py','--tunnel-id','tunnel_'+'0'*32,'--second-brain')
        python=fresh/'service/.venv/Scripts/python.exe'
        assert 'include-system-site-packages = false' in (fresh/'service/.venv/pyvenv.cfg').read_text().lower()
        run(python,'-m','pip','check')
        verify_legacy_launcher(fresh/'service',python)
        verify_service_tests(fresh/'service',python)
        run(python,BASE/'test_installation.py','--probe',fresh/'service','--initialize','--cli')
        config_path=fresh/'service/config.json'
        config=json.loads(config_path.read_text());config.pop('second_brain');config_path.write_text(json.dumps(config))
        run(python,BASE/'test_installation.py','--probe',fresh/'service','--count','20')
        run(python,fresh/'package.py')
        run(python,fresh/'test_package.py')
        for name in ['test_service.py','test_tray.py','test_second_brain.py','test_project_memory.py','test_memory_protocol.py','test_spreadsheets.py']:
            run(python,fresh/'service'/name)
        run(python,fresh/'service/tray.py','--self-test')
        legacy=workspace/'public baseline installation';legacy.mkdir()
        archive=workspace/'public-baseline.zip'
        run('git','-c','safe.directory='+BASE.as_posix(),'-C',BASE,'archive','--format=zip','--output',archive,PUBLIC_BASELINE)
        with zipfile.ZipFile(archive) as bundle:bundle.extractall(legacy)
        run(sys.executable,legacy/'setup.py','--tunnel-id','tunnel_'+'0'*32)
        old_python=legacy/'service/.venv/Scripts/python.exe'
        run(old_python,legacy/'service/test_service.py')
        config_path=legacy/'service/config.json'
        before=json.loads(config_path.read_text())
        before['operator_setting']='synthetic preserved setting'
        config_path.write_text(json.dumps(before))
        vault=Path(before['roots']['Vault']['path'])/'existing.txt';vault.write_bytes(b'Existing file\r\n')
        profile=legacy/'service/.runtime/profiles/celious.yaml';profile_bytes=profile.read_bytes()
        preview=subprocess.check_output([sys.executable,str(BASE/'upgrade.py'),'--installation',str(legacy),
                                         '--backup-dir',str(workspace/'private backups'),'--enable-memory'],text=True)
        assert not json.loads(preview)['applied']
        assert json.loads(config_path.read_text())==before
        status=legacy/'service/.runtime/tray-status.json'
        status.write_text(json.dumps(dict(state='on',busy=False)))
        rejected=subprocess.run([sys.executable,str(BASE/'upgrade.py'),'--installation',str(legacy),
                                 '--backup-dir',str(workspace/'private backups'),'--apply','--connection-off'],capture_output=True)
        assert rejected.returncode != 0 and not (workspace/'private backups').exists()
        status.write_text(json.dumps(dict(state='off',busy=False)))
        rejected=subprocess.run([sys.executable,str(BASE/'upgrade.py'),'--installation',str(legacy),
                                 '--backup-dir',str(legacy/'unsafe-backup'),'--apply','--connection-off'],capture_output=True)
        assert rejected.returncode != 0 and not (legacy/'unsafe-backup').exists()
        rejected=subprocess.run([sys.executable,str(BASE/'upgrade.py'),'--installation',str(legacy),
                                 '--backup-dir',str(workspace/'private backups'),'--apply'],capture_output=True)
        assert rejected.returncode != 0 and not (workspace/'private backups').exists()
        run(sys.executable,BASE/'upgrade.py','--installation',legacy,'--backup-dir',workspace/'private backups',
            '--enable-memory','--apply','--connection-off')
        after=json.loads(config_path.read_text());spec=after.pop('second_brain')
        assert after==before and spec==dict(root='Projects',path='Archives',flat_projects=True)
        assert profile.read_bytes()==profile_bytes and vault.read_bytes()==b'Existing file\r\n'
        assert (legacy/'service/engine.py').read_bytes()==(BASE/'service/engine.py').read_bytes()
        checkpoints=list((workspace/'private backups').glob('*/overlay-before.zip'));assert len(checkpoints)==1
        with zipfile.ZipFile(checkpoints[0]) as bundle:
            assert bundle.testzip() is None
            assert json.loads(bundle.read('service/config.json'))==before
            assert bundle.read('service/engine.py') != (BASE/'service/engine.py').read_bytes()
        run(old_python,'-m','pip','check')
        verify_service_tests(legacy/'service',old_python)
        run(old_python,BASE/'test_installation.py','--probe',legacy/'service','--initialize','--legacy')
        print('Real fresh install, opt-in/off 33/20 tools, public v0.2 source upgrade, preserved config/profile/files, verified overlay checkpoint, legacy byte migration and workflow preservation passed.',flush=True)
        v03=workspace/'v0.3 existing custom memory';v03.mkdir()
        archive=workspace/'memory-baseline.zip'
        run('git','-c','safe.directory='+BASE.as_posix(),'-C',BASE,'archive','--format=zip','--output',archive,MEMORY_BASELINE)
        with zipfile.ZipFile(archive) as bundle:bundle.extractall(v03)
        run(sys.executable,v03/'setup.py','--tunnel-id','tunnel_'+'0'*32)
        v03_python=v03/'service/.venv/Scripts/python.exe'
        config_path=v03/'service/config.json'
        config=json.loads(config_path.read_text());config['second_brain']=dict(root='Projects',path='Legacy Memory')
        config_path.write_text(json.dumps(config))
        original_config=config_path.read_bytes()
        profile=v03/'service/.runtime/profiles/celious.yaml';profile_bytes=profile.read_bytes()
        manifest=workspace/'v03-original-records.json'
        run(v03_python,BASE/'test_installation.py','--probe',v03/'service','--seed-v03',manifest)
        run(sys.executable,BASE/'upgrade.py','--installation',v03,'--backup-dir',workspace/'v03 private backups',
            '--enable-memory','--apply','--connection-off')
        assert config_path.read_bytes()==original_config and profile.read_bytes()==profile_bytes
        run(v03_python,'-m','pip','check')
        verify_service_tests(v03/'service',v03_python)
        run(v03_python,BASE/'test_installation.py','--probe',v03/'service','--initialize','--cli','--expected-records',manifest)
        assert not (Path(config['roots']['Projects']['path'])/'Archives').exists()
        print('Pinned v0.3 19-tool archive -> source overlay -> OFF CLI migration -> 33-tool retrieval passed; custom prefix, config/profile, CRLF workflow and exact source/knowledge bytes preserved.',flush=True)

if __name__=='__main__':main()
