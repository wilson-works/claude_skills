---
name: marathon-orders
description: "Automated deep-work loop that spawns 1-2 Opus agents per wave, each completing ONE work order with a review-and-merge gate between waves. Designed for 4-8 hour unattended sessions. Invoke with /marathon-orders [category] [--wave N] [--stop] [--status]."
---

# Marathon Orders Skill

## Configure for your project

Before using this skill, swap these placeholders for values that fit your environment:

- `<your-project-backlog-path>` -- absolute path to the directory holding `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, `completed.md`
- `<state-dir>` -- absolute path to the directory where the marathon state file should live (e.g. `<project-root>/.claude`)
- `<project-root>` -- absolute path to the repository root the skill operates against
- `<PRODUCT_DESCRIPTION>` -- a short paragraph describing your product (positioning, stack, hard rules) that gets injected into the Opus agent prompt

## Purpose

Runs work orders as a sustained, unattended deep-work loop. Unlike `/work-orders` (which uses Sonnet and runs one session), this skill:

- Uses **Opus** for each agent -- deeper reasoning, better code quality, less spaghetti
- Runs **one work order per agent** -- no multitasking, full focus
- Loops via **CronCreate** -- fires every 20 minutes to check agents and launch next wave
- Gates every merge behind a **diff + build + confidence review** -- bad code cannot land
- Keeps the **main session lean** -- it only orchestrates and reviews, never executes

Use `/work-orders` for quick batches of 4-15 shallow items. Use `/marathon-orders` when you need depth: security fixes, complex features, multi-file architectural changes, or anything that has failed a Sonnet agent before.

## Invocation

```
/marathon-orders                     Start fresh, all categories, wave size 1
/marathon-orders bugs                Process only bugs
/marathon-orders features            Process only features
/marathon-orders tech-debt           Process only tech debt
/marathon-orders design              Process only design
/marathon-orders --wave 2            Use 2 concurrent agents (default 1)
/marathon-orders bugs --wave 2       Bugs only, 2 at a time
/marathon-orders --stop              Pause after current wave completes
/marathon-orders --status            Show current wave, queue depth, elapsed times
/marathon-orders --continue          Manual re-entry if cron misfired
/marathon-orders dry-run             Show prioritized queue without launching
```

## Backlog Location

```
<your-project-backlog-path>
```

Files: `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, `completed.md`

## State File

```
<state-dir>/marathon-state.json
```

Written exclusively via `Bash(node -e ...)` -- never via the Write tool. This keeps it inside the already-approved Bash permission scope, so no approval is needed during unattended cron ticks.

Schema:
```json
{
  "sessionId": "marathon-YYYY-MM-DDTHH-MM",
  "status": "running | paused | complete",
  "paused": false,
  "waveSize": 1,
  "waveNumber": 0,
  "category": "all | bugs | features | tech-debt | design",
  "cronJobId": "cron_xxx",
  "startedAt": "ISO timestamp",
  "queue": [
    { "id": "BUG-016", "title": "...", "priority": "critical", "category": "bugs", "details": "...", "context": "...", "attempts": 0 }
  ],
  "inFlight": [
    {
      "id": "BUG-016",
      "title": "...",
      "branch": "marathon/BUG-016",
      "startedAt": "ISO",
      "waveNumber": 1,
      "brief": {
        "hotspotFiles": ["path/to/rules", "path/to/handler.ts"],
        "priorArt": "BUG-012 used field mask pattern in rules",
        "callers": ["path/to/caller.ts"],
        "approach": "Add field-level allow constraint to the rule; enforce server-side in the handler",
        "avoid": "Do not solve this client-side -- writable at the data layer"
      }
    }
  ],
  "completed": [
    { "id": "BUG-020", "title": "...", "completedAt": "ISO", "resolution": "...", "confidence": 4, "filesModified": ["..."], "waveNumber": 2 }
  ],
  "failed": [
    { "id": "BUG-022", "title": "...", "reason": "...", "attempts": 1, "failedAt": "ISO", "waveNumber": 2 }
  ]
}
```

---

## Workflow

### Phase 0: Invocation Parsing

Parse flags before doing anything else:

