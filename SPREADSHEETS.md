# Spreadsheet operations

Celious processes spreadsheets inside the existing local MCP file server. Paths use configured root aliases and relative paths. No additional service, database or network dependency is required. Spreadsheet data is untrusted input. Macros and formulas are never executed or recalculated.

## Formats and dependencies

| Format | Read | Create/edit | Conversion |
| --- | --- | --- | --- |
| ODS | Typed cells, formulas/cached results, worksheets, merged ranges | Data-only rebuild with explicit acknowledgement | XLSX, ODS, CSV/TSV |
| XLSX | Typed cells, formulas/cached results, worksheets, merged ranges | Common native features retained by openpyxl, explicit acknowledgement required | ODS, XLSX, CSV/TSV |
| CSV/TSV | UTF-8 or UTF-8 BOM, quoted fields, empty cells | Data-only | XLSX, ODS, CSV/TSV |
| XLS | Unsupported | Unsupported | Use a trusted spreadsheet application to export XLSX first |

CSV/TSV fields remain strings, including identifiers with leading zeros. Empty fields become empty cells. There is no automatic locale guessing or date/number inference. ODS numeric, date and boolean types remain distinct. ODS times are reported as ISO duration strings. XLSX dates are ISO strings in responses. Styled empty tails are excluded from populated dimensions. The first populated row is the assumed header. Record counts exclude that row and completely blank rows. A blank string stored as an explicit cell can count as populated.

Dependencies remain Python 3.12 and the existing `openpyxl==3.1.5`. ZIP, XML and delimited processing use Python's standard library. No dependencies were added. Install using the existing `setup.py` and locked requirements. The source package allowlist and upgrade overlay include the spreadsheet module and tests.

## Tools

All tools return structured JSON or actionable tool errors. Call `list_roots` before choosing paths. Prefer narrow queries for personal data.

* `inspect_spreadsheet(root, path)`: worksheet names, populated dimensions, cell/record counts, headers with types, formula counts, merged ranges and blank row/column counts. Up to 100 headers and merged ranges are included, with explicit counts/continuation information. Use bounded reads for further headers. Metadata over 200000 characters is rejected.
* `read_spreadsheet(root, path, worksheet?, start_row=1, row_count=100, start_column=1, column_count=30)`: one-based typed cell rectangles, cell addresses, formula text and cached results. Specify a worksheet for multi-sheet files. Follow both `next_row` and `next_column` until the required area is covered. A response is limited to 500 rows, 100 columns, 10000 requested cells and 200000 characters. An oversized request fails explicitly, without silent truncation.
* `search_spreadsheet(root, path, worksheet?, query='', columns?, mode='contains', offset=0, limit=100)`: `contains`, `duplicates`, `missing` or `inconsistent`. Returns coordinates rather than source values. `columns` is a list of one-based integers (up to 100). `limit` is 1–500; follow `next_offset`. Duplicate keys trim/casefold typed values and ignore completely blank keys. Missing checks examine populated data rows. Inconsistency means deviation from the most frequent nonempty cell type per selected column, not semantic validation. CSV/TSV columns remain string typed.
* `convert_spreadsheet(root, path, destination, worksheet?, acknowledge_loss=false, formula_mode='reject')`: creates a new destination only. CSV/TSV conversion of a multi-sheet workbook requires an explicit worksheet. Set `acknowledge_loss=true` only after reviewing the limitations below. `formula_mode='cached_values'` explicitly discards formulas and uses possibly stale or absent cached values. Formula translation is not supported.
* `write_spreadsheet(root, destination, workbook_json, expected_sha256='')`: JSON list of `{name, rows}` worksheets with scalar cell values. Empty digest requires an absent destination. Replacing an existing file requires its current SHA256. Strings always remain literal strings in XLSX. No implicit formulas.
* `edit_spreadsheet(root, path, destination, operations_json, acknowledge_loss=false, allow_formulas=false, expected_sha256='')`: applies controlled operations. Use a new destination by default. In-place replacement requires the current SHA256 and creates a verified recoverable backup. Common XLSX cell styles, formulas and worksheets are retained by openpyxl; feature preservation is not universal. Other formats use a data-only rebuild. All editing requires explicit feature-loss acknowledgement.

The existing `read_document` now extracts ODS and XLSX text with ordinary character pagination. It includes populated row and column coordinates, worksheet names and formula text; use spreadsheet tools for typed values and caches. This reader no longer silently stops at 10000 rows. `read_file_bytes`, `write_file` and all existing operations remain available.

### Examples

```json
{"root":"Projects","path":"Leads/Leads.ods"}
```

Pass that to `inspect_spreadsheet`, then read only the needed rows:

```json
{"root":"Projects","path":"Leads/Leads.ods","worksheet":"Leads","start_row":1,"row_count":20,"start_column":1,"column_count":15}
```

Potential duplicates by email (column 4):

```json
{"root":"Projects","path":"Leads/Leads.ods","worksheet":"Leads","columns":[4],"mode":"duplicates"}
```

ODS to XLSX data transfer:

```json
{"root":"Projects","path":"Leads/Leads.ods","destination":"Leads/Leads-working.xlsx","acknowledge_loss":true}
```

Create `workbook_json` as a JSON string containing:

```json
[{"name":"Leads","rows":[["Name","Status"],["José","New"]]}]
```

For edits, `operations_json` is a JSON string containing:

```json
[
  {"action":"set_cell","sheet":"Leads","row":2,"column":2,"value":"Qualified"},
  {"action":"append_rows","sheet":"Leads","rows":[["Ana","New"]]},
  {"action":"add_sheet","sheet":"Research"}
]
```

Headers and new columns can be written with `set_cell`. A new column does not shift existing columns. To write a formula, use `formula` instead of `value` in `set_cell`, native XLSX source/destination and `allow_formulas=true`. Only local arithmetic and an allowlist of common functions are accepted. Formula caches are not calculated; open in a trusted spreadsheet engine when current results are needed.

## Conversion and preservation limits

Conversions are data transfers, not lossless document conversions. Formatting, charts, comments, macros, validation, names, links and workbook metadata are not transferred. ODS-to-XLSX merged ranges are transferred only when they do not discard populated cells. XLSX names must satisfy Excel's name constraints. ODS data export rejects merged ranges, durations and error cells. CSV/TSV loses typing and all workbook structure. ISO durations/timezones and other unsupported values may be rejected explicitly.

ODS and XLSX formula languages differ. Conversion rejects formulas unless cached-values mode is acknowledged; cached values may be absent or stale. Native XLSX editing retains existing formula text but does not evaluate it. Unsupported openpyxl extensions may be removed, so editing also requires acknowledgement and preferably saves a new working copy. No feature-perfect preservation is claimed. Do not overwrite feature-rich workbooks unless those limitations are acceptable.

## Safety, bounds and recovery

The existing authorized-root policy applies to all reads/writes, including historical aliases, read-only mode, direct-operation mode, path traversal, reserved Windows paths, symlinks, junctions and hard links. No arbitrary paths or shell commands are exposed. Archive content is validated: 10 MB compressed input, 50 MB expanded ZIP, 10000 archive entries, no encrypted/duplicate entries, no DTD/entities, content signatures checked. XML is never extracted to the filesystem.

Each workbook is limited to 256 sheets, 200000 populated cells and 5 million cell/formula text characters. Coordinates are limited to 1048576 rows and 16384 columns. Repeated blank ODS tails do not allocate dense worksheets. Excesses produce errors requiring the source to be split. Bounded responses do not imply streaming parsing of arbitrarily large input. XLSX uses the pinned openpyxl sparse cell collection to avoid iterating inflated dimensions. Delimited/ODS data export has a 200000-cell rectangular bound.

CSV/TSV exports reject strings beginning with formula-like prefixes (including after leading whitespace). XLSX stores imported text as literal strings, including leading `=`, `+`, `-` or `@`. Formula insertion requires explicit permission and blocks external references and non-allowlisted functions. Existing formulas are untrusted and never executed by Celious.

Output is serialized to a temporary sibling, reopened and validated before the existing atomic write is invoked. Writes flush and fsync before atomic replacement. Before replacing a file, the original bytes are backed up and read back for verification. The destination digest is checked immediately before replacement, and the final digest is verified. Failed serialization/validation leaves originals and existing destinations intact. Temporary verification files are removed even on failure. Atomic replacement failure leaves the original destination intact.

Recoverable overwrite backups are under private `service/.runtime/backups/<backup_id>/original.bin`, with `record.json` identifying root, relative path and action. To recover: disconnect Celious; inspect the record and copy `original.bin` to a NEW file with the original extension inside its authorized root; validate that file before replacing anything. To restore the former production state, preserve the current working file first and restore the validated backup. Backups are private and never included in source packages. Audit logs record operation/path metadata, not cell contents. Search responses expose coordinates to avoid unnecessary personal data.

## Deployment, testing and troubleshooting

Stop the connection before overlaying `engine.py`, `server.py`, `spreadsheets.py` and the documentation. Preserve configuration, private runtime, Vault and credentials. Restart using Celious Switch, then refresh/reconnect the ChatGPT plugin if its cached tool schema is unchanged. A new stdio session must enumerate the six spreadsheet tools. Existing running Python processes retain imported modules until restarted. Do not claim live availability from source files alone.

Run the existing unit suites and `python -m unittest discover -s service -p test_spreadsheets.py -v`. Spreadsheet tests cover types, Unicode, ranges, blanks, multiple sheets, merges, formulas, conversion, bounded responses, duplicates/missing/types, injection rejection, permission restrictions, backup recovery and simulated atomic failure. Real MCP integration tests use a copied server and disposable roots. Production acceptance evidence belongs outside the public repository.

If Windows sandbox restrictions prevent using the default temporary directory, set TEMP and TMP to a writable workspace directory for the test process. Malformed/mismatched files, unsupported values, excessive repeats or oversized pages fail with tool errors. Reduce query bounds or split an oversized workbook. Legacy XLS requires external export. The service does not guess a replacement file format or silently discard unsupported data.
