"""Privacy rejection and package tampering checks in disposable files."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import json
from contextlib import redirect_stdout
import io
import runpy
import sys
import shutil
import zipfile
from package import scan,sources,verify,BASE
import upgrade
import package

class PackageTests(unittest.TestCase):
    def complete_fixture(self, source):
        files = ['service/server.py', 'service/requirements.lock.txt', 'README.md']
        (source/'service').mkdir(parents=True)
        for name, data in zip(files, [b'new server', b'fixed lock', b'new guide']):
            (source/name).write_bytes(data)
        hashes={name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in files}
        build=dict(commit='a'*40,dirty=False,files=hashes,source_digest=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest())
        (source/'BUILD-IDENTITY.json').write_text(json.dumps(build),'utf-8')
        (source/'PACKAGE-MANIFEST.json').write_text(json.dumps(hashes),'utf-8')
        return files,build

    def test_complete_build_refuses_tampering_dirty_or_missing_identity(self):
        with tempfile.TemporaryDirectory(prefix='celious-complete-package-') as temporary:
            source=Path(temporary)/'source'
            names,build=self.complete_fixture(source)
            with patch.object(upgrade,'BASE',source),patch.object(package,'FILES',names):
                self.assertEqual(set(upgrade.complete_build()),set(names)|{'BUILD-IDENTITY.json','PACKAGE-MANIFEST.json'})
                (source/'README.md').write_bytes(b'tampered')
                with self.assertRaisesRegex(ValueError,'hashes'): upgrade.complete_build()
                (source/'README.md').write_bytes(b'new guide')
                build['dirty']=True
                (source/'BUILD-IDENTITY.json').write_text(json.dumps(build),'utf-8')
                with self.assertRaisesRegex(ValueError,'clean commit'): upgrade.complete_build()
                (source/'BUILD-IDENTITY.json').unlink()
                with self.assertRaisesRegex(ValueError,'extracted clean'): upgrade.complete_build()

    def test_complete_upgrade_preserves_private_state_and_recovers_failed_apply(self):
        with tempfile.TemporaryDirectory(prefix='celious-complete-upgrade-') as temporary:
            root=Path(temporary);source=root/'source';live=root/'installed';backup=root/'recovery'
            names,build=self.complete_fixture(source)
            (live/'service/.runtime').mkdir(parents=True)
            (root/'projects').mkdir()
            config=json.dumps(dict(roots=dict(Projects=dict(path=str(root/'projects'),writable=True)))).encode()
            (live/'service/config.json').write_bytes(config)
            (live/'service/.runtime/sentinel').write_bytes(b'private durable state')
            (live/'service/requirements.lock.txt').write_bytes(b'fixed lock')
            (live/'service/server.py').write_bytes(b'old server')
            (live/'BUILD-IDENTITY.json').write_bytes(b'old identity')
            original={str(p.relative_to(live)):p.read_bytes() for p in live.rglob('*') if p.is_file()}
            argv=['upgrade.py','--installation',str(live),'--backup-dir',str(backup),'--complete-build','--apply','--connection-off']
            replace=upgrade.replace
            def fail_identity(path,data):
                if path.name=='BUILD-IDENTITY.json' and data!=b'old identity': raise OSError('Injected identity-write failure')
                replace(path,data)
            with patch.object(upgrade,'BASE',source),patch.object(package,'FILES',names),patch('sys.argv',argv),redirect_stdout(io.StringIO()):
                with patch.object(upgrade,'replace',fail_identity),self.assertRaises(OSError): upgrade.main()
                self.assertEqual(original,{str(p.relative_to(live)):p.read_bytes() for p in live.rglob('*') if p.is_file()})
                upgrade.main()
            self.assertEqual((live/'service/config.json').read_bytes(),config)
            self.assertEqual((live/'service/.runtime/sentinel').read_bytes(),b'private durable state')
            self.assertEqual(json.loads((live/'BUILD-IDENTITY.json').read_text())['commit'],build['commit'])
            self.assertTrue(all((live/name).read_bytes()==(source/name).read_bytes() for name in names))

    def launcher(self, config, profile=None):
        temporary = tempfile.TemporaryDirectory(prefix='celious-launcher-test-')
        self.addCleanup(temporary.cleanup)
        service = Path(temporary.name) / 'service'
        service.mkdir()
        shutil.copy2(BASE/'service/connect.py', service/'connect.py')
        shutil.copy2(BASE/'service/connection_settings.py', service/'connection_settings.py')
        (service/'config.json').write_text(json.dumps(config), 'utf-8')
        if profile is not None:
            profiles = service/'.runtime/profiles'
            profiles.mkdir(parents=True)
            (profiles/'celious.yaml').write_text(profile, 'utf-8')
        before = {p.relative_to(service):p.read_bytes() for p in service.rglob('*') if p.is_file()}
        with patch('sys.path', [str(service), *sys.path]):
            namespace = runpy.run_path(str(service/'connect.py'), run_name='launcher_fixture')
        self.assertEqual(before, {p.relative_to(service):p.read_bytes() for p in service.rglob('*') if p.is_file() and p.suffix != '.pyc'})
        return namespace

    def test_launcher_explicit_identity_does_not_require_profile(self):
        identity = 'tunnel_'+'0'*32
        self.assertEqual(self.launcher({'tunnel_id':identity})['TUNNEL_ID'], identity)
        self.assertEqual(self.launcher({'tunnel_id':identity}, 'invalid profile')['TUNNEL_ID'], identity)

    def test_launcher_legacy_profile_quotes_and_section_scope(self):
        identity = 'tunnel_'+'0'*32
        for quote in ['', '"', "'"]:
            with self.subTest(quote=quote):
                profile = 'control_plane:\n  tunnel_id: '+quote+identity+quote+'\nlogging:\n  tunnel_id: ignored\n'
                self.assertEqual(self.launcher({}, profile)['TUNNEL_ID'], identity)

    def test_launcher_rejects_invalid_explicit_identity_without_fallback(self):
        for value in [None, '', 'invalid', 42]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.launcher({'tunnel_id':value}, 'control_plane:\n  tunnel_id: '+'tunnel_'+'0'*32+'\n')

    def test_launcher_rejects_missing_malformed_and_ambiguous_profiles(self):
        identity = 'tunnel_'+'0'*32
        line = '  tunnel_id: '+identity+'\n'
        for profile in [None, 'other:\n'+line, 'control_plane:\n  tunnel_id: invalid\n',
                        'control_plane:\n'+line+line, 'control_plane:\n'+line+'control_plane:\n'+line,
                        'control_plane:\n'+line+'  tunnel_id: invalid\n',
                        'control_plane:\n  tunnel_id: "'+identity+"'\n"]:
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                self.launcher({}, profile)

    def test_missing_dependency_lock_is_an_actionable_refusal(self):
        with tempfile.TemporaryDirectory(prefix='celious-missing-lock-') as temporary:
            root=Path(temporary);source=root/'source';live=root/'installed'
            for p in [source/'service', live/'service']:p.mkdir(parents=True)
            for name in upgrade.MODULES+upgrade.TESTS:(source/'service'/name).write_bytes(b'fixture')
            (live/'service/config.json').write_text(json.dumps({'roots':{}}), 'utf-8')
            argv=['upgrade.py','--installation',str(live),'--backup-dir',str(root/'recovery')]
            with patch.object(upgrade,'BASE',source),patch('sys.argv',argv),redirect_stdout(io.StringIO()),patch('sys.stderr',new_callable=io.StringIO) as error:
                with self.assertRaises(SystemExit):upgrade.main()
            self.assertIn('Dependency lock missing',error.getvalue())
            self.assertFalse((root/'recovery').exists())

    def test_privacy_patterns(self):
        samples=['sk-'+'x'*30,'tunnel_'+'a'*32,'plugin_asdk_app_'+'a'*24,
                 'C:/'+ 'Users/'+'Synthetic/private.txt','synthetic'+'@'+'example.invalid']
        for value in samples:
            with self.subTest(value=value[:10]):
                with self.assertRaises(ValueError):scan('fixture.md',value.encode())
        scan('fixture.md',('tunnel_'+'0'*32).encode())

    def test_tampered_package_rejected(self):
        data=sources()
        archive=BASE/'dist/celious-files-source.zip'
        verify(archive,data)
        with tempfile.TemporaryDirectory(prefix='celious-package-test-') as tmp:
            target=Path(tmp)/archive.name
            with zipfile.ZipFile(archive) as original,zipfile.ZipFile(target,'w') as altered:
                for name in original.namelist():
                    content=original.read(name)
                    if name.endswith('/README.md'):content+=b'\nTampered'
                    altered.writestr(name,content)
            (target.parent/'SHA256SUMS.txt').write_text(hashlib.sha256(target.read_bytes()).hexdigest()+'  '+target.name+'\n','ascii')
            with self.assertRaises(ValueError):verify(target,data)

    def test_overlay_failure_restores_originals_and_preserves_new_files(self):
        with tempfile.TemporaryDirectory(prefix='celious-overlay-test-') as tmp:
            root=Path(tmp);source=root/'source';live=root/'installed';backup=root/'backups'
            for p in [source/'service',live/'service',root/'projects',root/'vault']:p.mkdir(parents=True)
            for name in upgrade.MODULES+upgrade.TESTS:(source/'service'/name).write_bytes(b'new module')
            for name in upgrade.GUIDES:(source/name).write_bytes(b'new guide')
            (source/'service/requirements.lock.txt').write_bytes(b'same lock\r\n')
            (live/'service/requirements.lock.txt').write_bytes(b'same lock\n')
            for name in ['engine.py','server.py']:(live/'service'/name).write_bytes(b'old module')
            (live/'service/test_service.py').write_bytes(b'stale installed test')
            config=json.dumps(dict(roots=dict(Projects=dict(path=str(root/'projects')),Vault=dict(path=str(root/'vault'))))).encode()
            (live/'service/config.json').write_bytes(config)
            real_replace=upgrade.replace;count=0
            def interrupted(path,data):
                nonlocal count
                count+=1
                if count==4:raise OSError('Injected overlay interruption')
                real_replace(path,data)
            argv=['upgrade.py','--installation',str(live),'--backup-dir',str(backup),'--enable-memory','--apply','--connection-off']
            with patch.object(upgrade,'BASE',source),patch.object(upgrade,'replace',interrupted),patch('sys.argv',argv),redirect_stdout(io.StringIO()):
                with self.assertRaises(OSError):upgrade.main()
            self.assertEqual((live/'service/engine.py').read_bytes(),b'old module')
            self.assertEqual((live/'service/server.py').read_bytes(),b'old module')
            self.assertEqual((live/'service/config.json').read_bytes(),config)
            self.assertEqual((live/'service/test_service.py').read_bytes(),b'stale installed test')
            self.assertFalse((live/'service/second_brain.py').exists())
            self.assertEqual(len(list(backup.glob('*/failed-new-files/service/second_brain.py'))),1)
            with patch.object(upgrade,'BASE',source),patch('sys.argv',argv),redirect_stdout(io.StringIO()):
                upgrade.main()
            self.assertEqual((live/'LICENSE').read_bytes(),(source/'LICENSE').read_bytes())
            self.assertEqual((live/'service/engine.py').read_bytes(),b'new module')
            for name in upgrade.TESTS:
                self.assertEqual((live/'service'/name).read_bytes(),(source/'service'/name).read_bytes())
            with zipfile.ZipFile(next(backup.glob('*/overlay-before.zip'))) as checkpoint:
                self.assertEqual(checkpoint.read('service/test_service.py'),b'stale installed test')
            self.assertEqual(json.loads((live/'service/config.json').read_bytes())['roots'],json.loads(config)['roots'])

if __name__=='__main__':unittest.main(verbosity=2)