- `--stop` flag: read state file. If it exists, write `paused: true` via node, call `CronDelete(state.cronJobId)`, print current wave status. If no state file, print "No marathon in progress." Stop.
- `--status` flag: read state file. Pretty-print: session ID, current wave, items in queue, in-flight agents with elapsed time, completed count, failed count. Stop.
- `--continue` flag: skip to Phase 3 directly -- use when the cron misfired and you want to manually resume.
- `dry-run` argument: run Phase 1 through queue-building, print the prioritized queue, stop before asking for confirmation.
- **No state file exists**: fresh start, continue to Phase 1.
- **State file exists and `paused: false`**: this is a cron re-entry, skip to Phase 3.

### Phase 1: Fresh Start (user is present -- the one human gate)

This phase runs once, while the user is still at the keyboard.

**Step 1 -- Prune completed.md**

Remove entries from `completed.md` older than 30 days. Use:
```bash
node -e "
const fs = require('fs');
const path = '<your-project-backlog-path>/completed.md';
const content = fs.readFileSync(path, 'utf8');
const cutoff = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
// Split on '### [' to get item blocks, filter by Completed date field
const header = content.split('### [')[0];
const blocks = content.split('### [').slice(1).map(b => '### [' + b);
const kept = blocks.filter(b => {
  const m = b.match(/\*\*Completed\*\*: (\d{4}-\d{2}-\d{2})/);
  return !m || m[1] >= cutoff;
});
const pruned = blocks.length - kept.length;
fs.writeFileSync(path, header + kept.join(''));
console.log('PRUNED:' + pruned);
"
```
Report how many were pruned.

**Step 2 -- Read and parse backlog**

Read the relevant backlog files (all four, or filtered by category arg). For each `### [ID]` block, extract:
- ID, title, priority (from `**Priority**: ...` field), category, full details, full context, and date added

**Step 3 -- Sort the queue**

Sort by:
1. Priority: critical > high > medium > low
2. Age: oldest (lowest ID number) first within same priority
3. Category: bugs > design > features > tech-debt

**Step 4 -- Present the queue**

```
MARATHON RUN PLAN
==================
Model: Opus | Wave size: 1 | Category: all

Queue (N items, highest priority first):

 1. [BUG-016] critical -- short title
 2. [BUG-017] high    -- short title
 3. [FTR-023] high    -- short title
 ...

For dry-run: stop here.
```

**Step 5 -- Pre-flight settings update (REQUIRED)**

Before asking for confirmation, update `C:\Users\patri\.claude\settings.json` to add these 5 entries to the `permissions.allow` array if they are not already present:

```json
"Edit(<your-project-backlog-path>/**)",
"Write(<your-project-backlog-path>/**)",
"Edit(<state-dir>/marathon-state.json)",
"Write(<state-dir>/marathon-state.json)",
"Edit(~/.claude/skills/marathon-orders/**)"
```

Tell the user: "Updating settings.json to pre-approve backlog writes for unattended operation. This is the one approval you need to give before the marathon runs."

**Step 6 -- Confirm and configure**

Ask: "Ready to launch marathon with [N] items at wave size [waveSize]? (Opus agents, ~20-min cron loop) [y/n]"

If n: stop. If y: continue.

**Step 7 -- Write initial state file**

```bash
node -e "
const fs = require('fs');
const state = {
  sessionId: 'marathon-' + new Date().toISOString().slice(0, 16).replace('T', 'T').replace(':', '-').replace(':', '-'),
  status: 'running',
  paused: false,
  waveSize: WAVE_SIZE,
  waveNumber: 0,
  category: 'CATEGORY',
  cronJobId: '',
  startedAt: new Date().toISOString(),
  queue: QUEUE_JSON,
  inFlight: [],
  completed: [],
  failed: []
};
fs.mkdirSync('<state-dir>', { recursive: true });
fs.writeFileSync('<state-dir>/marathon-state.json', JSON.stringify(state, null, 2));
console.log('STATE_WRITTEN');
"
```

**Step 8 -- Register the cron loop**

Use CronCreate:
- `cron`: `7/20 * * * *` (fires at :07, :27, :47 of every hour -- avoids fleet collision at :00/:30)
- `durable`: `true` (survives Claude session restart; written to `.claude/scheduled_tasks.json`)
- `recurring`: `true`
- `prompt`:

