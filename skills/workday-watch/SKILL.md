---
name: workday-watch
description: "Optional C-suite surveillance session for an in-flight /workday parallel run. A non-destructive 5th session that periodically has the responsible C-suite agent inspect each lane for breaking / drifting / misunderstanding / hallucinating, then posts [WATCH][LANE-X] steering corrections the lanes obey — catching problems in ~20 min instead of at the morning merge. Never edits lane code or git. Invoke with /workday-watch [--once] [--status] [--stop]. Use when the user wants to 'watch the lanes', 'monitor the overnight run', or 'catch drift faster'."
---

# Workday Watch Skill

The optional fifth session of a `/workday` run. The four work lanes (A/B/C/D) and the
automated Lane E merge run fine without it — `/workday-watch` exists only to **shorten
time-to-correction**. Without it, a lane that drifts, misunderstands its WO, or hallucinates
a file/contract is not caught until John reviews at the morning Lane E merge (hours of wasted
unattended work). With it, the responsible C-suite agent catches the problem on the next
~20-minute tick and posts a correction the lane reads before its next work order.

It is **read-and-comms-only**: it never edits lane code, never runs git, never holds claims,
never merges. Its only outputs are steering posts on the comms bus and an escalation post to
the owner for things no C-suite agent may decide alone.

## Prerequisite

A `/workday` run must be in flight. `/workday-watch` auto-detects the newest run directory and
reads, per lane: the state file (queue, in-flight WO, lane GOAL), the lane worktree
(`git -C <worktree> log <trunk>..lane/{x} --oneline` and `... status --porcelain`,
read-only), and the comms bus (`c-suite` / `dept-heads` / `dev-floor` tails + active claims).

