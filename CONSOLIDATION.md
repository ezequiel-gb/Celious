# Consolidated installation and operational contract

Celious remains one modular Windows application: the tray controls one outbound tunnel and one stdio MCP server. Files enforces root policy; spreadsheets implements typed workbook operations; project memory coordinates canonical Markdown; workflows coordinates durable bounded steps and supplied-source ingestion. There is no additional daemon, database or unrestricted execution service.

## Installation and source identity

Use **Install.cmd**, or an explicitly selected standalone 64-bit Python 3.12 interpreter running `setup.py`. The interpreter must have Tcl/Tk and venv/ensurepip. Setup creates an isolated environment with no inherited site-packages, installs the exact lock, verifies dependencies and the tunnel archive checksum, and generates the profile. It rejects a pre-existing shared environment instead of silently altering it. An interrupted pip bootstrap can be resumed. No secret is collected by setup.

An installation must retain its Python base interpreter. A virtual environment is not a portable standalone Python distribution. Use a permanent independent Python installation, not a transient development cache. Source packages do not include Python or third-party dependencies. Exact package versions are pinned; Python patch, wheel hashes and Windows builds are not universally frozen.

`package.py` emits a manifest and BUILD-IDENTITY.json containing the source commit, dirty state, file hashes and aggregate source digest. Diagnostics validates packaged source against those hashes. A source checkout reports its actual Git commit/dirty state. A missing or mismatched identity is explicit; version 0.6.0 alone does not identify deployed bytes. No publication is implied.

Use a separate permanent installation and environment when upgrading a legacy missing-lock/shared-runtime installation. Keep its original files/environment in place for rollback. `upgrade.py` remains a separate **compatible source overlay**, with lock and OFF guards; it does not replace the launcher, tray, Python or arbitrary private configuration. It installs matching modules/tests/diagnostics and invalidates an obsolete build identity rather than reporting a false match. Do not use it to bypass incompatible environments.

For an existing compatible isolated installation, `upgrade.py --complete-build` from a separate extracted **clean identified source package** installs all allowlisted public source files and their matching manifest/build identity. It verifies every source hash, exact manifest membership, clean commit identity and the installed dependency lock before any apply. It preserves private configuration, profile, user data, runtime and Python environment. The complete package mode includes the supported launcher/tray and tooling sources as part of that verified build; the default narrow overlay retains its historical compatibility contract. Both modes require OFF confirmation, create a verified overlay checkpoint and restore previous files if application fails. See [MAINTENANCE.md](MAINTENANCE.md).

## Configuration authority

`service/config.json` owns authorized roots, writable/read-only policy, direct operations, approval mode, optional second_brain, project bindings and historical read aliases. Keep private values outside Git. An explicit tunnel_id is authoritative; validated legacy profile fallback remains supported. The generated `service/.runtime/profiles/celious.yaml` owns executable command paths. Retain existing identities and aliases when preparing a replacement; do not replace operational config with the example.

Fresh setup defaults to `approval_mode: local`. Existing configurations without that field retain **client** mode for compatibility, and diagnostics labels this explicitly. During a deliberate reconfiguration, supply every desired setup option. Setup is not an automatic migration of arbitrary historical settings. A legacy deployment is prepared with its original policy/aliases and generated new executable paths, then accepted separately.

## Explicit mutation approval

In **local** mode, every direct mutation requires an owner-issued, expiring directory scope. This covers binary/text writes, edits, moves, recoverable deletion/restoration, spreadsheet writes, memory commits and workflow actions through Files. Root/read-only/path/link restrictions and expected hashes still apply. Reads do not require a scope. Scoped approval authorizes the whole described batch/window, not a per-file confirmation.

Run locally, never through a server shell endpoint:

```text
Diagnostics.cmd approve --root Projects --path Example --minutes 15
Diagnostics.cmd revoke
```

The approval prompt displays the root alias, relative scope and duration. Verify the selected folder before typing APPROVE. A blank path explicitly grants the entire selected root; prefer a narrow project directory. Scopes expire after 1–60 minutes. Renewing a scope replaces that scope; other live scopes remain available for multi-root workflows. Revocation invalidates all scopes and blocks subsequent operations; an operation already executing may finish. CLI `--yes` is intended only for owner-controlled local automation/tests. There is no MCP approval-issuing endpoint and private grant storage is outside authorized roots.

For initial memory administration, approve the configured archive directory deliberately. If a multi-step transaction outlives approval, it may enter recovery-required state; renew the same scope and run the documented recovery before further work. Keep sufficient time for the reviewed transaction and recovery. Existing pending proposals, history and data are retained. Local proposal review.py remains a separate explicit owner action.

**Client** mode requires the reasoning client/user's authorization and preserves previous interfaces and automation. Select it explicitly with `setup.py --approval-mode client` only when that trust policy is intended. The server does not independently prove human approval in this mode. MCP annotations and plan hashes alone are not human authorization. Local mode provides an independent local gate, not an OS sandbox: same-user software can alter files and process memory.

## Startup, shutdown and diagnostics

**Start-Celious.cmd** (or its tray shortcut) is the supported operational startup. Login starts the icon OFF. ON requests the private credential; OFF stops the managed process tree; Exit also forgets the session key. Keep only one installation connected to a tunnel/archive. Foreground connect.py is a diagnostic alternative; direct server.py is developer stdio, not a user connection. Legacy PowerShell entry points in older installations are retained for recovery, not preferred startup.

**Diagnostics.cmd** is the primary diagnostic entry point. The tray Diagnostics button uses the same implementation. Default status parses local sources/configuration, dependency metadata, build identity, tray status age and recovery inventories. It does not import Files/Workspace, create directories/locks, append audit records, expose raw errors/logs/credentials or probe the network. Tool counts are static registration evidence, not an authenticated handshake. Log existence is reported; inspect connection logs locally for detailed startup errors before sharing redacted excerpts.

Missing config, lock drift, inherited site-packages, unknown/OFF status, legacy approval mode and mismatched builds are distinct states. Read-only diagnostics is separate from the explicitly mutating approve/revoke commands.

## Preservation, tests and recovery

All 46 existing tool interfaces remain available with memory configured; 33 are registered without memory. Registration does not initialize memory or authenticate external integrations. Supported documents/spreadsheets, extraction-only and formula/data-loss limits remain unchanged. Ingestion needs supplied accessible source; workflows run only when called and cannot undo external side effects or accepted memory.

Run service unit discovery, package tests, standalone file/memory/workspace protocols and test_installation.py in disposable roots. Installer mutation fixtures explicitly select client mode; local-mode tests prove denial, scope/expiry/revocation and preserved operations. Never use operational documents as destructive fixtures. Run both optional-memory modes. GUI/account cutover requires separate acceptance even when all local tests pass.

Before cutover: verify a consistent code/config/profile/shortcut/environment inventory, canonical memory and full private runtime recovery checkpoint. Verify archive CRC, membership, hashes and restored bytes in a disposable folder. Preserve business-data backup coverage separately. An overlay checkpoint is not a complete data/environment backup.

On failed acceptance: stop the replacement chain, preserve logs and newer work, and restart the retained installation with its matching original environment/configuration/profile. Do not overwrite newer user data or run old code against a newer incompatible memory layout. Keep the existing version-4 memory layout; neither discovery nor consolidation requires reinitialization. Do not delete old recovery material. Publication and production cutover are independently authorized actions.