```
This is an automated marathon-orders loop tick.

1. Read the marathon state file:
   <state-dir>/marathon-state.json

2. Read the full marathon-orders skill instructions:
   C:\Users\patri\.claude\skills\marathon-orders\SKILL.md

3. Execute Phase 3 (Wave Loop Tick) as documented in the skill.

The skill will check for paused state, handle timeouts, collect completed agent results, run the review gate, merge approved work, and launch the next wave. It will delete the cron job when the marathon is complete or paused.

Do not ask the user for confirmation except for review gates with confidence 1-2 or when project rule violations are detected in the diff.
```

Immediately write the returned `cronJobId` into the state file:
```bash
node -e "
const fs = require('fs');
const state = JSON.parse(fs.readFileSync('<state-dir>/marathon-state.json', 'utf8'));
state.cronJobId = 'CRON_JOB_ID_HERE';
fs.writeFileSync('<state-dir>/marathon-state.json', JSON.stringify(state, null, 2));
"
```

**Step 9 -- Launch Wave 1 immediately**

Do not wait for the first cron tick. Go to Phase 2 now.

---

### Phase 2: Launch Wave

Read the state file. Pop `waveSize` items from the front of `queue`. For each item:

1. Add to `inFlight` array with `startedAt: new Date().toISOString()` and `waveNumber: state.waveNumber + 1`
2. Remove from `queue`
3. Increment `waveNumber`
4. Write updated state via node

**Before spawning any agent, run Phase 2.5 (Reconnaissance) for each item.**

---

### Phase 2.5: Reconnaissance (orchestrator makes directional decisions)

This is the most important upgrade over `/work-orders`. The orchestrator -- not the Opus agent -- does the initial codebase analysis. The agent starts with a directional brief, not a cold start.

Run this for each item individually, in full, before spawning its agent.

**Step A -- Extract search terms**

From the work order's `title`, `details`, and `context`, extract:
- Named identifiers: component names, hook names, function names, data collection or field names, server function names, type names
- File hints: any filenames mentioned in the details
- Pattern keywords: the nature of the problem (e.g., "rate limit", "data rule", "field mask", "subscription", "allow update")

**Step B -- Grep for hotspot files**

Run targeted Grep searches for the extracted identifiers across the codebase. Use `output_mode: "files_with_matches"` to get file paths first, then read the top 3-5 results. Look for:
- Where the named thing is defined (the source)
- Where it is imported or called (the consumers)
- The relevant data security rules file if the issue is a security bug
- The relevant server function if it involves server-side logic

Identify the **3-5 hotspot files** -- the files most central to implementing this work order.

**Step C -- Check prior art**

Read the last 20 entries in `completed.md`. Find any items with:
- The same category (bugs to bugs, etc.)
- Overlapping keywords (same component, same data collection, same pattern)
- A resolution that is structurally similar to what this work order needs

If prior art is found, note the resolution approach -- this is a working pattern the Opus agent can follow.

**Step D -- Trace callers (for bugs and security items)**

For each hotspot file, run a Grep to find what imports or calls the affected symbol. This maps the blast radius -- what could break if the fix is wrong. Record the top 3 callers.

**Step E -- Form the directional brief**

Based on Steps A-D, the orchestrator makes a directional call. Write a brief covering:

1. **Start here** -- the single most important file to read first
2. **The pattern** -- the approach that prior art or code conventions suggest (e.g., "similar bugs in this area were fixed by adding a field mask to the data rule, not by restructuring the function")
3. **Blast radius** -- files that call into the hotspot and could be broken by a wrong fix
4. **Our approach** -- a 2-3 sentence directional recommendation. Be specific: not "fix the rule" but a concrete, actionable recommendation that names the rule, function, or constraint to add
5. **Avoid** -- one specific wrong approach if it is obvious from the code (e.g., "do not try to solve this client-side -- the field is writable at the data layer")

Store the brief in the state file under `inFlight[item].brief` via node.

**Step F -- Update inFlight with brief**

```bash
node -e "
const fs = require('fs');
const state = JSON.parse(fs.readFileSync('<state-dir>/marathon-state.json', 'utf8'));
const item = state.inFlight.find(i => i.id === 'ID');
item.brief = {
  hotspotFiles: ['path/to/file1', 'path/to/file2'],
  priorArt: 'BUG-012 used field mask pattern in rules line 47',
  callers: ['path/to/caller1.ts', 'path/to/caller2.ts'],
  approach: 'APPROACH TEXT',
  avoid: 'AVOID TEXT'
};
fs.writeFileSync('<state-dir>/marathon-state.json', JSON.stringify(state, null, 2));
"
```

