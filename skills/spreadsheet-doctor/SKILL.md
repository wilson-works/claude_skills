---
name: spreadsheet-doctor
description: "Diagnose and clean messy CSV/XLSX files with a three-phase medical-triage discipline: EXAMINE profiles the file read-only and presents a diagnosis report, PRESCRIBE proposes an explicit numbered cleaning plan that requires your approval before anything changes, TREAT executes via a generated Python script that always writes to a new file (never the original) and accounts for every cell it changed, with an optional SUMMARIZE phase for pivots and aggregates once the data is trustworthy. Invoke with /spreadsheet-doctor [args]."
---

# Spreadsheet Doctor Skill

## Purpose

Turn a spreadsheet you don't trust into one you do — without ever putting the original at risk. Most "just clean this CSV" requests go wrong in one of two ways: the cleaner destroys information silently (stripped leading zeros, collapsed rows, dates coerced that were never dates), or it cleans the wrong things because nobody looked first. This skill borrows the discipline of medical triage:

1. **EXAMINE** — profile the file without modifying a single byte; present a diagnosis
2. **PRESCRIBE** — propose a numbered cleaning plan and get explicit approval
3. **TREAT** — execute via a generated Python script that writes to a NEW file and reports every change per rule
4. **SUMMARIZE** (optional) — pivots and aggregates, once the data deserves them

The order is non-negotiable. Never treat without a prescription. Never prescribe without an examination.

## Configure for your project

Before using this skill, set these placeholders:

- `<scratch-dir>`: directory for generated Python scripts and intermediate output (e.g. `C:\Users\you\AppData\Local\Temp\doctor\` or `~/tmp/doctor/`). Scripts stay here as an audit trail; cleaned outputs go next to the source file.
- `<default-data-dir>`: optional — folder to check first when the user names a file without a path (e.g. `C:\Users\you\Downloads\`).

## Invocation

```
/spreadsheet-doctor <file>                        Full course: examine → prescribe → (approval) → treat
/spreadsheet-doctor examine <file>                Phase 1 only — diagnosis report, zero modification
/spreadsheet-doctor examine <file> --sheet "Q2"   Target one sheet of an XLSX workbook
/spreadsheet-doctor treat <file>                  Re-run treatment using the last approved plan
/spreadsheet-doctor summarize <file> [request]    Phase 4 — pivots/aggregates ("totals by region by month")
```

## Phase 1 — EXAMINE (read-only, always first)

Profile the file WITHOUT modifying it. Do the profiling with a generated Python script — pandas if installed, `csv` + `openpyxl` stdlib fallback — written to `<scratch-dir>` and run with `py profile-<name>.py`.

> macOS/Linux: use `python3` instead of `py`. (Windows uses the `py` launcher because the bare `python` command is often a Microsoft Store stub.)

Collect, at minimum:

1. **Shape** — row count, column count. For XLSX: a full sheet inventory first (name, dimensions, hidden or not, merged-cell ranges) — the user may not know sheet 3 exists.
2. **Encoding** — BOM detection (UTF-8-BOM is Excel's signature move), UTF-8 vs cp1252 vs latin-1; also the delimiter actually in use (comma, semicolon, tab).
3. **Header check** — does row 1 look like headers (short, unique, non-numeric strings) or like data? Never assume. Check for multi-row headers in XLSX.
4. **Per-column profile** — inferred type, null %, distinct %, min/max for numerics, and 3 example values verbatim.
5. **Duplicate candidates** — count of fully identical rows AND near-duplicates sharing likely key columns.
6. **Date-format inventory** — every distinct pattern per date-ish column: `03/04/2025`, `2025-03-04`, `4-Mar-25`, raw Excel serials like `45720`.
7. **Dirt inventory** — leading/trailing whitespace, currency symbols and thousands separators inside "numeric" columns, mixed case in categorical columns, blank-vs-`N/A`-vs-`null` inconsistency.

Present the diagnosis in this format:

```
SPREADSHEET DIAGNOSIS — vendor-payments.csv
============================================
Shape:      4,812 rows x 11 columns | encoding: UTF-8 with BOM | delimiter: comma
Header row: detected (row 1)

| # | Column      | Type (inferred) | Null % | Distinct % | Findings                                        |
|---|-------------|-----------------|--------|------------|-------------------------------------------------|
| 1 | invoice_id  | string          | 0.0%   | 97.4%      | 126 exact-duplicate rows share an ID            |
| 2 | Vendor Name | string          | 0.2%   | 4.1%       | mixed case: "NORTHWIND LLC" vs "Northwind Llc"  |
| 3 | amount      | string (!)      | 1.1%   | 88.0%      | "$1,240.50" — currency symbol + thousands sep   |
| 4 | paid_date   | mixed (!)       | 3.4%   | 41.2%      | 3 formats: MM/DD/YYYY (4102), ISO (512), Excel serial (34) |
| 5 | zip         | int (!)         | 0.0%   | 12.3%      | leading zeros stripped: "7016" should be "07016" |
| … | …           | …               | …      | …          | …                                               |

Duplicates:  126 fully identical rows; 214 more share invoice_id but differ in paid_date
Sheets:      n/a (CSV)
Verdict:     TREATABLE — 6 issues found, none fatal. Prescription follows.
```

The examination NEVER writes to the source file — not even to "fix the encoding so it opens". Read with `errors="replace"` and note the damage instead.

## Phase 2 — PRESCRIBE (plan + explicit approval)

Propose the cleaning plan as an explicit numbered list. Every item names the rule, the columns it touches, and the expected blast radius (rows/cells affected, estimated from the examination):

```
PRESCRIPTION — vendor-payments.csv
==================================
1. Dedupe on [invoice_id + amount + paid_date] — removes 126 identical rows.
   (NOT on invoice_id alone: 214 rows legitimately share an ID across payment dates.)
2. Coerce `amount` to decimal: strip "$" and "," first (~4,760 cells).
3. Normalize `paid_date` to ISO YYYY-MM-DD; convert 34 Excel serials (origin 1899-12-30).
4. Re-type `zip` as string; left-pad to 5 digits to restore leading zeros (~590 cells).
5. Trim whitespace on all string columns (~1,913 cells); Title Case `Vendor Name` (~3,200 cells).
6. Standardize blanks: "", "N/A", "null" → empty cell (~57 cells).
7. Rename headers to snake_case: "Vendor Name" → vendor_name (11 columns).

Output: vendor-payments-clean.csv (original untouched).
Approve as-is, or amend by number ("skip 5", "dates to MM/DD/YYYY instead").
```

**REQUIRE approval — never clean without showing the plan.** The user may drop items, change targets (a different date format, a different dedupe key), or add rules. If the amendment is non-trivial, re-present the revised plan before treating.

## Phase 3 — TREAT (execute, account for everything)

1. Generate the cleaning script at `<scratch-dir>/clean-<name>.py`. Use pandas if `py -c "import pandas"` succeeds; otherwise stdlib `csv` (plus `openpyxl` for XLSX). One clearly labeled block per prescription item, each incrementing its own change counter — the counters ARE the safety mechanism.
2. Run it: `py <scratch-dir>/clean-<name>.py` (macOS/Linux: `python3`).
3. **ALWAYS write to a new file**: `<name>-clean.csv` (or `-clean.xlsx`) next to the original. NEVER overwrite the original — even if the user says "just fix it in place", write the new file and explain that the original is the only ground truth if a rule went wrong.
4. Anything the script cannot confidently convert is left unchanged and flagged — never guessed.
5. Report before/after, per rule:

```
TREATMENT REPORT — vendor-payments.csv → vendor-payments-clean.csv
==================================================================
Rows in: 4,812 → rows out: 4,686 (126 removed by rule 1)

| Rule | Action                    | Changed     | Notes                                 |
|------|---------------------------|-------------|---------------------------------------|
| 1    | dedupe (3-column key)     | 126 rows    | kept first occurrence                 |
| 2    | amount → decimal          | 4,758 cells | 2 unparseable ("TBD") left + flagged  |
| 3    | paid_date → YYYY-MM-DD    | 4,648 cells | 34 Excel serials converted            |
| 4    | zip → 5-char string       | 590 cells   | leading zeros restored                |
| 5    | trim + title-case         | 5,113 cells |                                       |
| 6    | blank standardization     | 57 cells    |                                       |
| 7    | header rename             | 11 headers  |                                       |

Flagged for human review: 2 cells (rows 3117, 4402 — amount "TBD")
Script kept at: <scratch-dir>/clean-vendor-payments.py
```

If any rule's actual change count differs wildly from the prescription estimate (say, 10x), stop and say so before presenting the output as done — that gap usually means the rule matched something it shouldn't have.

## Phase 4 — SUMMARIZE (optional, on request)

Once a clean file exists, answer aggregate questions with quick pivots, scripted the same way. Output as markdown tables in chat, or as a `<name>-summary.xlsx` sheet if the user wants a file. Example: "payments by vendor by quarter" → pivot with row totals, sorted descending, top 20 plus an "all others" tail row. Always state which file the summary came from — the clean one, never the original.

## Gotchas — the classic spreadsheet injuries

| Gotcha | What goes wrong | Treatment |
|--------|-----------------|-----------|
| Excel date serials | `45720` is a date; Excel's 1900 system also believes 1900 was a leap year (serial 60 = the nonexistent Feb 29, 1900) | convert with origin 1899-12-30; treat serials ≤ 60 with suspicion |
| Leading zeros stripped | ZIP codes / IDs read as int: "07016" becomes 7016, irreversibly | read ID-like columns as `dtype=str` from the start — this is why EXAMINE precedes any typed read |
| Currency symbols & thousands separators | "$1,240.50" makes a numeric column string; naive coercion nulls it | strip symbols/separators before coercion; count what failed |
| Locale decimal commas | European "1.240,50" parsed as US-style gives garbage | detect the grouping convention from the data before coercing; never assume period-decimal |
| Mojibake / UTF-8-BOM / Excel-CSV encoding | "Café" arrives as "CafÃ©"; a BOM contaminates the first header name | detect encoding at EXAMINE; read `utf-8-sig`; write BOM-free UTF-8 (or `utf-8-sig` if the user round-trips through Excel) |
| Merged cells & multi-row headers (XLSX) | merged regions read as one value plus blanks; two header rows become junk column names | openpyxl exposes merged ranges at EXAMINE; flatten headers as an explicit prescription item |
| Scientific notation on long IDs | "9780136019701" saved as "9.78014E+12" — the low digits are already gone | `dtype=str` prevents new damage; if already mangled, flag as unrecoverable — never reconstruct digits |
| Trailing whitespace | "Acme " ≠ "Acme" silently defeats joins and dedupe | trim as an EARLY rule so later key-based rules see clean values |

## Failure Modes

1. **Cleaning destroys information silently.** The defense is the per-rule change counter in the treatment report — a rule that "worked" but changed 40,000 cells when the diagnosis predicted 600 is a misfire, not a success. Always report counts; always keep the original untouched.
2. **Dedupe on the wrong key collapses legitimate rows.** One column is almost never a safe key (repeat orders share a customer_id; installment payments share an invoice_id). The prescription must name the key AND say why, with the near-duplicate counts from EXAMINE as evidence. When in doubt, dedupe only fully-identical rows.
3. **Assuming a header row exists.** Headerless exports get row 1 eaten as "headers" and every column named after a data value. EXAMINE's header check is mandatory; if ambiguous, show row 1 and ask.
4. **pandas not installed.** Fall back to stdlib `csv`/`openpyxl` — slower and wordier, but every phase still works. Never make the user install anything to get a diagnosis.
5. **File locked by Excel** (common on Windows). Copy to `<scratch-dir>` and examine the copy; note that treatment needs the file closed so the clean output can be written beside a stable original.

## Important Notes

- **The original file is sacred.** Every output is a new file. If the user wants the clean file to take the original's name, they rename it themselves — after checking it.
- **Scripts are the audit trail.** Keep the generated `.py` in `<scratch-dir>` and name it in the treatment report, so the exact transformation can be re-read or re-run.
- **Estimates before, counts after.** The prescription carries estimated blast radius; the treatment report carries actuals. The comparison between them is where mistakes surface.
- **Flag, don't guess.** An unparseable cell left as-is with a flag is a good outcome. An unparseable cell silently converted to null or to a guessed value is the worst outcome this skill can produce.
- Pairs with: `/file-organizer` (rounds up scattered exports before you treat them), `/sop-writer` (turn a recurring prescription into a standing procedure), `/weekly-review` (fold treatment reports into the week's record).
