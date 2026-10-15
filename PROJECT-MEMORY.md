# Celious project memory v0.4.0

This is the current upgrade, archive and retrieval guide. Celious physically separates project memory while preserving original evidence and the existing file policy, tray, credentials and tunnel. No background observer, worker, model API call, new dependency, extra plugin or authorized root is added.

## Layout and identities

```text
Archives/
  INDEX.md
  WORKFLOW.md
  LAYOUT.md
  <project-name>/
    PROJECT.md
    INDEX.md
    Sources/
    Knowledge/
    History/
  Shared Knowledge/
    PROJECT.md
    INDEX.md
    Sources/
    Knowledge/
    History/
  Inbox/
    INDEX.md
    candidate-<uuid>.md
```

PROJECT.md contains an immutable project UUID and display name. Location comes from its containing folder. Display-name edits retain identity; physically renaming a collection still requires a reviewed link/index migration. Runtime plans, locks and journals remain outside the Markdown collection.

Sources preserves accessible text, completeness/reference and body SHA-256. Knowledge holds reviewed claims with ID, timestamps, type, topic/key/value, status, epistemic label, uncertainty, exact source quote/character offsets and links. History retains former versions. Indexes are rebuildable. The existing restricted YAML format and exact CRLF source fidelity remain unchanged.

## Fresh installation and reviewed initialization

Commands are for Command Prompt from the extracted source folder. Follow INSTALLATION-A-TO-Z.md for prerequisites, account/tunnel access and private key handling. Current development setup has 14 filesystem and six spreadsheet tools (20 total). To opt into 33 tools:

```bat
py -3.12 setup.py --tunnel-id YOUR_TUNNEL_ID --second-brain --shortcuts
```

Use the actual tunnel ID, never a secret, and deliberate --projects/--vault options only if changing default folders. Setup verifies dependencies and adds `"second_brain": {"root": "Projects", "path": "Archives", "flat_projects": true}`. It does NOT initialize/migrate notes. Fresh initialization creates empty Celious/shared collections and WORKFLOW.md through a separately reviewed plan. Existing workflows are preserved.

This is an alternative to the file-only installer, not a second setup run afterward. If you already configured 14-tool v0.4, extract another complete source copy into a separate folder and use the reviewed upgrade.py --enable-memory procedure below; it preserves the existing configuration. Do not use --replace-config simply to enable memory.

**Local CLI sequence, with the actual connection OFF:** change directory to the configured installation and run:

```bat
service\.venv\Scripts\python.exe service/second_brain.py plan-migrate
```

Review all returned contents, paths, warnings, plan_id and plan_sha256. For existing notes, verify the complete recovery backup and obtain authorization for migration first. Then substitute the exact returned values:

```bat
service\.venv\Scripts\python.exe service/second_brain.py commit PLAN_ID REVIEWED_SHA256
service\.venv\Scripts\python.exe service/second_brain.py inspect
service\.venv\Scripts\python.exe service/second_brain.py projects
```

Turn the existing switch ON, enter the existing key privately if needed, refresh ChatGPT tool discovery, and verify memory_projects, memory_inspect and scoped retrieval. Empty fresh collections have no search hits.

**MCP alternative:** turn ON and refresh discovery FIRST; then call memory_migrate_preview, review its complete map/digest, and memory_commit only the exact authorized plan. Inspect and list projects afterward. Do not attempt MCP calls while OFF or change notes concurrently. Initialization never runs automatically at startup; an activated v4 layout rejects repeat migration.

## Upgrade from public v0.2.0 or private v0.3.0

The pinned public v0.2 baseline is `1181f82fd6df5802cf5cc4317dd35ce3f42799b0`. Extract the complete new source into a SEPARATE folder. Do not use setup.py --replace-config to upgrade a configured installation. Public v0.2 lacks both the memory modules and the engine's absent-target expected-digest check.

The source-only overlay refreshes the six core modules and their six service test scripts together, including the safe copied-server file protocol check. It preserves the launcher/tray, dependency environment and existing profiles. Test script bytes are included in the same overlay checkpoint and rollback as modules. Use the updated scripts rather than an older installed file-only test that assumes an obsolete tool catalogue.

