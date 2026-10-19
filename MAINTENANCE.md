# Celious installation, operation and recovery

Celious is one modular Windows MCP server. The normal path is ChatGPT → authenticated MCP connection → Celious → authorized local resources. The tray manages the connection; no background task supervisor or second daemon is installed. Supervision and durable workflow execution are explicitly invoked by the client.

## Install independently

Use an identified clean source ZIP, its SHA256SUMS.txt and a permanent standalone 64-bit CPython 3.12 runtime with Tcl/Tk, venv and ensurepip. The tested runtime is CPython 3.12.14 on the recorded Windows host; other Windows builds and Python distributions require their own checks. Keep the runtime installed for the lifetime of its virtual environment. The source ZIP does not contain Python or dependencies.

1. Verify the ZIP checksum with `Get-FileHash -Algorithm SHA256`. Extract it to a short permanent directory separate from user data. Keep BUILD-IDENTITY.json and PACKAGE-MANIFEST.json. Deep paths can exceed Windows limits when pip installs dependency resources; use a shorter folder instead of changing system-wide policy.
2. Run Install.cmd using the chosen permanent Python, or invoke its full path with `setup.py --tunnel-id YOUR_TUNNEL_ID --projects YOUR_PROJECTS_PATH --vault YOUR_VAULT_PATH --second-brain`. Quote paths containing spaces. Leave `--second-brain` off to use the 33-tool mode; the integrated mode exposes 46 tools. Setup does not collect a secret. Actual connection identity belongs in private configuration, never Git.
3. Setup creates `service/.venv`, installs requirements.lock.txt without inherited site-packages, verifies dependencies and the tunnel-client download, and generates the private configuration/profile. Run Diagnostics.cmd and review version, packaged commit, build_matches, isolated environment, dependency matches and connection identity validity.
4. Memory discovery does not initialize or migrate knowledge. For an empty archive use the reviewed memory migration/commit flow; for existing knowledge inspect its layout and use the documented reviewed migration only if needed. Never initialize over operational knowledge as a connectivity test.

The normal configuration is `service/config.json`. It defines root aliases, writable policy, direct operations, optional memory, approval mode and existing path aliases. Configure selected data folders, never the application/service directory or its parent. The generated `.runtime/profiles/celious.yaml` defines the matching executable paths. Do not replace an existing operational configuration with the example. See CONSOLIDATION.md and PROJECT-MEMORY.md.

## Start, connect and stop

Open Start-Celious.cmd or its tray shortcut. ON asks for the private runtime credential; enter it locally, never into a chat, command log or report. The tray starts the outbound connection. Keep it running while the authorized ChatGPT connection discovers and calls tools. Use the existing configured ChatGPT application/connector identity; refresh its tool discovery after an upgrade. Source or diagnostic tool counts alone are not live account acceptance.

OFF stops the managed connection/server process tree. Exit also forgets the session credential. Login startup, if deliberately installed, starts the tray OFF. Only one installation should own a connection identity and archive at a time. Do not start a candidate against the operational account before cutover approval.

In local approval mode, mutations require owner-issued time-limited directory scope. For example, `Diagnostics.cmd approve --root Projects --path Acceptance --minutes 15`; review the scope and type APPROVE. `Diagnostics.cmd revoke` revokes scopes. Do not grant an entire data root when a narrow folder suffices. A grant does not bypass read-only roots, path policy, expected hashes or reviewed memory/workflow plans. Legacy client mode remains explicitly supported; it relies on the client's authorization rather than an independent local grant.

## Diagnose and test

Diagnostics.cmd is read-only by default and does not connect, initialize memory or expose credentials. Check build identity, environment, lock matches, configuration validity, tray status age and pending recovery inventories. The existing MCP integration_status endpoint also reports packaged commit, source digest and verified build hashes, allowing a real client to identify the serving build. Static registration and a tray status file do not prove an authenticated ChatGPT call. Detailed startup errors belong in private local logs; redact before sharing.

