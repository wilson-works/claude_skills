---
name: marathon-condenser
description: "Long-running walkaway session that condenses a markdown-based work order backlog — merging duplicates, closing already-completed items, rewriting vague entries, and pruning stale ones. Goal: reduce the open work order count by at least 25%. Invoke with /marathon-condenser [--stop] [--status] [--continue] [--target 25] [dry-run]."
---

# Marathon Condenser Skill

## Configure for your project

Before using this skill, swap these placeholders for your project values:

- `<project-root>` — absolute path to your project root
- `<backlog-dir>` — absolute path to the directory holding `bugs.md`, `features.md`, `design.md`, `tech-debt.md`, `completed.md`
- `<state-dir>` — absolute path where this skill writes its state JSON and lock file
- `<memory-file>` — optional path to a memory/context file the agent reads to know which features are SHELVED, renamed, or superseded (e.g. `<project-root>/.claude/MEMORY.md`). Skip if you don't keep one.
- `<project-md>` — optional path to your top-level project context file (e.g. `<project-root>/CLAUDE.md`, `<project-root>/README.md`)
- `<temp-dir>` — temp directory for orchestration scripts (e.g. `<project-root>/.tmp/condenser`)

The backlog files are expected to use the convention:
- `### [PREFIX-NNN] Title` for each item
- `<!-- Next ID: N -->` comment near the top of the file as the next-id counter

## Purpose

Runs a sustained, unattended condensing loop over a markdown backlog. Each wave:

1. Picks the next **condense strategy** from a rotation queue
2. **Reads** a chunk of the backlog + `completed.md` + relevant code
3. Spawns an **Opus condenser agent** with direct Edit permission on backlog files
4. The agent applies decisions: CLOSE (already done), MERGE (duplicates), REWRITE (vague), PRUNE (stale), KEEP
5. Tracks running reduction vs a target (default **25%**)
6. Loops via **CronCreate** every 30 minutes until target met or all strategies exhausted

Use this skill when the backlog has grown past a couple hundred open items or feels redundant.

## Invocation

```
/marathon-condenser                    Start fresh, default 25% reduction target
/marathon-condenser --target 30        Override reduction target (percent)
/marathon-condenser --stop             Pause after current wave completes
/marathon-condenser --status           Show current wave, reduction progress
/marathon-condenser --continue         Manual re-entry if cron misfired
/marathon-condenser dry-run            Show baseline counts + strategy rotation, stop
```

## State File

```
<state-dir>/marathon-condenser-state.json
```

Written via the **temp JS file pattern**.

Schema:
```json
{
  "sessionId": "condenser-YYYY-MM-DDTHH-MM",
  "status": "running | paused | complete | aborted",
  "paused": false,
  "cronJobId": "cron_xxx",
  "startedAt": "ISO timestamp",
  "targetReductionPct": 25,
  "baseline": {
    "bugs": 11,
    "features": 198,
    "design": 41,
    "techDebt": 47,
    "total": 297
  },
  "currentWave": 0,
  "strategyQueue": [
    { "strategy": "completed-check", "file": "features.md", "chunk": "1-50" },
    { "strategy": "dedupe-merge",    "file": "features.md", "chunk": "1-50" },
    { "strategy": "vague-rewrite",   "file": "features.md", "chunk": "1-50" }
  ],
  "rotationIndex": 0,
  "waves": [
    {
      "waveNumber": 1,
      "strategy": "completed-check",
      "file": "features.md",
      "chunk": "1-50",
      "startedAt": "ISO",
      "completedAt": "ISO",
      "status": "complete",
      "itemsInspected": 48,
      "closed": 6,
      "merged": 3,
      "rewritten": 4,
      "pruned": 1,
      "kept": 34,
      "netRemoved": 10,
      "reasoning": "brief summary line from agent"
    }
  ],
  "cumulative": {
    "closed": 0,
    "merged": 0,
    "rewritten": 0,
    "pruned": 0,
    "netRemoved": 0,
    "currentTotal": 297,
    "reductionPct": 0
  }
}
```

## Backlog Location