---

Now spawn the Opus background agent with the brief injected into its prompt:

```
Agent(
  model: "opus",
  isolation: "worktree",
  run_in_background: true,
  description: "[ID] [title]",
  prompt: <Opus Agent Prompt Template -- see below, filled in for this item including RECONNAISSANCE section>
)
```

Report to user:
```
MARATHON WAVE [N] LAUNCHED
===========================
Agent 1: [ID] [title] -- branch marathon/[ID]
  Hotspots: [file1], [file2], [file3]
  Approach: [one-line summary of directional brief]
[Agent 2: [ID] [title] -- branch marathon/[ID]
  Hotspots: [file1], [file2]
  Approach: [one-line summary]]

Queue remaining: [N] items
Next check-in: ~20 min via cron
```

---

### Phase 3: Wave Loop Tick (cron re-entry -- no user present)

This runs every 20 minutes. Read the state file first. Then:

**3a. Paused check**

If `state.paused === true`: call `CronDelete(state.cronJobId)`. Stop. Do not touch agents or queue.

**3b. Timeout check**

For each entry in `state.inFlight`:
- Compute `elapsedMin = (Date.now() - new Date(entry.startedAt).getTime()) / 60000`
- If `elapsedMin > 90`:
  - The agent has been running too long. Declare timeout.
  - Remove from `inFlight`
  - Increment `entry.attempts` on the original queue item
  - If `attempts < 2`: push item back to front of `queue` with incremented attempts
  - If `attempts >= 2`: push to `failed` with `reason: "timed out twice"`. Annotate the backlog file (see Phase 4 -- failed path)
  - Write state via node

**3c. Completion check**

For each entry in `state.inFlight`, the Agent tool result is available once the background agent has completed. Check if the agent's result is available. If yes:
- Parse the `MARATHON_RESULT_START...MARATHON_RESULT_END` block from the agent output
- If block is missing or malformed: treat as failed, note `reason: "malformed result -- no MARATHON_RESULT block"`
- Otherwise: proceed to Phase 4 (review gate)

If all in-flight agents are still running and none timed out: stop here. Cron will check again in 20 min.

**3d. Slot check**

After processing completions and timeouts: if `inFlight.length < waveSize` and `queue.length > 0`: go to Phase 2 to fill the open slots.

**3e. Marathon complete check**

If `queue.length === 0` and `inFlight.length === 0`: go to Phase 5.

---

### Phase 4: Review Gate + Merge

Run this for each agent result that successfully parsed.

**Step 1 -- Parse result fields**
```
id, title, status, confidence (1-5), build (passed|failed), files_modified[], resolution, concerns
```

**Step 2 -- Handle failed status**

If `status === "failed"`: skip merge. Move to `failed` with `reason: state.resolution`. Annotate backlog file:
```bash
node -e "
const fs = require('fs');
const filePath = '<your-project-backlog-path>/CATEGORY.md';
let content = fs.readFileSync(filePath, 'utf8');
// Find the item block and append a Last attempt field
content = content.replace(
  /(### \[ID\][\s\S]*?)(\n###|\n*$)/,
  '\$1\n- **Last attempt**: DATE -- REASON\$2'
);
fs.writeFileSync(filePath, content);
"
```
Update state via node. Continue to next result.

**Step 3 -- Build check**

If `build === "failed"`: treat as failed (same as above). Note `reason: "agent reported build failure"`.

**Step 4 -- Read the diff**

```bash
git -C <project-root> diff master...marathon/[ID] 2>&1 | head -200
```

**Step 5 -- Project rule violation scan**

Scan diff output for any rules listed in your project's CLAUDE.md or equivalent (e.g., banned type assertions, banned terminology, formatting rules).

Flag any matches.

**Step 6 -- Confidence + flag decision**

```
REVIEW GATE: [ID] [title]
==========================
Build: PASSED
Confidence: [N]/5
Files modified: [N] files ([list])
[Concerns: [text if any]]
[Flags: [list if any]]

Diff (first 200 lines):
[diff output]
```