If startup fails, inspect the retained Python location, virtual environment isolation, dependency lock, identity/profile command paths and private error log. If the connection is absent, confirm the tray is ON and the account connection is refreshed; do not create another daemon to compensate. If writes are refused, check approval expiry, path scope and read-only policy. If memory is recovery-required, renew the intended scope and use the reviewed recovery procedure before further commits.

Use only disposable fixtures for tests. Run service unit discovery, test_package.py, the standalone file/memory/workspace protocol scripts, test_documents.py, tray.py --self-test and test_installation.py. The installation matrix creates fresh environments and may download dependencies. Tests cover DOCX/ODT selective text workflows, ODS/XLSX/CSV/TSV, memory modes, ingestion, recovery and boundaries. See DOCUMENTS.md and SPREADSHEETS.md for format limits. Real ChatGPT acceptance remains a separate stage.

## Upgrade a compatible installation

1. Preserve the existing working installation and collect a current private checkpoint of code, config, profiles, all runtime journals/workflows/trash/backups, canonical memory, data required for restoration, shortcuts and retained Python/environment provenance. Verify archive membership, CRC, hashes and restored bytes. An overlay archive alone is not a full backup. Do not store backup credentials or private data in the public repository.
2. Rehearse the upgrade in a short disposable installation with synthetic data. Confirm the installed lock matches the candidate. A legacy shared or missing-lock environment requires a separate installation and reviewed cutover; do not copy in a lock to bypass the check.
3. Extract the new clean source package to a separate short source directory. From there, preview `upgrade.py --installation EXISTING_PATH --backup-dir PRIVATE_BACKUP_PATH --complete-build`. Review its file hashes. All public package source plus matching build metadata will be installed; private configuration, data, runtime, environment and connection profile are preserved. The backup directory must be outside installation and authorized data roots.
4. With explicit owner authorization, turn the affected installation OFF and verify matching processes have stopped. Apply the reviewed command with `--apply --connection-off`. The flag is a truthful owner confirmation, not a process-killing mechanism. The upgrader verifies the package and lock again, creates an overlay checkpoint and rolls back file replacements on an apply failure.
5. Run diagnostics: the packaged commit and all build hashes must match. Run source-matched isolated tests. Start the tray, reconnect privately and complete actual ChatGPT read/write/document/spreadsheet/memory/workflow/refusal/recovery acceptance using a designated test folder. Record successful calls and failures before declaring production acceptance.

The historical narrow source overlay remains available without --complete-build for its documented compatibility role. It does not constitute an exact complete release installation; diagnostics may identify a stale old package identity after such an overlay. Use complete package mode for an identifiable compatible build. Neither mode changes dependency versions or repairs a shared environment.

## Recover and continue development

For a failed file apply, retain the automatic overlay checkpoint and failure evidence. The upgrader restores original replaced files and moves partially created files into its recovery checkpoint. If acceptance fails after a cutover, stop the candidate, preserve newer user work and logs, and restart the retained installation with its original matching configuration/profile/environment and private credential. Restore shortcuts only if changed. Do not bulk restore older data over newer work, or run old code on a newer incompatible memory layout. Inspect every pending journal and schema compatibility before resuming.

File overwrites have verified original bytes in private backup records; deletion uses recoverable trash. Restore to a disposable destination first when checking integrity. Workflow rollback reverses its guarded filesystem effects; it preserves accepted knowledge and external artifacts and cannot undo external side effects. Memory history, rejected claims and superseded evidence are intentional recovery/context data.

OneDrive synchronization belongs to the existing authenticated OneDrive storage client, not Celious. Celious can operate on authorized local files supplied by that client; remote sync requires its own acceptance. Conversation ingestion accepts supplied exports or handovers, not inaccessible account history. GitHub and other actions require separately authorized clients and artifact receipts; Celious has no arbitrary shell execution endpoint.

Continue development on a dedicated local branch from the deployed commit. Preserve history, keep credentials/private reports/runtime/data outside the allowlist, run relevant tests, build and verify a clean source artifact, and stage before requesting cutover. Publishing, pushing, merging and changing production are separate authorized actions.
