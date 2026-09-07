# MANDATORY lines — the single source of truth

Source: `D:\Hub\50-AI\fleet-ops\notes\2026-08-31-run-builder-design.md` §7.

Seven lines. They go in **every** lane prompt, **verbatim**. Each has a recorded failure behind
it and none can be enforced mechanically at prompt time. `templates\PROMPT-BUILDER.md.tmpl` and
`templates\PROMPT-GATE.md.tmpl` copy from this file — if a line changes, it changes here first.

Builder prompts carry lines **1-7**. The gate prompt carries lines **1-6** plus the gate
checklist (line 7 is builder-only: the gate *is* the terminal authority).

---

## The block (copy verbatim into a prompt)

```
MANDATORY (verbatim, non-negotiable):
1. Commit with an explicit pathspec and a `-F` message file; judge success by `git log -1`
   grepping your marker, never by exit code. One retry loop maximum. Never clear a peer
   `index.lock`.
2. Every git command is prefixed `cd <target-repo> &&`. A bare git command from the run dir
   steers the MAIN tree.
3. Name every test root explicitly (including `tests/ppn`). Judge pytest by the summary line,
   not the exit code. Never reuse a basetemp — the wrapper mints a fresh one; you pass
   `--basetemp=$env:SCRATCH_RUN_DIR\pytest` and nothing else.
4. Browser work: `new_page` with `isolatedContext: "lane-<X>-<role>"` from the first
   navigation. One debug shortcut; never invent a user-data-dir.
5. Quote rulings verbatim from the source spine, never from a prior run summary or memo.
   A green suite can defend the wrong contract.
6. Every number you write is re-read from the artifact at the moment of writing.
   Unpushed-commit counts are re-derived, never carried.
7. You are a builder: you mark `AWAITING_VERIFICATION`, never `VERIFIED`. A `BLOCKED` post
   without evidence is not a blocker. A `WATCH` from the gate is obeyed.
```

**Marker format (fixed, not a choice):** every lane commit carries
`[run-NN][lane-x][<row-id>] <subject>` as its first line. Line 1's "your marker" means exactly
this string. Written into the `-F` file, never typed on the command line. The gate's conformance
check #3 reads it. The prep commit (`run-NN prep: <shape> <theme> <shift>`) deliberately has no
lane marker — it is not a lane commit and does not count as one in any conformance check.

---

## What does NOT belong in a prompt

**Lives in the skill mechanics** (the skill does it, so a lane cannot forget): worktree
provisioning, `--basetemp` wiring via `scratch-run.ps1`, scratch-policy caps, run-dir scaffold,
ledger row, prep commit, comms channel creation, concurrency cap.

**Lives in the GATE checklist** (`templates\PROMPT-GATE.md.tmpl`), never in a builder prompt:
zombie-process enumeration by `--basetemp` via `Win32_Process` with an ownership check before
any kill; the clean-worktree discriminator for suspicious reds; rule-70 different-modality
sampling; the frozen-baseline serial sweep; verified scratch deletion; the conformance JSON.

---

## Per-line provenance (why each line exists)

| # | Recorded failure |
|---|---|
| 1 | Multi-lane shared index: git reported exit 0 on a commit that did not land; a killed inline commit died at tool timeout. |
| 2 | The run dir sits inside the main repo — a bare git command after `cd run-NN/` steered the MAIN tree. |
| 3 | `tests/ppn` is outside every sweep (100+ tests silently lost, reported green); a killed pytest run reports exit 0; a reused basetemp cost 250x. |
| 4 | Lanes sharing Chrome on 9222 share portal localStorage — one magic link logged every other lane out and read as a 404 data bug. |
| 5 | Ruling R3 was disregarded across runs 59-64 by quoting a prior run's summary; 13 tests asserted a ruling violation and stayed green. |
| 6 | Numbers carried from memory into a report were wrong three times in one run; unpushed-commit counts drifted. |
| 7 | Builder != verifier is doctrine (runs 62-63). A blocker claim without evidence is not a blocker (run-62 MECHANICS #10). |