Decision logic:
- `confidence >= 3` AND build passed AND no flags -> **auto-approve**, squash merge, continue
- `confidence >= 3` AND minor flags (style only) -> **auto-approve with note** in completed.md
- `confidence <= 2` OR project rule violation flags -> **pause and notify user**, wait for "merge" or "skip" input before continuing

**Step 7 -- Squash merge (auto-approved path)**

```bash
git -C <project-root> checkout master
git -C <project-root> merge --squash marathon/[ID]
git -C <project-root> commit -m "[ID] [Title]

Completed by marathon-orders (Opus, wave [N])
Confidence: [N]/5
[If concerns]: Follow-up: [concerns]"
git -C <project-root> branch -d marathon/[ID]
```

**Step 8 -- Update backlog files**

Remove the item from its source backlog file:
```bash
node -e "
const fs = require('fs');
const filePath = '<your-project-backlog-path>/CATEGORY.md';
let content = fs.readFileSync(filePath, 'utf8');
// Remove the entire ### [ID] block (from the heading to just before the next ### or end of file)
content = content.replace(/### \[ID\][^\n]*\n[\s\S]*?(?=\n### |\n*$)/, '');
fs.writeFileSync(filePath, content);
"
```

Prepend to `completed.md`:
```bash
node -e "
const fs = require('fs');
const path = '<your-project-backlog-path>/completed.md';
const existing = fs.readFileSync(path, 'utf8');
const entry = \`### [ID] TITLE
- **Completed**: DATE
- **Completed by**: marathon-orders session (Opus)
- **Wave**: WAVE_NUM
- **Confidence**: N/5
- **Resolution**: RESOLUTION
\` + (concerns !== 'none' ? \`- **Follow-up**: CONCERNS\n\` : '') + '\n';
// Find insertion point: after the header comment block, before first existing entry
const insertAt = existing.indexOf('\n### [');
if (insertAt === -1) {
  fs.writeFileSync(path, existing + entry);
} else {
  fs.writeFileSync(path, existing.slice(0, insertAt + 1) + entry + existing.slice(insertAt + 1));
}
"
```

**Step 9 -- Update state**

Move item from `inFlight` to `completed` via node. Write state.

**Step 10 -- Close feedback loop (if applicable)**

If the completed work order's context field contains `Promoted from dev proposal`, extract the proposal ID and update its status to `implemented` via the internal Support page using Chrome DevTools MCP:

1. Navigate to the internal Support page:
   ```
   mcp__chrome-devtools__navigate_page({ url: 'http://localhost:5174/support' })
   ```

2. Filter to "filed" status and find the proposal card:
   ```
   mcp__chrome-devtools__click({ selector: '[data-filter="filed"]' })
   ```

3. Click "Mark Implemented" on the target card:
   ```
   mcp__chrome-devtools__click({ selector: '[data-action="mark-implemented"][data-proposal-id="PROPOSAL_ID"]' })
   ```

4. Enter the implementation note in the prompt dialog:
   ```
   mcp__chrome-devtools__handle_dialog({ accept: true, promptText: 'RESOLUTION_SUMMARY' })
   ```

This closes the feedback loop: the user's original feedback now has a traceable path from submission through council debate, human approval, and implementation. The internal Support page handles the write through its authenticated session -- no service-account credentials needed.

If the context field does not mention a dev proposal, skip this step silently.

---

### Phase 5: Marathon Complete

1. Call `CronDelete(state.cronJobId)`
2. Update state to `status: "complete"` via node
3. Print final report:

```
MARATHON COMPLETE
=================
Session: [sessionId]
Started: [startedAt]
Completed: [now]
Waves: [waveNumber]

Completed ([N] items):
  [BUG-016] short title -- resolution summary. Confidence: 4/5
  [BUG-020] short title -- resolution summary. Confidence: 5/5
  ...

Failed ([N] items, remain in backlog):
  [BUG-022] short title -- timed out twice (complex setup)
  ...

All branches merged to master and cleaned up.
```

---

## Opus Agent Prompt Template

Fill in all `[PLACEHOLDERS]` before spawning. This prompt is self-contained -- the agent knows nothing about the main conversation.

