"""Incremental import of supplied sources into the existing reviewed memory journal."""
import json
import uuid
from operations_state import State, sha


class Ingestion:
    def __init__(self, files, brain):
        self.files, self.brain = files, brain
        self.state = State(files)

    def messages(self, root, path, conversation_id):
        node = self.files.path(root, path)
        if not node.is_file() or node.stat().st_size > 10 * 1024 * 1024:
            raise ValueError('Supply a source file below 10 MB; split larger exports locally')
        fingerprint = sha(node.read_bytes())
        if node.suffix.lower() == '.json':
            data = json.loads(node.read_text('utf-8-sig'))
            choices = data if isinstance(data, list) else [data]
            selected = [c for c in choices if isinstance(c, dict) and str(c.get('id', c.get('conversation_id', ''))) == conversation_id]
            if len(selected) != 1:
                raise ValueError('Choose exactly one conversation_id from the export')
            chat = selected[0]
            if 'mapping' in chat:
                mapping = chat['mapping']
                current, seen, chain = chat.get('current_node'), set(), []
                if not current:
                    raise ValueError('Export must identify its active current_node; ambiguous branches are not imported')
                while current is not None:
                    if current in seen or current not in mapping or len(seen) >= 10000:
                        raise ValueError('Invalid, cyclic or oversized conversation chain')
                    seen.add(current)
                    item = mapping[current]
                    message = item.get('message')
                    if message:
                        chain.append(message)
                    current = item.get('parent')
                messages = list(reversed(chain))
            else:
                messages = chat.get('messages', [])
            rows = []
            for message in messages:
                role = message.get('author', {}).get('role', message.get('role', 'unknown'))
                content = message.get('content', '')
                parts = content.get('parts', []) if isinstance(content, dict) else [content]
                text = '\n'.join(p for p in parts if isinstance(p, str))
                if text.strip():
                    ident = message.get('id')
                    if not isinstance(ident, str) or not ident or role not in {'user', 'assistant', 'system', 'tool', 'developer'}:
                        raise ValueError('Every imported message needs a stable ID and recognized role')
                    rows.append((ident, role + ': ' + text))
            title = str(chat.get('title', 'Supplied conversation'))[:200]
            completeness = 'partial'  # Only text on the active branch; attachments are not inferred.
        else:
            offset, chunks = 0, []
            while True:
                result = self.files.read(root, path, offset, 20000)
                chunks.append(result['text'])
                offset = result.get('next_offset')
                if sum(len(t.encode()) for t in chunks) > 900000:
                    raise ValueError('Extracted text exceeds import limit; split source locally')
                if offset is None:
                    break
            rows = [(str(i), line) for i, line in enumerate(''.join(chunks).splitlines()) if line.strip()]
            title, completeness = node.name[:200], 'user_supplied'
        if not rows or len(rows) > 10000 or len({key for key, _ in rows}) != len(rows):
            raise ValueError('Source requires unique stable message/line IDs and at most 10000 messages')
        if sum(len(text.encode()) for _, text in rows) > 900000:
            raise ValueError('Selected conversation text exceeds 900 KB')
        if sha(node.read_bytes()) != fingerprint:
            raise ValueError('Source changed during extraction')
        return rows, title, completeness, fingerprint

    def preview(self, root, path, stream_id, project_id, conversation_id='', claims=None):
        if not isinstance(stream_id, str) or not 1 <= len(stream_id) <= 160:
            raise ValueError('Provide a stable stream_id for this source and revision')
        if not self.brain or not project_id:
            raise ValueError('Configured initialized memory and an explicit project_id are required')
        with self.state.locked(), self.brain.locked():
            self.brain.healthy()
            self.brain.project(project_id)
            rows, title, completeness, fingerprint = self.messages(root, path, conversation_id)
            stream = sha((stream_id + '\n' + conversation_id).encode())
            prior = {}
            for record in self.brain.records():
                ref = record['meta'].get('source_ref', '')
                if record['meta']['type'] != 'source' or not ref.startswith('ingest-v1:'):
                    continue
                meta = json.loads(ref[len('ingest-v1:'):])
                if meta['stream'] == stream:
                    if record['project_id'] != project_id:
                        raise ValueError('Stream already belongs to another project')
                    prior.update(meta['messages'])
            current = {ident: sha(text.encode()) for ident, text in rows}
            if any(current.get(key) != value for key, value in prior.items()):
                raise ValueError('Previously imported messages were edited/removed; use an explicit new revision stream after review')
            delta = [(ident, text) for ident, text in rows if ident not in prior]
            if not delta:
                return dict(status='unchanged', new_messages=0, skipped_messages=len(prior), project_id=project_id)
            text = '\n\n'.join('Message ' + ident + '\n' + body for ident, body in delta)
            ref = 'ingest-v1:' + json.dumps(dict(stream=stream, messages={key: current[key] for key, _ in delta}), sort_keys=True)
            plan = self.brain.plan_archive(title, text, ref, completeness, claims or [], project_id)
            ident = 'ingest-' + uuid.uuid4().hex
            job = dict(id=ident, root=root, path=path, fingerprint=fingerprint, plan=plan, status='review')
            self.state.save(job)
            return dict(id=ident, status='review', project_id=project_id, new_messages=len(delta), skipped_messages=len(prior),
                        source_sha256=fingerprint, text=text, candidates=self.brain.identify(text, project_id)['candidates'],
                        memory_plan=plan, limitations='Only supplied text is imported; attachments and inaccessible history are not retrieved. Candidates require review.')

    def commit(self, ident, approved_sha256):
        with self.state.locked():
            job = self.state.load(ident)
            if job.get('status') == 'committed':
                if approved_sha256 != job['plan']['plan_sha256']:
                    raise ValueError('Wrong reviewed digest')
                return job['result']
            if approved_sha256 != job['plan']['plan_sha256']:
                raise ValueError('Approve the exact reviewed memory digest')
            node = self.files.path(job['root'], job['path'])
            if not node.is_file() or sha(node.read_bytes()) != job['fingerprint']:
                raise ValueError('Import source changed; prepare a new preview')
            # The memory coordinator owns commit/rollback. Its journal is authoritative
            # if the process stops between that commit and this receipt.
            journal = self.brain.state / ('journal-' + job['plan']['plan_id'] + '.json')
            if journal.exists() and json.loads(journal.read_text('utf-8')).get('status') == 'committed':
                result = dict(status='committed', plan_id=job['plan']['plan_id'], recovered_receipt=True)
            else:
                result = self.brain.commit(job['plan']['plan_id'], approved_sha256)
            job.update(status='committed', result=result)
            self.state.save(job)
            return result
