"""Durable bounded workflows over existing policy-aware services, with exact review."""
import base64
import inspect
import json
import re
import uuid
from datetime import datetime, timezone
from operations_state import State, canonical, sha
from spreadsheets import Spreadsheets, read as read_sheet


class Workflows:
    def __init__(self, files, brain=None):
        self.files, self.brain = files, brain
        self.state = State(files)
        sheets = Spreadsheets(files)
        self.handlers = dict(read=files.read, search=files.search, write=files.write, edit=files.edit,
                             mkdir=files.mkdir, move=files.move, delete=files.delete,
                             spreadsheet_inspect=sheets.inspect, spreadsheet_write=sheets.write,
                             spreadsheet_edit=sheets.edit, spreadsheet_convert=sheets.convert,
                             spreadsheet_read=lambda root, path, worksheet=None: read_sheet(sheets.load(root, path), worksheet))
        self.mutations = {'write', 'edit', 'mkdir', 'move', 'delete', 'spreadsheet_write', 'spreadsheet_edit', 'spreadsheet_convert'}
        self._interrupt_after_effect = False  # Private fault injection, never exposed as a tool.

    def event(self, job, action, step=None):
        job['events'].append(dict(time=datetime.now(timezone.utc).isoformat(), action=action, step=step))
        self.state.save(job)

    def location(self, op, args):
        field = 'destination' if op in {'spreadsheet_write', 'spreadsheet_edit', 'spreadsheet_convert'} else ('relative' if op in {'write', 'edit', 'mkdir', 'move', 'delete'} else 'path')
        return args['root'], args[field]

    def stamp(self, root, path, data=False):
        node = self.files.path(root, path)
        if not node.exists():
            return dict(kind='absent')
        if node.is_dir():
            return dict(kind='directory')
        if not node.is_file() or node.stat().st_size > 10 * 1024 * 1024:
            raise ValueError('Workflow files must be regular files below 10 MB')
        value = node.read_bytes()
        return dict(kind='file', sha256=sha(value), **({'base64': base64.b64encode(value).decode()} if data else {}))

    def clean_stamp(self, value):
        return {key: val for key, val in value.items() if key != 'base64'}

    def paths(self, op, args):
        if op in {'handoff', 'memory_search'}:
            return []
        return [(args['root'], value) for key, value in args.items() if key in {'relative', 'path', 'destination'}]

    def changed_paths(self, op, args):
        if op not in self.mutations:
            return []
        targets = [self.location(op, args)]
        if op == 'move':
            targets.append((args['root'], args['destination']))
        return targets

    def path_key(self, root, path):
        return root + '/' + path.replace('\\', '/').strip('/').casefold()

    def create(self, title, steps, project_id=None):
        if not isinstance(title, str) or not 1 <= len(title) <= 200 or not isinstance(steps, list) or not 1 <= len(steps) <= 50:
            raise ValueError('Provide a title and 1–50 bounded steps')
        if len(canonical(steps)) > 1000000:
            raise ValueError('Workflow specification exceeds 1 MB')
        if re.search(r'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}', canonical(steps).decode()):
            raise ValueError('Do not put credentials into workflow specifications')
        if project_id:
            if not self.brain:
                raise ValueError('Project memory is unavailable')
            with self.brain.locked():
                self.brain.healthy()
                self.brain.project(project_id)
                context = self.brain.search(title[:500], project_id=project_id)
        else:
            context = None
        known, normalized, writers = set(), [], {}
        for spec in steps:
            if not isinstance(spec, dict) or not set(spec) <= {'id', 'op', 'args', 'needs'}:
                raise ValueError('Each step must contain only id, op, args and optional needs')
            ident, op, args = spec.get('id'), spec.get('op'), spec.get('args', {})
            needs = spec.get('needs', [])
            if not isinstance(ident, str) or not re.fullmatch('[a-zA-Z][a-zA-Z0-9_-]{0,39}', ident) or ident in known:
                raise ValueError('Use unique simple step IDs')
            if not isinstance(needs, list) or any(not isinstance(n, str) for n in needs) or not set(needs) <= known or not isinstance(args, dict) or not isinstance(op, str):
                raise ValueError('Dependencies must reference earlier steps')
            if op == 'handoff':
                if set(args) != {'task', 'artifact_root', 'artifact_path'} or not isinstance(args['task'], str) or not args['task'].strip():
                    raise ValueError('Handoff needs task, artifact_root and artifact_path; no arbitrary server-side execution')
                self.files.path(args['artifact_root'], args['artifact_path'])
            elif op == 'memory_search':
                if not project_id or not set(args) <= {'query', 'include_shared'} or 'query' not in args:
                    raise ValueError('Memory workflow search requires explicit project and query')
            elif op in self.handlers:
                try:
                    inspect.signature(self.handlers[op]).bind(**args)
                except TypeError:
                    raise ValueError('Operation arguments do not match the documented adapter signature') from None
                for key, value in args.items():
                    if key in {'root', 'relative', 'path', 'destination', 'content', 'encoding', 'old_text', 'new_text', 'workbook_json', 'operations_json', 'query'}:
                        if not isinstance(value, str) and not (isinstance(value, dict) and '$step' in value and key in {'content', 'old_text', 'new_text'}):
                            raise ValueError('Text, root and path arguments must be strings or supported dependency references')
                # File safety paths must be literal, never inferred from tool output.
                for key in ('relative', 'path', 'destination'):
                    if key in args:
                        if not isinstance(args[key], str):
                            raise ValueError('Paths must be explicit strings')
                        self.files.path(args['root'], args[key], write=op in self.mutations)
                if op == 'delete' and args.get('recursive'):
                    raise ValueError('Workflow deletion is limited to files; review folder deletion separately')
                if op in self.mutations:
                    root, path = self.location(op, args)
                    self.files.mutation_path(root, path)
                    if op != 'mkdir' and self.stamp(root, path)['kind'] == 'directory':
                        raise ValueError('Workflow mutations except mkdir are file-only')
            else:
                raise ValueError('Unknown workflow operation')
            for value in args.values():
                if isinstance(value, dict) and '$step' in value:
                    if set(value) != {'$step', 'field'} or value['$step'] not in needs or value['field'] not in {'sha256', 'text'}:
                        raise ValueError('Output references require a declared dependency and sha256/text field')
            guards = []
            for root, path in self.paths(op, args):
                previous = writers.get(self.path_key(root, path))
                if previous and previous not in needs:
                    raise ValueError('A later use of a changed path must depend on its earlier writer')
                guards.append(dict(root=root, path=path, writer=previous, expected=None if previous else self.stamp(root, path)))
            normalized.append(dict(id=ident, op=op, args=args, needs=needs, guards=guards))
            for root, path in self.changed_paths(op, args):
                writers[self.path_key(root, path)] = ident
            known.add(ident)
        plan = dict(title=title, project_id=project_id, steps=normalized)
        job = dict(id='workflow-' + uuid.uuid4().hex, schema_version=1, plan=plan, digest=sha(canonical(plan)), status='review',
                   steps={step['id']: dict(status='pending') for step in normalized}, events=[])
        with self.state.locked():
            self.event(job, 'created')
        return dict(id=job['id'], plan_sha256=job['digest'], plan=plan, status='review', context=context,
                    approval='Review all mutations and external actions; pass the exact digest to run. Handoffs require their own tool permissions.')

    def view(self, job):
        return dict(id=job['id'], title=job['plan']['title'], project_id=job['plan']['project_id'], status=job['status'],
                    plan_sha256=job['digest'], steps={key: {k: v for k, v in value.items() if k not in {'before', 'args', 'trash_before'}} for key, value in job['steps'].items()},
                    events=job['events'][-100:])

    def status(self, ident):
        with self.state.locked():
            return self.view(self.state.load(ident))

    def listing(self, project_id=None, offset=0, limit=20):
        with self.state.locked():
            jobs = []
            for path in sorted(self.state.path.glob('workflow-*.json')):
                job = self.state.load(path.stem)
                if job['plan']['project_id'] == project_id:
                    jobs.append(dict(id=job['id'], title=job['plan']['title'], status=job['status']))
            offset, limit = max(0, offset), max(1, min(50, limit))
            return dict(workflows=jobs[offset:offset+limit], total=len(jobs), next_offset=offset+limit if offset+limit < len(jobs) else None)

    def resolve(self, args, job):
        result = dict(args)
        for key, value in args.items():
            if isinstance(value, dict) and '$step' in value:
                parent = job['steps'][value['$step']]
                if parent['status'] != 'done' or value['field'] not in parent['result']:
                    raise ValueError('Dependency output is unavailable')
                result[key] = parent['result'][value['field']]
        return result

    def post(self, spec, item):
        op, args = spec['op'], item['args']
        if op not in self.mutations:
            if op == 'handoff' and 'artifact' in item:
                return self.stamp(args['artifact_root'], args['artifact_path']) == item['artifact']
            return True
        root, path = self.location(op, args)
        current = self.stamp(root, path)
        if op == 'move':
            return current['kind'] == 'absent' and self.stamp(root, args['destination']) == self.clean_stamp(item['before'])
        if op == 'delete':
            return current['kind'] == 'absent' and bool(item.get('deletion_id'))
        if op == 'mkdir':
            return current['kind'] == 'directory'
        return current.get('sha256') == item.get('after_sha256') and item.get('after_sha256') is not None

    def prepare(self, spec, item, args):
        op = spec['op']
        item['args'] = args
        if op not in self.mutations:
            return
        root, path = self.location(op, args)
        item['before'] = self.stamp(root, path, True)
        if op == 'mkdir':
            # One reversible directory per step. Parents must already exist.
            node = self.files.mutation_path(root, path)
            if not node.parent.is_dir():
                raise ValueError('Create missing parent directories in separate steps')
        if op in {'move', 'delete', 'edit'} and item['before']['kind'] != 'file':
            raise ValueError('This step requires an existing regular file')
        if op == 'move':
            if self.stamp(root, args['destination'])['kind'] != 'absent':
                raise ValueError('Move destination already exists')
            self.files.mutation_path(root, args['destination'])
        if op == 'delete':
            item['trash_before'] = [p.name for p in (self.files.runtime/'trash').glob('*')]
        if op == 'write':
            data = args['content'].encode() if args.get('encoding', 'utf-8') == 'utf-8' else base64.b64decode(args['content'], validate=True)
            item['after_sha256'] = sha(data)
            args['expected_sha256'] = args.get('expected_sha256', item['before'].get('sha256', ''))
        if op == 'edit':
            text = base64.b64decode(item['before']['base64']).decode('utf-8')
            if not args['old_text'] or text.count(args['old_text']) != 1:
                raise ValueError('Edit requires exactly one occurrence')
            item['after_sha256'] = sha(text.replace(args['old_text'], args['new_text'], 1).encode())
            args['expected_sha256'] = args.get('expected_sha256', item['before']['sha256'])
        if op.startswith('spreadsheet_'):
            # Unknown binary output after a crash is never assumed safe to replay.
            if op != 'spreadsheet_convert':
                args.setdefault('expected_sha256', item['before'].get('sha256', ''))

    def recover_running(self, spec, item):
        op, args = spec['op'], item['args']
        if op == 'delete' and self.stamp(args['root'], args['relative'])['kind'] == 'absent':
            matches = []
            for folder in (self.files.runtime/'trash').glob('*'):
                if folder.name in item['trash_before']:
                    continue
                record = folder/'record.json'
                self.files._no_links(record)
                if record.is_file():
                    meta = json.loads(record.read_text('utf-8'))
                    payload = folder/'payload'
                    self.files._no_links(payload)
                    if meta.get('root') == args['root'] and meta.get('path') == args['relative'] and payload.is_file() and sha(payload.read_bytes()) == item['before']['sha256']:
                        if meta.get('status') == 'prepared':
                            meta['status'] = 'deleted'
                            self.state.replace(record, meta)
                        matches.append(folder.name)
            if len(matches) == 1:
                item['deletion_id'] = matches[0]
        if self.post(spec, item) and (op in self.mutations):
            item.update(status='done', result=dict(status='verified_after_interruption', **({'sha256': item['after_sha256']} if item.get('after_sha256') else {})))
            return
        if op not in self.mutations:
            item['status'] = 'pending'
        elif self.stamp(*self.location(op, args)) == self.clean_stamp(item['before']):
            item['status'] = 'pending'
        else:
            raise ValueError('Interrupted mutation has uncertain output; inspect checkpoint and reconcile explicitly, never replay blindly')

    def run(self, ident, approved_sha256, max_steps=50):
        with self.state.locked():
            job = self.state.load(ident)
            if approved_sha256 != job['digest'] or sha(canonical(job['plan'])) != job['digest']:
                raise ValueError('Approve the exact immutable workflow plan')
            if job['status'] in {'rolled_back', 'rolling_back'}:
                raise ValueError('Rolled-back workflows cannot be replayed')
            # Completed outputs are reverified before further work; changed artifacts block resume.
            for spec in job['plan']['steps']:
                item = job['steps'][spec['id']]
                # Earlier outputs deliberately changed by later steps are checked at the latest writer only.
                later = job['plan']['steps'][job['plan']['steps'].index(spec)+1:]
                changed = False
                if item['status'] == 'done' and spec['op'] in self.mutations:
                    for root, path in self.changed_paths(spec['op'], item['args']):
                        key = self.path_key(root, path)
                        overwritten = any(job['steps'][s['id']]['status'] == 'done' and key in {self.path_key(r, p) for r, p in self.changed_paths(s['op'], s['args'])} for s in later)
                        if not overwritten and self.stamp(root, path) != item.get('post_stamps', {}).get(key):
                            changed = True
                elif item['status'] == 'done' and not self.post(spec, item):
                    changed = True
                if changed:
                    job['status'] = 'conflict'
                    self.event(job, 'output_changed', spec['id'])
                    return self.view(job)
            executed = 0
            for spec in job['plan']['steps']:
                item = job['steps'][spec['id']]
                if item['status'] in {'done', 'undone'}:
                    continue
                if executed >= max(1, min(50, max_steps)):
                    break
                try:
                    if item['status'] == 'running':
                        self.recover_running(spec, item)
                        self.event(job, 'reconciled', spec['id'])
                        if item['status'] == 'done':
                            item['post_stamps'] = {self.path_key(root, path): self.stamp(root, path) for root, path in self.changed_paths(spec['op'], item['args'])}
                            self.state.save(job)
                            continue
                    if any(job['steps'][dep]['status'] != 'done' for dep in spec['needs']):
                        break
                    args = self.resolve(spec['args'], job)
                    if spec['op'] == 'handoff':
                        if item['status'] != 'waiting':
                            item.update(status='waiting', args=args, token=uuid.uuid4().hex,
                                        artifact_before=self.stamp(args['artifact_root'], args['artifact_path']))
                        job['status'] = 'waiting'
                        self.event(job, 'awaiting_authorized_client_tool', spec['id'])
                        return self.view(job)
                    for guard in spec['guards']:
                        expected = job['steps'][guard['writer']].get('post_stamps', {}).get(self.path_key(guard['root'], guard['path'])) if guard['writer'] else guard['expected']
                        if self.stamp(guard['root'], guard['path']) != expected:
                            raise ValueError('Reviewed input/output changed; preserve current data and prepare a new plan')
                    self.prepare(spec, item, args)
                    if sum(len(s.get('before', {}).get('base64', '')) for s in job['steps'].values()) > 28 * 1024 * 1024:
                        raise ValueError('Workflow recovery checkpoint exceeds 20 MB; split the task')
                    item['status'] = 'running'
                    job['status'] = 'running'
                    self.event(job, 'begin', spec['id'])
                    if spec['op'] == 'memory_search':
                        result = self.brain.search(project_id=job['plan']['project_id'], **args)
                    else:
                        result = self.handlers[spec['op']](**args)
                    if self._interrupt_after_effect:
                        raise SystemExit('Injected interruption')
                    if spec['op'].startswith('spreadsheet_') and spec['op'] in self.mutations:
                        item['after_sha256'] = result['sha256']
                    if spec['op'] == 'delete':
                        item['deletion_id'] = result['deletion_id']
                    if not self.post(spec, item):
                        raise ValueError('Operation returned without satisfying its filesystem postcondition')
                    item.update(status='done', result=result)
                    item['post_stamps'] = {self.path_key(root, path): self.stamp(root, path) for root, path in self.changed_paths(spec['op'], args)}
                    item.pop('error', None)
                    executed += 1
                    self.event(job, 'verified', spec['id'])
                except (ValueError, PermissionError, OSError, KeyError, TypeError) as error:
                    # Keep a running intent after possible effects for safe reconciliation.
                    item['error'] = type(error).__name__ + ': ' + str(error)[:250]
                    job['status'] = 'blocked'
                    self.event(job, 'blocked', spec['id'])
                    return self.view(job)
            job['status'] = 'completed' if all(i['status'] == 'done' for i in job['steps'].values()) else 'paused'
            self.event(job, job['status'])
            return self.view(job)

    def receipt(self, ident, step_id, token, artifact_sha256):
        with self.state.locked():
            job = self.state.load(ident)
            item = job['steps'].get(step_id)
            if job['status'] != 'waiting' or not item or item['status'] != 'waiting' or item['token'] != token:
                raise ValueError('Only the current handoff token can be completed')
            args = item['args']
            actual = self.stamp(args['artifact_root'], args['artifact_path'])
            if actual['kind'] != 'file' or actual.get('sha256') != artifact_sha256 or actual == item['artifact_before']:
                raise ValueError('A new/changed artifact with the exact digest is required')
            item.update(status='done', artifact=actual, result=dict(sha256=artifact_sha256, verification='artifact integrity only; semantic/external success requires client review'))
            job['status'] = 'paused'
            self.event(job, 'handoff_artifact_verified', step_id)
            return self.view(job)

    def reconcile(self, ident, step_id, approved_sha256, output_sha256):
        """Owner-reviewed recovery of an uncertain binary result; never automatic success."""
        with self.state.locked():
            job = self.state.load(ident)
            spec = next((s for s in job['plan']['steps'] if s['id'] == step_id), None)
            item = job['steps'].get(step_id)
            if job['status'] in {'rolling_back', 'rolled_back'} or approved_sha256 != job['digest'] or not spec or not item or item['status'] != 'running' or spec['op'] not in {'spreadsheet_write', 'spreadsheet_edit', 'spreadsheet_convert'}:
                raise ValueError('Only a reviewed uncertain spreadsheet mutation can be reconciled')
            root, path = self.location(spec['op'], item['args'])
            actual = self.stamp(root, path)
            if actual.get('sha256') != output_sha256 or actual == self.clean_stamp(item['before']):
                raise ValueError('Review the new output bytes and supply their exact digest')
            Spreadsheets(self.files).inspect(root, path)
            item.update(status='done', after_sha256=output_sha256,
                        result=dict(sha256=output_sha256, verification='owner-reviewed binary result; parsed and hash-verified'),
                        post_stamps={self.path_key(root, path): actual})
            job['status'] = 'paused'
            self.event(job, 'owner_reconciled_binary_output', step_id)
            return self.view(job)

    def rollback(self, ident, approved_sha256):
        with self.state.locked():
            job = self.state.load(ident)
            if approved_sha256 != job['digest'] or sha(canonical(job['plan'])) != job['digest']:
                raise ValueError('Approve the exact workflow rollback')
            job['status'] = 'rolling_back'
            self.event(job, 'rollback_begin')
            for spec in reversed(job['plan']['steps']):
                item = job['steps'][spec['id']]
                if item['status'] == 'running':
                    self.recover_running(spec, item)
                if item['status'] not in {'done', 'undoing'} or spec['op'] not in self.mutations:
                    continue
                root, path = self.location(spec['op'], item['args'])
                before = self.clean_stamp(item['before'])
                # An interrupted rollback is considered complete only at its exact pre-state.
                if item['status'] == 'undoing' and self.stamp(root, path) == before:
                    item['status'] = 'undone'
                    self.event(job, 'rollback_reconciled', spec['id'])
                    continue
                if not self.post(spec, item):
                    raise ValueError('Output changed; rollback refuses to overwrite newer work')
                item['status'] = 'undoing'
                self.event(job, 'undo_begin', spec['id'])
                if spec['op'] == 'move':
                    self.files.move(root, item['args']['destination'], path)
                elif spec['op'] == 'delete':
                    self.files.restore(item['deletion_id'])
                elif before['kind'] == 'file':
                    self.files.write(root, path, item['before']['base64'], 'base64', item.get('after_sha256'))
                elif before['kind'] == 'absent':
                    node = self.files.mutation_path(root, path)
                    if node.is_dir():
                        if any(node.iterdir()):
                            raise ValueError('Created folder is not empty; preserve newer work')
                        node.rmdir()
                    else:
                        self.files.delete(root, path)
                if self.stamp(root, path) != before:
                    raise ValueError('Rollback verification failed')
                item['status'] = 'undone'
                self.event(job, 'undone', spec['id'])
            job['status'] = 'rolled_back'
            self.event(job, 'rolled_back')
            return self.view(job)
