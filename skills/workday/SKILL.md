---
name: workday
description: "Standardized 4-lane parallel overnight engineering run. Plans 4 territory-disjoint lanes (A=schema/db, B=backend, C=frontend, D=api) + an automated Lane E merge, each lane an org-routed marathon in its own git worktree, with a John-authored completion goal per lane, staggered safety crons for long-session limits, and keep-last-1 cleanup of old runs. Built for 8-hour unattended runs. Invoke with /workday [theme] [--lanes N] [--stop-at HH:MM] [--cleanup] [--status] [--dry-run]. Use whenever the user wants 'the overnight run', 'parallel lanes', 'plan tonight's lanes', or a big bite out of the backlog while they sleep. Optional companion: /workday-watch."
---

# Workday Skill

The standardized, repeatable form of a parallel overnight run: four worktree-isolated lanes
(A/B/C/D) plus an automated Lane E merge, each lane an org-routed marathon. It replaces
hand-writing a fresh per-night prompt file every time. `/workday` plans the lanes, partitions
the codebase so they cannot collide on writes, has the Chief Engineer set each lane's true
definition-of-done, generates paste-ready prompts plus a plain-language launch card,
registers staggered safety crons, and prunes old runs so future sessions never re-read a
stale plan.

**One sentence:** `/workday` turns "let me re-explain the 4-lane process again" into one command.

## Mental model

```
  /workday  (you, ~10 min)                          owner (one window, that night)
  ========                                          ============================
   plan 4 disjoint lane queues from backlog/plans     session 1 -> paste PROMPT-A  (Lane A: schema)
   John authors a completion GOAL per lane            session 2 -> paste PROMPT-B  (Lane B: backend)
   provision 4 git worktrees (no shared tree)         session 3 -> paste PROMPT-C  (Lane C: frontend)
   write <runs-dir>/ prompt set + README              session 4 -> paste PROMPT-D  (Lane D: api)
   register 4 staggered safety crons                      ... ~8 hours, unattended ...
   prune all but the last completed run               morning -> paste PROMPT-E  (Lane E: merge+cleanup)
```

Each lane is a **separate Claude Code session in the same editor window**, pointed at its own
worktree. Each session *is* its own lane orchestrator: it runs the org-routed marathon and
dispatches sub-agents to complete its work orders one at a time, unattended. Lane E is one
more session the next morning that merges all four into the trunk and cleans up. `/workday`
itself does not run the lanes — it produces the artifacts and the launch card.

## When to use this vs the other marathons

| Skill | Shape | Use when |
|---|---|---|
| `/work-orders` | 1 Sonnet session, shallow batch | 4-15 trivial independent items, you're watching |
| `/marathon-orders` | 1 Opus agent per WO, single tree | deep queue, one lane, you're semi-watching |
| `/marathon-org` | org-routed, single tree | named accountability, one lane |
| **`/workday`** | **4 org-routed lanes + auto Lane E, worktree-isolated, 8h unattended** | **big overnight bite across schema+backend+frontend+api with zero write collisions** |

`/workday` reuses the per-lane internal loop of `/marathon-org`. The new parts are the 4-lane
territory partition, John's per-lane goal, worktree provisioning, staggered safety crons,
the automated Lane E, and the keep-last-1 cleanup.

## Configure for your project

Swap these placeholders (most are read once at plan time; the skill writes concrete values
into the generated prompts so the lane sessions need no further configuration):

