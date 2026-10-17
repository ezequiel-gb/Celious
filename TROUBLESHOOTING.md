# Troubleshooting learned during setup

Start with **Diagnostics.cmd** (or the tray Diagnostics button). It reports local version/build identity, environment/lock status, static tools, configuration validity, tray status age and recovery inventories without creating application state. OFF is expected unavailability; local status is not live ChatGPT acceptance. For scope-approval refusal, the owner locally approves the intended directory with Diagnostics.cmd approve; do not disable root restrictions. See [consolidated operation](CONSOLIDATION.md).

| Symptom | Resolution in this package |
| --- | --- |
| PowerShell says running scripts is disabled | Use Install.cmd and Start-Celious.cmd. They launch Python directly; changing global execution policy is unnecessary. |
| “No valid key entered” or paste appears to do nothing | Use the masked graphical input, Ctrl+V, and the actual secret beginning with sk-. “Celious API” is its label. The field intentionally hides input. |
| I have Plus; why am I asked for an API key? | It authenticates the private tunnel, rather than paying for an AI model. Creating it is not buying credits. Read the guide's [costs and account explanation](INSTALLATION-A-TO-Z.md#costs-keys-and-chatgpt-plus-access) before creating it. |
| Platform offers Buy credits or asks for payment details | Do not assume this is a Celious requirement. Credit purchases and automatic recharge are not setup steps here. Review the linked billing explanation; if your account requires activation, ask OpenAI for tunnel-specific clarification before accepting it. |
| I have Plus but cannot add the custom connection or use write actions | Check actual account/workspace access. Full personal Plus read/write entitlement is not established by the current official guidance. Purchasing API credits does not grant these permissions. Follow the guide's access check or ask OpenAI Support. |
| I reach a ChatGPT usage limit | Celious conversations still use the applicable ChatGPT allowances; the connection does not create an unlimited allowance. This application does not switch to paid API model calls when a ChatGPT limit is reached. |
| “n8n” appears as a service/project | A Platform project label does not install or require n8n. This program has no n8n dependency. Verify the selected organisation and tunnel permissions. |
| Server executable not found when the folder contains spaces | Setup creates a quoted command with forward-slash paths. Regenerate the profile through setup instead of manually inserting unescaped backslashes. |
| Tray stays Starting | The controller keeps full MCP imports out of the GUI worker thread, initialises COM on WMI threads and prevents concurrent monitoring while the key dialog is open. Inspect service/.runtime/tray-connection.log if the current version still fails. |
| Tunnel absent from ChatGPT | Confirm the tunnel belongs to the intended Platform organisation, is associated with the target ChatGPT workspace and the operator has Tunnels Read + Use. Workspace plugin permissions are separate. |
| Discovery fails | Keep the tray green during discovery. Check the local diagnostic log, authorised roots and installed Python dependencies. Run service/.venv/Scripts/python.exe service/connect.py --check for local checks without a key. |
| Connected terminal closes and tools stop responding | A foreground terminal owns its process. Use the tray shortcut for a hidden managed process. Closing the panel leaves the tray running; Exit stops the connection. |
| Icon is not next to the clock | Look in the Windows hidden-icons arrow and drag the Celious icon onto the visible tray area. |
| Access denied for a path | Use a configured root alias and a relative path. Check writable/read-only flags and whether the path is hidden, linked or outside the root. Cloud placeholders and junctions are not ordinary local folders. |
| Delete fails on another drive | Recovery storage is under service/.runtime. Recoverable rename requires the target and recovery storage to share a volume; use same-volume roots or keep those files undeleted. |
| Old terminal and tray are both running | After successful diagnostics, the tray stops matching clients for this installed executable and tunnel before starting its managed connection. Do not share one tunnel across simultaneous installations. |
| Key was pasted into chat, a screenshot or a repository | Revoke it in Platform, create a replacement with minimal tunnel permissions, exit Celious to forget the old key, then enter the replacement privately. Removing text alone does not revoke a key. |

Review logs locally before sharing: paths and account metadata may appear even when file contents and secrets are omitted. Never upload .runtime, config.json, .env files, copied keys or your working vault.

## Second Brain and upgrade diagnostics

