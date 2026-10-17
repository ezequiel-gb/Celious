# Release validation

## Consolidation validation contract

The consolidation branch preserves the integrated 0.6.0 interface and adds local approval, read-only diagnostics, isolated-environment guards and packaged build identity. Run service/test_stabilisation.py alongside the existing suites and real file/memory/workspace protocols. Installer fixtures explicitly select client approval for automated mutations; local-mode denial/scope/revocation is tested separately. A passing local suite does not establish hosted CI or production account/GUI acceptance. Exact executed results and commit/artifact identities belong to the private delivery report, separate from historical results below.

## Integrated 0.6.0 development source

The new behavioral suite is `service/test_workflows.py`; actual cross-process MCP acceptance is `service/test_workspace_protocol.py`. They cover incremental exports, source/project isolation, reviewed claims, stale plans, competing writes, resumable multi-file work, interruption reconciliation, typed workbooks, client artifact handoffs and reverse recovery. Run both with the locked interpreter after setup, alongside every existing service/package test and `test_installation.py`. Discovery is 33 tools without memory and 46 with memory. No hosted CI or production acceptance is inferred from local checks. Later sections retain historical baseline evidence.


## Historical v0.5.0 candidate baseline

The earlier 0.5.0 candidate `0502d30` follows stabilisation commit `e3e40a7`. Its only application-source change from that baseline was the server version identifier. The 0.6.0 implementation extends that preserved baseline; historical checks below are not evidence for new behavior.

The final candidate must be committed before acceptance. Record its commit/tree and package checksum in a separate validation record, then keep source fixed while running: all service tests, eight package/compatibility cases, standalone file and memory protocols, real fresh/public-v0.2/pinned-v0.3 installers, locked-dependency checks, installed-test matching, documentation links and package/history privacy. The expected public-fixture count is 71 passed and one unavailable-private-fixture skip across 72 unique unit cases; repeated installer executions are not extra cases. These are expected counts until execution is recorded.

Passing earlier source does not certify this exact candidate. Hosted CI, another account, production GUI/startup and actual deployment remain separate acceptance gates. No remote publication or production action is implied. The dated sections below are executed pre-candidate evidence, not a self-certifying candidate result.

## Stabilisation verification — 15 October 2026

The stabilisation branch follows documentation baseline `e4349c5`. Changes are limited to legacy launcher identity resolution, source-matched service tests during reviewed upgrades, safe isolated file-protocol acceptance, an actionable missing-lock refusal and related tests/documentation. The requirements and lock are unchanged. No operational deployment or new capability is implied.

- The existing service suite passed all **64 tests** on Windows/Python 3.12.14 with the available private migration fixture. Public/disposable installations retain its expected skip. The separate memory protocol passed all 13 endpoints across two processes; the standalone file protocol passed with a copied server and 20 tools.
- Focused tests cover explicit configuration precedence, generated-profile legacy identities, consistent quoting, malformed/missing/duplicate refusal, no config/profile rewrite, missing-lock refusal and preservation/refresh of service tests through interrupted/successful overlays. They are part of the eight package/compatibility cases, including existing package privacy/tamper checks.
- All **eight package/compatibility cases passed**. The full disposable fresh/public-v0.2/pinned-v0.3 installation and upgrade matrix passed with locked environments, 20/33 discovery, original config/profile/record preservation, refreshed installed tests, memory migration and actual hidden process-tree shutdown. Repeated installer suites are not additional unique cases.
- Installer acceptance checks that all six service tests match the current source after fresh installation and each supported overlay. It temporarily supplies an unusable synthetic installed configuration and runs the standalone file suite; success proves that the suite uses its own copied server/roots. The synthetic config is restored byte-for-byte.
- Legacy launcher acceptance removes tunnel_id/plugin_url from a disposable configuration, runs the local launcher check and imports the tray, then verifies config/profile preservation. The existing generated profile format was also inspected read-only locally; no account-specific content enters fixtures or source.
- Fresh installation uses the pinned lock. An existing environment can pass functionality and pip check while differing from that lock; this is not lock equality. Source overlays do not alter dependencies, launchers, trays or existing profiles. Missing locks require separate environment qualification, not a fabricated lock or automatic package upgrade.

No new hosted CI, public release, production restart or operational memory mutation is claimed. The following sections retain source-specific earlier evidence and its original limits.

## Pre-stabilisation development verification — 15 October 2026

The inspected implementation is spreadsheet commit `6fdf2f2`, based on published v0.4.0 at `da20c3c`. The documentation consolidation changes no application source or runtime configuration. The spreadsheet extension is local development, not a newly published release; the server version identifier remains 0.4.0. Current discovery is 20 tools without memory and 33 with memory.

