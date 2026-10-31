# Install Celious on Windows

The distribution targets Windows 11, x64. It includes Celious Switch, the service, a dedicated Python runtime and the pinned third-party libraries. No Seelen UI, separate Python installation or Microsoft Office is required.

## Before starting

Prepare two separate data folders, one for Projects and one for your Vault. Keep them outside the extracted installation directory. Choose only folders the assistant should be allowed to access.

The current ChatGPT connection requires an account/client with the supported MCP tunnel setup, a tunnel ID and the associated runtime connection key. Create these through the provider's supported connection flow. Credentials are user-provided; Celious does not create an account or bypass account eligibility requirements.

## Fresh installation

1. Download the Windows x64 ZIP and its SHA-256 checksum from [Releases](https://github.com/ezequiel-gb/Celious/releases).
2. Verify it in PowerShell with `Get-FileHash .\Celious-Windows-x64.zip -Algorithm SHA256`. Compare the result with the release checksum before extracting.
3. Extract the entire package to a permanent folder writable by your Windows account. Keep its directory structure intact.
4. Open a terminal in that folder and run `Configure Celious.cmd`. Enter your tunnel ID and the full paths of your Projects and Vault folders when prompted.
5. Open `Celious Switch.cmd`. The connection starts off. Turn it on and enter the runtime key in the masked dialog. The key is retained only for the running connection session.
6. Connect the corresponding tunnel app in ChatGPT. Ask it to list Celious's tools, list an authorised folder and read a disposable test file before using real projects.

For explicit setup options:

```bat
"Configure Celious.cmd" --tunnel-id tunnel_YOUR32CHARACTERIDENTIFIERHERE00 --projects "D:\Knowledge\Projects" --vault "D:\Knowledge\Vault" --second-brain --approval-mode client --shortcuts
```

Replace the placeholder with the exact valid tunnel ID provided by your account. `--shortcuts` creates Desktop and installation-folder shortcuts. `--startup` optionally adds the tray at Windows login with the connection **off**. These are standard Windows shortcuts; no replacement desktop shell is needed.

The default approval mode is `local`, which requires a time-limited local scope approval for mutations. Choose `--approval-mode client` only when the connected client is trusted to authorise supported changes within both selected roots. This removes the extra local mutation prompt; it does not expand folder access or remove conflict, recovery and format safeguards.

`--second-brain` registers the memory tools. Initialising project memory remains a separate reviewed operation and does not import unrelated conversations automatically.

## Everyday operation

- **Celious Switch.cmd:** show the connection control panel.
- **Diagnostics.cmd:** inspect configuration, installed dependency versions, build integrity and tool inventory without connecting or exposing the runtime key.
- **MCP Server.cmd:** run the local stdio MCP service for a separately tested compatible client. This is a machine protocol, not an interactive terminal application.
- **Approve scope.cmd:** manage a time-limited local grant when using the local approval policy; pass `approve --root Projects --path relative-folder` or `revoke` as required.

Memory and context retrieval require the assistant to invoke the relevant tools. Other AI clients may use MCP, but their connection configuration and full compatibility require separate testing.

## Updates and recovery

Keep a verified copy of the prior package and a private checkpoint of configuration, tunnel profiles, operation recovery records and project memory. Keep credentials out of shared archives.

Extract updates into a **separate** folder. Do not run this fresh-install configurator over an existing installation, and do not delete existing data or runtime recovery records. Qualify configuration and dependency compatibility before a controlled migration. Do not run old and new Switch instances against the same tunnel simultaneously.

Stop the old connection only when ready for the controlled change. Preserve its installation intact until the replacement passes connectivity, file, spreadsheet and memory checks. If acceptance fails, stop the replacement and return to the preserved installation and configuration. Backups of project content remain necessary; per-operation recovery is not a full system backup.

## Troubleshooting

Run `Diagnostics.cmd` and inspect local logs if the connection fails. Check the tunnel ID, folder availability, client/account permissions and runtime key without posting credentials publicly. If a format or integration is unavailable, use the supported formats or configure the integration separately; the explorer is explanatory and does not activate missing account features.

Phone access requires the Windows computer to be awake, online and connected. Turning Switch off prevents remote tools from reaching this local service.
