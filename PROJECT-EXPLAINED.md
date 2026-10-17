# What Celious Files is and how it works

Celious connects ChatGPT to selected Windows folders, structured spreadsheet operations and optional evidence-backed project memory. The 0.6.0 development source adds incremental supplied-source ingestion, durable workflows, context selection, recovery checkpoints and reviewed client-tool handoffs. The published baseline remains v0.4.0; memory retains layout version 4. No publication or production deployment is implied.

Celious Files lets you use ChatGPT to work with files in folders you explicitly select on your Windows computer. You can ask for a document summary, a file search, an edited note, a new folder or a recoverable deletion. The assistant chooses tools, while local software performs permitted operations on disk.

## The problem it solves

A conversation alone does not provide direct access to an arbitrary local project folder. Manually uploading each file becomes cumbersome and can separate the answer from the latest version on disk. Celious Files provides a controlled working surface: the assistant can read the current file and save a requested result back into the selected workspace.

A Markdown vault adds durable context. Project notes, decisions and next actions can be saved as normal files, reviewed by a person and read in a later session. This only happens when information is actually saved; the software does not convert every conversation into memory automatically.

## The components

| Component | Responsibility | Where it lives |
| --- | --- | --- |
| ChatGPT | Understand requests and decide which tools to call | Your OpenAI account |
| Celious Files plugin | Present the server's tools in a conversation | ChatGPT plugin configuration |
| Secure MCP Tunnel | Transport requests between OpenAI and the local client | OpenAI tunnel plus local client |
| tunnel-client | Run the private connection and invoke the MCP server | Windows background process |
| Celious MCP server | Expose 14 file tools, six spreadsheet tools, 13 workspace/workflow tools and 13 opt-in memory tools; enforce file policy | Local Python process |
| Celious tray switch | Start, check and stop the local connection | Windows icon and small control panel |
| Projects and Vault | Store the files you authorise | Selected local directories |

MCP means Model Context Protocol, the interface used to describe tools and exchange calls/results. “Celious API” is the runtime credential's name. This package does not create a separate public REST API or a new AI model.