- All **64 service unit tests passed** on Windows/Python 3.12.14 using disposable roots. This includes all 20 spreadsheet cases and real calls to all six spreadsheet tools through a copied server. The available private-baseline migration case also ran; public environments without that fixture retain the expected skip. No private fixture is included in source.
- The separate memory protocol check passed across two independent copied-server MCP sessions: 33 tools advertised, all 13 memory endpoints exercised, exact approval rejection/commit, project/shared/cross retrieval, queue resolution/rejection, supersession, integrity, rebuild and persisted fresh-session retrieval. Expected error responses test refusal paths; they are not suite failures.
- Initial sandbox execution blocked hard-link fixture creation and stalled local asyncio protocol startup. The isolated tests were rerun outside that sandbox and passed; the initial partial run is not counted as another successful suite.
- The live connector exposed the six spreadsheet schemas. Read-only inspection and a bounded spreadsheet read succeeded. Live mutation operations, another account's access and automatic model invocation were not tested by this review. Operational inputs and results remain private.
- Published-baseline installation and hosted evidence below is historical. The full fresh/v0.2/v0.3 installer matrix has **not** been rerun for the spreadsheet extension. There is no new hosted CI, tag, release or deployment implied by these local checks.

Documentation links, public source privacy and tracked package membership are checked separately during consolidation. Application files and private project data are preserved. Installed source can differ from release source; source-only tests do not certify every deployed component.

## Published v0.4.0 baseline

