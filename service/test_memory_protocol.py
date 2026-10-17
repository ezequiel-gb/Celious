"""Two real MCP sessions with disposable roots and a separate copied server."""
import asyncio
import json
from pathlib import Path
import shutil
import sys
import tempfile
from mcp import Client
from mcp.client.stdio import StdioServerParameters


def unpack(result):
    assert not result.is_error, result
    for item in result.content:
        if getattr(item, 'type', None) == 'text':
            return json.loads(item.text)
    raise AssertionError('No JSON result')


async def run():
    with tempfile.TemporaryDirectory(prefix='celious-memory-mcp-') as temporary:
        base = Path(temporary)
        service = base / 'service'
        service.mkdir()
        for name in ['engine.py', 'server.py', 'second_brain.py', 'project_memory.py', 'memory_tools.py', 'spreadsheets.py',
                     'operations_state.py', 'ingestion.py', 'workflows.py', 'workspace_tools.py', 'authorization.py', 'diagnostics.py', 'connection_settings.py']:
            shutil.copy2(Path(__file__).parent / name, service / name)
        for name in ['vault', 'projects']:
            (base/name).mkdir()
        (base/'vault/INDEX.md').write_text('# Disposable vault', 'utf-8')
        config = dict(direct_operations=True, roots={name.title(): dict(path=str(base/name), writable=True) for name in ['vault','projects']},
                      second_brain=dict(root='Projects', path='Celious/Second Brain'))
        (service/'config.json').write_text(json.dumps(config), 'utf-8')
        transport = StdioServerParameters(command=sys.executable, args=[str(service/'server.py')])
        async with Client(transport) as client:
            names = {t.name for t in (await client.list_tools()).tools}
            assert len(names) == 46, names
            assert {'memory_search','memory_archive_preview','memory_commit','memory_inspect','memory_supersede_preview'} <= names
            initialization = unpack(await client.call_tool('memory_migrate_preview', {}))
            unpack(await client.call_tool('memory_commit', dict(plan_id=initialization['plan_id'], approved_sha256=initialization['plan_sha256'])))
            args = dict(title='Actually supplied transcript', text='User: Prefer portable Markdown memory.',
                        source_ref='disposable MCP session A', completeness='excerpt', project_id=initialization['default_project_id'], claims_json=json.dumps([
                            dict(type='preference', title='Portable memory', topic='Celious', key='format', value='portable Markdown',
                                 evidence='Prefer portable Markdown memory.', epistemic='asserted', uncertainty='Supplied excerpt only')]))
            preview = unpack(await client.call_tool('memory_archive_preview', args))
            assert not preview['saved_to_memory']
            denied = await client.call_tool('memory_commit', dict(plan_id=preview['plan_id'], approved_sha256='wrong'))
            assert denied.is_error
            result = unpack(await client.call_tool('memory_commit', dict(plan_id=preview['plan_id'], approved_sha256=preview['plan_sha256'])))
            assert result['status'] == 'committed'
            original_hit = unpack(await client.call_tool('memory_search', dict(query='portable Markdown')))['hits'][0]
            project_preview = unpack(await client.call_tool('memory_project_preview', dict(name='Project-B')))
            unpack(await client.call_tool('memory_commit', dict(plan_id=project_preview['plan_id'], approved_sha256=project_preview['plan_sha256'])))
            projects = unpack(await client.call_tool('memory_projects', {}))
            assert len(projects['projects']) == 3
            identified = unpack(await client.call_tool('memory_identify', dict(text='User: We decided to use portable Markdown.',project_id=initialization['default_project_id'])))
            assert identified['candidates'] and not identified['saved_to_memory']
            unassigned_args = dict(args, title='Unassigned source', text='User: Prefer portable files.', claims_json=json.dumps([
                dict(type='preference',title='Portable files',topic='Other',key='files',value='portable files',
                     evidence='Prefer portable files.',epistemic='asserted',uncertainty='Test excerpt')]))
            unassigned_args.pop('project_id')
            queue = unpack(await client.call_tool('memory_archive_preview', unassigned_args))
            assert queue['status'] == 'awaiting_project'
            assert unpack(await client.call_tool('memory_inbox', {}))['candidates']
            resolved = unpack(await client.call_tool('memory_inbox_resolve_preview', dict(queue_id=queue['queue_id'],project_id=project_preview['project_id'])))
            unpack(await client.call_tool('memory_commit', dict(plan_id=resolved['plan_id'],approved_sha256=resolved['plan_sha256'])))
            scoped_hits=unpack(await client.call_tool('memory_search',dict(query='portable files',project_id=initialization['default_project_id'],include_shared=False)))['hits']
            assert all(h['project_id']==initialization['default_project_id'] for h in scoped_hits)
            cross_hits=unpack(await client.call_tool('memory_search',dict(query='portable files',project_id=initialization['default_project_id'],cross_project=True)))['hits']
            assert any(h['project_id']==project_preview['project_id'] for h in cross_hits)
            reject_args = dict(args,title='Rejected source',text='User: Prefer rejected Markdown.')
            reject_args['claims_json']='[]'
            rejected = unpack(await client.call_tool('memory_archive_preview',reject_args))
            assert unpack(await client.call_tool('memory_reject',dict(proposal_id=rejected['plan_id'])))['accepted_knowledge_changed'] is False
            denied = await client.call_tool('memory_commit',dict(plan_id=rejected['plan_id'],approved_sha256=rejected['plan_sha256']))
            assert denied.is_error
            replacement_args = dict(args,title='Replacement source',text='User: Prefer SQLite memory.',claims_json=json.dumps([
                dict(type='preference',title='SQLite memory',topic='Celious',key='format',value='SQLite',
                     evidence='Prefer SQLite memory.',epistemic='asserted',uncertainty='Test revision')]))
            replacement = unpack(await client.call_tool('memory_archive_preview',replacement_args))
            assert replacement['warnings'][0]['kind']=='conflict'
            unpack(await client.call_tool('memory_commit',dict(plan_id=replacement['plan_id'],approved_sha256=replacement['plan_sha256'])))
            pending = unpack(await client.call_tool('memory_search',dict(query='SQLite',status='pending')))['hits'][0]
            supersede = unpack(await client.call_tool('memory_supersede_preview',dict(old_id=original_hit['id'],new_id=pending['id'],reason='Reviewed revision')))
            unpack(await client.call_tool('memory_commit',dict(plan_id=supersede['plan_id'],approved_sha256=supersede['plan_sha256'])))
            rebuild = unpack(await client.call_tool('memory_rebuild_preview',{}))
            unpack(await client.call_tool('memory_commit',dict(plan_id=rebuild['plan_id'],approved_sha256=rebuild['plan_sha256'])))
        # Fresh process, independent client state; retrieve only persisted Markdown.
        async with Client(transport) as client:
            hit = unpack(await client.call_tool('memory_search', dict(query='SQLite')))['hits'][0]
            assert hit['sources'][0]['completeness'] == 'excerpt'
            assert hit['evidence'][0]['quote'] == 'Prefer SQLite memory.'
            assert unpack(await client.call_tool('memory_inspect', {}))['issues'] == []
            assert not (await client.call_tool('list_roots', {})).is_error
            assert not (await client.call_tool('read_document', dict(root='Vault', path='INDEX.md'))).is_error
            denied = await client.call_tool('read_document', dict(root='Projects', path='../outside'))
            assert denied.is_error
        print('All 13 memory endpoints exercised across 46 advertised MCP tools: explicit project initialization/creation, scoped/cross retrieval, identification, queue/resolve/reject, exact commit, supersession, rebuild, integrity and a fresh-session read; original reads and traversal denial passed.')


if __name__ == '__main__':
    asyncio.run(run())
