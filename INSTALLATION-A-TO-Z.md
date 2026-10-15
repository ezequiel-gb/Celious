# Celious Files: installation from A to Z

This guide takes a new operator from an unconfigured Windows computer to a tested ChatGPT connection. Read [PROJECT-EXPLAINED.md](PROJECT-EXPLAINED.md) first for the purpose, architecture and limits.

Published baseline: **v0.4.0**; this is the **0.6.0 integrated development source**. It exposes 33 tools without memory and 46 with memory, including thirteen integrated context/ingestion/workflow/archive tools. For fresh memory setup use setup.py --second-brain, then review/commit initialization as documented in [PROJECT-MEMORY.md](PROJECT-MEMORY.md). That guide gives the public-v0.2/private-v0.3 upgrade and separate OFF-CLI versus ON-MCP migration sequences. [WORKFLOWS.md](WORKFLOWS.md) covers project continuity and recovery. Do not use --replace-config as a source-upgrade shortcut.

All commands below are for **Command Prompt**, unless stated otherwise. Do not paste your API secret into commands, ChatGPT, screenshots, GitHub or these documents. The setup command needs a tunnel ID; the secret belongs only in Celious's masked input window.

## Costs, keys and ChatGPT Plus access

### Six things that sound similar but do different jobs

| Term | What it means for this installation |
| --- | --- |
| ChatGPT Plus | Your existing ChatGPT subscription. Conversations using Celious still have the applicable ChatGPT message/model/tool limits. It is not a balance of API credits. |
| OpenAI Platform account | The account settings used to manage the tunnel and its permissions. Signing in here is separate from choosing to activate paid API billing. |
| API key | A secret access credential, similar in purpose to a password. Celious passes it to the tunnel client to authenticate the connection. Creating a key is not a model request, credit purchase or subscription checkout. |
| Paid model API usage | Software asking an OpenAI model to generate an answer through an API, outside this ChatGPT conversation route. Celious Files does not make those requests. |
| Secure MCP Tunnel | The connection carrying file-tool requests between ChatGPT and the local file service. It is not the AI model answering you. |
| ChatGPT usage limits | The allowances for the ChatGPT features you use. Connecting Celious does not give you unlimited model use or a separate allowance. |

