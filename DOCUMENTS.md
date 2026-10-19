# Native document workflows

The existing `write_file` and `edit_file` interfaces now support bounded DOCX and ODT workflows. No extra server or tool is needed. Ordinary UTF-8 and base64 calls retain their behavior.

To create a document, call `write_file` with a `.docx` or `.odt` path, `encoding="document"`, and a JSON string as `content`:

```json
{"title":"Handover","blocks":[{"type":"heading","level":1,"text":"Project"},{"type":"paragraph","text":"Decision: retain evidence."},{"type":"table","rows":[["Item","Status"],["Source","Reviewed"]]}]}
```

Creation supports paragraphs, heading levels 1–6 and rectangular text tables. Recipes are limited to 1 MB, 1,000 blocks and 10,000 table cells; files retain the existing 10 MB limit. ODT whitespace is represented explicitly. Read documents with `read_document`; extraction omits layout, images and comments. DOCX extraction retains its existing body/table presentation.

Use `edit_file` to replace one exact unique occurrence in one paragraph, including ordinary styled runs or table cells. Replacement text inherits the first contributing run's style. Other styles and unmodified ZIP part payloads are preserved. This does not guarantee identical rendered pagination. The optional `expected_sha256` prevents stale writes. Existing files are backed up and replacements are atomic through the existing filesystem policy.

Formatted edits refuse ambiguous matches, multiline replacements, explicit whitespace boundaries, signed or macro-bearing packages, encrypted packages, fields and tracked changes in the target paragraph. ODT replacements use ordinary single spaces. Complex layout editing, PDF generation/editing, legacy Office formats and OCR remain outside this workflow. Unsupported operations fail before saving. Binary transfer remains available for client-generated formats.

The same capabilities work inside durable workflow `write` and `edit` steps. The client must still reason about a document and supply the exact edit. Celious does not execute document macros or arbitrary shell commands.

For a project spanning conversations: create a project with `project_preview`/`memory_commit`, import supplied histories with `ingest_preview`/`ingest_commit`, retrieve `workspace_context`, create a workflow and invoke `workflow_run`. A fresh client can retrieve the same project and workflow IDs and resume. External actions remain explicit client handoffs with artifact receipts. Supervision is explicitly invoked; no background scheduler or autonomous worker is installed.

Run `service/test_documents.py` for native creation, styled edits, extraction, stale-write rejection, backups and recovery. `service/test_workspace_protocol.py` verifies the integrated project workflow across fresh MCP processes, including native documents, spreadsheets, source ingestion and client handoffs. Existing installation, diagnostics, configuration, dependency lock and rollback instructions remain in `CONSOLIDATION.md`.

On Windows systems with legacy path limits, choose a short installation directory. Deep folder names can prevent pip from extracting long dependency paths, including lxml resources. Do not change system-wide path policy merely to install a candidate; use a shorter isolated location and rerun installation checks.