```
<backlog-dir>/
  bugs.md
  design.md
  features.md
  tech-debt.md
  completed.md
```

The condenser has **write permission** on all four open backlog files. It does not modify `completed.md` except to append items it closes.

---

## The Five Condense Strategies

Each wave runs ONE strategy against ONE chunk of ONE backlog file.

1. **completed-check** — For each item, grep the codebase for the named components/files/functions and check `completed.md` for structural matches. If the work is already done: move the entry to `completed.md` with a `- **Resolution**: verified-by-condenser` tag. Biggest reduction lever.

2. **dedupe-merge** — Find items targeting the same component, feature, collection, or gap. Merge into one entry: keep the oldest ID, fold details, delete the rest.

3. **vague-rewrite** — Find items whose `- **Details**` is under ~200 chars, missing file paths, or uses generic language. Rewrite with concrete file paths and action items.

4. **scope-normalize** — Find items that are epics in disguise (5+ files, 3+ phases, "and" repeatedly linking distinct features). Flag with a scope-flag for human review. Inverse: find narrow items that belong together and merge them.

5. **stale-prune** — Find items superseded by architecture changes, retired features, or terminology renames recorded in `<memory-file>`. Remove with a pruned tag. Examples: items referencing deleted files, items referencing retired feature names.

---

<!-- STATIC BOUNDARY: everything above this line is stable across cron ticks. Everything below changes each tick. -->

## Workflow

### Phase 0: Invocation Parsing

- `--stop`: read state, mark `paused: true`, `CronDelete`, delete lock, print summary, stop.
- `--status`: pretty-print baseline, cumulative changes, current reduction %, waves completed. Stop.
- `--continue`: skip directly to Phase 3.
- `dry-run`: run Phase 1 through baseline counting and strategy queue generation, print plan, stop.
- `--target N`: override default 25% reduction target.
- No state file: fresh start, continue to Phase 1.
- State file present with `paused: false`: cron re-entry, skip to Phase 3.

#### Phase 0.1: Stale state detection

1. **Lock file staleness**: If `<state-dir>/scheduled_tasks.lock` exists with PID dead or older than 4 hours, delete silently.
2. **Cron consistency**: If state has `status: "running"` and a `cronJobId` not present in `CronList()` AND state has not been touched in >60 minutes, prompt to reset.
3. **12-hour hard cap**: Auto-abort if `startedAt` > 12 hours ago.

---

### Phase 1: Fresh Start (user is present)

**Step 1 — Count baseline**

Grep each backlog file for `^### \[` to count open work orders.

```bash
node -e "
const fs = require('fs');
const base = '<backlog-dir>/';
const files = { bugs: 'bugs.md', features: 'features.md', design: 'design.md', techDebt: 'tech-debt.md' };
const counts = {};
let total = 0;
for (const [key, f] of Object.entries(files)) {
  const c = fs.readFileSync(base + f, 'utf8');
  const n = (c.match(/^### \[/gm) || []).length;
  counts[key] = n;
  total += n;
}
counts.total = total;
console.log(JSON.stringify(counts));
"
```

**Step 2 — Build strategy queue**

For each file, generate a strategy rotation in priority order. Early strategies have the biggest reduction payoff.

For the largest file, chunk into groups of ~50 items and repeat the strategy sequence across chunks:

```
Chunk 1-50:   completed-check -> dedupe-merge -> vague-rewrite
Chunk 51-100: completed-check -> dedupe-merge -> vague-rewrite
...
```

For smaller files, one chunk each, full strategy sequence.

Stop building the queue once cumulative projected reduction could plausibly hit the target. Rough heuristic: ~8% per completed-check on a noisy file, ~3% per dedupe-merge, 0% per rewrite, 2% per prune. Err toward queueing too many waves; the skill auto-stops when target is hit.

**Step 3 — Present the plan**

```
MARATHON CONDENSER PLAN
========================
Baseline (open work orders):
  bugs.md       11
  design.md     41
  tech-debt.md  47
  features.md   198
  TOTAL         297

Target reduction: 25% (74 items)
Target end state: ~223 open items

Strategy queue ([N] waves, ~20-30 min each)
Cron interval: 30 minutes (fires at :13, :43)
Auto-stop: when reduction target met OR queue exhausted

For dry-run: stop here.
```