| Placeholder | Meaning | Example |
|---|---|---|
| `<project-root>` | repo root the run operates on | `/abs/path/to/repo` |
| `<backlog>` | dir with `bugs.md` `design.md` `features.md` `tech-debt.md` `completed.md` | `<project-root>/backlog` |
| `<plans>` | optional plan sources for a bigger bite | `docs/specs/**`, `docs/adr/**` |
| `<runs-dir>` | gitignored dir for run artifacts (trivial cleanup, invisible to context scans) | `<project-root>/.tmp/workday-<date>/` |
| `<archive>` | where superseded runs are parked | `<project-root>/.claude/archive/workday/<date>/` |
| `<comms-db>` | agent-org comms DB (shared across worktrees) | `<project-root>/.claude/comms/comms.db` |
| `<comms.py>` | comms CLI; prefix `AGENT_ORG_DB=<comms-db>` | `python <project-root>/.claude/comms/comms.py` |
| `<stop-clock>` | wall-clock stop; `--stop-at HH:MM` overrides; else launch + 8h | `08:30` local |
| `<guardrails>` | your project's locked architecture + constraints (from CLAUDE.md / ADRs) the lanes must respect when deciding in your absence | — |

Prerequisite: the agent-org install must be complete in `<project-root>` (`.claude/agents/`
with at least the CTO-branch agents, `comms.py`, the path-guard hook, and `org.config.json`
mapping your repo's dept path globs). `/workday` drives the same chain as `/marathon-org`.

## The lane model (the no-write-collision guarantee)

Four work lanes, territory-disjoint by department. **No two lanes may write the same path.**
This is the structural guarantee that lets them run in parallel safely: path-claims protect
within a lane; disjoint worktrees + disjoint territory protect across lanes (a shared working
tree loses work to cross-lane `git stash`/checkout interleaving — separate trees make that
impossible).

| Lane | Dept (persona chain) | Branch / worktree | Exclusive write territory |
|---|---|---|---|
| **A — Schema/DB** | database head + juniors | `lane/a-db` @ `../<repo>-lane-a-db` | the schema/migrations packages + DB infra. **Single migration writer** for the run. |
| **B — Backend** | backend head + juniors | `lane/b-backend` @ `../<repo>-lane-b-backend` | server/services/workers + domain packages *(source only — migrations → Lane A)* |
| **C — Frontend** | frontend head + juniors | `lane/c-frontend` @ main worktree on `lane/c-frontend` | the web app + shared UI kit |
| **D — API** | api head + juniors | `lane/d-api` @ `../<repo>-lane-d-api` | API routes/contracts/auth + the OpenAPI specs |
| **E — Merge** | chief engineer (John) | runs on the trunk after A–D finish | merges, verifies, archives, posts the closing summary, removes worktrees |

Derive each lane's exact globs from `org.config.json` department ownership — do not hardcode
package names; the four buckets above map onto whatever dept globs the target repo defines.
Shared, union-merged at Lane E (each lane edits only its own entries): `backlog/*.md`,
ADRs. **Cross-territory needs are requests, not edits:** a schema change needed by B or D is
a `[LANE-A]` contract request on `dept-heads`; a misrouted WO is a `[LANE-X]` reclassify
post. Never reach into another lane's territory.

`--lanes 3` drops Lane D (api work folds into B); `--lanes 2` keeps A+B only. Default 4. Lane
E always runs regardless of work-lane count — never leave the merge to bare human git.

## Execution model in this environment (READ THIS)

In this Claude Code environment a spawned sub-agent **cannot itself spawn sub-agents**. The
literal relay chain (cto-james → Tim → head → junior → John) assumes recursive spawn and is
mechanically impossible here. Therefore **each lane session (the top-level orchestrator) does
all spawning directly**:

- Spawn the **department head** agent (write-capable) to implement the WO in-territory.
- Spawn **chief-engineer-john** (review-only) as the per-WO merge gate.
- Optionally spawn **cto-james** / **Tim** first for advisory direction — they return
  judgment, they do not spawn. The junior tier collapses into the head.
- Preserve everything that matters — worktree isolation, path-guard territory, comms claims,
  the verification gate, independent review — and drop only the spawn-chain theater.

This is generic to the environment, not project-specific; the lane prompt template encodes it.

## Invocation

```
/workday                       Plan: 4 lanes + auto Lane E, theme = top of backlog, 8h stop
/workday "auth hardening"      Same, with an explicit run theme / north-star
/workday --lanes 3             3 work lanes + Lane E
/workday --stop-at 07:00       Override the wall-clock stop (else launch + 8h)
/workday --dry-run             Show the 4 planned lane queues + John goals, write nothing
/workday --status              Status of the in-flight run (per-lane state, commits, comms)
/workday --cleanup             Run the keep-last-1 prune now and exit (no new run)
/workday --resume              Re-emit the launch card for an already-planned run (no re-plan)
```

---

## Phase 0 — Flag parse + cleanup (always first)

1. `--status`: read the newest `<runs-dir>/state-*.json`; print per-lane queue depth,
   in-flight WO, commits ahead of trunk (`git -C <worktree> log <trunk>..lane/<x>
   --oneline | wc -l`), last comms line per lane, and whether each posted `final-status`.
   Stop.
2. `--cleanup`: run **Cleanup (keep-last-1)** below, report what moved, stop.
3. `--stop`: read newest run state; for each lane write `paused:true`; `CronDelete` every
   `safetyCronJobId`; print "Lanes halt after their current WO. Paste PROMPT-E when ready."
   Stop. (Does not yank a sub-agent mid-edit.)
4. `--resume`: re-print the launch card from the existing `<runs-dir>`. Stop.
5. Otherwise (fresh plan): run **Cleanup (keep-last-1)** first, then Phase 1.

### Cleanup (keep-last-1) — the anti-stale-context mechanism

Old run artifacts confuse future sessions and waste tokens on plans executed days ago. Keep
**only the single most-recent completed run** in place; archive everything older; prune the
archive at 14 days.

```bash
node -e "
const fs=require('fs'), p=require('path');
const tmp='<project-root>/.tmp';
const arcRoot='<project-root>/.claude/archive/workday';
fs.mkdirSync(arcRoot,{recursive:true});
const runs=fs.existsSync(tmp)?fs.readdirSync(tmp).filter(d=>/^workday-/.test(d)).sort():[];
const keep=runs.slice(-1)[0];                       // most recent stays put
let moved=0;
for(const r of runs.slice(0,-1)){
  fs.renameSync(p.join(tmp,r), p.join(arcRoot,r.replace(/^workday-/,''))); moved++;
}
const cut=Date.now()-14*864e5;
for(const d of fs.readdirSync(arcRoot)){
  const fp=p.join(arcRoot,d);
  if(fs.statSync(fp).mtimeMs<cut){ fs.rmSync(fp,{recursive:true,force:true}); }
}
console.log('CLEANUP kept='+(keep||'none')+' moved='+moved);
"
```

Then sweep worktrees/branches belonging to archived (already-merged) runs — but **never
force-remove a worktree with uncommitted changes**; if `git -C <wt> status --porcelain` is
non-empty, leave it and surface it to the user. Lane E removes its own worktrees on success;
this step only mops up runs Lane E never closed.

---

## Phase 1 — Plan the run (user present; the one human gate)

### Step 0 — Pre-merge any stale prior-session lanes

```bash
git -C <project-root> worktree list
```

If stale `lane/*` worktrees from an unmerged prior run exist: **run Lane E for them first**
before provisioning new worktrees. Branching new lanes off a stale trunk guarantees merge
pain. Emit a PROMPT-E-recovery for the old run, have the user paste it and confirm clean,
then continue. If clean (only the main worktree): proceed.

### Step 1 — Trunk / origin alignment

```bash
git -C <project-root> checkout <trunk> && git -C <project-root> fetch origin
git -C <project-root> log --oneline -1 <trunk> && git -C <project-root> log --oneline -1 origin/<trunk>
# aligned: proceed | local AHEAD: don't pull, note it | origin AHEAD: pull --ff-only | diverged: STOP, ask user
```

### Step 2 — Prune `completed.md`

Remove `completed.md` entries older than 30 days (same prune as `/marathon-orders`). Keeps
the prior-art window cheap to read.

### Step 3 — Build 4 territory-disjoint lane queues

Read `<backlog>` (all categories, or filtered to the theme/`<plans>` if a theme arg given)
and parse every `### [ID]` block. Bucket each WO into exactly one lane by the path territory
it must write (derive from `org.config.json`). Rules:

- A WO that needs both a migration and backend source → split: schema slice to Lane A,
  source slice to Lane B, with an explicit `[LANE-A]`/`[LANE-B]` cross-request noted in both
  queue entries. Never let one WO straddle two territories silently.
- Sort each lane's queue: priority (critical>high>medium>low) → age (oldest ID first) →
  category (bugs>design>features>tech-debt).
- Take a **big bite**: no wave-size cap. 8–12 WOs per lane across 8 hours is normal.
- Pre-reserve disjoint ID ranges per lane for any new IDs a lane will file so Lane E sees
  zero ID collisions. The first WO of Lane A re-verifies Next-ID against the freshly-merged
  backlog at runtime.

### Step 4 — John authors each lane's completion GOAL

Spawn **`chief-engineer-john`** (Agent tool, foreground, advisory — he returns judgment,
does not spawn). Prompt:

```
You are John, Chief Engineer. Here are the 4 planned lane queues for tonight's /workday run
and the run theme: {theme}.

{for each lane: lane letter, dept, territory, ordered WO list with one-line each}

For EACH lane, author a 2–4 sentence LANE GOAL: the provable end-state that means this lane's
night is *truly* complete — not "queue empty" but the mission objective plus the concrete
verification that proves it (suites green, artifact exists, acceptance holds). Specific enough
that a tired session at 6 AM can self-check "am I actually done, or just out of queue?"
Return exactly:
LANE A GOAL: ...
LANE B GOAL: ...
LANE C GOAL: ...
LANE D GOAL: ...
```

John's goal becomes each lane's **true stop condition** (see the lane prompt template).

### Step 5 — Pre-flight settings.json (REQUIRED, one approval)

Add to `permissions.allow` if absent: Edit/Write for `<backlog>/**` and `<runs-dir>/**`, the
`Bash(<comms.py>:*)` perm, and `Edit(~/.claude/skills/workday/**)`. Tell the user this is the
one approval before unattended operation. If the harness blocks the self-grant, do not fight
it — the lanes write the backlog via `node -e` (already in Bash scope) and the run-dir is a
gitignored `.tmp`.

### Step 6 — Provision worktrees

```bash
git -C <project-root> worktree add -b lane/a-db      ../<repo>-lane-a-db      <trunk>
git -C <project-root> worktree add -b lane/b-backend ../<repo>-lane-b-backend <trunk>
git -C <project-root> worktree add -b lane/d-api     ../<repo>-lane-d-api     <trunk>
# Lane C uses the MAIN worktree on branch lane/c-frontend, created as step 1 inside PROMPT-C
# AFTER the others exist, so the main tree is free for it.
```

All lanes point at the same comms DB via `AGENT_ORG_DB=<comms-db>` so the org sees itself
across worktrees.

### Step 7 — Write the run directory

Create `<runs-dir>` (append `-2`,`-3` for same-day reruns) containing: `PROMPT-A-db.md`,
`PROMPT-B-backend.md`, `PROMPT-C-frontend.md`, `PROMPT-D-api.md` (from the **Lane Prompt
Template**, fully filled), `PROMPT-E-merge.md` (from the **Lane E Template**),
`state-{a,b,c,d}.json` (written via `node -e`; schema = `/marathon-org` state +
`lane`,`goal`,`safetyCronJobId`,`stopClock`), `README.md` (the plain-language launch card),
and empty `safety-wakeup-log.md` + `watch-log.md`.

### Step 8 — Register staggered safety crons

A long-session limit can pause a lane mid-run. Each lane gets ONE durable safety cron,
**staggered ~15 min apart** so a limits-reset wake-up does not have all lanes hammer the API
at the same instant and immediately re-trip the limit. Example offsets: A `45 0 * * *`, B
`0 1 * * *`, C `15 1 * * *`, D `30 1 * * *` (local). `CronCreate` each with
`durable:true, recurring:true`. Prompt per cron:

```
Workday safety wake-up — Lane {X}, run {date}.
1. Read <runs-dir>/state-{x}.json. If status complete/failed: CronDelete self, stop.
2. If wall-clock >= {stopClock}: ensure the lane reported final-status; if not, post a
   final-status: partial for Lane {X}; CronDelete self; stop.
3. Else (lane likely paused on a session limit, now reset): re-read PROMPT-{X} and fire ONE
   internal marathon-org tick to resume the next WO. Do NOT idle-sleep. Append one line to
   <runs-dir>/safety-wakeup-log.md.
```

Store each returned id as `safetyCronJobId` in the lane state. **Honest limit:** when the
harness reports a cron as "session-only" it dies with the session even if `durable:true` was
requested — the safety cron mitigates *API-limit pauses within a live session*, not a full
session crash. Full-crash recovery is the owner re-pasting the lane prompt (the README says
so plainly).

### Step 9 — Kickoff posts + confirm

Post the run kickoff to `c-suite` and `dept-heads` via `<comms.py>` (lane map, theme,
reserved ID ranges, stop clock, "NO idle waves — chain WOs back-to-back"). Then print the
plan summary (per-lane WO count + one-line John goal + the staggered cron offsets + the run
dir) and ask: "Launch tonight? [y/n] (dry-run stops here)". On `y`, print the README inline
so the owner can act immediately.

---

## Lane Prompt Template (the reusable core — fill every `{…}`)

```
You are running **LANE {X} ({DEPT})** of a /workday parallel overnight run, {date}. James
(CTO) owns the work product; you orchestrate the org chain inline. The owner is away — never
block on them.

FIRST: `cd {worktree}` and run `git rev-parse --abbrev-ref HEAD`. It MUST read `lane/{x}`.
{Lane C only: from the main checkout run `git checkout {trunk} && git checkout -b
lane/c-frontend` then re-verify.} If the branch is wrong, STOP and post to c-suite for the
owner — do not work in the wrong tree.

LANE GOAL (authored by John — this is your TRUE definition of done):
{John's goal for this lane, verbatim}
You are done when (queue exhausted OR wall-clock >= {stopClock}) AND this goal is provably
met and verified. If the clock hits with the goal unmet: finish or fully revert the in-flight
WO (leave NO half-done commit), report `final-status: partial` with the precise gap. "Queue
empty" alone is NOT done if the goal is unmet — say so honestly.

EXECUTION MODEL (this environment forbids sub-agents spawning sub-agents): YOU do all
spawning. Spawn the dept-head agent (write-capable) to implement; spawn chief-engineer-john
(review-only) as the per-WO merge gate; optionally spawn cto-james/Tim for advisory direction
(they return judgment, don't spawn). Never write a prompt that asks a sub-agent to spawn one.

ORCHESTRATOR DISCIPLINE (HARD RULES):
- You NEVER read or grep source. Every Read/Grep/implementation goes to a sub-agent.
- DISPATCH ONE WO AT A TIME: implement → John reviews the diff → you commit on `lane/{x}` →
  IMMEDIATELY dispatch the next WO. **NO sleeps between WOs. NO idle waves.** A
  `ScheduleWakeup` only when the queue is empty before {stopClock} or genuinely blocked on a
  cross-lane request that has not arrived.
- Junior-commit guard: after every sub-agent returns, `git log --oneline -5`. If it
  auto-committed against instructions, `git reset --soft` before John's review. Forbid the
  sub-agent from running git stash/reset/checkout; verify `git status` after each sub-agent.
- WATCH integration: before dispatching each WO, run `AGENT_ORG_DB={comms-db} {comms.py} read
  c-suite --to lane-{x} --unread` and obey any `[WATCH][LANE-{X}]` steering post as binding
  (that is the optional /workday-watch session correcting drift). A `[WATCH]…STOP` post means
  stop the named WO and re-verify against ground truth before continuing.

EXCLUSIVE WRITE TERRITORY (path-guard enforces this; staying inside it is what makes the
lanes collision-free): {territory globs for this lane, derived from org.config.json}
NEVER write: {every other lane's territory + .claude/** + CI workflow + deploy infra}. A
schema change → `[LANE-A]` request on dept-heads. A misrouted WO → `[LANE-X]` reclassify.

STATE FILE: {runs-dir}/state-{x}.json — update via `node -e` only (Write tool not
pre-approved during unattended ticks; node is). Mark each WO in_flight →
completed/failed with resolution.

WORK-ORDER QUEUE ({n} items, priority order):
{numbered WO list — each with ID, priority, files-hint, acceptance, any [LANE-Y] request}
STRETCH (only on a green flag near the goal): {optional}

PER-WO DEFINITION OF DONE: acceptance met; the project's verification commands green for the
affected scope; every file within the project's size cap; backlog `completed.md` updated with
the closure block; committed on `lane/{x}` with a conventional message.

DECISIONS WITH THE OWNER AWAY: never block. Judgment call → convene `/llm-council`; its
verdict binds *only if* it aligns with {guardrails}. Irreversible or guardrail-level choices
(new paid vendor, architecture reversal) are owner-decisions — do NOT council them; post for
the owner and defer that WO, continue the rest.

COMMS: `AGENT_ORG_DB={comms-db} {comms.py} <cmd> …`, bodies < 1800 chars. Progress to
dev-floor; milestones to c-suite. On the goal being provably met (or {stopClock}), post
`final-status: complete` (or `partial` + gap) to c-suite.

Now invoke the **marathon-org** skill (Skill tool, skill=marathon-org) scoped to THIS lane's
queue to drive the loop. Where marathon-org defaults conflict with the rules above, THESE WIN
(esp.: no idle waves; walk the chain directly, no nested spawn; territory is hard).
```

## Lane E Template (automated merge + cleanup — runs the morning after)

```
You are LANE E (MERGE & CLEANUP) for the /workday run {date}, acting as John (Chief Engineer)
for merge review. Working dir = the MAIN checkout (`cd {project-root}` and confirm; NOT any
../<repo>-lane-* worktree). The owner may be non-technical and watching — explain in plain
words; STOP for a yes/no ONLY where this says to.

PRE-FLIGHT (report a short table, then continue):
1. Confirm trunk branch, tree clean. If dirty: STOP, explain in plain words.
2. Read c-suite for the {n} `final-status` posts (one per work lane). Note complete vs
   partial (+ the stated gap). A silent lane → escalate for the owner and proceed with rest.
3. Per lane branch: `git log {trunk}..lane/{x} --oneline` commit count, map every commit to a
   WO in that lane's state-file `completed`. Flag mismatches in plain language.
4. Origin: pull --ff-only if origin ahead; if trunk local-only, note it, proceed.

MERGE ORDER (DO NOT REORDER — dependency order): lane/a-db → lane/b-backend → lane/d-api →
lane/c-frontend. (Schema first: migrations are prerequisites. Frontend last: consumes API.)

PER MERGE: `git checkout {trunk} && git merge --no-ff lane/{x} -m "merge(workday-{date}):
lane/{x}"`, then run that lane's verification suite from the trunk. Honor any project-specific
toolchain note (e.g. per-package test runs, PATH fixes).

CONFLICTS: `backlog/*.md` → UNION (keep every lane's closures; Next-ID header → take the
HIGHEST). ID collisions → should be zero (ranges pre-reserved); if any, renumber the
later-merged lane to the next free in its range with a note. Same-source-file conflict (rare,
disjoint territory) → STOP, post the diff for the owner, escalate. Suite red after a merge →
do NOT revert silently; post for the owner, mark ATTENTION-NEEDED, stop merging further lanes.

POST-MERGE CLEANUP (only after merges verify green):
1. Run the project's full smoke check. Report result.
2. Push trunk to origin only if the owner explicitly says "push". Else note local-only trunk
   is fine for one cycle.
3. `git worktree remove ../<repo>-lane-a-db` (+ b-backend, d-api). If any worktree tree is
   dirty: tell the owner what would be lost FIRST — do not force-remove silently.
4. `git branch -d lane/a-db lane/b-backend lane/d-api lane/c-frontend`.
5. Move `<runs-dir>` → `<archive>/{date}/` (the run is now closed).
6. Leave the comms DB alone (durable shared log).
7. CronDelete every safetyCronJobId in the lane state files.

CLOSING REPORT — post to c-suite for the owner: date; merge graph (branches, order, hashes);
verify pass/fail per merge; total WOs landed + IDs; backlog delta; per-lane goal MET /
PARTIAL (+ gap) per John's goal; ID collisions (expect 0); escalations; worktrees removed +
run archived: confirmed; origin: pushed/deferred. End the run.

If anything goes wrong: STOP, post for the owner, do not push, do not force.
```

## Launch card (`README.md`) — plain words, no git literacy assumed

Write it so a non-technical owner never types git. State, in plain language: what was set up
(N work orders, 4 isolated worktrees that "cannot collide", the run theme); that night, open
4 new sessions in one window and for each set the working folder to the listed lane path and
paste the matching PROMPT file as the first message, order-independent, then walk away (they
checkpoint and auto-resume after a session-limit pause via the safety crons; a full crash
means re-paste that one prompt — the state file resumes it); each lane stops by `<stop-clock>`
on its own; in the morning open one more session on the main folder and paste
`PROMPT-E-merge.md` (it merges all four safely and cleans up, pausing for a yes/no only if it
hits something it shouldn't decide alone); a bad night is fully recoverable — nothing is
pushed, the live app is untouched, the lane branches hold all the work until cleanup is
confirmed; and one verification line ("you should see four sessions each post a short status
within ~20 min; a red error + stop means that lane is safely parked — tell me in the morning").

## Hard rules

- **Disjoint territory is the safety guarantee.** A lane writing outside its globs can
  collide with another lane and lose work. Path-guard enforces it; the prompts restate it;
  Lane E assumes it.
- **Lane E is never optional.** Even a 2-lane night gets an automated Lane E. Never leave the
  merge to bare human git.
- **No idle waves.** Chain WOs back-to-back. Crons are for the long-session-limit reset and
  staggered to avoid re-tripping the API limit — not a pacing mechanism.
- **No nested spawn.** The lane session does all spawning (head implements, John reviews).
  Never write a prompt that asks a sub-agent to spawn a sub-agent.
- **Keep-last-1 cleanup runs on every fresh `/workday`** so no session re-reads a plan from
  days ago. The run dir is gitignored — archived/pruned freely.
- **Never overwrite `org.config.json`** (project-customized). Never self-modify
  `comms.py` / the path-guard hook — those are install-managed.
- **`--stop` is clean:** lanes finish their current WO then halt; it does not yank a
  sub-agent mid-edit.

## Companion: `/workday-watch`

`/workday-watch` is the optional C-suite surveillance 5th session. It reads the in-flight run
(its `<runs-dir>` + per-lane state + worktrees + comms) and, on a periodic tick, has the
responsible C-suite agent inspect each lane for **breaking / drifting / misunderstanding /
hallucinating**, then posts `[WATCH][LANE-X]` corrections the lanes obey (the
WATCH-integration hook above is what makes that work). It never edits lane code or git. Start
it any time after the lanes launch; the 4 lanes + Lane E run fine without it.
