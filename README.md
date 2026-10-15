# Celious Files for Windows

Celious Files connects ChatGPT to selected local folders through an MCP file server and an outbound OpenAI Secure MCP Tunnel. A Windows tray switch starts and stops the connection without a terminal. Published baseline: v0.4.0. This development implementation reports 0.6.0 and adds integrated project context, incremental supplied-source ingestion, resumable workflows and reviewed client-tool handoffs. No 0.6.0 publication or production deployment is implied.

See [integrated workflows, ingestion and recovery](WORKFLOWS.md) for the complete user procedure, exact limits and platform boundaries. Start each project session with `workspace_context`; inspect actual adapter availability with `integration_status`.

## Second Brain extension

Version 0.4.0 adds physical project collections, stable project identities, explicit project/shared/cross-project retrieval, supervised Inbox routing and quote-backed candidate identification. It preserves v0.3.0 evidence, decision history and recovery. [Project memory setup, migration and limits](PROJECT-MEMORY.md). This development source exposes 14 filesystem, six spreadsheet and thirteen integrated tools (33 total); opt-in memory adds 13 endpoints (46 total) on the same service/tunnel. Identification depends on model/tool invocation; no continuous monitor, paid model API calls or background workers are added.

The default single memory home is Projects/Archives, with project folders directly inside it. Existing explicitly configured roots/layouts remain compatible. Fresh setup: use setup.py --second-brain, then separately review and commit initialization. Existing public v0.2/private v0.3 installations: use the reviewed upgrade.py overlay from a separate source folder, with a verified full backup and actual connection OFF; the engine update is included. [Complete commands and sequencing](PROJECT-MEMORY.md#fresh-installation-and-reviewed-initialization). The public source does not include private notes, reports or operational data.

## Spreadsheet processing

ODS, XLSX, CSV and TSV have typed, bounded inspection, reading, search, controlled editing and explicit data-only conversion through the existing MCP server. See [Spreadsheet operations and limits](SPREADSHEETS.md).

## Start here

1. [Understand the project](PROJECT-EXPLAINED.md): capabilities, components, terminology and limits.
2. [Install from zero](INSTALLATION-A-TO-Z.md): Windows/Python, account/tunnel, folders, credentials, connection and first-use checks.
3. [Enable or upgrade Second Brain](PROJECT-MEMORY.md): separate v0.2/v0.3/fresh paths, reviewed initialization, project retrieval and practical memory prompts.
4. [Troubleshoot and recover](TROUBLESHOOTING.md), read [security boundaries](SECURITY.md), and inspect [actual validation](VALIDATION.md).
5. Developers and maintainers: [architecture](PROJECT-EXPLAINED.md#developer-map) and [permanent release checklist](PUBLISHING.md#permanent-release-standard).

## Does Celious Files cost anything?

**Celious Files itself has no download, installation or subscription fee. It makes no paid AI model API calls. Purchasing API credits is not a step in this setup.** You use your own Windows computer and existing internet connection.

Your **ChatGPT Plus subscription** pays for ChatGPT access, with its normal usage limits. **OpenAI Platform** is where you manage the tunnel connecting ChatGPT to your computer. The **API key** is a private access credential for that connection: creating it is not a credit purchase or a new subscription. Celious uses it for tunnel authentication, not to buy AI responses. ChatGPT and paid model API usage have [separate billing](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform).

**What remains uncertain:** the [official tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) and [API pricing page](https://developers.openai.com/api/docs/pricing), checked on 13 October 2026, do not give a tunnel-specific creation/operation tariff or an explicit zero-charge guarantee. The available evidence does not establish that OpenAI's tunnel service is unconditionally free for every account or forever. This is not evidence that you need to buy API credits.

**Before installing:** check that your account offers the custom tunnel connection and the read/write actions you need. Current official guidance does not establish full Celious read/write access for every personal Plus account. Buying credits does not establish that permission. See the guide's [costs, keys and Plus access explanation](INSTALLATION-A-TO-Z.md#costs-keys-and-chatgpt-plus-access), including how to check billing without making a purchase.

## Installation at a glance

**If you have never used Celious:** [Follow the complete installation guide](INSTALLATION-A-TO-Z.md). It explains how to download this repository, prepare Windows, create your own OpenAI tunnel and key, enter the key privately, connect ChatGPT and verify every file operation. No knowledge of this project's development history is required.

Read [Project explained](PROJECT-EXPLAINED.md) for the purpose and components. You need a Windows x64 computer, Python 3.12 and the account permissions described above. You do not need Git, Codex or n8n.

| I want to… | Open |
| --- | --- |
| Install from scratch | [A-to-Z guide](INSTALLATION-A-TO-Z.md) |
| Understand the project | [Project explanation](PROJECT-EXPLAINED.md) |
| Fix a setup problem | [Troubleshooting](TROUBLESHOOTING.md) |
| Understand access and recovery | [Security boundaries](SECURITY.md) |
| Review actual verification | [Validation record](VALIDATION.md) |

The rest of this README is a compact installation and operation reference. [Architecture, capability status and development priorities](PROJECT-EXPLAINED.md#capability-status-and-development-priorities) distinguish current source from release evidence.

Download this public repository from **Code → Download ZIP**, extract it, and follow the A-to-Z guide. [Repository](https://github.com/ezequiel-gb/Celious).

This repository contains the file server, spreadsheet processing, Markdown vault starter, opt-in project memory and tray controller. It does not provide autonomous workers, task scheduling, arbitrary command execution or repository automation.

## Repeatable installation

1. Install **Python 3.12, 64-bit**, from [python.org](https://www.python.org/downloads/windows/), including Tcl/Tk, pip and the Python launcher. Windows x64 is required. Administrator privileges and PowerShell execution-policy changes are unnecessary.
2. Download or clone this repository into a permanent ordinary local folder, such as `C:\Apps\Celious Files`. Avoid OneDrive placeholders, junctions and symlinks; moving the installation later requires reconfiguration and new shortcuts.
3. In OpenAI Platform, choose the intended organisation and create a tunnel. Associate it with the ChatGPT workspace you actually use. Record its `tunnel_...` ID. Create a restricted runtime secret named **Celious API** with **Tunnels Read + Use**. The name is only a label; do not enter it as the secret. Creating or managing tunnels requires separate **Tunnels Read + Manage** permissions. Verify your account's access using the [official tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).
4. Double-click `Install.cmd`. Enter the tunnel ID when prompted. This creates an isolated Python environment, installs locked dependency versions, downloads official tunnel-client v0.0.16 with SHA-256 verification, prepares a local profile, creates empty authorised data folders and installs Desktop/local shortcuts. It never asks for an API key.
5. Open **Celious Switch** or `Start-Celious.cmd`. Click the switch and paste the actual runtime secret privately into the masked box using Ctrl+V. Wait for green **Connected in the background**.
6. If your account provides the required access, in [ChatGPT Plugins](https://chatgpt.com/plugins) add a custom MCP server, choose **Tunnel**, select your tunnel, configure authentication as required for your own server, review the permissions, and create the plugin. Enable it in your conversation. Follow the current [official connection instructions](https://developers.openai.com/api/docs/guides/custom-mcp-server) and the guide's Plus access check above.
7. Test from ChatGPT: “Use Celious Files to list the configured roots and read Vault/INDEX.md. Create Inbox/celious-check.txt containing hello, read it, edit hello to ready, then delete that test file.” Verify the requested operations succeeded. Only use a disposable test file.
8. Switch **OFF**, request a fresh Celious tool call, and confirm the local connection is unavailable. Switch ON again and retry. Cached answers do not prove availability.

### Choose your own folders

Instead of step 4, open Command Prompt in the repository and run:

```bat
py -3.12 setup.py --tunnel-id tunnel_YOUR_32_CHARACTER_ID_HERE --projects "D:\Work\Projects" --vault "D:\Work\Celious Vault" --shortcuts --startup
```

Replace the example ID with your actual tunnel ID. The defaults are `data/Projects` and `data/Vault` inside this installation. Both roots receive direct read/write access and recoverable deletion. Choose folders deliberately: every ordinary file under them is potentially available to the connected assistant. Select narrow roots, separate from application code and runtime data. Projects and Vault cannot overlap. Existing files and vault starter documents are preserved.

`--startup` installs the tray icon at login **with the connection OFF**. Without it, launch the shortcut when needed. Your key remains only in this application's memory during the session and in the child tunnel client's environment. OFF stops the tunnel; Exit and reboot discard the cached key. There is no stored password and no always-on Windows service.

Optional `--plugin-url https://chatgpt.com/plugins/...` sets the tray's ChatGPT button. Intentional reconfiguration requires `--replace-config`; turn OFF and exit first. Re-run shortcut installation after moving or changing the Python environment. A failed installation can be retried; if configuration already exists, review it and explicitly use `--replace-config`.

## Verification

Use a fresh installation with disposable roots. Tests create and recoverably delete data in the configured Vault; do not point test installations at your production folders.

```bat
service\.venv\Scripts\python.exe service/test_service.py
service\.venv\Scripts\python.exe service/test_tray.py
service\.venv\Scripts\python.exe service/tray.py --self-test
```

These cover the filesystem/tray foundation. For the complete current test organisation, see VALIDATION.md and PUBLISHING.md: legacy/project memory, all 13 memory endpoints, package privacy/integrity and real disposable fresh-install/pinned-v0.2/v0.3 upgrades are also included. The published v0.4.0 baseline recorded 46 passing public unit tests and one intentional private-backup skip. The spreadsheet extension has separate validation; see VALIDATION.md for source-specific evidence and limitations. Installer scenarios repeat relevant suites. No real API key is needed. CI uses dummy IDs, not account connections or secrets.

The current standalone file test copies its server into disposable roots and checks the 33-tool file/spreadsheet mode; it does not use installed project roots or operational memory. The separate memory protocol test checks 46 tools in its own disposable configuration. Reviewed source upgrades refresh the corresponding service tests with the core modules. Existing environments must be qualified separately from the fresh-install dependency lock; see [upgrade and dependency policy](PROJECT-MEMORY.md#upgrade-from-public-v020-or-private-v030).

The installer uses requirements.lock.txt, which records the tested direct and transitive Python dependency versions. requirements.txt describes the six direct dependencies for future deliberate upgrades. Python patch versions, package hashes and the Windows runner image are not frozen; this is a repeatable installation recipe rather than a byte-identical build. See [VALIDATION.md](VALIDATION.md) for the release's actual verification results.

## How the components fit

```text
ChatGPT -> OpenAI tunnel -> hidden tunnel-client -> stdio MCP server -> authorised roots
                              ^
                       Windows tray switch
```

The server supports directory listing, text/document extraction, search, paginated base64 reads, UTF-8/base64 writes, exact-text edits, folder creation, moves, recoverable deletion and restoration. Optional proposed changes can be reviewed locally using `service/review.py`.

PDF, DOCX, ODT, ODS and XLSX reads extract content; they are not OCR or full document-layout editors. Overwriting a rich document should use a valid binary payload. Writes are limited to 10 MB per call. Paths must be relative to a configured root alias. Root deletion, traversal, hidden paths, Windows special paths, symlinks, junctions and hard-linked files are blocked by application policy.

Backups, trash and metadata logs are private local files under `service/.runtime`. Recovery is provided through `restore_deleted`; nonempty-folder deletion requires `recursive=true`. Moving items into recovery storage requires the same volume; a root on a different drive can therefore be read/written but deletion may fail. Test this before depending on recovery across drive boundaries.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md), [SECURITY.md](SECURITY.md) and [PUBLISHING.md](PUBLISHING.md).

## Distribution

This package connects a private server. Publishing its source on GitHub does not itself publish a ChatGPT marketplace plugin. For costs and account access, use the section at the beginning of this README.

Celious source is distributed under the [MIT licence](LICENSE). Preserve its copyright and licence notice. Downloaded dependencies retain their own licences and are not bundled in the source ZIP.