**Step 4 — Pre-flight settings update (REQUIRED)**

Update `~/.claude/settings.json` `permissions.allow`:

```json
"Edit(<backlog-dir>/**)",
"Write(<backlog-dir>/**)",
"Edit(<state-dir>/marathon-condenser-state.json)",
"Write(<state-dir>/marathon-condenser-state.json)"
```

**Step 5 — Confirm**

Ask: "Ready to launch marathon condenser with target [N]% reduction from [baseline]? [y/n]"

**Step 6 — Write initial state file**

Use the temp JS file pattern.

**Step 7 — Register the cron loop**

Use CronCreate:
- `cron`: `13,43 * * * *`
- `durable`: `true`
- `recurring`: `true`
- `prompt`:

```
This is an automated marathon-condenser loop tick.

RESOURCE DISCIPLINE — MANDATORY:
- Do NOT invoke any mcp__chrome-devtools__* tools in this tick. The condenser works against files and codebase greps only.
- Always run Phase 3a (self-heal / terminal-state check) FIRST. If any terminal condition is met, CronDelete and exit.

WORKFLOW:
1. Read the state file at <state-dir>/marathon-condenser-state.json
2. Read the full marathon-condenser skill instructions
3. Execute Phase 3 (Wave Loop Tick).

Do not ask the user for confirmation.
```

Write the returned `cronJobId` into the state file.

**Step 8 — Launch Wave 1 immediately**

Go to Phase 2.

---

### Phase 2: Launch Wave

**Step 1 — Read the target chunk**

Load the target backlog file. Parse into `### [ID]` blocks. Slice to the chunk range. Also read `completed.md` (last 30 entries) for pattern-matching against prior resolutions.

**Step 2 — Read project memory**

Read `<memory-file>` if it exists, so the agent knows which features are SHELVED, renamed, or superseded. Also read `<project-md>` if relevant.

**Step 3 — Spawn the condenser agent**

Use Agent with `subagent_type: general-purpose`, model Opus, **not** isolated (it edits files in the live backlog directory). The agent has Edit/Write permission on `<backlog-dir>/**` (pre-approved in Phase 1) and can grep/read the codebase freely.

**Step 4 — Parse manifest, update state**

Extract the `CONDENSER_MANIFEST_START...CONDENSER_MANIFEST_END` block. Parse fields. If missing or malformed: mark wave failed, do not advance the rotation index, log. After two consecutive failures on the same entry, skip it.

**Step 5 — Verify the edits**

Re-count open items in the target file. Compare to expected. Trust the observed count over the agent's claim.

**Step 6 — Update state file**

Push wave entry, increment cumulative counters, update `currentTotal` and `reductionPct` from the re-count.

**Step 7 — Target-hit check**

If `cumulative.reductionPct >= state.targetReductionPct`: set `status: "complete"`, go to Phase 4 immediately.

**Step 8 — Report wave results**

```
MARATHON CONDENSER WAVE [N] COMPLETE
======================================
Strategy: [strategy] on [file] chunk [range]
Items inspected: [N]
  Closed (done):    [N]
  Merged:           [N]
  Rewritten:        [N]
  Pruned (stale):   [N]
  Kept:             [N]
Net removed:        [N]
Agent reasoning:    [one-line]

Cumulative reduction: [N] items removed ([X]% of baseline)
Target: [25]% — [MET | X% to go]
Next wave in ~30 min: [next strategy]
```

---

### Phase 3: Wave Loop Tick (cron re-entry)

**3a. Self-heal / terminal-state check (FIRST)**

Terminate with `CronDelete` if ANY of:

- State file missing
- `state.status === "complete" | "failed" | "aborted"`
- `state.paused === true`
- `state.cronJobId` empty or mismatched
- `state.startedAt` > 12 hours ago
- `state.cumulative.reductionPct >= state.targetReductionPct` (target hit, set complete, go to Phase 4)
- `state.rotationIndex >= state.strategyQueue.length` (queue exhausted, go to Phase 4)