OpenAI documents [separate ChatGPT/API billing](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform), [Plus usage limits](https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus) and [app usage limits](https://help.openai.com/en/articles/11487775-connected-apps-in-chatgpt). Do not confuse this file connection with a different application that calls the model API or implements Sign in with ChatGPT plan sharing.

### Verification, conclusions and unresolved questions

Account/cost evidence was checked on **13 October 2026** for the published v0.2.0 file/tunnel path. v0.4 retains that path and adds no model API usage. These observations are historical account evidence, not a new billing audit or a guarantee for another account.

| Question | Finding and confidence |
| --- | --- |
| Does Celious charge for installing or running its software? | **Verified in this project:** there is no software fee, payment screen, credit purchase or subscription mechanism. Your own computer/internet costs remain yours. |
| Does Celious make paid model API calls? | **Verified by source review:** no model inference endpoint/client is called by the installer, file server or controller. The key is passed to the tunnel client, not to a model API. |
| Does creating a key automatically buy AI usage? | **Reasonable conclusion from the credential-only workflow:** creating a credential is not purchasing credits or requesting a model response. Using it with a separately billable service is a different action. Keep its permissions limited to the tunnel. |
| Are tunnel creation, authentication and operation definitely free? | **Unresolved at the 13 October review:** the [tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) and [pricing page](https://developers.openai.com/api/docs/pricing) did not publish a tunnel-specific tariff or explicitly guarantee zero charges. That evidence does not conclusively classify tunnel traffic as billable or non-billable. Missing pricing is not a permanent free-service promise. |
| Must I buy API credits or add a card? | **No purchase/card step is prescribed here.** The published tunnel prerequisites do not list prepaid credits or a payment method. That does not establish that every account can be provisioned without a billing requirement. If your account asks to activate billing, obtain tunnel-specific clarification before accepting; do not buy credits just to follow this guide. |
| Which allowance does a Celious conversation use? | **Verified product distinction:** ChatGPT conversations remain subject to ChatGPT's allowances; app/provider limits may also apply. **Code-based conclusion:** Celious generates no API model-token usage to debit API credits. This does not settle the separate tunnel-pricing question above. |

OpenAI's [MCP API guide](https://developers.openai.com/api/docs/guides/tools-connectors-mcp) describes model-token billing when developers call MCP through the **Responses API**, with no extra per-tool-call fee in that API flow. Those paid model-request examples are not part of Celious's ChatGPT installation and are not a tunnel-wide pricing guarantee. Do not run them as a connection test.

### Can I use it with my personal Plus account?

The [custom MCP server guide](https://developers.openai.com/api/docs/guides/custom-mcp-server) describes read/write plugins and workspace restrictions but does not provide a Plus-specific entitlement guarantee. The [Help Centre developer-mode guide](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt) currently assigns full MCP write/modify beta access to Business, Enterprise and Edu, and describes Pro read/fetch access. It does not establish full personal Plus support.

The maintainer's personal Plus setup previously completed Celious read/write tests. That is an observation about one account, not a promise that every Plus account has the same access. Confirm that **your** ChatGPT web account offers **Add custom MCP server → Tunnel** and permits the required actions. A visible plugin menu alone is not evidence that editing/deletion is enabled. Finish the disposable read/write test in section 10 before relying on it for real work.

If the connection or write actions are unavailable, check the account/workspace permissions or ask OpenAI Support. Paying for API credits does not grant ChatGPT plugin or write permissions. This guide does not recommend purchasing credits or upgrading your ChatGPT plan to resolve unverified eligibility.

### Check billing and usage without buying anything

1. Sign in to [OpenAI Platform billing](https://platform.openai.com/account/billing/overview). Select the organisation owning your tunnel and review its billing status, payment methods and any existing prepaid/automatic recharge settings. **Viewing this page is a check, not a purchase.** Do not select Add payment method, Buy credits or enable automatic recharge as part of Celious setup.
2. Open the [Usage Dashboard](https://platform.openai.com/usage). Choose that organisation, the relevant date range and project filters; review activity and spend before/after a disposable connection test. Other applications in the same organisation may contribute usage. A zero model-token total does not prove that every possible charge is zero.
3. If those pages are unavailable, ask the organisation owner for a review. Dashboard visibility is a separate permission. See [OpenAI's usage explanation](https://help.openai.com/en/articles/10478918-reviewing-api-usage-and-costs).
4. To review your existing ChatGPT subscription, open **ChatGPT → Settings → Billing**; it is a separate account view. See [OpenAI's billing instructions](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform).

If you see an explicit charge or billing activation requirement that you did not intend, pause before accepting it and ask OpenAI Support about **Secure MCP Tunnel for a ChatGPT connection**, not paid API model access. This documentation cannot inspect your account-specific contract or billing state.

### Required and optional steps

**Required:** supported Windows/Python, selected folders, tunnel permissions/ID, a private runtime key, a working local connection and ChatGPT permission to use it. **Optional:** your own alternative data folders, starting the tray OFF at login, a customised plugin URL and maintainer-only automated tests. **Not prescribed:** buying API credits, adding payment details, enabling automatic recharge, running paid API model examples or taking an additional subscription. If your account presents different prerequisites, clarify them rather than treating an optional purchase as mandatory.

## Before you begin: the whole path

Read the explanation → check Windows and account eligibility → download the source → install Python → choose folders → create a tunnel → create a private runtime key → run Install.cmd → turn the tray ON and enter the key → add Celious Files in ChatGPT → test file operations and OFF/ON.

| Term | What it means here |
| --- | --- |
| Platform organisation | The OpenAI account context that owns the tunnel and grants tunnel permissions |
| ChatGPT workspace | The personal or organisational ChatGPT context where you install the Celious Files plugin |
| Tunnel ID | Identifier beginning with `tunnel_`; setup uses it to select your connection |
| API secret | Private credential beginning with `sk-`; enter it only in the masked connection dialog |
| Root alias | Short name such as Vault that refers to a selected local folder |
| MCP plugin | The installed ChatGPT connection exposing Celious's tools |

You provide three installation-specific inputs: your own tunnel ID, your private runtime key and the folders you want to authorise. The repository deliberately contains no working account credential. If your account cannot use tunnels/custom MCP connections, local installation alone cannot complete the connection.

## 1. Understand what “ready” means

The package is prepared for installation on Windows x64 with Python 3.12. Its local installer and automated checks passed in an isolated installation, as recorded in VALIDATION.md. Complete the acceptance checklist in section 11 to verify your own computer and account.

OpenAI account access is separate from Windows installation. You must be able to create/use your own tunnel and add a custom MCP plugin. Your computer must stay awake, online and connected for local file calls to work. This is a source package with an installer, rather than a standalone signed Windows executable.

## 2. Prepare the computer and installation location

1. Use a Windows **x64** computer and a normal Windows user account that can write to the chosen installation and data folders. ARM64 and 32-bit installations are not validated by this release.
2. Use an ordinary local folder you own. Avoid Program Files, network shares, cloud placeholders, symbolic links and junctions.
3. Make sure internet access allows Python package downloads, GitHub release downloads and the OpenAI connection. On a managed computer, have IT review the requirements rather than changing company restrictions.
4. On this GitHub repository's main page, choose the green **Code** button, then **Download ZIP**. You do not need to create a GitHub account to download a public repository. Alternatively, use a separately supplied `celious-files-source.zip`.
5. In File Explorer, open Downloads, right-click the downloaded ZIP and choose **Extract All**. Extract into a permanent user-writable local folder. Open the extracted top-level folder, usually named `Celious-main` for this repository's GitHub download or `celious-files` for the source package. You should see `Install.cmd`, `Start-Celious.cmd`, `setup.py`, `service` and `assets` together. That is the installation folder. Do not run files inside the unopened ZIP.
6. Keep this folder in its final location. The generated profile and shortcuts use absolute paths. Moving it later requires reinstallation/reconfiguration.

Git, Codex and n8n are not required to install or run this package. A browser and your own ChatGPT account are required for the ChatGPT connection.

**Checkpoint:** the extracted folder contains the source files and is writable by your Windows account.

## 3. Install and verify Python

Use a full **Python 3.12 x64** distribution from [python.org Windows downloads](https://www.python.org/downloads/windows/). If it is already installed, run the verification commands below before downloading anything.

For the traditional Python 3.12 installer:

1. On an official Python 3.12 release page with Windows installers, go to **Files** and choose **Windows installer (64-bit)**. Do not choose source code, ARM64, 32-bit or the embeddable ZIP. [Python 3.12.10](https://www.python.org/downloads/release/python-31210/) is the last full maintenance release with the traditional Windows installer; newer security releases may have different distribution options. It is not the latest security patch. An already maintained full 3.12 distribution can also be used after verification.
2. Open the downloaded installer. Select **Customize installation**.
3. Keep **pip**, **Tcl/Tk and IDLE**, and the **Python launcher** selected. Continue with installation for your user where available. The installer may request approval for its launcher options; follow your computer's normal installation policy.
4. Finish installation, close any old Command Prompt windows and open a new one.

The [official Python Windows installation guide](https://docs.python.org/3.12/using/windows.html) explains these components. Celious's double-click installer currently expects `py -3.12` to work. If you use the newer Python install manager, first install the 3.12 runtime through that manager's documented workflow and run the checks below; installing the manager alone is insufficient.

Open Start, type **Command Prompt**, and open it. Run:

```bat
py -3.12 --version
py -3.12 -c "import struct, tkinter, venv; print('Python bits:', struct.calcsize('P') * 8); print('Required modules available')"
```

Expect Python `3.12.x`, `Python bits: 64`, and `Required modules available`. If `py` is missing, repair/install the launcher and reopen Command Prompt. If tkinter is missing, add Tcl/Tk through the Python installer. A Microsoft Store shortcut that merely offers to install Python is not a working interpreter.

If you have a real Python 3.12 executable but no launcher, substitute its quoted full path for `py -3.12` in setup commands. The installed Celious shortcut will use its private virtual environment directly.

**Checkpoint:** both verification commands succeed before proceeding.

## 4. Plan the folder permissions

This release uses two named roots:

| Alias used by ChatGPT | Purpose | Default location |
| --- | --- | --- |
| Projects | Files you choose to work on | `celious-files/data/Projects` |
| Vault | Markdown notes and durable project context | `celious-files/data/Vault` |

Both receive direct read, write, create, edit, move and recoverable delete permissions. Windows file permissions and application path checks still apply. A request in ChatGPT may also require approval under ChatGPT's own controls; a local setting does not override those controls.

For a first installation, use the empty defaults and add a few disposable sample files. For existing work, choose two specific non-overlapping folders. Back up valuable files before giving an assistant write access. Do not select an entire drive, Windows profile, the application folder or a folder containing keys and passwords. Keep Projects, Vault and the installation on the **same drive** if you need recoverable deletion: recovery uses a rename into private local storage on the installation's drive.

**Checkpoint:** you know exactly which folders will be available and have copies of valuable data.

## 5. Create the OpenAI tunnel

First sign in to [ChatGPT](https://chatgpt.com/) and note whether you are using your personal workspace or an organisation workspace. Then sign in to [OpenAI Platform](https://platform.openai.com/) using the intended account. If you do not have an account, complete OpenAI's own signup first. There is no account registration or purchase inside Celious's installer.

Before continuing, complete the [Plus access and billing checks above](#costs-keys-and-chatgpt-plus-access). Platform must offer the necessary tunnel permissions, and ChatGPT must permit the connection/actions you need. This is an access check, not a recommendation to buy API credits. Names and availability may change; the official guides linked below govern account setup.

1. Sign in to [Platform tunnel settings](https://platform.openai.com/settings/organization/tunnels).
2. Select the intended Platform organisation by its identity. Do not choose an organisation just because it is first in a list.
3. Use the page's **Create tunnel** action. Enter a recognisable name, for example **Celious Files — this computer**, and a description such as “Private access to selected local Windows folders.” Creating/editing requires **Tunnels Read + Manage**.
4. In the tunnel's organisation/workspace associations, include its owning Platform organisation and the ChatGPT workspace you noted above. Select your own workspace when personal accounts are offered; verify its identity rather than copying someone else's workspace ID. Save the associations. If the page creates the tunnel before offering association editing, open its details and edit those associations there.
5. Copy the `tunnel_...` ID. Setup expects 32 lowercase letters/digits after the prefix. Give each computer its own tunnel to avoid competing clients.

If access or workspace association is unavailable, resolve it with the account/workspace administrator before continuing. [Official OpenAI tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

**Checkpoint:** you have your own tunnel ID and the correct workspace association. The placeholder in config.example.json is not a real tunnel.

## 6. Create the private runtime credential

This key proves that the local tunnel client may connect to your tunnel. It is not a request for paid AI answers. Creating it is not purchasing credits or taking out an additional subscription; the unresolved tunnel-pricing/account requirements are explained [above](#costs-keys-and-chatgpt-plus-access). Do not add a payment method or buy credits merely because a key is required.

1. Open [Platform API keys](https://platform.openai.com/settings/organization/api-keys) in the intended organisation/project.
2. Use **Create new secret key** (or the equivalent key-creation action). Name the key **Celious API**. Select the project/account context intended for this tunnel. A project selection is not an instruction to install software with that project's name.
3. Choose **Restricted** permissions and enable the tunnel runtime permissions **Read + Use**. Leave unrelated model/resource permissions disabled. The organisation must also grant the required tunnel access; a key cannot elevate an account that lacks it. If the page uses a different permission editor, use its equivalent tunnel runtime scope and consult the official guide rather than granting all permissions.
4. Create the key and privately copy the secret when shown. Preserve it in storage you control before dismissing the dialog, because the complete secret may not be displayed again. The name “Celious API” is a label; the secret is the long value beginning with `sk-`.
5. Do not use an organisation admin key or enable model inference permissions for this file connection. A project label such as n8n does not add an n8n dependency.

If the required permission is absent, resolve it before connecting. Celious cannot grant itself account access. [Official permissions explanation](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

**Checkpoint:** a suitable runtime secret is available privately. It has not been added to source files or shared in a conversation.

## 7. Install the local software

Choose ONE option before running setup. Options A/B create an installation without memory (33 tools, including spreadsheets). For the complete Second Brain installation, choose Option C instead. Do not run setup again over a configured installation to change its memory mode; use the reviewed existing-installation procedure in PROJECT-MEMORY.md.

### Option A: simplest installation with empty default folders

Double-click **Install.cmd** inside the extracted folder. At `Your tunnel ID (not an API secret):`, paste your tunnel ID and press Enter. Do not enter the secret key here.

The installer creates an isolated environment under `service/.venv`, installs the tested dependency versions, downloads the official tunnel client, verifies its archive checksum, prepares the profile and folder configuration, creates vault starter files, checks the local launcher and creates the **Celious Switch** shortcuts. It does not connect to a live account or ask for the API key.

Wait for **Local installation ready**. The installation window can then close.

### Option B: specify your own folders and optional login icon

Open the extracted `celious-files` folder in File Explorer. Click its address bar, type `cmd`, and press Enter. Command Prompt opens in that folder. Run:

```bat
py -3.12 setup.py --projects "C:\CeliousData\Projects" --vault "C:\CeliousData\Vault" --shortcuts --startup
```

Replace the example paths with user-writable folders on the installation's drive. Setup creates missing folders; it preserves existing vault starter files. Enter your tunnel ID when asked. Omit `--startup` if you do not want an icon at Windows login. Login startup starts the icon **OFF**, not an authenticated connection.

You can instead supply `--tunnel-id YOUR_ACTUAL_TUNNEL_ID` on the command line. A tunnel ID is not the secret. An optional `--plugin-url` can be set later to your plugin's ChatGPT URL.

### Option C: fresh filesystem plus Second Brain installation

Open Command Prompt in the extracted folder as described in Option B. With default folders:

```bat
py -3.12 setup.py --second-brain --shortcuts
```

Enter only your tunnel ID when prompted. To use chosen folders, add the same --projects/--vault options as Option B; --startup remains optional. Expect dependency verification and Local installation ready. Memory tools are enabled, but no notes/layout are silently initialized. Keep the switch OFF and complete the reviewed local CLI initialization in PROJECT-MEMORY.md, or turn ON/connect/refresh first and use its MCP alternative. Continue sections 8–10 to enter the secret privately, install the ChatGPT connection and test file access; then complete the memory first-use test. A fresh --second-brain setup should expose 46 tools; a setup without memory exposes 20.

### If installation fails

Read the first error, resolve it using [TROUBLESHOOTING.md](TROUBLESHOOTING.md), and retry. Python dependencies and the tunnel download need internet access. Do not bypass a checksum mismatch or solve unrelated errors by changing PowerShell execution policy.

If setup says **Already configured**, inspect `service/config.json`. To intentionally rerun setup, turn OFF and exit any Celious tray, then add `--replace-config`, preserving all desired folder arguments. Omitting custom folder arguments during reconfiguration selects the defaults again. Never add a key to config.json.

**Checkpoint:** Local installation ready was printed and the shortcut exists. No live connection has started yet.

## 8. Start the tray and connect

1. Open **Celious Switch** on the Desktop, or double-click **Start-Celious.cmd** in the installation folder.
2. The small Celious panel and tray icon should appear. If the icon is hidden, check the arrow near the clock.
3. Click the switch. In the masked **Celious API key** dialog, paste the actual secret with **Ctrl+V** and confirm. Nothing visible in the field does not imply a failed paste: characters are hidden.
4. Wait for green **Connected** and **Connected in the background**. Amber means it is starting; red means attention is needed. Use **Connection log** to inspect failures locally.
5. Choose **Hide** or close the panel. This hides the panel while the tray remains running. Choose **Exit** from the tray menu to stop everything.

The secret is held in memory for the application session. OFF stops the tunnel but keeps the cached secret for a later ON in that session. Exit, a process restart or reboot requires entering it again. Do not run a foreground terminal launcher alongside the tray for the same tunnel.

**Checkpoint:** green status is visible before you add or discover the plugin in ChatGPT.

## 9. Add the connection to ChatGPT

If your account passed the access check above, use ChatGPT on the web while Celious is green. These steps describe the custom-plugin interface; account/workspace restrictions can limit the available controls or actions:

1. Open [ChatGPT Plugins](https://chatgpt.com/plugins) in the workspace associated with your tunnel.
2. Select **+**, then **Add custom MCP server**.
3. Name it **Celious Files** and choose **Tunnel** under Connection. Select your tunnel or enter its ID.
4. This bundled stdio server has no separate OAuth server; choose **No authentication** for the server interface where offered. The tunnel itself still uses the private runtime credential and OpenAI account permissions. Do not paste that runtime credential into an OAuth field.
5. Review the permissions and risk notice, then create and install the plugin.
6. In a conversation, type **@** and select your installed **Celious Files** plugin.

Workspace restrictions may prevent these steps. Follow the current [official custom MCP instructions](https://developers.openai.com/api/docs/guides/custom-mcp-server) if labels change.

**Checkpoint:** Celious Files is installed, selectable in a conversation and can discover its tools.

## 10. Perform a disposable end-to-end test

Send these requests one at a time in a conversation with Celious Files selected. Wait for a successful tool result at each stage.

1. “Use Celious Files to call list_roots and read Vault/INDEX.md. Tell me the configured root aliases.” Confirm the roots match your selections.
2. “Create Vault/Inbox/celious-install-check.txt containing `hello`.” Verify it appears in File Explorer.
3. “Read that file using Celious Files.” Expect `hello` from a fresh tool call.
4. “Edit that file, replacing `hello` with `ready`.” Open it locally and confirm `ready`.
5. “Move it to Vault/Inbox/celious-install-check-renamed.txt.” Confirm the new name and absence of the old name.
6. “Delete only that renamed test file using Celious Files and return its deletion_id.” Save the returned ID. Confirm the file disappears from its original folder.
7. “Restore that test file using restore_deleted and the deletion_id you returned.” Confirm it reappears. The original location must be unused and its parent must exist.
8. “Delete only the test file again.” Keep the deletion record if you want to retain the test's recovery option.
9. Switch OFF. Ask for a fresh read of Vault/INDEX.md and confirm that the local connection is unavailable. A repeated answer from conversation context is not a successful test.
10. Switch ON and request the read again. Confirm a fresh tool call succeeds.

Do not test deletion with existing valuable files. Recovery data is not the Windows Recycle Bin. If ChatGPT asks for confirmation under its own permissions, complete that review yourself.

## 11. Verify and record your installation

For Second Brain, now follow [reviewed initialization and the complete first-use memory test](PROJECT-MEMORY.md#first-use-memory-test). Confirm 46 tools when enabled, actual project UUIDs, version 4, clean inspection, a reviewed synthetic project/archive and cited retrieval. The filesystem test above remains necessary; a successful memory search alone does not validate editing, recovery or OFF/ON behavior. These account/UI checks are manual; the installer cannot grant ChatGPT access or confirm which tools your model chose.

Fill this table after testing. This is the evidence needed to call your installation ready.

| Check | Result to record |
| --- | --- |
| Windows architecture and Python | x64 and Python version |
| Local installer | Completed successfully |
| Roots | Actual Projects/Vault folders reviewed |
| Connection | Green in the tray |
| ChatGPT discovery | Celious Files selectable and tools available |
| Optional Second Brain | 46 tools, reviewed initialized layout, clean inspection, synthetic project/archive and scoped source citation |
| File operations | Create, read, edit, move, delete and restore passed |
| OFF/ON | Fresh calls fail OFF and work ON |
| Panel close | Connection remains available while panel is hidden |
| Exit | Tray and connection stop; reopening requests the secret |
| Login, if configured | Icon appears OFF |

Keep results private if they include personal paths or account details. For maintainers, the automated verification commands are in README.md. Run those only with disposable configured folders. GitHub checks cannot establish another person's ChatGPT access.

## 12. Use Celious every day

Open the switch, turn ON, enter the key if requested, and select Celious Files in ChatGPT. Begin work by asking it to read the relevant project notes. For durable continuity, explicitly ask it to save decisions and next actions in Vault Markdown and link them from INDEX.md. Files stored on disk provide continuity; Celious does not automatically remember unsaved conversations.

When finished, turn OFF. You can leave the tray available or Exit to discard its cached key. The computer must remain powered, awake and online while you use the connection. Closing the browser does not automatically stop the local tray. An idle green connection remains available but does not autonomously read every file.

## 13. Recover files and protect recovery history

`delete_file` returns a `deletion_id`; use `restore_deleted` with that ID while connected. Recovery storage is `service/.runtime/trash`. Restoring requires the original location to be free and its parent folder to exist. Nonempty-folder deletion needs `recursive=true`, and all contained paths must pass policy checks.

Overwrites produce a separate `backup_id` and save the former contents under `service/.runtime/backups`. There is no backup-restore MCP tool in this release. Turn OFF and exit, inspect the relevant `record.json` locally, copy `original.bin` to a separate recovery location, and verify it before replacing the intended file. Do not ask ChatGPT to access private runtime storage by expanding its roots.

Neither backup nor trash is an independent backup of your disk. Preserve it when migrating or uninstalling if you may need recovery. It can contain sensitive file contents and is intentionally excluded from GitHub uploads.

## 14. Change folders, keys or computers

For a folder/tunnel change, turn OFF, Exit and rerun setup with **all** desired options plus `--replace-config`. Verify the new roots and repeat the disposable test. Old data is not automatically moved. Keep recovery records and the original folders until no longer needed.

For a leaked/replaced key, revoke the old secret in Platform, create a replacement, Exit Celious, reopen it and enter the replacement privately. Editing or deleting a chat message does not revoke a credential.

For another computer, transfer the **source ZIP**, install its own Python environment and create a separate tunnel/runtime credential. Transfer selected project/vault files separately if you want their contents there. Do not copy `.venv`, `config.json`, generated profiles or shortcuts and expect them to work unchanged. Turn off the old connection before retiring the old computer.

## 15. Uninstall without losing your work

1. Turn OFF and **Exit** the tray.
2. Preserve your Projects, Vault and any needed recovery history. The default data folders live inside the installation, so deleting that installation would also delete those files.
3. Remove the **Celious Switch** Desktop shortcut. If startup was enabled, press Win+R, enter `shell:startup`, and remove only the Celious Switch shortcut.
4. Remove or disconnect the Celious Files plugin in ChatGPT. Revoke a dedicated key and remove the dedicated tunnel in Platform when you no longer need them.
5. Once your data is preserved, remove the local installation folder using File Explorer. Other separately configured folders stay wherever you placed them.

Python can remain installed for other software. There is no Celious Windows service, paid model integration or n8n workflow to remove.

## 16. Share the project

Follow [PUBLISHING.md](PUBLISHING.md). Publish the sanitised source package, choose a licence and run the included Windows workflow. Never upload your live installation folder, working vault, API secrets or runtime recovery files. Read [SECURITY.md](SECURITY.md) for the application's actual security boundaries and [VALIDATION.md](VALIDATION.md) for what has and has not been tested.

## 17. Moving an earlier installation

The current desktop controller is **Celious Switch**, the launcher is **Start-Celious.cmd**, the tunnel profile is **celious**, and the repository is [ezequiel-gb/Celious](https://github.com/ezequiel-gb/Celious). Confirm which source version is installed before choosing an upgrade procedure.

Before migrating an existing installation, back up its configuration, vault, recovery storage and shortcuts. Turn OFF and Exit the old tray. Install the new source into a separate permanent folder using the same installation procedure and deliberate folder selections; recreate its Python environment rather than copying or simply moving the old one. Preserve your working files and recovery history before retiring the old installation. Generated profile and shortcut paths must point to the new location.

Renaming a project or a display label does not invalidate its existing tunnel ID or secret key. You can keep the same connection and privately re-enter its existing key after restart. Rename the existing ChatGPT app/Platform display labels if desired; do not change credentials, permissions or associations merely to change the name. If you keep both versions during migration, run only one client for the same tunnel at a time.

## Integrated source and task continuity

This 0.6.0 development source includes thirteen context, incremental ingestion, workflow and archive tools alongside the existing file/spreadsheet/memory interfaces. [WORKFLOWS.md](WORKFLOWS.md) provides installation compatibility, explicit session-start prompts, reviewed import, client-tool handoffs, bounded execution and recovery. Historical validation below does not establish live account acceptance for this source.
