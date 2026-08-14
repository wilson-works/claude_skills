---
name: cleanup-stale
description: Survey-and-prune stale scratch artifacts from the project root, the `.claude/` orchestration directory, and the shared `d:\tmp` scratch dir. Two-phase pipeline -- Phase 1 produces a dated cleanup manifest (read-only, never deletes), Phase 2 applies the manifest after explicit founder approval. Models on the 2026-05-17 manual cleanup precedent. Targets: marathon screenshots, brief-*.json scratch, cdp-*.js debug scripts, marathon-*.mjs helpers, archived marathon state JSON, final-summary markdown reports, work-lobby council reports, extracted archive directories, and d:/tmp scratch. Never touches comms.db, agents/, hooks/, settings*, ORG-INDEX, the current marathon-org-state.json, playbooks/, councils/, crew/, or any worktree with uncommitted work. Invoke with /cleanup-stale [--apply] [--age-days N] [--area <name>] [--include-tmp] [--dry-run]. Default is survey-only.
---

# Cleanup Stale -- Project + .claude/ scratch sweeper

The project root and `.claude/` directory accumulate scratch artifacts from every marathon, council, work-order run, and one-off debug session: chrome devtools scripts, brief JSONs that fed completed work orders, screenshots taken for verification long after the verification was done, archived marathon state from finished runs, and final-summary markdowns that were already promoted to backlog/completed. None of it is harmful, but it bloats the directory and obscures what's actually live.

This skill runs a two-phase cleanup. Phase 1 is a read-only survey that produces a dated manifest. Phase 2 applies the manifest under founder review.

## The two-phase contract

**Phase 1 (default, safe):**
1. Walk every target directory.
2. Classify each candidate as `safe`, `ambiguous`, or `protect`.
3. Write a single markdown manifest to `.claude/cleanup-manifest-YYYY-MM-DD.md` with a parallel JSON sidecar `.claude/cleanup-manifest-YYYY-MM-DD.json`.
4. Print a chat summary: counts, sizes, top-10-by-size, and the path to the manifest.
5. **Nothing is moved or deleted.** The founder reviews offline.

**Phase 2 (`--apply`, destructive):**
1. Read the most recent manifest in `.claude/cleanup-manifest-YYYY-MM-DD.json`.
2. Delete only the entries flagged `safe`. Ambiguous and protected entries are skipped.
3. Append a `cleanup-applied-YYYY-MM-DD.md` log next to the manifest with what was removed and total bytes freed.
4. Never run Phase 2 without an explicit `--apply` flag from the founder. If the latest manifest is older than 3 days, refuse and ask for a fresh survey.

## Scope -- five areas

### Area 1: `.claude/` root scratch

Watched patterns (`safe` if matched AND mtime > age threshold):
- `brief-*.json` -- work-order briefs from completed marathons
- `cdp-*.js` -- chrome devtools manual debug scripts
- `complete-wo.js`, `marathon-brief-update.mjs`, `marathon-complete-item.mjs`, `marathon-queue-builder.mjs`, `marathon-frontend-queue-builder.mjs`, `marathon-stale-cleanup.mjs` -- marathon helper scripts (regenerate from skill on demand)
- `marathon-current-item.txt` -- pre-cleared marathon scratch
- `marathon-org-state.archived-*.json` -- archived marathon state (already gitignored)
- `marathon-*-final-summary.md` -- final-summary markdowns from completed marathon runs
- `work-lobby-council-*.{md,html}` -- old council reports
- `cleanup-manifest-*.{md,json}` older than 30 days -- prior cleanup manifests
- `*.png` at `.claude/` root -- marathon QA screenshots (matches `marathon-*.png`, `stream-*-*.png`, `bug*-*.png`, `comms-viewer-*.png`)

Protected (never touched):
- `comms.db`, `comms.db-shm`, `comms.db-wal`, `comms/` -- live agent comms bus
- `agents/`, `hooks/` -- definition surfaces
- `settings.json`, `settings.local.json` -- harness config
- `ORG-INDEX.md` -- org topology
- `marathon-org-state.json` (current, not archived) -- live orchestration state
- `playbooks/`, `councils/`, `crew/`, `marathon-briefs/` index files, `marathon-J/` and any other named-run subdir with recent (<14d) activity
- `scheduled_tasks.lock`

### Area 2: `.claude/screenshots/` and `.claude/marathon-screenshots/`

If the directory exists and every file is older than the age threshold, mark the whole directory `safe`. Otherwise mark each file individually.

### Area 3: `.claude/marathon-briefs/` stale briefs

Match `*.json` and `*.txt` files older than the age threshold. The directory itself stays.

### Area 4: `.claude/archive/workday/_*` internal scratch

The workday archive keeps run summaries, but the per-run `_*.py`, `_*.json`, `_*.txt`, `_*.b64` internal scratch from the cleanup-manifest generator (`_area1.json`, `_assemble.py`, etc.) is `safe` once the parent run is >7 days old.

### Area 5: `d:\tmp` shared scratch (opt-in with `--include-tmp`)