The target must already have a matching requirements.lock.txt; missing or different locks require separate environment review. Do not copy a lock into an unqualified installation merely to pass that guard. A matching file identifies the intended dependency set, not necessarily the packages actually installed. Fresh installations use the pinned lock unchanged. For existing environments, run that installation's Python `-m pip check` and review `-m pip freeze` against the lock: pip check verifies dependency compatibility, not exact pin equality. A working older environment can be retained after explicit acceptance, but must not be described as lock-identical. Package changes require separate review and testing; this overlay never runs pip or automatically reconciles versions.

Create a complete private backup of installation/config, runtime/profile/recovery, authorized data and shortcuts, outside the source/installation/authorized roots. Verify hashes and isolated restoration, resolve incomplete transactions and preserve every prior backup. Obtain authorization for the overlay/migration. Turn OFF all actual clients for this installation/tunnel. Exit only if necessary; it clears the cached key. Test in disposable roots before production.

From the NEW source folder, review this non-mutating preview. Replace example paths with your actual absolute paths:

```bat
py -3.12 upgrade.py --installation "D:\CeliousInstalled" --backup-dir "D:\PrivateRecovery" --enable-memory
```

After reviewing hashes/list and stopping the actual clients:

```bat
py -3.12 upgrade.py --installation "D:\CeliousInstalled" --backup-dir "D:\PrivateRecovery" --enable-memory --apply --connection-off
```

The overlay installs **engine.py, server.py, second_brain.py, project_memory.py and memory_tools.py** plus current guides. It preserves roots/config fields/tunnel/profile/notes and adds memory opt-in only when requested and absent. Existing memory configuration is preserved; omit --enable-memory to retain a disabled setup. It rejects linked/overlapping paths and an ON/busy tray status, but does not stop clients itself. Review customized engine/server changes first: complete modules are replaced. The dependency lock must match; a differing custom lock needs a separately reviewed environment upgrade.

The helper verifies a unique private overlay checkpoint before replacement: original config/files, absent-file list and ZIP hash. This is NOT the required full installation/data backup. An overlay failure restores prior files and preserves newly added files separately in that checkpoint.

Next change directory to the EXISTING installation, run its Python `-m pip check`, then follow either the OFF local-CLI or ON/refresh-first MCP sequence above. Verify original hashes/IDs/quotes, links/indexes and retrieval. Source replacement never migrates notes automatically. Rollback must restore code/config AND memory from the same pre-migration snapshot; never run older memory code on a v4 layout. Preserve newer work separately.

Migration uses journaled copy-and-redirect writes. Original source/knowledge/history files are preserved byte-for-byte in the selected project. Old paths become navigation-only redirects, excluded from knowledge scanning; they preserve previous citations/wiki links without duplicating facts. The layout marker activates last. Incomplete transactions block cooperating readers until recovery. Old-layout proposals remain private evidence but cannot be replayed.

In this development source, memory disabled exposes **20 tools: 14 file tools and six spreadsheet tools**. Enabled memory exposes **33 tools**, adding 13 memory endpoints. The published v0.4.0 baseline exposed 14/27; its package does not include the spreadsheet extension. No separate tunnel is created. Fresh installations use Archives with project folders directly inside it. Existing configured memory paths/layouts remain compatible; do not move them by hand. memory_projects reports the authoritative archive_root. A source upgrade preserves the configured location rather than silently relocating existing records.

## Retrieval

### Which installation path applies?

| Starting point | What to do |
| --- | --- |
| Fresh v0.4 | Install with --second-brain, review empty initialization, inspect, turn ON/refresh and complete the first-use test below |
| Public v0.2 | Verify full backup; use the separate-source upgrade.py overlay WITH the engine update; enable tools, review initialization/migration and verify unchanged existing files/profile |
| Compatible v0.3 | Verify full backup; preserve the existing memory root/prefix and workflow; overlay the five modules, then review migration of legacy Sources/Knowledge/History |
| Already initialized v0.4 | Do not rerun migration; inspect/retrieve and use ordinary project/archive workflows; any later source upgrade still needs backup/review |

### First-use memory test

Complete the file-operation test in INSTALLATION-A-TO-Z.md first. This test deliberately creates only synthetic material in a clearly named test project. Use a chat with Celious Files selected. Read-only checks do not save notes. Project/archive/supersession previews require review; commits actually write Markdown. ChatGPT may ask for its own confirmations.