```
You are an Opus agent running a deep-work marathon session. You have been assigned exactly ONE work order. Your only job is to implement it completely and correctly.

This is a focused depth session. You will not rush. You will read before you write. You will verify before you report.

== PROJECT CONTEXT ==

Working directory: <project-root>
Project rules: <project-root>/CLAUDE.md -- read this FIRST before doing anything else.

Product: <PRODUCT_DESCRIPTION>

== YOUR WORK ORDER ==

ID: [ID]
Category: [bugs | design | features | tech-debt]
Title: [title]
Priority: [critical | high | medium | low]

Details:
[details -- verbatim from backlog item]

Context:
[context -- verbatim from backlog item]

[If attempts > 0]: Previous attempt note: [lastAttempt text from backlog item]
[If related items exist]: Related: [related IDs]

== RECONNAISSANCE ==

The orchestrator analyzed the codebase before assigning this to you. Use this as your starting point -- do not ignore it, but do not blindly follow it either. If you read the code and find the brief is wrong, trust the code.

Start here (most relevant files):
[hotspot files -- one per line, relative paths]

Prior art (similar completed work you can pattern-match):
[priorArt -- or "None found"]

Blast radius (files that call into the hotspot -- could break if fix is wrong):
[callers -- one per line]

Suggested approach:
[approach -- orchestrator's directional recommendation]

Do not do this:
[avoid -- specific wrong approach to skip]

== MANDATORY PROCESS -- DO NOT SKIP ANY STEP ==

Step 1: Read CLAUDE.md in full before touching any code.

Step 2: Read the hotspot files from RECONNAISSANCE before reading anything else.
- Start with the files listed above -- they are the orchestrator's best guess at ground zero.
- Then read their callers to understand the blast radius.
- Expand outward from there only if needed.
- If you read the hotspot files and find the suggested approach is wrong, note why in your `concerns` field and implement the correct fix instead.
- For security bugs: read the affected data security rules file in full and the relevant server function in full.
- For design changes: read the project's design system docs before touching components.
- Spend at least the first 20% of your effort reading. Do not start writing until you have a complete picture.

Step 3: Plan your change explicitly (in your scratchpad, not a file).
- List exactly which files you will modify and why.
- If your plan touches more than 6 files, stop and re-scope. This is one focused work order.

Step 4: Implement.
Follow all CLAUDE.md rules strictly. Common rules to respect:
- TypeScript-first -- no `any` types, no `as any`
- No client-side-only security enforcement -- data rules or server functions must enforce server-side
- No new files unless the work order explicitly requires them
- No refactoring surrounding code beyond what the work order requires
- Honor any style/terminology/formatting rules listed in the project's CLAUDE.md

Step 5: Verify the build.
Run the project's build command (e.g., `cd <project-root> && <build command> 2>&1 | tail -30`).
If the build fails, fix all errors before proceeding. Do not report done if the build is broken.

Step 6: Write your result summary.
Your final message must be EXACTLY the structured result block below, filled in completely.
The main session's review gate reads this block. Do not add commentary outside it.

== REQUIRED OUTPUT FORMAT ==

MARATHON_RESULT_START
id: [ID]
title: [title]
status: success | partial | failed
confidence: [1-5]
build: passed | failed
files_modified:
  - [relative path from repo root]
  - [relative path from repo root]
resolution: [1-3 sentences. What exactly was changed and why. No filler.]
concerns: [1-3 sentences of follow-up items, risks, or things the reviewer should check. Write "none" if there are no concerns.]
MARATHON_RESULT_END

== CONFIDENCE SCORE GUIDE ==

1 -- I made changes but am not confident they address the root cause. Fix may be incomplete.
2 -- I believe this is correct but could not fully verify (e.g., a runtime path I cannot test statically).
3 -- Reasonably confident. Logic is sound and build passes, but a reviewer should check the implementation.
4 -- Confident. Root cause addressed, fix is clean, build passes. Normal review is sufficient.
5 -- Very confident. Traced the full system path, fix is minimal and correct, build passes, no follow-up concerns.

== SCOPE CONSTRAINTS ==

- This is your only work order. If you notice other bugs while reading, note them in `concerns` but do NOT fix them.
- Do not refactor surrounding code beyond what the work order requires.
- Do not add tests unless the work order explicitly asks for them.
- If completing this work order requires changing more than 6 files, stop and explain the blocker in `concerns`. Report `status: partial`.
```

---

## Review Gate Checklist

The main session runs this for every completed agent before merging. Quick reference:

| Check | Pass condition | Fail action |
|---|---|---|
| Result block present | `MARATHON_RESULT_START` found and parseable | Treat as failed |
| Status field | `success` or `partial` | Move to failed |
| Build field | `passed` | Move to failed |
| Git diff readable | `git diff master...marathon/[ID]` returns output | Flag, pause |
| Files match | diff files match `files_modified` list | Note in completed |
| Project rule violations | None of the rules listed in CLAUDE.md are broken | Flag, pause for 1-2, note for 3-5 |
| Confidence 4-5, no flags | All clear | Auto-approve, squash merge |
| Confidence 3, minor flags | Style only | Auto-approve with note |
| Confidence 1-2 | Low confidence | Pause, wait for user input |
| Project rule violation | Rule broken | Pause, wait for user input |

---

## CronCreate Scheduling

```
cron: "7/20 * * * *"      Fires at :07, :27, :47 -- avoids :00/:30 fleet collision
durable: true              Persists to .claude/scheduled_tasks.json, survives restart
recurring: true            Runs until manually deleted or 7-day auto-expiry
```

The 7-day auto-expiry is a hard CronCreate limit. Marathon sessions are designed for 4-8 hours, not week-long runs. If you need to run again the next day, start a fresh `/marathon-orders` session.

The cron prompt is fully self-contained -- it reads the SKILL.md and state file from disk on every tick. No reliance on conversation history.

**Cron job lifecycle:**
- Created in Phase 1 -> ID stored in state file
- Deleted in Phase 5 (marathon complete) or Phase 0 `--stop` command
- If a cron tick fires and state file is missing: stop silently (session was externally cleaned up)

---

## Timeout Handling

- Threshold: 90 minutes per agent (hardcoded -- Opus agents rarely need more than 60 min for a single work order)
- Max attempts: 2. After 2 timeouts, item is permanently moved to `failed` and annotated in the backlog with `**Last attempt**`
- Retried items go to the front of the queue (not the back) so they are not perpetually deferred
- Timeout reason logged in `failed` entry: `"timed out after 90 minutes (attempt N/2)"`

---

## Completing Items (completed.md format)

New entries are **prepended** (newest first) after the file header. Match this format exactly:

```markdown
### [BUG-016] Short title summarizing the change
- **Completed**: 2026-04-09
- **Completed by**: marathon-orders session (Opus)
- **Wave**: 1
- **Confidence**: 4/5
- **Resolution**: 1-3 sentences explaining the change.
- **Follow-up**: Optional follow-up notes if the agent flagged concerns.
```

The `Follow-up` line is omitted if the agent reported `concerns: none`.

---

## Important Notes

- **Opus is expensive.** Default wave size is 1 intentionally. Only use `--wave 2` when the next two items are clearly independent (different files, different systems).
- **Opus-per-WO is this skill's deliberate exception to the "Sonnet ships" rule** (docs/MODELS.md): the queue that reaches marathon-orders is depth work — security fixes, multi-file architecture, items that already failed a Sonnet agent. If a queue turns out to be mostly shallow items, stop and run `/work-orders` instead; don't pay Opus rates for Sonnet work. For a budget pass over a deep queue, `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` downgrades every spawned agent for the session — the review gate still runs.
- **The review gate always runs.** Even for confidence 5 items, the diff is read and the build is checked. This is the anti-spaghetti guard.
- **Cron auto-expires after 7 days.** This is a CronCreate hard limit. Marathon is not designed for week-long unattended runs.
- **The state file is the single source of truth.** If it is deleted or corrupted mid-marathon, the marathon cannot be resumed. Background agents will continue running and their worktree branches will still exist -- you can manually merge them after checking their diffs.
- **Worktree branches named `marathon/[ID]`** are cleaned up by the skill after successful merge. Do not delete them manually -- the skill handles it.
- **Do not use `/marathon-orders` and `/work-orders` simultaneously.** Both use worktree isolation but their branches have different naming conventions. Running both at once risks git checkout conflicts.
- **This skill does not deploy.** It merges to master but never pushes. Run `/deploy` separately after reviewing the merged commits.
- **File writes during cron ticks use Bash (node -e) exclusively** -- not the Write or Edit tools. This is because `Bash(node -e ':*` is pre-approved in `settings.json`, while Write/Edit permissions for backlog files are added during the Phase 1 pre-flight step.
