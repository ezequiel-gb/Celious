# Publish this source to GitHub

Upload only this source folder, never the live installation's parent folder. The generated source ZIP contains no local configuration, working vault, API keys, runtime recovery data or tunnel binaries.

The project repository is [ezequiel-gb/Celious](https://github.com/ezequiel-gb/Celious). New users should follow INSTALLATION-A-TO-Z.md; these instructions are for maintaining and repackaging the source.

1. Work in the existing development checkout or a source-only branch of this repository. Preserve its Git history and connect it to the intended repository; never initialize another repository over an existing installation.
2. Stage the source, inspect the staged diff and ensure ignored personal files are absent. Do not force-add ignored files.
3. Commit locally and run package.py --check-tracked --check-history 1181f82fd6df5802cf5cc4317dd35ce3f42799b0, package.py --verify --check-tracked, test_package.py, the isolated suites and test_installation.py. Preserve prior commits; inspect all unpublished commit trees, not just the final ZIP. Do not run mutation tests against a production installation.
4. Only after explicit publication approval, push a development branch (never directly overwrite main) and inspect Windows verification for its exact SHA. It fetches history for pinned v0.2/v0.3 source fixtures, installs/checks dependencies, validates package privacy/membership/manifest/checksum and subsequent commit trees, runs real disposable fresh-install/upgrade tests and all file/memory/tray checks. No OpenAI secret is needed. A ZIP alone in the repository does not run CI.
5. Record the actual passing run URL/SHA in VALIDATION.md without presenting historical runs as new evidence. Review the complete PR before approved merge/tag/release steps. Further commits need their own passing checks.
6. MIT is the approved source licence; include LICENSE in the allowlist and preserve notices. GitHub Private Vulnerability Reporting is enabled, without a personal email; use SECURITY.md. Stop after a passing reviewed PR for explicit owner approval before merge/tag/release. Another operator's account/ChatGPT acceptance and optional Markdown application use remain separate checks.

To build the allowlisted ZIP (deterministic for identical source bytes), run `py -3.12 package.py --check-tracked`. It checks likely secrets, personal profile paths, account-specific IDs and email addresses requiring review, rejects linked source files and requires Git tracked paths to equal the allowlist. It includes a generated per-file PACKAGE-MANIFEST.json and writes dist/celious-files-source.zip plus SHA256SUMS.txt. Run `py -3.12 package.py --verify --check-tracked` to check CRC, exact membership, every source byte, privacy rules, manifest and ZIP checksum. Private config/runtime/data/binaries/environments remain excluded. Automated patterns do not identify every possible private datum; review manually too. LICENSE is included in the current allowlist; any future licence changes require deliberate review and package verification.

Local test success does not establish marketplace eligibility or OpenAI access for other accounts. A private tunnel and a public source repository are separate things.

## Permanent release standard

Every Celious update must build on the working implementation, preserve backward compatibility where feasible, retain recoverable development history and provide documentation that an independent beginner can reproduce from a clean Windows environment. This is a standing project requirement, not a one-release exception.

Before every public update, review these existing guides rather than scattering duplicate instructions:

- README: obvious starting point, capability/status summary, version, limits and licence.
- INSTALLATION-A-TO-Z: prerequisites/download/extraction/Python, account/tunnel/credential/folder choices, exact commands, manual versus automatic actions, expected results and complete file/memory first-use checks.
- PROJECT-MEMORY: separate fresh/public-v0.2/compatible-v0.3 paths, OFF/CLI versus ON/MCP sequencing, project/archive/retrieval examples, supervised proposal states and rollback.
- PROJECT-EXPLAINED: component/source/tool/configuration/data formats, provenance, transactions, migration, tests and safe extension guidance.
- TROUBLESHOOTING/SECURITY: diagnosis, recovery commands and evidence limits, permission/credential boundaries and private reporting.
- VALIDATION: candidate-specific local/hosted results, exact CI SHA/run URL, expected skips and explicit unperformed checks.

A release needs executable public fixtures, locked dependency verification, checked package/history privacy and real disposable installation/upgrade coverage that use no private notes, backups, configuration, account credentials or conversation history. A new operator still needs their own account access; do not guarantee identical entitlement or natural proactive invocation.

Preserve the working installation during source publication. Never rewrite/remove old implementation history or upload private recovery material. Push only a reviewed development branch, wait for exact-tip Windows CI, review the real PR diff/checks/mergeability and obtain the owner's explicit merge/release approval. Rebuild/check the final merged source package before attaching it to an approved release. Maintain a versioned source-only checkpoint and a verified private operational recovery baseline separately.