1. Ask: “Call memory_projects and memory_inspect. Show the layout version, project names/IDs and any issues.” Expect version 4, separate Celious and Shared Knowledge collections, no incomplete transactions. Fresh notes count is zero. If tools are missing, enable config and refresh; if layout is absent, use reviewed initialization above.
2. Ask: “Prepare memory_project_preview for Installation Demo. Show what would be created; do not commit yet.” Review the new directory/descriptor/index and UUID. Then ask: “Commit that exact reviewed project plan.” Expect committed paths. List projects again and retain the returned demo ID; never guess it.
3. Ask: “Use memory_identify read-only on this exact text: User: The Installation Demo requires portable Markdown. Use the demo project ID. Do not archive.” Expect tentative candidates and saved_to_memory=false. This explicit trigger is reliable; natural automatic selection is not guaranteed.
4. Ask: “For Installation Demo, preview archiving the exact text User: The Installation Demo requires portable Markdown. Source reference: synthetic installation test; completeness: user_supplied. Extract one requirement with exact quote The Installation Demo requires portable Markdown., topic Installation Demo, key format, value Markdown, epistemic accepted, uncertainty Synthetic test requirement only. Show the full plan; do not commit.” Verify the project ID, source text/quote, paths, uncertainty and digest. Then explicitly authorize that exact reviewed commit.
5. Ask: “Search portable Markdown in Installation Demo only; include_shared=false and cross_project=false. Cite the note, original source and quote.” Expect the synthetic active claim, valid provenance and demo project scope. Confirm the files in its Sources/Knowledge folders with File Explorer or paginated read_document. Other project context must not appear.
6. Ask: “Search Installation Demo in the Celious project only with include_shared=false.” It must not retrieve the unrelated demo claim. Multiword lexical terms use OR matching, so unrelated existing matches are possible; judge project IDs/scope rather than expecting zero results in every existing corpus.
7. Ask: “Search portable Markdown across projects explicitly, cross_project=true.” The demo may now appear and must be labelled by project. Shared retrieval is demonstrated by the automated synthetic suite; on a fresh installation shared space is empty until reviewed material is assigned there.
8. Ask: “Prepare another demo archive proposal, then reject its plan with memory_reject; do not commit.” Expect rejection; previously accepted notes remain unchanged. Inspect/retrieve again. Do not test interruption or raw deletion against valuable notes.

The synthetic demo records remain saved unless you separately approve their removal. There is no dedicated project-delete memory endpoint; do not remove just a descriptor or bypass coordinated relationships to clean up. Keep the demo clearly labelled or retain it only in a disposable installation. Never treat this synthetic requirement as real project policy.

### Everyday prompts and operation states

| Goal | Example prompt | State |
| --- | --- | --- |
| Project-only retrieval | “Retrieve the current deployment decisions in project X; exclude shared and unrelated projects; cite sources and uncertainty.” | Read-only |
| Relevant shared context | “Retrieve relevant shared knowledge alongside project X. Label shared results separately.” | Read-only; include_shared=true |
| Shared-only context | “Use the Shared Knowledge project ID as the scope and search the reviewed reusable guidance.” | Read-only |
| Intentional broad search | “Search this topic across projects explicitly and label each result's project.” | Read-only; cross_project=true |
| Identify useful information | “Review this accessible excerpt for potential memory in project X; do not save.” | Read-only candidates |
| Archive | “Archive this supplied excerpt to project X. Show sources/claims, duplicates/conflicts and exact changes before saving.” | Preview, then separately authorized commit |
| Uncertain project | “Queue this excerpt for project-assignment review; do not accept it as knowledge.” | Writes an Inbox candidate, not accepted knowledge |
| Resolve Inbox | “List Inbox, then preview assigning candidate ID to project X; show comparisons before commit.” | Read-only list, reviewed resolution/commit |
| Reject | “Reject proposal/candidate ID. Leave accepted knowledge unchanged.” | Writes review state |
| Update decision | “Archive the supplied new evidence in the same project; flag conflict. Preview superseding old ID with the reviewed new ID and reason; retain history.” | Archive and supersession are separate reviewed commits |
| Inspect evidence | “Run memory_inspect, then read the cited source with pagination and verify the quote and completeness.” | Read-only |

### All memory endpoints

