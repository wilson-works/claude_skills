---
name: run-builder
description: "Standardized parallel-run builder. One command composes a whole run of a named shape (AB / ABC / ABCD / ABCDE) for a named shift (night / morning / afternoon / evening), emits the run object as a COMMITTED directory before launch (RUN.md, PROMPTS.md, per-lane prompt files, fixed row queues, ledger row, empty evidence and next-shift dirs), provisions one git worktree per building lane, opens the run-NN comms channel, and makes the prep commit. The last lane is always a non-building GATE with sole terminal authority: builders mark AWAITING_VERIFICATION, only the gate marks VERIFIED. The skill does NOT launch lanes - the owner pastes. Supersedes /workday, /parallel-session and /fable-marathon as the launch path. Invoke with /run-builder <shape> [theme] --shift <night|morning|afternoon|evening> [--repo <name>] [--stop-at HH:MM] [--from-handoff <path>] [--dry-run] [--status] [--cleanup]. Use whenever the user wants an overnight run, a parallel run, 'lanes', 'tonight's run', an afternoon or evening shift, or asks to compose the next shift."
---

# Run Builder

One skill, one command, four shapes, four shifts. It turns "compose tonight's run" into a
committed directory the owner pastes from.

**Design authority:** `D:\Hub\50-AI\fleet-ops\notes\2026-08-31-run-builder-design.md` (Victor,
2026-08-31). Evidence base: `…\2026-08-31-run-standard-research.md`. Where this file and the
spec disagree, the spec wins and this file is the bug.

**One sentence:** `/run-builder` replaces three incompatible hand-written 4-lane dialects with
one run object, one gate, one message bus, and seven mandatory lines.

## Command surface

```
/run-builder <shape> [theme] --shift <night|morning|afternoon|evening>
             [--repo <name>] [--stop-at HH:MM] [--from-handoff <path>]
             [--dry-run] [--status] [--cleanup]
```

| Flag | Meaning |
|---|---|
| `<shape>` | `AB` `ABC` `ABCD` `ABCDE`. **No other shapes.** See "Why no new shapes". |
| `[theme]` | the run's north star, one phrase. Becomes the MUST-MEET goal's subject. |
| `--shift` | the shift the run **will execute in**, not when you type the command. `--shift morning` is legal and means "build the Afternoon run now, during the attended window." |
| `--repo` | resolved under the code zone at runtime. Omit to use the current repo. |
| `--stop-at` | wall-clock stop. Default per shift: night 08:00, morning 11:00, afternoon 17:00, evening 22:00. |
| `--from-handoff` | boot from a prior run's `HANDOFF.md`; its do-not-re-verify list is folded into every prompt. |
| `--dry-run` | print the plan — shape, lanes, legs, queues — and write nothing. |
| `--status` | read the newest `runs/run-NN/`, print per-lane row state, commits, unread comms, gate progress. Stop. |
| `--cleanup` | remove merged run worktrees and sweep scratch. Never force-removes a dirty worktree. Stop. |

## What it emits — the run object, committed BEFORE launch

```
<repo>/runs/run-NN/                 # committed, NOT gitignored
  RUN.md                 shape, theme, shift, stop-at, MUST-MEET goal in named judged legs
  PROMPTS.md             every lane prompt in one file (the owner pastes from here)
  prompts/PROMPT-<X>.md  one per lane, content identical to its PROMPTS.md section
  queue/<x>.md           that lane's FIXED row queue - no lane invents work
  LEDGER-ROW.md          the row appended to the fleet-ops runs ledger
  evidence/<lane>/       created empty; lanes write proof here
  next-shift/            created empty; the gate's final turn fills it
  HANDOFF.md             created empty; the gate fills it at close
```

Plus one row appended to `<hub>\50-AI\fleet-ops\runs\LEDGER.md`, and **one prep commit**
(`run-NN prep: <shape> <theme> <shift>`) before the owner pastes anything.

The ledger row is the **dispatcher-visible run-open marker** and must live on the branch the
run starts from — a marker invisible from the dispatcher's branch is how run-54 got a duplicate
dispatch.

**The skill does not launch lanes. The owner pastes.** One-shot lanes, not self-loops.

## Prerequisites

- **Requires agent-org `comms.py` >= the 2026-08-31 lane-roster patch** (`LANE_AGENTS` +
  `run-NN` channel matching). If a repo's `.claude/comms/comms.py` predates it, lane agents die
  with `unknown agent 'lane-a'` on the first post — re-copy it from the agent-org skill
  (`C:\Users\patri\.claude\skills\agent-org\comms\comms.py`).
