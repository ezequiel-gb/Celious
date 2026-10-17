"""Local authorization and genuinely read-only diagnostics in disposable roots."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time
import unittest
import asyncio
import sys
import subprocess
import importlib.util
import io
from contextlib import redirect_stderr
from unittest.mock import patch
from authorization import grant, revoke
from diagnostics import status
from engine import Files


class StabilisationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='celious-stabilisation-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'projects'
        self.root.mkdir()
        (self.root / 'allowed').mkdir()
        self.config = dict(approval_mode='local', direct_operations=True,
                           roots={'Projects': dict(path=str(self.root), writable=True)})
        self.files = Files(self.config, self.base / 'runtime')

    def test_unapproved_mutations_refused_without_data_changes(self):
        (self.root / 'allowed/a.txt').write_text('original')
        for call in [lambda: self.files.write('Projects', 'allowed/a.txt', 'changed'),
                     lambda: self.files.edit('Projects', 'allowed/a.txt', 'original', 'changed'),
                     lambda: self.files.move('Projects', 'allowed/a.txt', 'allowed/b.txt'),
                     lambda: self.files.delete('Projects', 'allowed/a.txt'),
                     lambda: self.files.mkdir('Projects', 'new')]:
            with self.assertRaises(PermissionError):
                call()
        self.assertEqual((self.root / 'allowed/a.txt').read_text(), 'original')
        self.assertFalse((self.files.runtime / 'trash').exists())
        self.assertFalse((self.files.runtime / 'backups').exists())

    def test_local_scope_preserves_write_edit_move_backup_delete_restore(self):
        grant(self.files, 'Projects', 'allowed', 15)
        self.files.write('Projects', 'allowed/a.txt', 'first')
        edited = self.files.edit('Projects', 'allowed/a.txt', 'first', 'second')
        self.assertEqual((self.files.runtime / 'backups' / edited['backup_id'] / 'original.bin').read_bytes(), b'first')
        self.files.move('Projects', 'allowed/a.txt', 'allowed/b.txt')
        deleted = self.files.delete('Projects', 'allowed/b.txt')
        self.files.restore(deleted['deletion_id'])
        self.assertEqual((self.root / 'allowed/b.txt').read_text(), 'second')
        with self.assertRaises(PermissionError):
            self.files.write('Projects', 'outside.txt', 'no')
        revoke(self.files)
        with self.assertRaises(PermissionError):
            self.files.delete('Projects', 'allowed/b.txt')

    def test_expiry_and_changed_root_invalidate_approval(self):
        with patch('authorization.time.time', return_value=100):
            grant(self.files, 'Projects', 'allowed', 1)
        with patch('authorization.time.time', return_value=161), self.assertRaises(PermissionError):
            self.files.write('Projects', 'allowed/a.txt', 'no')
        grant(self.files, 'Projects', 'allowed', 1)
        other = self.base / 'other'
        (other / 'allowed').mkdir(parents=True)
        config = dict(self.config, roots={'Projects': dict(path=str(other), writable=True)})
        changed = Files(config, self.files.runtime)
        with self.assertRaises(PermissionError):
            changed.write('Projects', 'allowed/a.txt', 'no')

    def test_multiple_scopes_survive_until_explicit_revocation(self):
        (self.root / 'other').mkdir()
        grant(self.files, 'Projects', 'allowed', 1)
        grant(self.files, 'Projects', 'other', 1)
        self.files.write('Projects', 'allowed/a.txt', 'a')
        self.files.write('Projects', 'other/b.txt', 'b')
        revoke(self.files)
        with self.assertRaises(PermissionError):
            self.files.delete('Projects', 'other/b.txt')

    def test_shared_environment_installer_refuses_before_data_creation(self):
        spec = importlib.util.spec_from_file_location('installer_fixture', Path(__file__).parent.parent / 'setup.py')
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        source = self.base / 'installation'
        scripts = source / 'service/.venv/Scripts'
        scripts.mkdir(parents=True)
        (scripts / 'python.exe').write_bytes(b'not executed')
        (scripts.parent / 'pyvenv.cfg').write_text('include-system-site-packages = true\n')
        argv = ['setup.py', '--tunnel-id', 'tunnel_' + '0' * 32, '--projects', str(source / 'new-projects')]
        with patch.object(installer, 'BASE', source), patch('sys.argv', argv), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                installer.main()
        self.assertFalse((source / 'new-projects').exists())
        self.assertFalse((source / 'service/config.json').exists())

    def test_malformed_grant_and_unknown_policy_fail_closed(self):
        for value in ['invalid', '{}', '[{}]']:
            (self.files.runtime / 'local-approval.json').write_text(value)
            with self.assertRaises(PermissionError):
                self.files.write('Projects', 'allowed/a.txt', 'no')
        with self.assertRaises(ValueError):
            Files(dict(self.config, approval_mode='typo'), self.files.runtime)

    def test_approved_scope_never_bypasses_readonly_or_traversal(self):
        grant(self.files, 'Projects', '', 1)
        with self.assertRaises(PermissionError):
            self.files.write('Projects', '../outside.txt', 'no')
        with self.assertRaises(PermissionError):
            self.files.delete('Projects', '', True)
        self.files.config['read_only'] = True
        with self.assertRaises(PermissionError):
            self.files.write('Projects', 'allowed/a.txt', 'no')
        for duration in [0, 61]:
            with self.assertRaises(ValueError):
                grant(self.files, 'Projects', '', duration)

    def test_legacy_client_mode_preserves_established_workflows(self):
        self.files.config.pop('approval_mode')
        self.files.write('Projects', 'allowed/a.txt', 'yes')
        self.assertEqual((self.root / 'allowed/a.txt').read_text(), 'yes')

    def test_local_proposal_review_still_explicitly_applies_without_scope(self):
        plan = self.files.stage('write', 'Projects', 'allowed/review.md', 'reviewed')
        self.files.apply(plan['request_id'])
        self.assertEqual((self.root / 'allowed/review.md').read_text(), 'reviewed')

    def test_revoked_memory_transaction_is_recoverable_after_scope_renewal(self):
        from project_memory import ProjectBrain
        self.files.config['second_brain'] = dict(root='Projects', path='Archives')
        brain = ProjectBrain(self.files, 'Projects', 'Archives')
        grant(self.files, 'Projects', 'Archives', 1)
        plan = brain.plan_migrate('Synthetic')
        original_write = self.files.write

        def interrupted(*args, **kwargs):
            result = original_write(*args, **kwargs)
            revoke(self.files)
            return result
        with patch.object(self.files, 'write', interrupted), self.assertRaises(PermissionError):
            brain.commit(plan['plan_id'], plan['plan_sha256'])
        self.assertTrue(brain.pending())
        grant(self.files, 'Projects', 'Archives', 1)
        brain.recover()
        self.assertFalse(brain.pending())
        self.assertFalse((self.root / 'Archives/LAYOUT.md').exists())

    def diagnostic_fixture(self):
        service = self.base / 'service'
        service.mkdir()
        for node in Path(__file__).parent.glob('*.py'):
            if not node.name.startswith('test_'):
                shutil.copy2(node, service / node.name)
        shutil.copy2(Path(__file__).parent / 'requirements.lock.txt', service / 'requirements.lock.txt')
        (service / 'config.json').write_text(json.dumps(self.config))
        return service

    def snapshot(self, base):
        return {p.relative_to(base).as_posix(): (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
                for p in base.rglob('*') if p.is_file()}

    def test_diagnostics_absent_runtime_is_readonly_and_inventory_matches_modes(self):
        service = self.diagnostic_fixture()
        before = self.snapshot(service)
        result = status(service)
        self.assertTrue(result['configuration']['valid'])
        self.assertEqual(result['tools']['count'], 33)
        self.assertEqual(result['connection']['reported_state'], 'unknown')
        self.assertEqual(self.snapshot(service), before)
        self.assertFalse((service / '.runtime').exists())
        self.config['second_brain'] = dict(root='Projects', path='Archives')
        (service / 'config.json').write_text(json.dumps(self.config))
        self.assertEqual(status(service)['tools']['count'], 46)

    def test_diagnostic_cli_does_not_create_bytecode_or_runtime(self):
        service = self.diagnostic_fixture()
        before = self.snapshot(service)
        result = json.loads(subprocess.check_output([sys.executable, str(service / 'diagnostics.py')], text=True))
        self.assertEqual(result['tools']['count'], 33)
        self.assertEqual(before, self.snapshot(service))
        self.assertFalse((service / '__pycache__').exists())

    def test_diagnostics_redacts_logs_and_configuration_values(self):
        service = self.diagnostic_fixture()
        runtime = service / '.runtime'
        runtime.mkdir()
        (runtime / 'tray-status.json').write_text(json.dumps(dict(state='error', busy=False, message='PRIVATE_SENTINEL')))
        (runtime / 'tray-connection.log').write_text('PRIVATE_SENTINEL')
        before = self.snapshot(service)
        result = status(service)
        self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))
        self.assertNotIn(str(self.root), json.dumps(result))
        self.assertEqual(result['connection']['reported_state'], 'error')
        self.assertEqual(self.snapshot(service), before)

    def test_diagnostics_shared_identity_fallback_and_packaged_hash_tampering(self):
        service = self.diagnostic_fixture()
        profiles = service / '.runtime/profiles'
        profiles.mkdir(parents=True)
        (profiles / 'celious.yaml').write_text('control_plane:\n  tunnel_id: tunnel_' + '0' * 32 + '\n')
        self.assertTrue(status(service)['connection_configuration']['identity_valid'])
        hashes = {'service/server.py': hashlib.sha256((service / 'server.py').read_bytes()).hexdigest()}
        manifest = dict(commit='synthetic', files=hashes, source_digest=hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest())
        (service.parent / 'BUILD-IDENTITY.json').write_text(json.dumps(manifest))
        self.assertTrue(status(service)['build']['build_matches'])
        (service / 'server.py').write_text((service / 'server.py').read_text() + '\n# Changed bytes\n')
        before = self.snapshot(service)
        self.assertFalse(status(service)['build']['build_matches'])
        self.assertEqual(before, self.snapshot(service))

    def test_malformed_configuration_reports_failure_without_creating_state(self):
        service = self.diagnostic_fixture()
        for value in ['[]', '{}', 'invalid']:
            (service / 'config.json').write_text(value)
            before = self.snapshot(service)
            self.assertFalse(status(service)['configuration']['valid'])
            self.assertEqual(self.snapshot(service), before)

    def test_real_mcp_refuses_then_accepts_only_locally_approved_scope(self):
        from mcp import Client
        from mcp.client.stdio import StdioServerParameters
        service = self.diagnostic_fixture()

        async def exercise():
            async with Client(StdioServerParameters(command=sys.executable, args=[str(service / 'server.py')])) as client:
                self.assertEqual(len((await client.list_tools()).tools), 33)
                args = dict(root='Projects', path='allowed/mcp.txt', content='approved')
                self.assertTrue((await client.call_tool('write_file', args)).is_error)
                self.assertFalse((self.root / 'allowed/mcp.txt').exists())
                local = Files(self.config, service / '.runtime')
                grant(local, 'Projects', 'allowed', 1)
                self.assertFalse((await client.call_tool('write_file', args)).is_error)
                outside = dict(root='Projects', path='outside.txt', content='no')
                self.assertTrue((await client.call_tool('write_file', outside)).is_error)
                revoke(local)
                self.assertTrue((await client.call_tool('delete_file', dict(root='Projects', path='allowed/mcp.txt'))).is_error)
                self.assertEqual((self.root / 'allowed/mcp.txt').read_text(), 'approved')
        asyncio.run(exercise())


if __name__ == '__main__':
    unittest.main(verbosity=2)