Read-only: memory_projects, memory_search, memory_identify, memory_inspect, memory_inbox. Proposed changes: memory_project_preview, memory_migrate_preview, memory_supersede_preview, memory_inbox_resolve_preview, memory_rebuild_preview. memory_archive_preview proposes an explicit-project archive; omitted routing instead saves an Inbox candidate. memory_commit writes the exact reviewed plan; memory_reject writes rejection state. These 13 endpoints share the existing file policy/tunnel. A preview is not an accepted archive, and an Inbox save is not “nothing written.”

Call memory_projects to obtain the actual stable project ID. Pass project_id to memory_search for the selected project. Legacy search calls transparently use the default project (Celious) plus Shared Knowledge; every result reports its scope. include_shared defaults true and labels shared hits. Set it false for project-only work. cross_project defaults false and must be enabled only for an explicit broader request.

Matching selected-project records are prioritized; allowed shared/cross-project records follow lexical ranking. Search terms use OR matching, not exact multiword conjunction. Filters include topic, note_type and status. Default status is active. Empty status includes source/superseded record states for requested historical context; former History copies remain navigable separately.

Results include evidence, source paths/completeness, uncertainty, epistemic labels and provenance validity. A pending/superseded claim is not an accepted current decision, and an assertion remains an assertion. Related-note traversal does not import another project's text merely because a link exists. Invalid project IDs fail rather than guessing. There is no global mutable active-project setting across chats.

Project separation is a context-quality boundary; it does not revoke the owner's existing raw filesystem access. Those tools can bypass coordinated multi-note operations.

## Proactive identification and Archive to Celious

Server guidance asks ChatGPT to use memory_identify when the active, connector-enabled conversation contains decisions, requirements, preferences, fixes, milestones, lessons or unresolved questions. Supply only actually accessible text. The tool returns bounded exact quote spans, suggested types, speaker/provisional indicators and pending epistemic status, without saving notes.

Local cues are suggestions, not proof of importance or truth. Hypotheses, assistant suggestions and unknown speakers are not automatically accepted facts. Model recognition/tool invocation is best effort; there is no continuous conversation monitor or forced tool call.

Reliable explicit fallback: “Review this accessible conversation for Celious memory in project X.” Archive trigger: “Archive to Celious for project X.” The reasoning client should identify useful material, obtain the project ID, compare the proposal and explain what will be saved/skipped/pending/superseded.

1. Provide actual accessible chat text, export or explicit input. Mark partial, excerpt, user_supplied or complete_export honestly; never infer complete history from a title/summary.
2. Supply reviewed claims_json with string fields type, title, topic, key, value, evidence, epistemic and uncertainty. Optional links contain existing stable IDs. Evidence must match the supplied source exactly.
3. Call memory_archive_preview with explicit project_id. Review proposed contents, expected hashes, warnings and exact digest. Preview is not an accepted archive.
4. With owner authorization covering that exact retention, call memory_commit with the returned digest. Stale, altered, rejected or used plans fail.
5. Call memory_inspect and retrieve the saved note/source before reporting success.

Missing/uncertain project assignment creates a candidate in Inbox, not accepted project knowledge. memory_inbox returns bounded summaries; use existing paginated file reads for full review. memory_inbox_resolve_preview requires candidate ID plus explicit project ID, compares the chosen project's memory and prepares one archival/queue-closing plan. Review and commit separately. memory_reject records rejection and leaves accepted sources/knowledge/history unchanged.

Duplicate/conflict grouping uses project/topic/key. Identical keys in unrelated projects are not contradictions. Duplicate claims are skipped while retaining the new source; different active values become pending review. Shared promotion/cross-project consolidation is never silent. Multi-project material needs reviewed assignments/splits with exact excerpts and honest completeness. No original multi-project archive is retained as shared context without authorization.

## Decision changes

Archive the new source and reviewed replacement in the same project. memory_supersede_preview requires distinct knowledge IDs, matching topic/key, a reason and a replacement that is not epistemically pending. The reviewed plan retains exact prior versions in project History, marks the old record superseded and adds reciprocal links. Cross-project supersession is rejected. A hypothesis cannot silently become an accepted decision.

## Automation boundaries

