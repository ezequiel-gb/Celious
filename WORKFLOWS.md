# Integrated project work

Fresh installations use local approval scopes for direct filesystem changes, including workflow execution and memory commits. The owner grants appropriate directory scopes locally before the reviewed workflow; renew them before expiry if recovery is required. See [CONSOLIDATION.md](CONSOLIDATION.md) for the supported approval, diagnostics and deployment contract. Client-mode automation remains explicitly available.

The 0.6.0 development implementation adds thirteen MCP tools to the existing service: 33 tools without optional memory, 46 with memory. Existing file, spreadsheet and memory tools retain their interfaces. No new dependency is needed. Memory remains layout version 4; discovery never initializes an archive.

## Start a conversation

Ask the reasoning client: “Call `workspace_context` for project `<PROJECT_ID>` with query `<TASK_TOPIC>`, review the relevant decisions and resume the matching workflow.” Use `memory_projects` to select a stable project ID. With no ID or reliable path binding, the service asks for selection. It does not guess from conversation text or leak another project's default context. Shared knowledge is included through existing scoped retrieval.

Optional local configuration can bind a project directory to its memory ID:

```json
"project_bindings": [
  {"root": "Projects", "path": "Example", "project_id": "<PROJECT_ID>"}
]
```

The most specific matching path wins; equal-depth conflicting IDs fail. Pass `root` and `path` to `workspace_context` to use a binding. This configuration is optional and must be reviewed locally. Existing configurations need no change.

MCP instructions encourage contextual retrieval and reviewed capture. ChatGPT decides whether to invoke tools. The service cannot monitor conversations, force client invocation, access inaccessible chat history or run continuously between calls. The explicit start/resume request above is the dependable alternative.