- `scratch-run.ps1` present under `<hub>\50-AI\fleet-ops\policy\` — `new-run.ps1` refuses to
  build a run that cannot test cleanly.

## Phase order

```
0  parse flags; --status / --cleanup short-circuit and stop
1  resolve hub root + code zone + repo (runtime probe, never hardcoded)
2  read --from-handoff if given; extract the do-not-re-verify list
3  decompose the theme into the MUST-MEET goal and its NAMED JUDGED LEGS
4  decide gate modality from the legs (browser vs suite-only) + name the 2 rule-70 re-samples
5  build one FIXED row queue per building lane, territory-disjoint
6  run scripts\new-run.ps1  -> scaffold, worktrees, comms channel, ledger OPEN row, prep commit
7  render RUN.md, prompts/PROMPT-<X>.md, PROMPTS.md from the templates
8  amend the prep commit to include the rendered files; verify by `git log -1` grep
9  print the launch card: what to open, what to paste, what recovery is
```

Steps 3-5 are the judgment work; everything else is mechanics the scripts own.

---

## Lane roles per shape

The **last lane is ALWAYS the non-building GATE** with sole terminal authority. Builders mark
`AWAITING_VERIFICATION`; only the gate marks `VERIFIED`. Builder != verifier is doctrine.

| Shape | A | B | C | D | Gate |
|---|---|---|---|---|---|
| `AB` | full-stack builder | — | — | — | **B** gate |
| `ABC` | frontend | backend | — | — | **C** gate |
| `ABCD` | frontend | backend-1 | backend-2 | — | **D** gate |
| `ABCDE` | frontend | backend | schema/migrations | api/integration | **E** gate |

The gate never edits product code. It may write only under `runs/run-NN/` and backlog files.

### Why no new shapes

The run evidence supports exactly **one axis of variation** — how many builders feed one gate.
Adding a shape without a run behind it is precisely the drift this skill exists to stop: three
incompatible "4-lane" definitions (workday, parallel-session, fable-marathon) is what the
inventory found. A fifth shape needs a run first, then a spec amendment, then this table.

### Gate modality — decided at build time, written into RUN.md

Decided by the run's MUST-MEET legs, **before** any builder runs. Never chosen afterward by
whoever just read the builders' reports.

- **Browser gate** — required if ANY leg is user-facing / visual / portal-session.
  Mandatory: `new_page` with `isolatedContext: "lane-<X>-gate"` from the **first** navigation.
  Also mandatory: re-mint magic links after any backend restart (a restart kills portal
  sessions and reads as a 404 data bug); read input **values**, not `innerText` (a grid of
  `<input>` cells reads as empty to a text probe — it cost a false P1).
- **Suite-only gate** — legal only when every leg is API / schema / logic. The gate runs an
  **independent serial full-suite sweep against a frozen baseline**, not targeted sampling.
  Sweeps have caught what sampling missed.
- **Both modalities additionally run rule-70 different-modality sampling on at least 2 legs:**
  a leg proven by browser is re-sampled by DB/query, and vice versa. Name the two in RUN.md.

---

## Isolation

**Default: git worktrees, one per building lane.** The gate runs in the main checkout,
read-only on product code. The evidence is unambiguous: shared-tree partitions buy every
shared-index hazard, and we paid for them repeatedly — pathspec commits, `index.lock`
contention, commits that reported exit 0 without landing.

**The one exception:** `AB` and `ABC` on a single-repo run **where the lanes share one running
dev service** (e.g. a backend on :5001) may run shared-tree with `comms.py` path claims. A
shared service dies with its host lane, so worktree separation buys little when one process is
the real shared resource. The cost: the shared-index mitigations in the mandatory lines become
**load-bearing rather than belt-and-suspenders**. The exception is invoked only at build time,
by the skill, via the explicit `-SharedTree` flag, with the shared service named in `RUN.md`.
Absent that flag, worktrees. A lane never elects shared-tree at runtime.
`ABCD` and `ABCDE` are **always** worktrees;
`new-run.ps1` refuses `-SharedTree` for them.

> **Dissent on the record (Victor, spec §10):** the exception is carved on an argument, not on
> a run. If the conformance eval or any of the first five runs shows a shared-index failure on
> an `AB` or `ABC` run, **the exception is deleted and worktrees become unconditional** — no
> further adjudication. Owner of that call: Victor.

**Concurrency cap: 4 building lanes max on HQ.** D: is a spinning HDD and multi-lane runs
seek-thrash it. `new-run.ps1` enforces the cap.

### Path resolution — runtime, never hardcoded

Two things differ between machines, not one:

| | HQ (Studio_Omen) | ENGINE / FIELD |
|---|---|---|
| Hub root | `D:\Hub\` | `C:\Hub\` |
| code zone | `20-Coding\`**`Projects`**`\` | `20-Coding\`**`Active`**`\` |

Probe `D:\Hub\CLAUDE.md` then `C:\Hub\CLAUDE.md` for the root — **string concat, not
`Join-Path`**, so a missing drive does not throw. Probe `Projects\` then `Active\` for the code
zone, **failing loudly if neither exists**. A silent fall-through is how a runner "works" while
resolving nothing. Reference implementation: `scripts\new-run.ps1` -> `Resolve-HubRoot` /
`Resolve-CodeZone`.

### Scratch policy — the skill wires it, the lane cannot forget it

`D:\Hub\50-AI\fleet-ops\policy\hq-scratch-policy.md` is canonical and is **never duplicated
into a prompt**. Any lane that runs tests gets this line rendered into its prompt, with the
wrapper path resolved from the live hub root:

```powershell
<hub>\50-AI\fleet-ops\policy\scratch-run.ps1 -Command 'python -m pytest --basetemp=$env:SCRATCH_RUN_DIR\pytest <roots>'
```

**Single quotes are required** — `$env:SCRATCH_RUN_DIR` must reach the wrapper unexpanded; the
wrapper sets it, the caller cannot. Never pass a `--basetemp` or `PYTEST_DEBUG_TEMPROOT` that
already exists, never reuse a `run-*` dir, never set either outside the wrapper. A rotted
basetemp measured 250x slower on identical work. `new-run.ps1` refuses to build a run if
`scratch-run.ps1` is missing.

Also carried: `npx <tool>` is forbidden if `<tool>` appears anywhere in `package.json` — grep
first, and treat an unreadable `package.json` as a hit.

---

## Inner-session messaging

**The `comms.py` SQLite bus is the single mechanism.** The markdown queue reinvention —
`work-queue.md`, `done.md`, `findings.md`, `watch-log.md` as *coordination surfaces* — is
retired. Markdown files survive only as **artifacts the gate writes**; they are never read for
coordination. This kills the third dialect.

Channel per run: `run-NN`. Agents: `lane-a` … `lane-e`.

### Five verbs. The subject line starts with the verb.

| Verb | Who | When | Body must contain |
|---|---|---|---|
| `STATUS` | every lane | every row start and row close | row id, one line, current commit sha |
| `BLOCKED` | builders | never speculatively | the evidence: command + output excerpt. **A blocker claim without evidence is not a blocker.** |
| `CROSS-REQ` | builders | needs another lane's territory | target lane, exact path(s), why it cannot be avoided |
| `VERIFY` | builders -> gate | a row reaches AWAITING_VERIFICATION | row id, commit sha, evidence paths under `evidence/<lane>/` |
| `WATCH` | gate -> any lane | the gate observes drift or a hazard | the instruction. **WATCH is obeyed, not debated.** |

```bash
python .claude/comms/comms.py read run-NN lane-a --unread
python .claude/comms/comms.py post run-NN lane-a --wo <row> --subject "VERIFY <row>: <one line>" "<body>"
```

**Cadence: post on state change, not on a timer.** Read the inbox at the top of every row and
after every `VERIFY`. No polling loops.

**How the gate consumes it:** `read run-NN --unread` -> drain the `VERIFY` queue FIFO -> judge
against the **named leg** (not the builder's narrative) -> post `VERIFY-PASS` or
`VERIFY-BOUNCE` with the failing evidence -> **then, and only then**, run its own sweeps.
Bounces are expected and healthy; the single bounce in run-63 is the proof the gate was real.
`VERIFY-PASS` / `VERIFY-BOUNCE` are the gate's two replies on the `VERIFY` verb, not additional
verbs. No lane invents a sixth verb.

## Looping

Per-lane wave loop (one lane, its own session):

```
read inbox -> claim next row from queue/<x>.md -> build -> test (name every root explicitly)
  -> commit (explicit pathspec, -F message file, judge by `git log -1` grep of the marker)
  -> write evidence/<lane>/<row>-<fresh-name>.* -> post VERIFY -> post STATUS -> repeat
