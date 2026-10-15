"""Behavioral acceptance for incremental ingestion, workflow recovery and isolation."""
import hashlib
import json
import multiprocessing
from pathlib import Path
import tempfile
import unittest
import zipfile
from engine import Files
from operations_state import sha
from workspace_tools import Workspace


def competing_run(config, runtime, plan, queue):
    files = Files(config, runtime)
    queue.put(Workspace(files).workflows.run(plan['id'], plan['plan_sha256'])['status'])


class IntegratedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='celious-integrated-')
        self.base = Path(self.temp.name)
        (self.base/'projects').mkdir()
        (self.base/'readonly').mkdir()
        self.config = dict(direct_operations=True, roots=dict(Projects=dict(path=str(self.base/'projects'), writable=True),
                           Reference=dict(path=str(self.base/'readonly'), writable=False)), second_brain=dict(root='Projects', path='Archives'))
        self.files = Files(self.config, self.base/'runtime')
        self.workspace = Workspace(self.files)
        self.brain = self.workspace.brain
        plan = self.brain.plan_migrate()
        self.brain.commit(plan['plan_id'], plan['plan_sha256'])
        self.project = self.brain.project()['id']
        plan = self.brain.plan_project('Separate')
        self.brain.commit(plan['plan_id'], plan['plan_sha256'])
        self.other = plan['project_id']
        self.flow = self.workspace.workflows

    def tearDown(self):
        self.temp.cleanup()

    def file(self, name, content):
        (self.base/'projects'/name).write_text(content, 'utf-8')

    def step(self, ident, op, needs=None, **args):
        return dict(id=ident, op=op, args=dict(root='Projects', **args), needs=needs or [])

    def make(self, steps):
        return self.flow.create('Synthetic integrated task', steps, self.project)

    def run_flow(self, plan):
        return self.flow.run(plan['id'], plan['plan_sha256'])

    def export(self, messages):
        self.file('export.json', json.dumps([dict(id='conversation-a', title='Supplied source', messages=messages)]))

    def ingest(self, stream='source-a', project=None, claims=None):
        return self.workspace.ingestion.preview('Projects', 'export.json', stream, project or self.project, 'conversation-a', claims)

    def test_incremental_export_preserves_roles_and_exact_claims(self):
        messages = [dict(id='m1', role='user', content='We decided to retain source evidence.')]
        self.export(messages)
        claim = dict(type='decision', title='Evidence retention', topic='Audit', key='retention', value='retain source evidence',
                     evidence='We decided to retain source evidence.', epistemic='accepted', uncertainty='Supplied synthetic transcript')
        first = self.ingest(claims=[claim])
        self.assertEqual(first['new_messages'], 1)
        self.assertIn('user:', first['text'])
        committed = self.workspace.ingestion.commit(first['id'], first['memory_plan']['plan_sha256'])
        self.assertEqual(self.workspace.ingestion.commit(first['id'], first['memory_plan']['plan_sha256']), committed)
        self.assertEqual(self.ingest()['status'], 'unchanged')
        messages.append(dict(id='m2', role='assistant', content='Maybe use another format.'))
        self.export(messages)
        second = self.ingest()
        self.assertEqual((second['new_messages'], second['skipped_messages']), (1, 1))
        self.assertNotIn('We decided', second['text'])
        self.assertTrue(all(c['epistemic'] == 'pending' for c in second['candidates']))
        self.workspace.ingestion.commit(second['id'], second['memory_plan']['plan_sha256'])
        self.assertTrue(self.brain.search('retain source evidence', project_id=self.project)['hits'])
        self.assertEqual(self.brain.search('retain source evidence', project_id=self.other)['hits'], [])
        self.assertEqual(self.brain.inspect()['issues'], [])

    def test_import_stream_cannot_cross_projects_or_silently_change_history(self):
        messages = [dict(id='m1', role='user', content='Original')]
        self.export(messages)
        plan = self.ingest()
        self.workspace.ingestion.commit(plan['id'], plan['memory_plan']['plan_sha256'])
        with self.assertRaises(ValueError): self.ingest(project=self.other)
        messages[0]['content'] = 'Edited'
        self.export(messages)
        with self.assertRaises(ValueError): self.ingest()
        self.assertEqual(self.ingest(stream='explicit-revision-2')['new_messages'], 1)

    def test_import_refuses_changed_source_wrong_digest_and_stale_memory(self):
        self.export([dict(id='m1', role='user', content='We must preserve history.')])
        plan = self.ingest()
        with self.assertRaises(ValueError): self.workspace.ingestion.commit(plan['id'], 'wrong')
        self.export([dict(id='m1', role='user', content='Changed')])
        with self.assertRaises(ValueError): self.workspace.ingestion.commit(plan['id'], plan['memory_plan']['plan_sha256'])
        plan = self.ingest()
        other = self.brain.plan_project('New collection')
        self.brain.commit(other['plan_id'], other['plan_sha256'])
        with self.assertRaises(ValueError): self.workspace.ingestion.commit(plan['id'], plan['memory_plan']['plan_sha256'])

    def test_active_export_branch_only_and_missing_conversation_refused(self):
        mapping = dict(root=dict(parent=None, message=None), selected=dict(parent='root', message=dict(id='m1', author=dict(role='user'), content=dict(parts=['Selected']))),
                       sibling=dict(parent='root', message=dict(id='m2', role='user', content='Unrelated branch')))
        self.file('export.json', json.dumps([dict(id='conversation-a', current_node='selected', mapping=mapping), dict(id='other', messages=[])]))
        plan = self.ingest()
        self.assertIn('Selected', plan['text'])
        self.assertNotIn('Unrelated branch', plan['text'])
        with self.assertRaises(ValueError): self.workspace.ingestion.preview('Projects', 'export.json', 'a', self.project)
        mapping['root']['parent'] = 'selected'
        self.file('export.json', json.dumps([dict(id='conversation-a', current_node='selected', mapping=mapping)]))
        with self.assertRaises(ValueError): self.ingest()

    def test_incremental_handover_append(self):
        self.file('handover.md', 'User: Requirement: keep evidence.\n')
        first = self.workspace.ingestion.preview('Projects', 'handover.md', 'handover', self.project)
        self.workspace.ingestion.commit(first['id'], first['memory_plan']['plan_sha256'])
        self.file('handover.md', 'User: Requirement: keep evidence.\nUser: Prefer plain text.\n')
        second = self.workspace.ingestion.preview('Projects', 'handover.md', 'handover', self.project)
        self.assertEqual((second['new_messages'], second['skipped_messages']), (1, 1))
        self.assertIn('Prefer plain text', second['text'])

    def test_context_requires_selection_and_path_binding_is_unambiguous(self):
        self.assertEqual(self.workspace.context()['status'], 'selection_required')
        self.config['project_bindings'] = [dict(root='Projects', path='Work', project_id=self.project)]
        result = self.workspace.context(root='Projects', path='Work/file.txt', query='')
        self.assertEqual(result['project_id'], self.project)
        self.assertFalse(result['automatic_invocation'])
        self.config['project_bindings'].append(dict(root='Projects', path='Work', project_id=self.other))
        with self.assertRaises(ValueError): self.workspace.context(root='Projects', path='Work/file.txt')
        self.assertEqual(self.workspace.context(project_id=self.other)['project_id'], self.other)

    def test_health_reports_client_tools_as_handoff_not_remote_execution(self):
        status = self.workspace.health()
        self.assertEqual(status['memory']['status'], 'ready')
        self.assertEqual(status['adapters'][-1]['status'], 'handoff_only')
        self.assertNotIn('credential', json.dumps(status['dependencies']))

    def test_multi_file_write_edit_move_idempotence_and_reverse_recovery(self):
        steps = [self.step('folder', 'mkdir', relative='Output'),
                 self.step('write', 'write', ['folder'], relative='Output/note.md', content='Original'),
                 self.step('edit', 'edit', ['write'], relative='Output/note.md', old_text='Original', new_text='Reviewed', expected_sha256={'$step': 'write', 'field': 'sha256'}),
                 self.step('move', 'move', ['edit'], relative='Output/note.md', destination='Output/final.md'),
                 self.step('second', 'write', ['move'], relative='Output/second.txt', content='Second')]
        plan = self.make(steps)
        result = self.run_flow(plan)
        self.assertEqual(result['status'], 'completed', result)
        self.assertEqual((self.base/'projects/Output/final.md').read_text(), 'Reviewed')
        self.assertEqual(self.run_flow(plan)['status'], 'completed')
        self.assertEqual(self.flow.rollback(plan['id'], plan['plan_sha256'])['status'], 'rolled_back')
        self.assertFalse((self.base/'projects/Output').exists())
        with self.assertRaises(ValueError): self.run_flow(plan)

    def test_recoverable_delete_and_rollback(self):
        self.file('existing.txt', 'Keep bytes')
        plan = self.make([self.step('delete', 'delete', relative='existing.txt')])
        self.assertEqual(self.run_flow(plan)['status'], 'completed')
        self.assertFalse((self.base/'projects/existing.txt').exists())
        self.flow.rollback(plan['id'], plan['plan_sha256'])
        self.assertEqual((self.base/'projects/existing.txt').read_text(), 'Keep bytes')

    def test_review_digest_stale_input_and_competing_plans_preserve_work(self):
        plan = self.make([self.step('save', 'write', relative='new.txt', content='One')])
        second = self.make([self.step('save', 'write', relative='new.txt', content='Two')])
        with self.assertRaises(ValueError): self.flow.run(plan['id'], 'wrong')
        self.assertEqual(self.run_flow(plan)['status'], 'completed')
        self.assertEqual(self.run_flow(second)['status'], 'blocked')
        self.assertEqual((self.base/'projects/new.txt').read_text(), 'One')
        self.file('new.txt', 'Newer work')
        self.assertEqual(self.run_flow(plan)['status'], 'conflict')
        with self.assertRaises(ValueError): self.flow.rollback(plan['id'], plan['plan_sha256'])
        self.assertEqual((self.base/'projects/new.txt').read_text(), 'Newer work')

    def test_interrupted_delete_repairs_prepared_recovery_receipt(self):
        self.file('existing.txt', 'Keep bytes')
        plan = self.make([self.step('delete', 'delete', relative='existing.txt')])
        self.flow._interrupt_after_effect = True
        with self.assertRaises(SystemExit): self.run_flow(plan)
        record = next((self.base/'runtime/trash').glob('*/record.json'))
        meta = json.loads(record.read_text()); meta['status'] = 'prepared'
        record.write_text(json.dumps(meta))
        resumed = Workspace(self.files).workflows
        self.assertEqual(resumed.run(plan['id'], plan['plan_sha256'])['status'], 'completed')
        resumed.rollback(plan['id'], plan['plan_sha256'])
        self.assertEqual((self.base/'projects/existing.txt').read_text(), 'Keep bytes')

    def test_two_processes_run_one_workflow_without_duplicate_writes(self):
        self.file('existing.txt', 'Before')
        plan = self.make([self.step('save', 'write', relative='existing.txt', content='After')])
        before = set((self.base/'runtime/backups').glob('*'))
        context = multiprocessing.get_context('spawn')
        queue = context.Queue()
        processes = [context.Process(target=competing_run, args=(self.config, self.base/'runtime', plan, queue)) for _ in range(2)]
        for process in processes: process.start()
        for process in processes:
            process.join(30)
            self.assertEqual(process.exitcode, 0)
        self.assertEqual([queue.get(timeout=5) for _ in processes], ['completed', 'completed'])
        self.assertEqual(len(set((self.base/'runtime/backups').glob('*')) - before), 1)
        self.assertEqual((self.base/'projects/existing.txt').read_text(), 'After')
        queue.close()

    def test_interrupted_reverse_write_resumes_from_verified_prestate(self):
        self.file('existing.txt', 'Before')
        plan = self.make([self.step('save', 'write', relative='existing.txt', content='After')])
        self.assertEqual(self.run_flow(plan)['status'], 'completed')
        original_write = self.files.write
        def interrupted_write(*args, **kwargs):
            original_write(*args, **kwargs)
            raise SystemExit('Synthetic rollback interruption')
        self.files.write = interrupted_write
        with self.assertRaises(SystemExit): self.flow.rollback(plan['id'], plan['plan_sha256'])
        resumed = Workspace(Files(self.config, self.base/'runtime')).workflows
        self.assertEqual(resumed.rollback(plan['id'], plan['plan_sha256'])['status'], 'rolled_back')
        self.assertEqual((self.base/'projects/existing.txt').read_text(), 'Before')

    def test_memory_commit_receipt_recovered_after_ingestion_process_interruption(self):
        self.export([dict(id='m1', role='user', content='We must retain sources.')])
        plan = self.ingest()
        self.brain.commit(plan['memory_plan']['plan_id'], plan['memory_plan']['plan_sha256'])
        resumed = Workspace(self.files).ingestion
        self.assertTrue(resumed.commit(plan['id'], plan['memory_plan']['plan_sha256'])['recovered_receipt'])
        self.assertEqual(self.ingest()['status'], 'unchanged')

    def test_mid_write_interruption_reconciles_without_duplicate_effect(self):
        backups_before = set((self.base/'runtime/backups').glob('*'))
        plan = self.make([self.step('save', 'write', relative='new.txt', content='Once')])
        self.flow._interrupt_after_effect = True
        with self.assertRaises(SystemExit): self.run_flow(plan)
        resumed = Workspace(self.files).workflows
        self.assertEqual(resumed.run(plan['id'], plan['plan_sha256'])['status'], 'completed')
        self.assertEqual((self.base/'projects/new.txt').read_text(), 'Once')
        self.assertEqual(set((self.base/'runtime/backups').glob('*')), backups_before)
        resumed.rollback(plan['id'], plan['plan_sha256'])
        self.assertFalse((self.base/'projects/new.txt').exists())

    def test_interrupted_binary_output_requires_reviewed_reconciliation(self):
        plan = self.make([self.step('sheet', 'spreadsheet_write', destination='book.xlsx', workbook_json=json.dumps([dict(name='Data', rows=[['Value'], [7]])]))])
        self.flow._interrupt_after_effect = True
        with self.assertRaises(SystemExit): self.run_flow(plan)
        resumed = Workspace(self.files).workflows
        self.assertEqual(resumed.run(plan['id'], plan['plan_sha256'])['status'], 'blocked')
        digest = sha((self.base/'projects/book.xlsx').read_bytes())
        resumed.reconcile(plan['id'], 'sheet', plan['plan_sha256'], digest)
        self.assertEqual(resumed.run(plan['id'], plan['plan_sha256'])['status'], 'completed')
        resumed.rollback(plan['id'], plan['plan_sha256'])
        self.assertFalse((self.base/'projects/book.xlsx').exists())

    def test_handoff_requires_new_hashed_artifact_and_does_not_claim_semantic_success(self):
        spec = dict(id='research', op='handoff', args=dict(task='Use an authorized research tool and save reviewed evidence', artifact_root='Projects', artifact_path='research.md'), needs=[])
        plan = self.make([spec])
        waiting = self.run_flow(plan)
        self.assertEqual(waiting['status'], 'waiting')
        token = waiting['steps']['research']['token']
        with self.assertRaises(ValueError): self.flow.receipt(plan['id'], 'research', token, 'invented')
        self.file('research.md', 'Evidence from authorized client')
        digest = sha((self.base/'projects/research.md').read_bytes())
        self.flow.receipt(plan['id'], 'research', token, digest)
        self.assertEqual(self.run_flow(plan)['status'], 'completed')
        self.assertIn('artifact integrity only', self.flow.status(plan['id'])['steps']['research']['result']['verification'])
        with self.assertRaises(ValueError): self.flow.receipt(plan['id'], 'research', token, digest)

    def test_rollback_revokes_pending_handoff_receipt(self):
        spec = dict(id='review', op='handoff', args=dict(task='Review', artifact_root='Projects', artifact_path='review.md'))
        plan = self.make([spec])
        waiting = self.run_flow(plan)
        token = waiting['steps']['review']['token']
        self.flow.rollback(plan['id'], plan['plan_sha256'])
        self.file('review.md', 'Later external evidence')
        with self.assertRaises(ValueError):
            self.flow.receipt(plan['id'], 'review', token, sha((self.base/'projects/review.md').read_bytes()))
        self.assertEqual(self.flow.status(plan['id'])['status'], 'rolled_back')

    def test_dependency_output_and_paused_workflow_persist_across_instances(self):
        plan = self.make([self.step('first', 'write', relative='one.txt', content='Copied content'),
                          self.step('read', 'read', ['first'], path='one.txt'),
                          self.step('copy', 'write', ['read'], relative='two.txt', content={'$step': 'read', 'field': 'text'})])
        self.assertEqual(self.flow.run(plan['id'], plan['plan_sha256'], 1)['status'], 'paused')
        resumed = Workspace(self.files).workflows
        self.assertEqual(resumed.run(plan['id'], plan['plan_sha256'])['status'], 'completed')
        self.assertEqual((self.base/'projects/two.txt').read_text(), 'Copied content')
        self.assertEqual(resumed.listing(self.other)['total'], 0)
        self.assertEqual(resumed.listing(self.project)['total'], 1)

    def test_archive_checked_extraction_and_rollback(self):
        archive = self.base/'projects/input.zip'
        with zipfile.ZipFile(archive, 'w') as output:
            output.writestr('nested/document.txt', 'Safe synthetic archive')
        self.assertEqual(self.workspace.archive('Projects', 'input.zip')['expanded_bytes'], 22)
        plan = self.workspace.extract_preview('Projects', 'input.zip', 'Extracted', ['nested/document.txt'])
        self.assertEqual(self.run_flow(plan)['status'], 'completed')
        self.assertEqual((self.base/'projects/Extracted/nested/document.txt').read_text(), 'Safe synthetic archive')
        self.flow.rollback(plan['id'], plan['plan_sha256'])
        self.assertFalse((self.base/'projects/Extracted').exists())

    def test_archive_traversal_links_bombs_and_existing_targets_refused(self):
        archive = self.base/'projects/input.zip'
        for name in ['../escape.txt', '/absolute.txt', 'hidden/.token']:
            with zipfile.ZipFile(archive, 'w') as output: output.writestr(name, 'blocked')
            with self.assertRaises((ValueError, PermissionError)): self.workspace.archive('Projects', 'input.zip')
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output: output.writestr('bomb.txt', 'x'*100000)
        with self.assertRaises(ValueError): self.workspace.archive('Projects', 'input.zip')
        with zipfile.ZipFile(archive, 'w') as output:
            info = zipfile.ZipInfo('link'); info.external_attr = 0o120777 << 16
            output.writestr(info, 'target')
        with self.assertRaises(ValueError): self.workspace.archive('Projects', 'input.zip')

    def test_permissions_unknown_actions_dependencies_and_path_escape(self):
        with self.assertRaises(PermissionError): self.make([self.step('bad', 'write', relative='../escape', content='x')])
        with self.assertRaises(PermissionError): self.flow.create('Read only', [dict(id='bad', op='write', args=dict(root='Reference', relative='x', content='x'))])
        with self.assertRaises(ValueError): self.make([self.step('bad', 'shell', command='anything')])
        with self.assertRaises(ValueError): self.make([self.step('bad', 'write', ['future'], relative='x', content='x')])
        with self.assertRaises(ValueError): self.make([self.step('one', 'write', relative='x', content='x'), self.step('two', 'write', relative='x', content='y')])


if __name__ == '__main__':
    unittest.main()