| Behavior | Mechanism |
| --- | --- |
| Validation, scoped comparison, ranking, queue construction and transactions | Deterministic mechanics after a tool call |
| Identifying important material and choosing identify/preview | Model-dependent guidance in the active supported conversation |
| Explicit review/archive prompt | User-invoked fallback using available tools |
| Accepted archival/supersession | Reviewed exact-plan commit with owner authorization |
| Universal monitoring/inaccessible chat retrieval/guaranteed context injection | Not implemented or promised |

A successful proactive-trigger test demonstrates that session, not universal autonomy. A static imported skill is not assumed installed by a tool refresh. This upgrade adds neither another plugin nor an unverified draft-extension dependency.

## Inspection, indexes and recovery

memory_inspect checks source/candidate hashes, evidence, identity/location conflicts, duplicate/conflicting active claims, wiki links/redirects, indexes and pending review. memory_rebuild_preview deterministically proposes global/project/Inbox index repair; commit its exact digest separately. Pending reviews are surfaced, not silently resolved.

Plans bind the complete canonical Markdown snapshot, including descriptors/indexes/queue, to detect concurrent changes. The existing global process lock serializes cooperating clients. Journals preserve intent, expected hashes and original bytes before writes. Failed writes roll back; new files move to recoverable trash. Empty directories can remain and be reused safely. A hard interruption blocks memory operations until local recovery. Recovery preserves unrelated newer edits and requests local conflict review instead of overwriting them.

Generic raw file readers/writers do not participate in the multi-note lock and may observe intermediate files. Use memory tools for coordinated changes. Application policy is not an OS boundary against same-user software; no independent security audit is claimed.

Complete backups and Git checkpoints remain necessary. Full rollback: OFF/Exit, preserve newer work, verify/extract the independent baseline to a disposable location, restore only intended affected files/shortcuts, then restart and enter the existing key privately if Exit cleared it. Do not overwrite historical backups or unrelated Projects changes. Journals may contain private text and must not be published.

## Local use and Obsidian

```bat
service\.venv\Scripts\python.exe service/second_brain.py projects
service\.venv\Scripts\python.exe service/second_brain.py inspect
service\.venv\Scripts\python.exe service/second_brain.py search "query" --project-id PROJECT_ID
service\.venv\Scripts\python.exe service/second_brain.py plan-migrate
service\.venv\Scripts\python.exe service/second_brain.py recover
```

Other CLI commands: plan-project, plan-archive (private JSON with explicit project_id), plan-supersede, plan-rebuild, identify (accessible text file), inbox, reject and exact digest commit. Config/runtime/root/prefix overrides precede the subcommand for isolated use. Keep private inputs outside source control.

Open the canonical folder as an Obsidian vault when installed. Relative wiki links, project/global indexes and legacy redirects keep navigation portable. No plugin, sync service or hidden settings are required. Actual app navigation is a separate acceptance check. The public package requires no separate viewer.

## Verification

Run test_second_brain.py, test_project_memory.py, test_memory_protocol.py and original file/tray checks only in isolated configured roots. Project tests cover A/B/shared routing, supervised queue/rejection, identification limitations, scoped/cross/shared retrieval, supersession/history, exact plans, index repair, stale descriptors, interruptions, rollback and actual private-baseline migration when available. Public CI uses synthetic fixtures; private-baseline tests explicitly skip when unavailable.

The current protocol test advertises 33 tools and invokes all 13 memory endpoints through initialization, project creation, identification, queue/resolve/reject, archive/commit/search, supersession, inspection and rebuild. A fresh second MCP process retrieves persisted project memory. It uses no real key/tunnel. Actual ChatGPT discovery/triggers require live checks; unit tests do not establish universal model autonomy.

test_installation.py runs real setup in disposable fresh, public-v0.2 and pinned-v0.3 installations with fresh isolated environments, checksum-verified client downloads and pip check. It checks fresh opt-in/off 33/20 discovery, reviewed empty initialization, installation of the pinned public baseline, reviewed source upgrade, preserved config/profile/files and synthetic legacy migration/workflow preservation. No production roots, credentials or shortcuts are used. Git must contain the pinned baseline; CI fetches full history. Run package.py before test_package.py. The complete current-source installer matrix has not been rerun for the spreadsheet extension. See VALIDATION.md for commit-specific historical and current evidence.

Official references: [MCP instructions/tool metadata and testing](https://developers.openai.com/plugins/build/mcp-server), [skills and model-selected activation](https://developers.openai.com/plugins/concepts/skills).