Delete `<state-dir>/scheduled_tasks.lock` on termination.

Do NOT boot `chrome-devtools-mcp` in this tick — the condenser is pure file-and-grep.

**3b. In-progress check**

If the last wave entry has `status: "in-progress"`: stop.

**3c. Launch next wave**

Go to Phase 2.

---

### Phase 4: Marathon Complete

1. `CronDelete(state.cronJobId)`
2. Update state to `status: "complete"`.
3. Cleanup: delete lock file. Run a final re-count of all four backlog files; store in `state.finalCounts`.
4. Print final report:

```
MARATHON CONDENSER COMPLETE
============================
Session: [sessionId]
Started: [startedAt]
Completed: [now]
Waves completed: [N]

Baseline vs Final:
  bugs.md       11  ->  [N]
  design.md     41  ->  [N]
  tech-debt.md  47  ->  [N]
  features.md   198 ->  [N]
  TOTAL         297 ->  [N]

Reduction: [N] items ([X]% — target was [25]%)
  Closed as already done: [N]
  Merged duplicates:      [N]
  Rewritten for clarity:  [N]
  Pruned as stale:        [N]
```

If target was not hit, set `targetMet: false` and warn the user.

---

## Condenser Agent Prompt Template

Fill in `[PLACEHOLDERS]` before spawning. Self-contained.

```
You are an Opus condenser agent for a markdown work order backlog. You have ONE job: apply the [STRATEGY] strategy to [FILE] chunk [CHUNK] and return a manifest.

You have direct Edit and Write permission on:
  <backlog-dir>/*.md

You should edit those files directly. Do not produce diffs or snippets — make the edits yourself.

== CONTEXT ==

Working directory: <project-root>
Backlog directory: <backlog-dir>
Project memory:    <memory-file>  (read this to understand SHELVED / renamed / superseded features)
Project context:   <project-md>

== YOUR STRATEGY ==

Strategy: [STRATEGY]
Target file: [FILE]
Chunk: [CHUNK] (items [FROM]-[TO] in the file)

[INSERT STRATEGY-SPECIFIC INSTRUCTIONS]

== CHUNK CONTENT ==

The following [N] work orders are your chunk:

[FULL BLOCKS OF ### [ID] ITEMS IN THE CHUNK]

== RECENT COMPLETED ITEMS (for completed-check strategy) ==

The last 30 entries in completed.md:

[FULL BLOCKS FROM completed.md]

== PROJECT MEMORY EXCERPTS (for stale-prune strategy) ==

[EXCERPTS — list features that have been SHELVED, renamed, or superseded]

== MANDATORY PROCESS ==

Step 1: Read project memory and project context in full before touching anything.

Step 2: For each item in your chunk, apply the strategy's decision logic:

[STRATEGY-SPECIFIC DECISION LOGIC]

Step 3: Execute decisions by editing the backlog files directly:
  - CLOSE: Remove the ### [ID] block from the source file. Prepend a new entry to completed.md with today's date and a "Resolution: verified by condenser — [evidence]" field.
  - MERGE: Keep the oldest/lowest-ID item. Rewrite its **Details** to fold in unique content. Append "- **Merged**: [ID1], [ID2]". Remove merged-away items.
  - REWRITE: Replace the item's **Details** with a more concrete version citing specific file paths. Keep ID and other fields.
  - PRUNE: Remove the ### [ID] block. Add a pruned log entry in a code comment at the bottom of the file.
  - KEEP: No action.

Step 4: Re-verify the file parses cleanly.

Step 5: Return the MANIFEST block (exact format below).

== HARD RULES ==

- Never modify an item outside your chunk.
- Never modify a different backlog file. EXCEPT: CLOSE may append to completed.md.
- Never invent a Resolution. If you cannot point to specific evidence (commit hash, file path, completed.md entry, memory line), KEEP the item.
- For MERGE, the kept item's new details must not lose unique actionable content from the merged items.
- For REWRITE, do not change priority or ID. Only the Details field.
- Do not remove the `<!-- Next ID: N -->` comments at the top of backlog files.

== REQUIRED OUTPUT FORMAT ==

CONDENSER_MANIFEST_START
strategy: [STRATEGY]
file: [FILE]
chunk: [CHUNK]
items_inspected: [N]
closed: [N]
merged: [N]
rewritten: [N]
pruned: [N]
kept: [N]
net_removed: [N]
reasoning: [one-sentence summary]
closed_ids: [ID1, ID2, ...]
merged_groups: [[KEPT_ID, REMOVED_ID1, REMOVED_ID2], ...]
rewritten_ids: [ID1, ID2, ...]
pruned_ids: [ID1, ID2, ...]
CONDENSER_MANIFEST_END
```