Skipped by default because `d:\tmp` is shared across all projects. When the flag is set:
- Match scrub patterns from the 2026-05-17 manifest: `ftr*-brief.*`, `brief-ftr*.js`, `*-snapshot.txt`, `append-*.mjs`, `backlog-close-*.js`, `bug*-patch.diff`, `bug*-brief.txt`, `autoclose-*.js`, `auto-close-*.js`, `apply-url-replacements.js`, `archive-stale-*.js`, `analyze_mapping.py`, `write-brief-*.js`, `partb_*.py`, `partc_*.py`, `partd_*.py`, `rebuild_playbook.py`, `build-marathon-state.js`
- Plus age-only classification for unmatched files: >60d = `ambiguous`, <60d = `protect`.
- Worktree directories (`wt-FTR-*`, `wt-BUG-*`, `wt-DSN-*`, `wt-TDT-*`) are `safe` only if the worktree has no uncommitted changes AND its associated branch is fully merged to master (run `git -C <dir> status --porcelain` and `git branch --merged master`). Otherwise `protect`.

### Area 6: repo-root pollution (always on)

- Loose `screenshot-*.png` and `Screenshot*.png` at the repo root -- `safe` if matched
- Extracted archive directories at the repo root (e.g., `internal_claude_skills-main/`) -- `ambiguous` (flag, never auto-delete)
- `*.tgz`, `*.zip` at the repo root older than age threshold -- `ambiguous`

## Classification rules

| Class | Meaning | Phase 2 behavior |
|-------|---------|------------------|
| `safe` | Matched a known scrub pattern AND older than age threshold | Deleted |
| `ambiguous` | Old but no pattern match, OR pattern match but mtime within threshold, OR extracted-archive-dir | Flagged in manifest; skipped by `--apply` |
| `protect` | In protected list, OR recent activity (<7d), OR live state file | Never touched |

## Age thresholds

Default: **14 days**. Override with `--age-days N`.

- Use 14d (default) for routine weekly cleanups.
- Use 30d for cautious sweeps after a long break.
- Use 7d only when the founder confirms an aggressive prune.

## CLI flags

- `--apply` -- run Phase 2 against the most recent manifest. Refuses if manifest >3 days old.
- `--age-days N` -- override the default 14d threshold for what counts as stale.
- `--area <name>` -- restrict the survey to one area (`claude-root`, `screenshots`, `marathon-briefs`, `workday-archive`, `tmp`, `repo-root`).
- `--include-tmp` -- include Area 5 (`d:\tmp`). Off by default since `d:\tmp` is shared.
- `--dry-run` -- explicitly mark as survey-only (already the default; this is for readability when chaining).
- No flags = survey of all default areas with 14d threshold, no `d:\tmp`.

## Manifest schema

Markdown manifest follows the 2026-05-17 precedent:

```markdown
# Cleanup Manifest -- YYYY-MM-DD

Total candidates: N files, X GB

Phase 1 = READ-ONLY survey. Nothing moved, nothing deleted. CEO decides Phase 2.

## Summary
| Area | Files | Size | Safe | Ambiguous | Protect |
|------|-------|------|------|-----------|---------|
| 1 -- .claude/ root | ...  | ...  | ...  | ...       | ...     |
| 2 -- screenshots dirs | ...  | ...  | ...  | ...       | ...     |
| 3 -- marathon-briefs | ...  | ...  | ...  | ...       | ...     |
| 4 -- workday archive scratch | ...  | ...  | ...  | ...       | ...     |
| 5 -- d:\tmp (if --include-tmp) | ...  | ...  | ...  | ...       | ...     |
| 6 -- repo root | ...  | ...  | ...  | ...       | ...     |

## Area N -- top items by size
- 1234 KB  path/to/file  (pattern, class)
...

## Area N -- buckets
- pattern:  count files / total KB
...

## Next steps
- Review the table above. If counts and patterns look right, run:
  `/cleanup-stale --apply`
- To exclude any single bucket, edit the manifest JSON and re-run with --apply.
```

JSON sidecar mirrors the structure with one entry per file: `{path, size, mtime, pattern, class, area}`.

## Hard rules

1. **Never delete in Phase 1.** Phase 1 is read-only. If anything writes outside the manifest files, the skill failed.
2. **Never auto-run Phase 2.** `--apply` must be typed by the founder. Do not chain Phase 1 and Phase 2 in one invocation.
3. **Never touch protected paths even on `--apply`.** The protected list is hard-coded; classification cannot promote a path out of `protect`.
4. **Refuse stale Phase 2.** If the latest manifest is >3 days old, refuse `--apply` and prompt for a fresh survey.
5. **Always log Phase 2.** Every deletion is appended to `cleanup-applied-YYYY-MM-DD.md` with path, size, and reason (matched pattern).
6. **Honor `.gitignore`.** Anything gitignored is fine to delete (Phase 2 can prune them); anything tracked-but-untracked-to-task should be classified `ambiguous` and surfaced.
7. **No `.gitignore` edits.** This skill never modifies `.gitignore`. If a file recurs every run, the founder edits `.gitignore` separately.

## Output conventions

- Manifest paths: `.claude/cleanup-manifest-YYYY-MM-DD.{md,json}` in the project root (e.g., `C:\projects\your-app\.claude\`).
- Apply log: `.claude/cleanup-applied-YYYY-MM-DD.md`.
- Chat summary: a 6-row table (one row per area) + top-10-by-size + the path to the manifest. Under 25 lines. No restating the manifest body in chat.

## When to use this skill

- Routine: weekly or every-other-week, after a marathon run completes.
- Before pushing: if `.claude/` has accumulated screenshots that are slowing IDE indexing.
- After a session crash that left scratch files behind.
- Pre-handoff: before another agent or contributor pulls the repo and sees the noise.

## When NOT to use this skill

- During an active marathon (state files are live; classification will misfire).
- Right after a deploy if you haven't pushed (in case any scratch contains debug data you wanted to grep first).
- If `git status` shows uncommitted edits to anything in the candidate set -- commit or stash first.