The [OpenAI MCP server documentation](https://developers.openai.com/plugins/concepts/mcp-server) describes discovery, model-selected tool calls and server request validation. Celious does not infer a conversation-history API or mandatory client trigger from MCP connectivity.

## Import supplied conversations and handovers

1. Save an accessible export or handover inside an authorized root. Do not include credentials. Larger exports can be split locally; source files are limited to 10 MB and selected text to 900 KB.
2. Call `ingest_preview(root, path, stream_id, project_id, conversation_id, claims_json)`. Use a stable stream ID for this source/revision. For JSON exports, select exactly one conversation ID. Supported shapes are a conversation/list with `mapping` and `current_node`, or `messages` containing stable `id`, `role` and text `content` fields. Mapping exports follow only the selected parent chain, preserving roles and excluding sibling branches. Attachments are not retrieved; completeness remains partial.
3. Review returned delta text, quote-backed candidates, source digest and exact memory plan. Optional claims use the existing archive claim schema; the evidence must occur exactly in the delta. Automatic cue matches remain tentative. Reasoning/curation is performed by the client and reviewer, not an undisclosed local model.
4. With owner approval, call `ingest_commit(ingest_id, approved_sha256)` using `memory_plan.plan_sha256`. Stale memory or changed source is refused. The existing journal owns transactional commit and recovery.
5. Repeating the same source returns `unchanged`. Appended message IDs import only the delta. Editing/removing already imported messages requires an explicitly reviewed new revision stream; old evidence is preserved. A stream cannot silently move to another project. Document imports track stable extracted line positions, so reflowed documents require a new revision.

The ingestion ledger is derived from committed source provenance, not a volatile client cursor. A committed import remains discoverable after process restart. Existing duplicate/conflict detection, pending claims, supersession and portable Markdown history remain authoritative. Use `memory_supersede_preview` and exact reviewed `memory_commit` to replace outdated knowledge; ingestion never silently overwrites it.

## Durable workflows

`workflow_create(title, steps_json, project_id)` freezes a reviewable plan with input fingerprints and retrieves scoped context for a supplied project ID. Each step is `{id, op, args, needs}`. IDs are unique; dependencies reference earlier steps. A later use of a changed path must depend on its prior writer. Filesystem roots/paths must be literal and authorized.

Example `steps_json`:

```json
[
  {"id":"context","op":"memory_search","args":{"query":"requirements"},"needs":[]},
  {"id":"note","op":"write","args":{"root":"Projects","relative":"Example/summary.md","content":"Reviewed summary"},"needs":["context"]},
  {"id":"sheet","op":"spreadsheet_write","args":{"root":"Projects","destination":"Example/results.xlsx","workbook_json":"[{\"name\":\"Results\",\"rows\":[[\"Result\"],[\"Reviewed\"]]}]"},"needs":["note"]}
]
```

Review the plan, including overwrites/deletions and external requests. Call `workflow_run(workflow_id, approved_sha256, max_steps)` with the returned `plan_sha256` only within the user's authorization. `max_steps` allows bounded batches. Continue with the same ID/digest after a pause or client restart. Use `workflow_status` and project-scoped `workflow_list` to inspect progress, failures and event history. There is no background scheduler.

Supported local operations reuse existing adapters: `read`, `search`, `write`, `edit`, `mkdir`, `move`, `delete`, `spreadsheet_inspect`, `spreadsheet_read`, `spreadsheet_write`, `spreadsheet_edit`, `spreadsheet_convert`, and project-scoped `memory_search`. Arguments match the corresponding Python methods: file mutations use `relative`; document reads use `path`; spreadsheet writes use `destination`. See tool descriptions and [spreadsheet limits](SPREADSHEETS.md). `mkdir` creates one directory per step with an existing parent. Move/delete workflow steps are file-only; existing direct tools support separately reviewed directory operations.

A top-level argument may reference a dependency output using `{"$step":"earlier_id","field":"sha256"}` or `"field":"text"`. Paths cannot be dynamically inferred from output. No shell, arbitrary Python, executable source text or URL is evaluated. Inputs and results are untrusted data.

Plans allow 1–50 steps and 1 MB of specification. Recovery before-images are bounded to approximately 20 MB. Reads retain their existing pagination limits. Split larger tasks into named workflows. Operations are serialized across processes in private runtime state. This coordinates workflow execution; it does not exclusively lock external editors or unrelated tools.

## Client-tool integration

`integration_status` reports real local dependencies/adapters, memory health and configured permissions. It distinguishes `client_tools: handoff_only` from installed server execution. External research, coding agents, test runners, remote sources and accounts are available only when the reasoning client actually exposes/authorizes them. The local service does not invent connector access or run an implicit agent bridge.

A `handoff` step uses exactly `task`, `artifact_root`, `artifact_path`. Execution pauses and returns a token. The client performs the requested work through its own authorized tools, reviews outcomes and saves an evidence artifact to the declared location. Call `workflow_receipt` with the workflow ID, step ID, current token and actual artifact SHA-256. A missing, unchanged or mismatched artifact is refused. Then resume `workflow_run`.

This verifies artifact existence/integrity. It **does not independently prove research accuracy, external publication, command success or semantic correctness**. Review the actual evidence. Tool responses alone are not success criteria. External side effects need their own approval and rollback; a receipt does not bypass tool permissions. Without an account/connector, use a locally supplied document/artifact and record the missing integration honestly.

## Recovery and maintenance

Writes use existing guarded replacements and backups. Workflow intents/checkpoints are flushed before effects; observed postconditions are verified before steps complete. Completed work is not blindly replayed. Changed reviewed inputs or outputs block continuation. Interrupted text writes/moves/deletions are reconciled against exact filesystem evidence. An uncertain binary spreadsheet result remains blocked: inspect/read it, then use `workflow_reconcile` with the reviewed workflow digest and actual output digest. This explicit action parses and verifies bytes before allowing resume or rollback; it does not manufacture a missing result.

`workflow_rollback` reverses completed local file mutations using before-images. It refuses newer changed files, moves back only to unused paths, restores recoverably deleted files and removes only empty created folders. New files removed during rollback use recoverable deletion. External artifacts/side effects and accepted memory are retained. A failed/ambiguous rollback stops for inspection rather than destroying intervening work. Workflow execution is a sequence of recoverable steps, not an all-or-nothing transaction spanning accounts.

Private `.runtime/operations` contains plans, checkpoint contents and receipts. Keep it outside authorized shared roots and public packages; protect it like project data. Back it up together with application configuration, existing memory coordinator state and authorized data at a quiescent checkpoint. Do not delete it to “fix” an interrupted task. Inspect failures with `workflow_status`, local logs and `integration_status`.

Local read-only diagnostics are available without a ChatGPT connection:

```bat
service\.venv\Scripts\python.exe service/workspace_tools.py --health
service\.venv\Scripts\python.exe service/workspace_tools.py --project-context <PROJECT_ID> --query requirements
service\.venv\Scripts\python.exe service/workspace_tools.py --workflows --project-id <PROJECT_ID>
service\.venv\Scripts\python.exe service/workspace_tools.py --workflow-status <WORKFLOW_ID>
```

Health includes exact installed-versus-lock differences. It does not claim authenticated account connectivity. Diagnostic output can contain authorized project paths/content and is private operational material.

Installation uses the existing locked [setup procedure](INSTALLATION-A-TO-Z.md). Source upgrades copy all new modules and matching tests together; existing configuration, credentials, profiles, runtime state and memory are preserved. The source-only updater still requires a qualifying matching-lock environment and an OFF service. A missing-lock installation needs separately approved environment qualification/staging, never a copied lock to bypass the guard.

Intentional `setup.py --replace-config` reconfiguration also explicitly replaces its generated tunnel profile; ordinary repeat setup refuses changes. Turn the connection OFF first and review root/tunnel options. This flag is not a source-upgrade command and must not be used to reset existing operational configuration casually.

Run `service/test_workflows.py` and `service/test_workspace_protocol.py` with the installed interpreter. The second test executes actual MCP calls over two fresh processes with disposable roots, export ingestion, memory retrieval, typed workbook output, persistent workflow resume, a reviewed handoff, delta ingestion and conflict-safe rollback. These local checks do not assert hosted CI or live account deployment.