### Strategy-specific decision logic

**completed-check:**
```
For each item, determine if the work is already done.

Check order:
1. Scan the last 30 completed.md entries for structural overlap.
2. If not found: grep the codebase for the component, file path, symbol, or collection named in the item's details.
3. If the referenced code exists AND clearly implements what the item asks for: CLOSE with evidence (specific file + approximate line range + matching behavior).
4. If the code does NOT exist, or the item references a still-open gap: KEEP.
5. Never CLOSE on guesswork. The bar is: "a reviewer could verify this in 30 seconds by reading the cited file."
```

**dedupe-merge:**
```
For each item, check overlap with another item in the chunk OR earlier in the file.

Overlap signals:
- Same component / file path mentioned
- Same data collection + same operation
- Same user-visible symptom under two IDs
- Same framing or buyer objection verbatim

When overlap is found:
- Pick the kept item: prefer oldest (lowest ID), or the one with more detailed notes, or more specific file path.
- Fold any UNIQUE actionable content from merged items into the kept item's Details.
- Mark merged-away items as MERGED and remove.
- Record: [KEPT_ID, REMOVED_ID1, REMOVED_ID2, ...]

Do not merge items targeting the same area but with meaningfully different scopes (API vs UI for the same feature are legitimately distinct).
```

**vague-rewrite:**
```
Vague signals:
- Details under 200 characters
- Generic verbs without specifics ("improve X")
- No file path
- References a concept without naming a component

When vague:
- Grep the codebase to find the actual files
- Rewrite Details to cite specific files, the concrete change required, and a one-line acceptance criterion
- Do NOT change ID or priority
- Do NOT add speculative scope

Mark as REWRITTEN. If intent is too unclear to safely rewrite, leave it and mark KEPT.
```

**scope-normalize:**
```
Overscoped signals:
- 5+ distinct files / components
- 3+ phases or sub-tasks
- "and" linking distinct features
- Plausibly >1 day of focused work

When overscoped: append "- **Scope flag**: epic — needs breakdown" in place. Do NOT split (needs human judgment). Mark as REWRITTEN.

Underscoped signals (siblings to combine):
- Two items targeting the same file for trivially different changes
- Two items describing the same UI nit in different words

When found: merge them.
```

**stale-prune:**
```
Stale signals:
- A feature explicitly SHELVED in <memory-file>
- A deleted or renamed component (grep — file does not exist)
- Old terminology renamed in <memory-file>
- A category that no longer exists

When stale: remove the item, mark PRUNED with a one-line reason.

Do NOT prune items that use old terminology but describe a still-open gap under the new terminology — REWRITE those instead.
```

---

## CronCreate Scheduling

```
cron: "13,43 * * * *"
durable: true
recurring: true
```

30-minute interval: chunk read (2 min) + agent analysis + edits (15-20 min) + verification + state update (2 min).

---

## Failure Modes

1. **Agent claims to CLOSE items that aren't actually done**: caught by the requirement that every CLOSE cite specific evidence. If a CLOSE without evidence appears in the manifest, downgrade to KEEP and revert the file edit using `git checkout`.

2. **Agent corrupts a backlog file**: after every wave, Step 5 re-counts. If counts return 0 or wildly different numbers, assume corruption, revert via `git checkout`, mark wave failed, advance.

3. **Cron leak**: stale detection in Phase 0.1 + self-heal in Phase 3a.

4. **Target unreachable**: if the queue exhausts before the target is hit, Phase 4 reports `targetMet: false` and suggests running again. Do not loop indefinitely.