| Symptom | Check and action |
| --- | --- |
| Only 33 tools | Memory is opt-in in the spreadsheet development source. A published v0.4.0 installation without spreadsheets exposes 14. Inspect private config for second_brain; use --second-brain on fresh setup or reviewed upgrade --enable-memory. Restart/refresh discovery. Do not replace existing roots/config with an example. |
| 46 tools but project/layout unavailable | Tools enabled is not initialized. Review plan-migrate/commit while OFF, or use the ON/refresh-first MCP sequence in PROJECT-MEMORY.md. |
| Migration says already initialized | LAYOUT.md is version 4. Do not rerun; list projects, inspect and retrieve instead. |
| Upgrade requires OFF or rejects busy state | Stop actual clients for that installation/tunnel; do not edit tray-status.json to bypass the guard. --connection-off is your acknowledgement, not a stop command. |
| Upgrade rejects dependency lock or customized code | Do not bypass it. Review dependencies/environment and customized module diffs separately; the helper is a source overlay for compatible locks. |
| Stale/rejected/used plan or digest mismatch | Read current notes and prepare/review a new preview. Never substitute a digest or replay old-layout proposals. |
| Incomplete transaction after interruption | Turn OFF; preserve current files/runtime and run the installation's Python service/second_brain.py recover. Inspect afterward. If it reports unrelated edits, preserve both versions and review locally. |
| Unexpected project results | Verify the real project_id, include_shared and cross_project flags; defaults are Celious plus shared. Search is lexical OR matching. |
| Pending/conflicting knowledge | Review original evidence and uncertainty. Explicit supersession requires same project/topic/key and a reviewed non-provisional replacement; never silently promote a hypothesis. |
| Missing or altered source/quote/index | Inspect and preserve evidence. memory_rebuild_preview repairs indexes only through reviewed commit; it cannot invent missing source truth. Restore intended damaged files from a verified consistent backup. |

A current-source connection should expose six spreadsheet tool names plus the 14 filesystem tools, and 13 more when memory is enabled. An older v0.4.0 server exposes 14/27. If schemas stay stale, check installed source, restart through the normal operator procedure and refresh/reconnect the client. A schema listing alone does not prove successful invocation.

## Launcher, dependency and installed-test consistency

- For a legacy config without tunnel_id, the current launcher reads the existing generated profile's control_plane identity without changing configuration. Missing, malformed or duplicate identities require local review; an invalid explicit config identity never falls back silently. Missing plugin_url opens the generic plugin page.
- A missing/different dependency lock blocks the source-only overlay with an actionable error. Review the environment separately; never fabricate a matching lock to bypass this guard. pip check success does not establish equality with pinned versions. Fresh setup uses the lock; reviewed core overlays preserve installed packages.
- Use service test scripts from the same reviewed source overlay as the core modules. The updated standalone file protocol uses a copied server and synthetic roots, independently of installed memory settings. An old exact-14 assertion is not evidence that current 20/46-tool source is broken. Keep launcher and tray deployment separate from a core-only overlay.

## Complete rollback

Keep the connection OFF, preserve post-backup work separately, verify backup hashes and extract into a disposable folder first. Restore code/config and canonical memory from the SAME pre-upgrade snapshot, not a mixture of v0.3 code and v4 layout. An overlay checkpoint alone is not a full data/environment backup. Preserve v4-only/newer files separately instead of deleting them. Follow your manifest paths; do not overwrite unrelated folders or historical backups. Recreate the environment if paths changed, verify dependencies/inspection/roots/profile, then restart and privately enter the existing key if Exit cleared it.

Automated tests exercise rollback/interruption and synthetic migration; the maintainer also tested isolated restoration of a captured baseline. A real production rollback, another account's reauthentication and restoration of Windows ACLs/alternate streams/cloud settings are not claimed as performed. Consult VALIDATION.md before treating a recovery procedure as an executed acceptance check.

Reference: [OpenAI Secure MCP Tunnel troubleshooting](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

## Integrated workflows

Use `integration_status`, `workspace_context` and `workflow_status` to inspect availability, project selection, paused tasks and errors. A missing connector is a client-side limitation; use a supplied artifact rather than claiming account access. Changed inputs/outputs require review and a new plan. For interrupted spreadsheet output, inspect it before exact `workflow_reconcile`; never replay blindly. An edited import stream requires an explicit revision ID. See [WORKFLOWS.md](WORKFLOWS.md).
