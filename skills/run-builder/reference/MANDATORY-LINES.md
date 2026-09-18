# MANDATORY lines — the single source of truth

Source: `D:\Hub\50-AI\fleet-ops\notes\2026-08-31-run-builder-design.md` §7.

Seven lines (six from 2026-09-17 to 2026-09-18; line 7 renders on HQ-composed runs only). They go in **every** lane prompt, **verbatim**. Each has a recorded failure behind
it and none can be enforced mechanically at prompt time. `templates\PROMPT-BUILDER.md.tmpl` and
`templates\PROMPT-GATE.md.tmpl` copy from this file — if a line changes, it changes here first.

Builder prompts carry lines **1-6** (+7 on HQ). The gate prompt carries lines **1-5** (+7 on HQ) plus the gate
checklist (line 6 is builder-only: the gate *is* the terminal authority).

**Prompt budget (charter Article 6):** ≤ 90 lines per lane prompt. The lines the charter program added on
2026-09-18 — the tier text of line 3, the gate's `SCOPE:` / two-bounce line and the gate's office line — are
counted inside that budget, not on top of it.

Retired 2026-09-17 on ENGINE, **re-instated 2026-09-18 for HQ-composed runs as line 7** (owner ruling S5-13,
charter Article 18): ENGINE's `~/.claude.json` runs the chrome-devtools MCP with `--isolated`; HQ's runs
`--browserUrl http://127.0.0.1:9222` with no `--isolated`, so HQ lanes still share one Chrome. The line retires
on HQ the day HQ's registration carries `--isolated` (a user-scope change, owner's act).

---

## The block (copy verbatim into a prompt)

```
MANDATORY (verbatim, non-negotiable):
1. Commit with an explicit pathspec and a `-F` message file; judge success by `git log -1`
   grepping your marker, never by exit code. One retry loop maximum. Never clear a peer
   `index.lock`.
2. Every git command is prefixed `cd <target-repo> &&`. A bare git command from the run dir
   steers the MAIN tree.
3. Tests run in tiers; nobody judges their own work. T0: you may run `tools/smoke.sh` (60 s)
   on your row and nothing else — no pytest, vitest, jest, playwright, `npm test` or any suite.
   T1 (≤ 8 named files, 300 s, through `policy/scratch-run.ps1`) is the gate seat's alone; T2
   (the full suite) is the HQ merge gate's alone. Prove a row by the artifact: the page, the
   query, the curl, the diff. A test an order asks for is written and committed, never run by
   you (rule 10 as amended 2026-09-18; `guards/no_test_run_guard.py` enforces the shape).
4. Quote rulings verbatim from the source spine, never from a prior run summary or memo.
   A green suite can defend the wrong contract.
5. Every number you write is re-read from the artifact at the moment of writing.
   Unpushed-commit counts are re-derived, never carried.
6. You are a builder: you mark `AWAITING_VERIFICATION`, never `VERIFIED`. A `BLOCKED` post
   without evidence is not a blocker. A `WATCH` from the gate is obeyed.
7. HQ-composed runs only (until HQ's chrome-devtools MCP is registered with `--isolated`):
   browser work is `new_page` with `isolatedContext: "lane-<X>-<role>"` from the first
   navigation. One debug shortcut; never invent a user-data-dir. (ENGINE/FIELD: omit.)
```

**Marker format (fixed, not a choice):** every lane commit carries
`[run-NN][lane-x][<row-id>] <subject>` as its first line. Line 1's "your marker" means exactly
this string. Written into the `-F` file, never typed on the command line. The gate's conformance
check #3 reads it. The prep commit (`run-NN prep: <shape> <theme> <shift>`) deliberately has no
lane marker — it is not a lane commit and does not count as one in any conformance check.

---

## What does NOT belong in a prompt

**Lives in the skill mechanics** (the skill does it, so a lane cannot forget): worktree
provisioning, run-dir scaffold, ledger row, prep commit, comms channel creation, concurrency cap.

**Lives in the GATE checklist** (`templates\PROMPT-GATE.md.tmpl`), never in a builder prompt:
rule-70 different-modality sampling; the gate's own browser / artifact / query checks; verified
scratch deletion; the conformance JSON. (Pytest zombie enumeration, the clean-tree discriminator
for a suspicious red and the frozen-baseline serial sweep retired 2026-09-17 — no lane runs a suite.)

---

## Per-line provenance (why each line exists)

| # | Recorded failure |
|---|---|
| 1 | Multi-lane shared index: git reported exit 0 on a commit that did not land; a killed inline commit died at tool timeout. |
| 2 | The run dir sits inside the main repo — a bare git command after `cd run-NN/` steered the MAIN tree. |
| 3 | Owner ruling 2026-09-17: lanes spent hours per shift on suites — basetemps, summary lines, reds that were the measurer's own artefact (`guards/stable-read.sh`), `tests/ppn` silently lost, 13 tests asserting a ruling violation and staying green (runs 59-64). Suites moved to the HQ merge gate; `directives/2026-09-17-no-tests-outside-hq-merge-gate.md`. |
| 4 | Ruling R3 was disregarded across runs 59-64 by quoting a prior run's summary; 13 tests asserted a ruling violation and stayed green. |
| 5 | Numbers carried from memory into a report were wrong three times in one run; unpushed-commit counts drifted. |
| 6 | Builder != verifier is doctrine (runs 62-63). A blocker claim without evidence is not a blocker (run-62 MECHANICS #10). |
| 7 (was 4) | Lanes sharing Chrome on 9222 shared portal localStorage — fixed structurally by `--isolated` on ENGINE's MCP (2026-09-07); line removed 2026-09-17; measured absent on HQ (`grep -c -- '--isolated' ~/.claude.json` → 0) and re-instated for HQ-composed runs 2026-09-18 (S5-13). |
| 3 (amended) | Charter program 2026-09: the blanket ban was "a bit of an over correction" (owner); tiers T0/T1/T2 replace it (S2-01, S2-02; `evidence/s2/TESTING-STANDARD.md`). The `-v` hole in the guard closed the same day. |