The `/workday`-generated lane prompts include a WATCH-integration hook ("before each WO, read
c-suite for `[WATCH][LANE-X]` posts and obey them as binding"). That hook is what makes a
correction land. If a lane was launched from an older prompt without the hook,
`/workday-watch` can still detect and escalate, but its steering posts will not auto-apply —
note that in the watch log and escalate sooner.

## Invocation

```
/workday-watch            Start surveillance; register the ~20-min watch cron; run one pass now
/workday-watch --once     Single inspection pass across all lanes, no cron, then stop
/workday-watch --status   Print the latest per-lane verdicts + watch-log tail, then stop
/workday-watch --stop     CronDelete the watch cron, post a final watch summary, stop
```

## What each tick does

A tick is periodic surveillance — distinct from the lanes' "no idle waves" throughput rule.
The watch *should* tick on a cadence (it has nothing to do between passes).

### 1. Snapshot every lane (read-only)

Per lane gather: state file (queue depth, in-flight WO + how long, lane GOAL), commits ahead
of trunk + the actual diff stat, working-tree dirtiness, the last ~30 comms lines mentioning
the lane, and its active claims.

### 2. Route each lane to its responsible C-suite reviewer

Spawn the responsible agent(s) via the Agent tool (foreground, advisory — they return a
verdict, they don't act):

| Concern | Reviewer | Looks for |
|---|---|---|
| Code quality, territory, diff sanity (every lane) | `chief-engineer-john` | slop, files outside territory, diff not matching the WO |
| Domain correctness — Lane A (schema) | the database head | migration/ORM drift, lossy down(), missing backfill |
| Domain correctness — Lane B (backend) | the backend head | broken invariants, swallowed exceptions, audit gaps |
| Domain correctness — Lane C (frontend) | the frontend head | a11y regressions, white-screen risk, contract assumptions |
| Domain correctness — Lane D (api) | the api head | spec drift, auth/contract breaks |
| Cross-lane direction & scope | `cto-james` | a lane doing another lane's work, scope/theme drift |

Give the reviewer the lane GOAL, the territory globs, the ordered queue, the recent
diff/commits, and the comms narrative. Ask for a structured verdict:

```
LANE {X} VERDICT: OK | DRIFT | MISUNDERSTAND | BREAK | HALLUCINATE | STUCK
EVIDENCE: <2–4 sentences citing the commit/file/comms line that proves it>
CORRECTION: <if not OK: one specific, actionable paragraph the lane can execute>
SEVERITY: steerable | owner-decision
```

### 3. Detection rubric

| Signal observed | Category | Action |
|---|---|---|
| Suite red across ≥2 WOs; build failing; junior auto-commit not soft-reset | **BREAK** | `[WATCH][LANE-X]`: stop, fix the break, re-verify before next WO |
| Edits/claims outside territory globs; doing another lane's WO | **DRIFT** | `[WATCH][LANE-X]`: revert the out-of-territory change, file a `[LANE-Y]` request instead |
| Implementing against wrong acceptance; ignoring the lane GOAL; contradicting an ADR/CLAUDE.md rule | **MISUNDERSTAND** | `[WATCH][LANE-X]`: restate the correct acceptance + the GOAL; redo the WO |
| References a WO ID / file / migration / API contract that does not exist; claims a WO done with no commit/diff; invents prior art | **HALLUCINATE** | `[WATCH][LANE-X] STOP`: name the fabrication, force re-verify against ground truth, skip the WO if unrecoverable |
| Same WO in-flight past the marathon timeout; identical comms posts repeating; no commit in N hours | **STUCK** | `[WATCH][LANE-X]`: skip/abort the WO, move on; if blocked on a real cross-lane dep, say which |
| None of the above | **OK** | log only |

### 4. Act (comms-only, non-destructive)

- **steerable** → post the correction to `c-suite` from the reviewing agent's name, subject
  `[WATCH][LANE-{X}]` (or `[WATCH][LANE-{X}] STOP` for HALLUCINATE/BREAK), addressed so the
  lane's pre-WO comms read catches it:
  `AGENT_ORG_DB=<comms-db> <comms.py> post c-suite <agent> "<correction>" --to lane-{x} --subject "[WATCH][LANE-{X}]"`.
  Bodies < 1800 chars. Be specific: cite the exact WO/file/line and the exact next action.
- **owner-decision** (new paid vendor, architecture reversal, anything irreversible, or a
  BREAK no C-suite agent may steer alone) → post for the owner with evidence and a
  recommendation. **Do not block the lane on the owner's answer** — also post a
  `[WATCH][LANE-X]` telling the lane to defer that one WO and continue the rest. The owner
  decides later; the night is not lost.
- Always append one line to the run's `watch-log.md`:
  `<ISO> LANE-{X} <verdict> — <action taken>`.

### 5. Loop / stop

- Register a watch cron (~20-min, durable, recurring) whose prompt re-reads this SKILL.md +
  the run dir and runs one pass. Stagger it off the lanes' safety-cron minutes so the watch
  never wakes in the same instant as a lane resume.
- Stop when **all work lanes have posted a `final-status`** (complete or partial) — Lane E
  takes over from there. Also stop on wall-clock stop or `--stop`. On stop: post a final
  watch summary to `c-suite` for the owner (per-lane verdict history, corrections issued,
  anything escalated) and `CronDelete` the watch cron.

## What it must never do

- **Never edit lane code, never run git (no merge/branch/checkout/reset), never hold claims.**
  Drift is corrected by *telling the lane*, not by reaching into its tree. Reaching in would
  reintroduce the exact cross-lane collision class `/workday`'s worktree isolation prevents.
- **Never reorder or merge lanes.** That is Lane E's job, with John as the merge gate.
- **Never block a lane longer than necessary.** A correction should redirect, not halt — only
  HALLUCINATE/BREAK warrant a `STOP` on a single WO, and even then the lane continues with
  the rest of its queue.

## Hard rules

- **Optional and additive.** If `/workday-watch` is not running, nothing breaks — the lanes
  self-govern and Lane E + John catch issues at merge. The watch only makes correction
  faster.
- **Evidence-first.** Every correction cites the concrete commit/file/comms line that proves
  the problem. No vibes-based steering — a wrong correction is worse than a late one.
- **One reviewer owns each call.** John for code/territory, the domain head for domain
  correctness, James for cross-lane direction. Don't average opinions; route to the owner.
- **Read-only worktree access.** Inspect with `git -C <worktree> log/status/diff` only; never
  a mutating git verb in any worktree.
- Bodies < 1800 chars; `org.config.json` is never touched; `comms.py` / the path-guard hook
  are never self-modified.

## Companion: `/workday`

`/workday` plans and arms the 4-lane run and writes the `[WATCH][LANE-X]`-listening hook into
each lane prompt. `/workday-watch` consumes that run. Start `/workday-watch` any time after
the lanes are launched (or not at all — it is optional). See the `/workday` skill for the
lane model, territory partition, John's per-lane goal, safety crons, and keep-last-1 cleanup.