```

In-session cron ticks are allowed for a lane's **own** session. **No planner-registered recovery
crons, ever.** There are zero recorded successful automated recoveries.

### Honest recovery table — goes in every RUN.md and every launch card

| Failure mode | What a cron can do |
|---|---|
| Idle at context limit (session full, account has capacity) | **works** — but only if the cron lives inside that lane's own session |
| Wedged tooling | **cannot** — needs a NEW session, which a cron firing inside the existing one cannot create |
| Usage limit (account capacity exhausted) | **cannot — self-defeating.** A cron fires by spending the capacity a usage limit has removed. What recovers the run is the limit window resetting: time, not design |
| Full session crash / process death | **cannot** — the cron died with the session |

**Recovery is the owner re-pasting `runs/run-NN/prompts/PROMPT-<X>.md`.** That is exactly why
prompts are files and not chat scrollback. Never soften this in a launch card.

---

## Shifts

Only four things change between shifts. Everything else is identical — that is the point.
Full detail in `reference\SHIFTS.md`; the skill renders the matching block into every prompt.

| | **Night** 22:00->morning | **Afternoon** 11:00->17:00 | **Evening** 18:00->22:00 | **Morning** ~10:00 |
|---|---|---|---|---|
| Pings | **none** | ntfy allowed; informational only, never permission-blocking | none (owner present) | n/a |
| Blockers | ledger the blocker, **reroute** to the next row, never stop | ping ntfy once, **continue** | ask the owner in-channel | attended |
| Scope | full queue, up to 4 builders | full queue | **short work** — 1-2 rows per lane, gate-heavy | no build |
| Typical shape | ABCD / ABCDE | ABC / ABCD | AB / ABC | runs `/run-builder --shift afternoon` |
| Owner acts | pastes at 22:00 | pops in if free; 17:00 check-in | 22:00 launches Night | reviews Night, preps Afternoon |

**Night additionally forbids anything requiring an owner ruling, and any deploy.** Deploy is
always the owner's attended act, in every shift. **Findings are not authorization.**

### The ntfy ping (Afternoon only)

Reference the existing fleet pattern; **never embed server or topic values** anywhere — not in
this skill, not in a prompt, not in a run object. Config is read at
`<hub>\00-Inbox\_Review\fleet-notify.local.json`; the topic is an unauthenticated credential
and appears in no tracked file. Prefer the wired sender `fleet-ntfy-notify.ps1`, which resolves
the config itself and never prints the topic.

Rules: **one line**, lead with the outcome, name the artifact path. **No secrets, no client
PII, no money figures.** Completion or blockage/failure only — never a progress tick. Ping,
then **continue**; a lane that pings and waits has violated the shift.

## The final turn of the shift — the only automation

The **gate lane**, at `--stop-at` minus 20 minutes, stops verifying and writes:

```
runs/run-NN/next-shift/PROMPTS.md   paste-ready prompts for the next shift run
runs/run-NN/next-shift/RUN.md       proposed shape + theme + MUST-MEET legs
runs/run-NN/HANDOFF.md              gotchas + what was verified (next run MUST NOT re-verify it)
runs/run-NN/REPORT.md               what shipped; numbers re-read from artifacts at write time
runs/run-NN/OWNER-QUESTIONS.md      decisions needed, with a blank ## RULINGS section
```

Then `scripts\close-run.ps1`: tag `run-NN-close` at a named commit, flip the LEDGER row, delete
scratch and **verify the deletion**, emit `evidence/gate/CONFORMANCE.json`.

**The owner's check-in reads, in this order:** `REPORT.md` -> `OWNER-QUESTIONS.md` ->
`next-shift/PROMPTS.md`. That is the entire ritual: review, feedback, paste.

---

## The seven MANDATORY lines

Every lane prompt carries these **verbatim**. Single source of truth:
`reference\MANDATORY-LINES.md`. Builders carry 1-7; the gate carries 1-6 plus the gate
checklist. Each line has a recorded failure behind it and none can be enforced mechanically at
prompt time — which is exactly why they are in the prompt.

```
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

