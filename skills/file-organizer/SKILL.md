---
name: file-organizer
description: "Bring order to a messy folder — Downloads, Desktop, a shared-drive dump — with a plan-first, never-destructive discipline: SCAN inventories the folder read-only, PROPOSE presents a fitted taxonomy plus a complete reviewable move manifest that requires your approval, EXECUTE performs the moves via a generated script while writing an undo log and undo script into the folder, and REPORT tells you what moved, what was skipped, and how to reverse everything. Nothing is ever deleted; a maintenance mode re-applies your taxonomy to new arrivals. Invoke with /file-organizer [args]."
---

# File Organizer Skill

## Purpose

Turn a folder nobody wants to open into one that explains itself — without deleting a single file or moving anything the user hasn't seen coming. The failure mode of every "clean up my Downloads" attempt is the same: files vanish into folders the user didn't choose, names get "improved" into meaninglessness, and there's no way back. This skill's discipline:

1. **SCAN** — inventory the target folder read-only; understand what's actually there
2. **PROPOSE** — a taxonomy fitted to the contents plus a complete move manifest; explicit approval required
3. **EXECUTE** — perform moves via a generated script, writing an undo log and undo script as it goes
4. **REPORT** — what moved where, what was skipped, and exactly how to undo

And one standing promise: **this skill never deletes anything.** Suspected junk goes to a `_quarantine/` folder inside the target; only the user empties it.

## Configure for your project

Before using this skill, set these placeholders:

- `<target-folder>`: the folder to organize (e.g. `C:\Users\you\Downloads\` or `~/Desktop/`). The skill NEVER touches anything outside it.
- `<scratch-dir>`: directory for the generated move/undo scripts (e.g. `C:\Users\you\AppData\Local\Temp\organizer\`). Copies of both scripts also land in the target folder for the user's record.

## Invocation

```
/file-organizer <target-folder>              Full pass: scan → propose → (approval) → execute → report
/file-organizer scan <target-folder>         Phase 1 only — inventory report, zero changes
/file-organizer <target-folder> --routine    Maintenance mode: re-apply _organize-rules.md to new arrivals
/file-organizer undo <target-folder>         Reverse the last run using _organize-log.csv
```

## Phase 1 — SCAN (read-only)

Inventory the target folder without changing anything. Collect:

1. **Counts by extension** — grouped into families (images, documents, spreadsheets, archives, installers, media, code, other)
2. **Age distribution** — this week / this month / this year / older, by file count and total size
3. **Size outliers** — the 10 largest files; anything over ~500 MB called out individually
4. **Obvious groups** — screenshots (`Screenshot 2026-…`, `Screen Shot…`), invoices/statements (name + PDF heuristics), installers (`.exe`, `.msi`, `.dmg`, `.pkg`), fonts, exports (`.csv`/`.xlsx` with datestamps)
5. **Duplicate candidates** — same size AND near-identical names (`report.pdf` / `report (1).pdf` / `report - Copy.pdf`)
6. **Skip list** — hidden/system files, files currently open or locked, and anything that looks structural (app folders, `.ini`/`.lnk` at folder root) — counted and listed, never touched

Present the inventory:

```
FOLDER SCAN — C:\Users\you\Downloads (read-only)
================================================
Files: 1,347 | Size: 24.8 GB | Oldest: 2023-08-14 | Newest: today

| Family       | Count | Size    | Notes                                    |
|--------------|-------|---------|------------------------------------------|
| Images       | 512   | 3.1 GB  | 214 screenshots; 61 look like duplicates |
| Documents    | 298   | 1.2 GB  | 44 PDFs match invoice/statement patterns |
| Installers   | 87    | 9.4 GB  | .exe/.msi — will be SKIPPED by default   |
| Archives     | 66    | 6.2 GB  | 3 files over 500 MB                      |
| Spreadsheets | 59    | 0.3 GB  | 31 datestamped exports                   |
| Other        | 325   | 4.6 GB  |                                          |

Age: 62% older than 6 months | Skip list: 14 hidden/system, 2 locked (in use)
Duplicate candidates: 61 pairs (same size + similar name)
```

## Phase 2 — PROPOSE (taxonomy + manifest + approval)

**Fit the taxonomy to what's actually there** — never a generic template. A Downloads full of screenshots and invoices gets `Screenshots/`, `Invoices/`, `Installers/` (skipped but acknowledged); a shared-drive dump of exports gets `Exports/2026/`, `Reports/`. 4–8 top-level destinations is the sweet spot; propose subfolders only where a group exceeds ~50 files.

Then the **complete move manifest** — every file gets a row: destination, and a rename where the current name is garbage (`IMG_4821 (3) copy.png` → date-content pattern like `2026-05-14-whiteboard-photo.png`). Present as a reviewable table. If the manifest is huge, summarize by group first and expand any group on request — but the full manifest must exist and be available before approval:

```
PROPOSED ORGANIZATION — 1,331 files to move, 16 skipped
=======================================================
Screenshots/     214 files   rename to YYYY-MM-DD-HHMM-screenshot.png
Invoices/2026/    44 files   keep names
Exports/          59 files   keep names
Archives/         66 files   keep names
_quarantine/      61 files   duplicate candidates — REVIEW THEN EMPTY YOURSELF
(unmoved)         87 files   installers skipped by default (--include-installers to override)

Sample rows (full manifest on request, or per group: "show Screenshots"):
| File                        | → Destination   | → New name                        |
|-----------------------------|-----------------|-----------------------------------|
| Screenshot 2026-05-14 at…   | Screenshots/    | 2026-05-14-0932-screenshot.png    |
| inv_98214_final (2).pdf     | Invoices/2026/  | (unchanged)                       |
| IMG_4821 (3) copy.png       | Screenshots/    | 2026-04-02-1544-screenshot.png    |

Approve, or amend: "leave PDFs alone", "no renames", "quarantine nothing".
```

**Explicit approval required.** The user can amend by group or by rule ("leave PDFs alone", "screenshots keep original names"). Re-present the summary after amendments. No approval, no move — ever.

## Phase 3 — EXECUTE (script + undo log)

1. Generate the move script from the approved manifest into `<scratch-dir>` (PowerShell on Windows, bash on macOS/Linux; a Python variant run with `py` is fine too — macOS/Linux would use `python3`).
2. The script, for every file: create the destination folder if needed, move, and append a row to the **undo log** at `<target-folder>\_organize-log.csv`:

```
timestamp,original_path,new_path
2026-07-02T14:31:07,C:\Users\you\Downloads\IMG_4821 (3) copy.png,C:\Users\you\Downloads\Screenshots\2026-04-02-1544-screenshot.png
```

3. Generate the **undo script** alongside it (`_organize-undo.ps1` / `_organize-undo.sh`) — it replays the log in reverse, restoring every file to its original path and name.
4. Collision handling: destination already has that name → append ` (2)`, ` (3)`, … — NEVER overwrite.
5. Locked/open files: skip, log as skipped, keep going. Report them at the end.
6. First run also writes `_organize-rules.md` into the target folder: the approved taxonomy, the rename patterns, and the skip rules — in plain markdown the user can edit.

## Phase 4 — REPORT

```
ORGANIZE COMPLETE — C:\Users\you\Downloads
==========================================
Moved:        1,268 files into 6 folders
Quarantined:  61 duplicate candidates → _quarantine\  (review, then empty it yourself)
Skipped:      87 installers (by rule), 14 hidden/system, 2 locked (OneDrive sync in use)
Collisions:   3 renamed with " (2)" suffix

Undo:         _organize-log.csv (full record) + _organize-undo.ps1 (run it to reverse everything)
Rules saved:  _organize-rules.md — next time, run /file-organizer <target-folder> --routine
```

## Maintenance mode — `--routine`

This is how the skill grows with the user. If `_organize-rules.md` exists in the target folder:

1. SCAN only files not covered by the last log (new arrivals since the last run).
2. Apply the stored taxonomy; anything that matches no rule goes to the manifest under `(unmatched — needs a rule?)`.
3. Present the (much shorter) manifest for approval — routine runs still require it, they're just fast.
4. If unmatched files show a recurring pattern (three or more of a kind), propose a new rule and append it to `_organize-rules.md` on approval. Rules are earned by evidence, not invented up front.

## Hard Rules

| Rule | Enforcement |
|------|-------------|
| Never delete anything | there is no delete step in the generated script; junk/duplicates go to `_quarantine/` and only the user empties it |
| Never touch hidden/system/locked files | skip + report; the scan builds the skip list before the manifest exists |
| Never overwrite on collision | ` (2)` suffix, always |
| Never leave the target folder | every destination path is validated to be inside `<target-folder>` before the script is generated |
| Never move without an undo trail | the log row is written per file as part of the move, not after the batch |

## Failure Modes

1. **Moving files apps expect at fixed paths.** Installers, portable apps, anything an application dropped for itself. Defense: `.exe`/`.msi`/`.app`/`.dmg`/`.pkg` are skipped by default (user must opt in with `--include-installers`), and folders that look like an app's own structure are skip-listed at SCAN.
2. **Breaking shortcuts and links.** `.lnk`/`.url` files and anything a shortcut points at may break when moved. Move shortcuts last, flag them in the report, and never rename them.
3. **Renaming loses meaningful metadata.** `IMG_4821` might encode a sequence the user cares about. Defense: the original name is preserved forever in `_organize-log.csv`, renames are shown in the manifest before approval, and "no renames" is a one-word amendment.
4. **A 4,000-file manifest nobody reads.** An unread approval is no approval. Defense: summarize by group with counts and rename patterns; expand any group on request; call out the weird rows (huge files, old files, unmatched patterns) individually rather than burying them in row 3,207.
5. **Sync-folder churn** (OneDrive/Dropbox/Drive). Files mid-sync show as locked — skip and report rather than fighting the sync client; suggest re-running `--routine` later.

## Important Notes

- **Quarantine is the user's decision, twice.** Once when approving the manifest (what goes in), once when emptying the folder (what actually leaves the disk). The skill never takes the second step.
- **The undo script must be tested logic, not decoration.** It replays the log newest-first so nested moves reverse cleanly. If a run was partial (locked files, interruption), undo still works — it only reverses rows that exist in the log.
- **`_organize-rules.md` belongs to the user.** It's plain markdown in their folder; they can edit rules by hand and `--routine` will honor the edits.
- **One folder per engagement.** Asked to also do a second folder, run the full discipline there separately — never generalize approval from one folder to another.
- Pairs with: `/spreadsheet-doctor` (treat the CSVs you just filed under `Exports/`), `/weekly-review` (run `--routine` as part of the weekly sweep), `/notetaker` (capture folder conventions worth remembering).