The final publication record identifies merge/tag commit `da20c3c`. Its [main Windows run](https://github.com/ezequiel-gb/Celious/actions/runs/38495304393) and [tag Windows run](https://github.com/ezequiel-gb/Celious/actions/runs/38495727487) passed before publication of [v0.4.0](https://github.com/ezequiel-gb/Celious/releases/tag/v0.4.0). These are recorded release results, not new network checks performed during this documentation review. The following dated sections retain the earlier candidate and implementation evidence; statements about pending promotion describe their historical stage.

## Historical v0.4 release candidate

The readiness correction adds explicit memory opt-in (no silent initialization), reviewed public-baseline source upgrade, conditional WORKFLOW creation, package manifest/privacy/integrity checks and real disposable installer coverage. Local acceptance and fresh hosted results are recorded below. The older v0.2 clean-install/runner evidence is labelled historical.

Local Windows x64 / Python 3.12.14 acceptance on 13 October 2026 passed:

- Two real disposable installers, each creating a new virtual environment with system-site-packages disabled, installing the locked dependencies and downloading/checking official tunnel-client v0.0.16. No actual key, live tunnel, shortcuts or production roots were used. pip check passed in both environments.
- Fresh --second-brain setup exposed 27 tools without creating a layout. The OFF/local CLI reviewed initialization created empty project/shared collections and WORKFLOW.md; later MCP inspection passed. Disabling memory returned the original 14-tool schema.
- The pinned public v0.2 source was extracted from Git, actually installed and tested before overlay. upgrade.py preview was non-mutating; ON-state, overlapping-backup and missing OFF acknowledgement were rejected. Apply preserved config fields/roots/tunnel, profile bytes and existing files; original code/config checkpoint CRC and contents were verified. The updated engine was present. Synthetic legacy records migrated byte-for-byte through the MCP alternative, preserving an existing CRLF workflow and valid provenance.
- All suites ran using the freshly installed environment: 3 package/overlay tests, 9 file-policy tests, 4 tray tests, 13 legacy memory tests and 17 project cases. **45 passed, 1 expected private-baseline skip**. Both stdio workflows and actual hidden parent/child shutdown passed. The project suite also ran separately against the available private baseline: all 17 passed, including the private case.
- Package checks validate exact allowlisted membership, source bytes, per-file manifest, ZIP CRC and SHA-256; privacy fixtures and a tampered ZIP are rejected. An interrupted source overlay restores originals and preserves added files; dependency-lock comparison tolerates line-ending differences.
- Python syntax and local documentation file links passed. Source/history privacy checks are repeated at the final commit/package boundary; the package checksum belongs in its generated SHA256SUMS.txt, avoiding a self-referential documentation hash.

The Windows workflow includes dependency verification, package and unpublished-history checks, real fresh-install/public-baseline upgrade coverage and all suites, with a 30-minute limit. Public CI intentionally skips the private baseline and never receives private notes/backups. Real ChatGPT access, model-selected proactive invocation, interactive shortcuts on another computer and Obsidian remain environment-specific checks.

### Fresh hosted Windows v0.4 verification

[Windows run 38466885605](https://github.com/ezequiel-gb/Celious/actions/runs/38466885605) passed on development commit `6110037c7813afeb5b558d9163a536dcc3b49395`. Every test step succeeded: dependency installation/check, 41-file package/manifest/privacy and five subsequent commit-tree scans, real disposable fresh installation/public-v0.2 upgrade, file/tray/memory/MCP suites and hidden process shutdown. Logs confirm 45 passing public-fixture unit cases and one expected private-baseline skip, with repeated suites inside the disposable installation scenario. No real credential or production data was used.

This proves the hosted recipe for that exact source commit, not a general account-access guarantee. Subsequent documentation/source commits and the PR merge ref must pass their own workflow before promotion. Main remains the prior public version until the owner explicitly approves merge; no v0.4 tag/release is implied by a passing development run.

## Historical v0.2 clean installation

Verified on 2026-10-13 on the existing Windows x64 computer using Python 3.12.14, before the memory extension.

- Copied the source into a separate installation directory containing spaces.
- Created a fresh virtual environment with system-site-packages disabled.
- Installed dependencies from PyPI and recorded the complete installed versions in service/requirements.lock.txt. pip check reported no broken requirements.
- Downloaded the official tunnel-client v0.0.16 archive and verified its pinned SHA-256 before extraction.
- Generated a profile using a dummy tunnel ID and newly created disposable Projects/Vault folders. The installer completed its local launcher check without a credential or live tunnel connection.
- Passed all 9 filesystem policy tests and 4 tray lifecycle tests.
- Passed real stdio MCP discovery of 14 tools and create/write/edit/read/move/delete plus denied-path checks.
- Passed the Windows hidden-parent/child Job Object termination check.
- Replaced the original private ODT test dependency with a generated synthetic ODT fixture.
- Scanned the source upload for personal paths, known account identifiers, credential patterns and excluded runtime/data artifacts before packaging.

The working original installation's ChatGPT connection was previously tested separately. This release verification does not use its credentials, tunnel or data. It does not create a new OpenAI tunnel or test ChatGPT account eligibility for another user.

The original operator reported a personal ChatGPT Plus subscription and completed live read/write acceptance tests. This is account-specific evidence, not a guarantee of Plus eligibility. The checks below do not audit an OpenAI billing ledger or establish that tunnel traffic has a zero tariff. The documentation's current [costs and eligibility review](INSTALLATION-A-TO-Z.md#costs-keys-and-chatgpt-plus-access) separates those unresolved questions from verified application behaviour.

## Historical v0.2 GitHub Windows runner

The published repository also passed [Windows verification run 38319770042](https://github.com/ezequiel-gb/Celious/actions/runs/38319770042) for source commit `f5902c9e7fce54c64a3cf189d788213a0365fed1`.

The fresh GitHub-hosted windows-latest environment checked out this repository, installed Python 3.12 x64, ran setup with the locked dependencies and official tunnel download, then passed the 9 filesystem policy tests, 4 tray lifecycle tests, real stdio MCP protocol checks and hidden-process shutdown test. No API secret, live account connection or production folders were used.

This validates local installation on a second Windows environment. Another person's live ChatGPT account/connection and an interactive installation on a second physical PC have not been tested. Desktop/startup shortcut creation is inherited from the previously tested live installation and was intentionally not executed by either disposable installer, to avoid writing interactive user shortcuts during automated verification.
# Second Brain extension verification — 13 October 2026

Local Windows verification of v0.3.0 passed 13 isolated memory acceptance tests, the original 9 filesystem policy tests and 4 tray lifecycle tests. The original real stdio MCP workflow passed with memory disabled (14 tools). An isolated enabled server advertised 19 tools, rejected an incorrect approval digest, archived supplied text and retrieved its evidence through a fresh second MCP process. Hidden parent/child Job Object shutdown passed. No mutation test used production roots or a real tunnel credential.

Memory checks cover exact source/CRLF fidelity, evidence quotes, completeness, duplicate/conflict review, supersession and retained history, retrieval filters/ranking against distractors, nonexistent-result queries, output bounds, stable links, stale plans, failed writes/crash recovery, preservation of unrelated edits, path/read-only boundaries and competing processes. An explicit absence-conflict check protects against a file appearing after preview. Source/quote tampering is detected. These are bounded policy checks, not an independent security audit.

Deployment-specific live connector, account refresh, backup and application checks belong in a private installation report. The prior GitHub workflow results above describe v0.2.0; a v0.3.0 CI run is not claimed. Actual Obsidian navigation and a separate ChatGPT chat require environment-specific acceptance; a second MCP-session test does not establish those by itself.

# Project memory v0.4.0 — local isolated verification

The original 13 memory, 9 file-policy and 4 tray tests remain the regression baseline. The new 17-test project suite covers project spaces/identities, A/B/shared/cross retrieval, correct archive routing, review queue/resolve/reject, duplicate/conflict scope, supersession/history, provisional evidence, index rebuild, exact/stale plans, unrelated destination files, failed operations, hard interruption recovery, legacy byte preservation, isolated restoration to v0.3.0 and competing commit processes. A private verified-baseline migration case runs locally when available and explicitly skips in public environments without that private fixture.

The isolated stdio test advertises 27 tools and exercises all 13 memory endpoints, including supersede preview and rejection. A fresh second process retrieves persisted project data. The original 14-tool stdio workflow and real hidden parent/child shutdown remain tested separately. These checks use disposable roots and no real key or tunnel. Production migration/account refresh and model-selected proactive behavior belong in the private deployment report; unit tests alone do not prove universal tool invocation. No new GitHub workflow run/publication is claimed.


## Local archive organisation correction — 14 October 2026

Fresh memory opt-in now uses Archives with flat project folders. Existing layouts/configured prefixes remain supported. memory_projects reports the authoritative archive_root; server guidance directs conversation retention through the dedicated workflow. Optional read_path_aliases provide validated same-root, read-only compatibility for historical citations and reject writes through old locations. The CLI follows the configured memory root/prefix by default. A new isolated case covers flat collections, reserved names and alias boundary/write denial. This correction is local and not yet validated by a new hosted run; previous hosted success applies to its recorded commit only.

The flat-layout correction passed real disposable fresh-install/public-v0.2 upgrade acceptance locally on 14 October 2026, including CLI initialization, MCP migration and full suites: 46 passed and one expected private-baseline skip. The project suite separately passed all 18 with the private fixture available. Live reorganisation used an independently verified private copy and did not run synthetic mutation fixtures against production. The new read-only alias case verifies historical citation resolution, denied old-location writes and traversal denial.

## Final publication review — 14 October 2026

The follow-up review corrected historical aliases to match whole path segments case-insensitively on Windows, including backslash inputs, without following alias chains or allowing old-location writes. All 18 isolated project cases passed locally with the private fixture available. Documentation now states that CLI defaults follow configured root/path and that source upgrades preserve existing archive locations; the public guide no longer describes a particular private installation.

The real installer scenario passed again with three independent environments: fresh memory opt-in, the pinned public-v0.2 source, and actual v0.3 source at a1cb1890cc0ee93c46dd979d2c79a44ccf9a141f. The v0.3 server first advertised 19 tools and archived synthetic evidence; the source overlay preserved exact custom configuration/profile bytes, then OFF/local CLI migration and 27-tool retrieval preserved all original source/knowledge bytes, custom prefix and CRLF workflow. Fresh initialization, disabled 14-tool discovery, v0.2 upgrade, both stdio workflows, hidden shutdown and fresh-environment suites passed: 46 unit cases passed and one expected private-fixture skip. Repeated installer suites are not additional unique cases.

The Windows workflow now repeats the pinned v0.3 scenario as well as fresh/v0.2 checks. These results are local acceptance; the final pushed commit and PR must pass their own hosted checks. This source review did not redeploy the working installation. Package/history scans are repeated after the final commit, and exact commit/run/checksums are recorded in the owner's private publication report rather than a self-referential package hash.


## Spreadsheet extension validation

The spreadsheet extension adds six tools (20 without memory, 33 with memory).
`python -m unittest discover -s service -p test_spreadsheets.py -v` exercises typed ODS/XLSX/CSV/TSV data,
Unicode, dates, formulas/caches, repeated blank tails, merges, multiple sheets, ranges and pagination,
duplicate/missing/type checks, conversion, edits, injection prevention, verified backup recovery,
atomic failure, malformed input, root restrictions and real MCP calls using disposable roots.
The existing memory protocol suite now copies the spreadsheet module when constructing a temporary server.
Package and upgrade allowlists include it. No new dependencies are required.

Run tests with a short writable TEMP/TMP path on Windows: deep paths can exceed Windows path limits,
and restricted sandboxes may deny the operating-system hard-link fixture in `test_service.py`.
That fixture denial is an environment limitation, not a passing security test. Spreadsheet tests
also exercise the hard-link policy with a synthetic `st_nlink=2` file stat.
Actual-workbook evidence, installation checkpoints and personal data remain outside public source.
See SPREADSHEETS.md for limits, conversion losses, safe writes, rollback and reconnect requirements.