**Lives in the skill mechanics, NOT in prompts** (the skill does it, so a lane cannot forget):
worktree provisioning, `--basetemp` wiring, scratch-policy caps, run-dir scaffold, ledger row,
prep commit, comms channel creation, concurrency cap.

**Lives in the GATE checklist, NOT in builder prompts:** zombie-process enumeration by
`--basetemp` via `Win32_Process` with an **ownership check before any kill**; the
clean-worktree discriminator for suspicious reds; rule-70 different-modality sampling; the
frozen-baseline serial sweep; verified scratch deletion; the conformance JSON. Full text in
`templates\PROMPT-GATE.md.tmpl`.

---

## The named eval — run conformance

No AI-system change ships without a named eval. This one is **run-conformance**.

For the first 5 runs built by this skill, the gate lane emits
`runs/run-NN/evidence/gate/CONFORMANCE.json` scoring six **binary** checks:

| # | Check |
|---|---|
| 1 | run object committed pre-launch |
| 2 | lane count == shape |
| 3 | gate lane non-building |
| 4 | every lane prompt carries its MANDATORY block verbatim — builders lines 1-7, gate lines 1-6 plus the gate checklist |
| 5 | next-shift prompts written before close |
| 6 | ledger row flipped at close |

**Pass bar: 6/6 on 5 consecutive runs.** `close-run.ps1` computes and writes it.

