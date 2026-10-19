"""Actual MCP calls across fresh processes: export -> memory -> workflow -> artifacts."""
import asyncio
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from mcp import Client
from mcp.client.stdio import StdioServerParameters


def unpack(result):
    assert not result.is_error, str(result)
    return json.loads(next(item.text for item in result.content if getattr(item, 'type', None) == 'text'))


async def acceptance():
    with tempfile.TemporaryDirectory(prefix='celious-integrated-mcp-') as temporary:
        base = Path(temporary)
        service = base/'service'
        service.mkdir()
        for node in Path(__file__).parent.glob('*.py'):
            if not node.name.startswith('test_'):
                shutil.copy2(node, service/node.name)
        (base/'projects').mkdir()
        config = dict(direct_operations=True, roots=dict(Projects=dict(path=str(base/'projects'), writable=True)),
                      second_brain=dict(root='Projects', path='Archives'))
        (service/'config.json').write_text(json.dumps(config), 'utf-8')
        transport = StdioServerParameters(command=sys.executable, args=[str(service/'server.py')])
        async with Client(transport) as client:
            assert client.server_info.version == '0.6.0'
            names = {tool.name for tool in (await client.list_tools()).tools}
            assert len(names) == 46, names
            async def call(tool_name, **args): return unpack(await client.call_tool(tool_name, args))
            assert (await call('integration_status'))['memory']['status'] == 'initialization_required'
            assert not (base/'projects/Archives/LAYOUT.md').exists()
            plan = await call('memory_migrate_preview')
            await call('memory_commit', plan_id=plan['plan_id'], approved_sha256=plan['plan_sha256'])
            project = plan['default_project_id']
            plan = await call('memory_project_preview', name='Unrelated')
            await call('memory_commit', plan_id=plan['plan_id'], approved_sha256=plan['plan_sha256'])
            other = plan['project_id']
            export = [dict(id='demo-chat', title='Synthetic handover', messages=[dict(id='message-1', role='user', content='Decision: preserve exact source evidence.\nFact: Miles supervises this project on explicit request.')])]
            await call('write_file', root='Projects', path='conversation.json', content=json.dumps(export), expected_sha256='')
            claim = dict(type='decision', title='Preserve evidence', topic='Audit', key='source', value='preserve exact source evidence',
                         evidence='Decision: preserve exact source evidence.', epistemic='accepted', uncertainty='Synthetic integration evidence')
            supervisor = dict(type='fact',title='Project supervisor',topic='Operating model',key='supervisor',value='Miles supervises this project on explicit request',
                              evidence='Fact: Miles supervises this project on explicit request.',epistemic='accepted',uncertainty='Synthetic user-supplied operating rule, not autonomous execution')
            imported = await call('ingest_preview', root='Projects', path='conversation.json', stream_id='demo-stream', project_id=project,
                                  conversation_id='demo-chat', claims_json=json.dumps([claim,supervisor]))
            await call('ingest_commit', ingest_id=imported['id'], approved_sha256=imported['memory_plan']['plan_sha256'])
            assert (await call('workspace_context', project_id=project, query='evidence'))['memory']['hits']
            assert not (await call('workspace_context', project_id=other, query='evidence'))['memory']['hits']
            steps = [dict(id='context', op='memory_search', args=dict(query='evidence'), needs=[]),
                     dict(id='notes', op='write', args=dict(root='Projects', relative='notes.md', content='Reviewed evidence retained.'), needs=['context']),
                     dict(id='document', op='write', args=dict(root='Projects', relative='handover.docx', encoding='document', content=json.dumps(dict(title='Project handover',blocks=[dict(type='paragraph',text='Evidence retained.')]))), needs=['notes']),
                     dict(id='formatted_edit', op='edit', args=dict(root='Projects', relative='handover.docx', old_text='Evidence retained.',new_text='Attributed evidence retained.'), needs=['document']),
                     dict(id='sheet', op='spreadsheet_write', args=dict(root='Projects', destination='result.xlsx', workbook_json=json.dumps([dict(name='Results', rows=[['Item', 'Count'], ['Evidence', 1]])])), needs=['notes']),
                     dict(id='inspect', op='spreadsheet_inspect', args=dict(root='Projects', path='result.xlsx'), needs=['sheet']),
                     dict(id='review', op='handoff', args=dict(task='Review local outputs with authorized client tools; write the outcome artifact', artifact_root='Projects', artifact_path='review.md'), needs=['inspect'])]
            workflow = await call('workflow_create', title='Integrated evidence workflow', steps_json=json.dumps(steps), project_id=project)
            paused = await call('workflow_run', workflow_id=workflow['id'], approved_sha256=workflow['plan_sha256'], max_steps=5)
            assert paused['status'] == 'paused'
            content = await call('read_spreadsheet', root='Projects', path='result.xlsx')
            assert 'Evidence' in json.dumps(content) and 'Count' in json.dumps(content)
            assert not (await call('memory_inspect'))['issues']
            bad = await client.call_tool('workflow_run', dict(workflow_id=workflow['id'], approved_sha256='wrong'))
            assert bad.is_error
        # A completely fresh process has no conversation state; durable IDs recover work.
        async with Client(transport) as client:
            async def call(tool_name, **args): return unpack(await client.call_tool(tool_name, args))
            context = await call('workspace_context', project_id=project, query='evidence')
            assert context['memory']['hits'] and context['workflows']['total'] == 1
            assert (await call('workspace_context',project_id=project,query='Miles'))['memory']['hits']
            status = await call('workflow_status', workflow_id=workflow['id'])
            assert status['status'] == 'paused'
            waiting = await call('workflow_run', workflow_id=workflow['id'], approved_sha256=workflow['plan_sha256'])
            assert waiting['status'] == 'waiting'
            token = waiting['steps']['review']['token']
            result = await call('read_document', root='Projects', path='notes.md')
            assert result['text'] == 'Reviewed evidence retained.'
            assert (await call('read_document',root='Projects',path='handover.docx'))['text'] == 'Attributed evidence retained.'
            odt = json.dumps(dict(blocks=[dict(type='paragraph',text='Project continuity verified.')]))
            await call('write_file',root='Projects',path='summary.odt',content=odt,encoding='document',expected_sha256='')
            await call('edit_file',root='Projects',path='summary.odt',old_text='continuity',new_text='cross-session continuity')
            assert 'cross-session continuity' in (await call('read_document',root='Projects',path='summary.odt'))['text']
            # The reasoning client owns code execution; the server only waits for evidence.
            verifier = "from openpyxl import load_workbook\nimport sys\nb=load_workbook(sys.argv[1],read_only=True)\ns=b['Results']\nassert s['A2'].value=='Evidence' and s['B2'].value==1\nb.close()\nprint('Verified actual workbook cells: Evidence, 1')\n"
            await call('write_file', root='Projects', path='verify_result.py', content=verifier, expected_sha256='')
            verification = subprocess.run([sys.executable, str(base/'projects/verify_result.py'), str(base/'projects/result.xlsx')], capture_output=True, text=True, timeout=30)
            assert verification.returncode == 0, verification.stderr
            outcome = verification.stdout + 'Reviewed text: ' + result['text']
            await call('write_file', root='Projects', path='review.md', content=outcome, expected_sha256='')
            await call('workflow_receipt', workflow_id=workflow['id'], step_id='review', token=token, artifact_sha256=hashlib.sha256(outcome.encode()).hexdigest())
            completed = await call('workflow_run', workflow_id=workflow['id'], approved_sha256=workflow['plan_sha256'])
            assert completed['status'] == 'completed'
            assert (await call('ingest_preview', root='Projects', path='conversation.json', stream_id='demo-stream', project_id=project, conversation_id='demo-chat'))['status'] == 'unchanged'
            export[0]['messages'].append(dict(id='message-2', role='user', content='Verified: task completed with source retained.'))
            await call('write_file', root='Projects', path='conversation.json', content=json.dumps(export))
            delta = await call('ingest_preview', root='Projects', path='conversation.json', stream_id='demo-stream', project_id=project, conversation_id='demo-chat')
            assert delta['new_messages'] == 1 and delta['skipped_messages'] == 1
            await call('ingest_commit', ingest_id=delta['id'], approved_sha256=delta['memory_plan']['plan_sha256'])
            assert not (await call('memory_inspect'))['issues']
            assert (await call('workflow_list', project_id=other))['total'] == 0
            rollback = await call('workflow_rollback', workflow_id=workflow['id'], approved_sha256=workflow['plan_sha256'])
            assert rollback['status'] == 'rolled_back'
            assert not (base/'projects/result.xlsx').exists() and not (base/'projects/notes.md').exists()
            assert not (base/'projects/handover.docx').exists()
            assert (base/'projects/review.md').is_file()  # External artifacts are preserved.
            assert (await call('workspace_context', project_id=project, query='evidence'))['memory']['hits']
            assert (await call('integration_status'))['adapters'][-1]['status'] == 'handoff_only'
        print('Integrated MCP acceptance passed: 46 tools, source ingestion, reviewed knowledge, project isolation, typed workbook, fresh-process resume, client handoff artifact, delta import and conflict-safe file rollback; memory and external artifacts preserved.')


if __name__ == '__main__':
    asyncio.run(acceptance())