ChatGPT supplies the AI responses in your conversation. The local programme handles files; it does not call a paid model API. The Platform key authenticates the tunnel connection. Creating that key is not purchasing API credits. For the distinction between ChatGPT Plus, tunnel access and unresolved tunnel pricing, read [Does Celious Files cost anything?](README.md#does-celious-files-cost-anything) and the guide's [account checks](INSTALLATION-A-TO-Z.md#costs-keys-and-chatgpt-plus-access).

```text
You request work in ChatGPT
          |
ChatGPT calls a Celious Files tool
          |
OpenAI tunnel delivers the request to the local client
          |
Local MCP server validates the root and relative path
          |
The requested file operation runs inside the allowed folder
          |
The result returns to ChatGPT
```

The tunnel uses an outbound connection, allowing this design to keep the file server private. Account access and associations are described in the [official OpenAI tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

## Example: editing a project note

### Practical file prompts

Use actual configured aliases and relative paths. These examples use synthetic names; review write requests before applying them to important files.

| Task | Prompt | Operation state |
| --- | --- | --- |
| Browse | “List Projects/Example with list_directory; show folders and files.” | Read-only |
| Read document | “Read Projects/Example/brief.pdf with read_document; follow pagination and disclose missing extraction.” | Read-only; no OCR |
| Find | “Search filenames and extracted content under Projects/Example for deployment.” | Read-only, bounded |
| Create | “Create Projects/Example/status.md with this exact supplied text.” | Direct write, not just a proposal |
| Edit | “Read status.md, then replace this unique exact sentence with the supplied replacement.” | Read then backed-up direct edit |
| Organise | “Create Projects/Example/Archive, then move draft.md there without overwriting.” | Direct folder/move operation |
| Recover | “Recover only deletion ID returned for my synthetic test file with restore_deleted.” | Restore if original path is free |
| Stage instead | “Use propose_write for this Markdown change; show the diff and leave it pending.” | Proposal; local review.py applies/rejects |

Rich-document extraction is not a formatted editing workflow. For a valid DOCX/XLSX/PDF write, supply a valid binary payload within limits. Recoverable deletion is private recovery storage, not permanent purge or the Windows Recycle Bin. Memory changes should use the coordinated memory endpoints rather than raw-file edits.

You ask: “Use Celious Files to read Projects/Example/status.md and change the deadline to Friday.” ChatGPT reads the file through a tool, requests an exact-text edit and receives its result. The server checks that the root exists, is writable and contains the allowed relative path. It saves the previous content before updating the file. You can inspect the result directly in Windows.

The tray controls availability. ON starts the local tunnel and server. Hiding the panel leaves them running. OFF ends the connection; Exit also discards the tray's cached secret. Starting the icon at login leaves it OFF until you decide to connect.

## What the current source can do

The 14 filesystem tools cover listing, document/binary reads, search, writes/edits, folders, moves, recoverable deletion/restoration and proposals. Thirteen optional memory endpoints provide separate project collections, cited retrieval, candidates, Inbox review, exact reviewed commits and recovery. Thirteen workspace tools add durable workflows, supplied-source ingestion, context and ZIP operations. Setup exposes 33 tools; --second-brain enables 46 without silently initializing. Follow [PROJECT-MEMORY.md](PROJECT-MEMORY.md) for reviewed initialization/migration and [CONSOLIDATION.md](CONSOLIDATION.md) for local approval and deployment.

The server extracts text from PDF, DOCX, ODT, ODS and XLSX files and reads ordinary text/code files. Six dedicated tools add typed ODS/XLSX/CSV/TSV inspection, bounded reads/searches, controlled writes/edits and explicit data-only conversion. See [SPREADSHEETS.md](SPREADSHEETS.md) for parameter details and feature-loss acknowledgements. It does not provide OCR or rich-document layout editing. Binary writes must contain valid bytes for the intended format. File write/read limits and format behaviour are in README.md.

There is no direct copy-file tool; a client could read and write permitted file contents within the size limits. Proposed changes remain pending until reviewed locally. For example, run `service\.venv\Scripts\python.exe service/review.py` to list pending requests, then rerun it with a request ID to review and explicitly apply or reject it.

## Permission boundaries

The default installation grants direct mutations inside Projects and Vault. It rejects traversal, hidden/special paths, root deletion, symlinks, Windows junctions and hard-linked files. Overwrites receive backups; deletion moves content to private recovery storage. Recovery depends on retaining that storage and using the same volume.

These are application checks, not a separate Windows sandbox or independently audited security guarantee. Local software running as the same user may still access process memory or files. ChatGPT's own tool approvals and account restrictions remain separate. Read SECURITY.md before extending access.

## How this relates to the wider Celious project

Published v0.4.0 contains the file-access layer, starter vault, desktop switch and opt-in project-aware Second Brain. This source retains spreadsheet processing and durable bounded workflows with supplied-source ingestion. ChatGPT selects tool calls; there is no background worker scheduler, hidden-history retrieval or guaranteed proactive invocation. Workflow recovery and memory transactions have distinct scopes; external side effects and accepted knowledge are not undone by file rollback.

## Developer map

| File | Responsibility |
| --- | --- |
| setup.py / Install.cmd | Fresh environment, locked dependencies, checked tunnel client, folders/config/profile and optional shortcuts; no silent memory initialization |
| upgrade.py | Reviewed compatible source overlay, private checkpoint, preservation and rollback; does not migrate notes |
| service/engine.py | Root/path/file policy, document extraction, expected hashes, recoverable operations and private audit metadata |
| service/server.py / memory_tools.py | MCP tool definitions/annotations, bounded errors and opt-in memory registration |
| service/spreadsheets.py | Typed workbook parsing, bounded queries, data conversion, safe edits/writes and six spreadsheet tools |
| service/second_brain.py | Portable metadata, evidence/legacy coordinator, locking/journals/recovery and current CLI |
| service/project_memory.py | Project descriptors/layout, scoped records/search, reviewed migration, Inbox, candidates, supersession and indexes |
| service/connect.py / tray_core.py / tray.py | Credential input, outbound tunnel, loopback readiness and hidden process-tree lifecycle |
| service/review.py | Original optional filesystem proposal review; separate from exact memory-plan commits |
| service/authorization.py | Owner-issued directory/time approval scopes, enforced through the shared mutation policy |
| service/connection_settings.py | Pure configuration-first identity resolution with validated legacy profile fallback |
| service/diagnostics.py / Diagnostics.cmd | Shared read-only version/build/environment/configuration/recovery status and explicit local approval commands |
| package.py / test_package.py | Explicit public allowlist, history/privacy checks, deterministic package and tampering/recovery fixtures |
| test_installation.py | Real disposable fresh install, pinned v0.2/v0.3 source upgrades and fresh-environment suites |
| service/test_*.py / Windows workflow | File/tray/legacy/project/MCP acceptance and public CI |

MCP is the protocol carrying tool descriptions/calls/results. A root alias is a short name (Projects or Vault) mapped to an authorized folder. A profile is the local tunnel launch recipe. A plan digest is a SHA-256 fingerprint of the exact reviewed proposal; a journal records coordinated transaction intent for recovery. These are local software components, not a new model or unrestricted shell exposed to ChatGPT.

The 14 file endpoints are list_roots, list_directory, read_document, read_file_bytes, search_files (reads); create_directory, write_file, edit_file, move_file, delete_file, restore_deleted (direct/recoverable writes); propose_folder, propose_move, propose_write (local review). PROJECT-MEMORY.md classifies all 13 memory endpoints, including previews that may queue an unassigned candidate.

### Configuration and data format

setup.py generates private service/config.json. config.example.json is a portable example, not a file to copy over a working installation. It contains tunnel_id (identifier, not secret), plugin_url, read_only, direct_operations and roots with path/writable.

The launcher prefers an explicit valid tunnel_id in config. For older configurations that lack this field, it reads the single tunnel_id under control_plane in the existing generated service/.runtime/profiles/celious.yaml. This limited compatibility reader accepts unquoted or consistently quoted identifiers, rejects missing/invalid/ambiguous identities and never rewrites either file. An invalid explicit config value is not replaced by a profile fallback. A missing plugin_url uses the generic ChatGPT plugin page. Source-only core upgrades preserve the existing launcher, tray and profile; replacing those components is a separately reviewed operation.

Enabling memory adds:

```json
"second_brain": {"root": "Projects", "path": "Archives", "flat_projects": true}
```

The path is relative to an existing root and cannot grant new filesystem access. The runtime secret is not stored in config. The CLI follows the configured root/path unless --root/--prefix explicitly overrides them; use overrides consistently. Fresh layouts store an empty project_container in LAYOUT.md for direct project folders; older layouts retain their Projects container. Never put generated profiles/runtime/config or authorized user files in source control.

Optional private read_path_aliases map historical paths to canonical paths within the same authorized root. Matching follows Windows case-insensitive path semantics and whole folder segments. Targets receive the same path/link checks, alias chains are not followed, and writes through historical paths are denied. This preserves old citations after a separately reviewed relocation; upgrading source alone does not relocate existing notes or generate aliases.

Each project has PROJECT.md (stable UUID/display name), INDEX.md and separate Sources/Knowledge/History. Restricted YAML frontmatter uses JSON-encoded values; source bodies preserve decoded text/CRLF. Knowledge holds type/topic/key/value, status/epistemic/uncertainty, source IDs and exact quote/character ranges. LAYOUT.md selects the default/shared IDs. Inbox candidates are unassigned review material; redirects preserve legacy citation paths.

ProjectBrain reuses file policy and the global cooperating-process lock. Plans bind the full canonical Markdown snapshot and exact digest. Journals precede writes; failed writes restore original versions or preserve newer unrelated edits for review. Migration copies original bytes, creates redirects/indexes and activates the layout last. Sources prove what was supplied, not external truth; the client/operator must review semantic support. Raw file tools bypass multi-note coordination and project scope is not an OS sandbox.

### Safe extension procedure

Use a dedicated source branch and disposable roots; never develop mutation tests against the live installation. Preserve existing tool names/arguments where feasible and explicitly document intentional compatibility changes such as unassigned legacy archive calls entering Inbox. Add meaningful policy/migration/workflow tests, update existing guides and package allowlist, and run the permanent PUBLISHING.md checklist. New dependencies, permissions, observers or credential behavior need deliberate design/review. Do not claim a feature tested merely because its code exists or an old CI run passed.

## Integrated execution

The service registers `workspace_tools` alongside file/spreadsheet/memory tools. `ingestion` parses supplied source deltas into the existing reviewed memory coordinator. `workflows` executes bounded adapters with durable state/checkpoints in private `.runtime/operations`; `operations_state` serializes cooperating processes and flushes intents before effects. Client-side research/code/test capabilities use reviewed artifact handoffs; there is no server shell or autonomous account access. [User procedures and recovery](WORKFLOWS.md).

## Capability status and development priorities

Status is specific to the tested source and environment. Existing code alone does not establish operational availability. The published baseline has 14/27 tools; this development source has 33/46 with memory disabled/enabled. [VALIDATION.md](VALIDATION.md) separates historical release evidence from current checks.

| Capability | Status and evidence | Practical limit |
| --- | --- | --- |
| Filesystem access and recovery | Implemented; disposable filesystem and protocol checks are available | Authorized roots only; recoverable deletion can fail across volumes |
| Document extraction | Implemented; synthetic format tests cover extraction | Text extraction, no OCR or rich-layout editing |
| Spreadsheet operations | Implemented; dedicated suite invokes all six tools through copied-server MCP sessions | Bounded workbooks; conversion is data-only; XLS unsupported; no calculation |
| Project memory and evidence | Implemented; project/legacy suites and independent-process protocol retrieval | Bounded lexical retrieval; supplied evidence does not prove external truth |
| Supervised archive workflow | Implemented; preview/digest, Inbox, conflict and recovery tests | Approval binds the exact plan; raw writes bypass coordination |
| Tray and tunnel lifecycle | Implemented; lifecycle tests and historical Windows acceptance | Live account permissions and connector refresh require environment-specific checks |
| Installation and source upgrades | Implemented; fresh/v0.2/v0.3 matrix passed for stabilised spreadsheet source | Exact candidate checks are recorded separately; hosted CI and production cutover need their own acceptance |
| Durable task orchestration | Implemented with bounded dependency steps, persistent progress, output verification and reverse recovery | Explicit run/resume; client-tool handoffs pause for evidence; not a background scheduler |
| Scheduler, autonomous workers and agent bridge | Not implemented | No execution service or worker permission model is supplied |
| Supplied conversation/document ingestion | Implemented with project-bound incremental streams and reviewed evidence plans | No inaccessible-history retrieval; edited source requires explicit revision review |
| Semantic retrieval | Weighted lexical retrieval remains implemented | No embeddings or undisclosed inference dependency |

The candidate consolidates existing file, spreadsheet and project-memory behavior. No approved feature backlog is implied by this table. Remaining release steps are exact-candidate validation, hosted CI after an authorized push, explicit publication review and separately authorized production acceptance. Further implementation requires its own approved scope and acceptance criteria.

Development follows: investigate, verify, identify a gap, propose a solution, approve scope, implement, test, document and obtain release approval. Local development approval does not authorize publication, production deployment or unrelated enhancements. Private comparisons and operational reports stay outside the repository.

## Installation and project status

Start with [INSTALLATION-A-TO-Z.md](INSTALLATION-A-TO-Z.md). Source and configuration examples are portable; actual folder paths, tunnel IDs, credentials and shortcuts are generated separately for each computer. No personal documents or live account settings are included.

The installer creates the local environment and downloads required dependencies. Each operator completes their own OpenAI account setup and live ChatGPT test. [VALIDATION.md](VALIDATION.md) records successful local and fresh GitHub Windows-runner checks. Those tests do not establish another person's ChatGPT Plus/write permissions or account-specific billing terms. Use the linked account checks before installation and the disposable acceptance test afterwards.