**The failure mode it prevents:** the builder drifting back into hand-written per-night prompts
— exactly the divergence that produced three incompatible 4-lane dialects.

Status is binary against a written standard. Never report conformance as a percentage.

---

## Files in this skill

| Path | What |
|---|---|
| `SKILL.md` | this file |
| `reference\SHIFTS.md` | the four shifts, expanded; the block rendered into every prompt |
| `reference\MANDATORY-LINES.md` | the seven lines, single source of truth, with per-line provenance |
| `templates\RUN.md.tmpl` | the run object's spine |
| `templates\PROMPT-BUILDER.md.tmpl` | builder prompt; carries lines 1-7 verbatim |
| `templates\PROMPT-GATE.md.tmpl` | gate prompt; lines 1-6 + the gate checklist + the final turn |
| `templates\LEDGER-ROW.md.tmpl` | the ledger row + its column contract |
| `templates\HANDOFF.md.tmpl` | close-out handoff; the do-not-re-verify list |
| `templates\NEXT-SHIFT-PROMPTS.md.tmpl` | `next-shift/PROMPTS.md` shape |
| `scripts\new-run.ps1` | scaffold, hub/code-zone resolution, worktrees, comms channel, ledger row, prep commit |
| `scripts\close-run.ps1` | tag, ledger flip, scratch delete + verify, CONFORMANCE.json |

Mirror (so ENGINE and FIELD pick it up):
`D:\Hub\50-AI\fleet-ops\templates\run-builder\`. **Both copies ship together.** If you change
one, change the other in the same commit.

## Disposition of the skills this replaces

| Skill | Disposition | Migration |
|---|---|---|
| `workday` | **SUPERSEDED as a launch path** | `/workday [theme]` -> `/run-builder ABCDE [theme] --shift night`. Worktree provisioning and the honest-recovery table are absorbed; the Lane E merge becomes the gate close-out. |
| `parallel-session` | **SUPERSEDED as a launch path** | `/parallel-session [theme]` -> `/run-builder ABCD [theme] --shift night --repo barkey`. The Lane A council role is **deleted** — an orchestrator lane is neither a builder nor a gate. Lane B's browser-verify role becomes the gate. Its five Universal Rules survive as MANDATORY lines 1-7. |
| `fable-marathon` | **SUPERSEDED, hard** | Markdown comms and lane-recovery crons are both retired. -> `/run-builder ABC --shift night`. **Do not port its cron schedule.** |
| `marathon-org` / `marathon-orders` / `work-orders` | **STAY** | the per-lane inner loop; `/run-builder` composes them. Unchanged. |
| `workday-watch` and the watch skills | **STAY** | attended-window tooling, orthogonal to run construction. Repoint at `runs/run-NN/` instead of `.tmp/workday-<date>/`. |
| `hq-scratch-policy` | **STAY, canonical** | called by the skill mechanics; never duplicated into a prompt. |

The three superseded skills keep their full bodies and carry a deprecation banner. They are
**not stubbed** — in-flight runs still read them, and their lessons are the evidence base.
Deleting the vestigial skills (`crew`, nested dup dirs, the `claude_skills` mirror,
`ceo-deliverables.html`) is a **separate WO**; do not bundle it here.

## Hard rules

- **The run object is committed before the owner pastes anything.** No prep commit, no launch.
- **The gate never builds.** If the gate edits product code, the run has no gate.
- **Only the gate marks `VERIFIED`.** Builders mark `AWAITING_VERIFICATION`, always.
- **Deploy is always the owner's attended act.** A green gate is a finding, not an
  authorization. In every shift, including the attended ones.
- **No new shapes** without a run behind them and a spec amendment.
- **No cron registration** for shift transitions. **No recovery crons.** Ever.
- **No new markdown coordination queue.** The bus is the mechanism; markdown is an artifact.
- **No hardcoded hub root, no hardcoded code zone.** Probe both, fail loudly.
- **A lane never invents work.** The row queue is fixed at build time.
- **Never soften the recovery table** in a launch card. A failsafe that cannot fire, next to a
  card that says "walk away," buys unearned trust.
