---
name: marathon-research
description: "Long-running walkaway session that processes a queue of research topics. Each wave runs a Sonnet scope-check then an Opus deep researcher that uses WebSearch/WebFetch to produce a cited markdown report under 750 lines. Files claims with verifiable URLs only. Invoke with /marathon-research [topics...] [--queue <path>] [--hours N] [--stop] [--status] [--continue] [dry-run]."
---

# Marathon Deep Research Skill

## Configure for your project

Before using this skill, swap these placeholders for your project values:

- `<project-root>` — absolute path to your project root
- `<research-root>` — absolute path where this skill writes research outputs (e.g. `<project-root>/research`)
- `<state-dir>` — absolute path where this skill writes its state JSON and lock file
- `<temp-dir>` — temp directory for orchestration scripts (e.g. `<project-root>/.tmp/marathon-research`)
- `<project-md>` — optional path to your top-level project context file (e.g. `<project-root>/CLAUDE.md`, `<project-root>/README.md`). Used in the Sonnet scope-check prompt.

## Purpose

Runs a sustained, unattended deep-research loop over up to 8 hours. Each wave:

1. Pops the next **research topic** from a queue
2. Spawns a **Sonnet scope-check** front-runner that either produces a structured research brief or declares the topic out of scope
3. Spawns an **Opus deep researcher** that uses WebSearch and WebFetch to gather sources and writes a fully cited markdown report
4. Validates every claim has a URL, splits files at 750 lines, updates the R&D index
5. Loops via **CronCreate** every 30 minutes

Use when you want unattended, deep R&D over a list of topics that produces verifiable, cited markdown files.

## Five Hard Rules

These are enforced in code, not just prompts. Every rule has at least one orchestrator-side check.

1. **Every claim must carry a verifiable URL.** Enforced by the post-wave citation validator. Files with uncited claims quarantine to `<research-root>/flagged/` and the wave is marked `failed-validation`.
2. **If the agent does not understand the scope, FAIL the topic.** Enforced by the Sonnet front-runner gate. Topics that emit `SCOPE_UNCLEAR` never reach Opus, get a stub in `<research-root>/failed/`, and advance the rotation.
3. **Monitor RAM and clean up stale processes.** Enforced by the orchestrator at the start of every wave (Phase 2 step 1) and on every cron tick (Phase 3c). Kill stale node/chrome > 1 GB idle > 30 min when total RAM > 75%.
4. **Markdown files stay under 750 lines.** Enforced by the Opus prompt (self-monitor at line 700) AND the orchestrator (line-count check after Opus returns; auto-split agent if exceeded).
5. **No permission prompts after launch.** Enforced by the Phase 1 settings.json pre-flight that allowlists every path the run will touch.

## Invocation

```
/marathon-research                                    Read default queue file (if present), else prompt
/marathon-research "topic A" "topic B"                Queue these topics inline
/marathon-research --queue <path>/queue.md            Read a markdown queue file
/marathon-research "topic A" --queue queue.md         Combine inline + file
/marathon-research --hours 4                          Override 8h cap
/marathon-research --stop                             Pause after current wave
/marathon-research --status                           Show queue depth, completed/failed, sources
/marathon-research --continue                         Manual re-entry if cron misfired
/marathon-research dry-run                            Show queue + plan without launching
```

### Queue file format

```markdown
# Research Queue

## What HRIS systems integrate with Slack via webhook?
Optional framing paragraph — passed to the Sonnet front-runner as additional context.
Bullets, examples, sub-questions all welcome here.

## Top 5 productivity gamification competitors 2026
Another optional framing paragraph.
```

Each `## ` heading is one topic. The body becomes the framing brief.

## R&D Folder Layout

```
<research-root>/
├── INDEX.md                                          Auto-managed top-level index
├── 2026-04-25-<topic-slug>/
│   ├── 00-brief.md                                   Sonnet scope-check brief (audit trail)
│   ├── 01-overview.md                                Opus part 1, <750 lines
│   ├── 02-deep-dive.md                               Opus part 2 (only if needed)
│   ├── sources.md                                    Bibliography: title + URL + retrieval date
│   └── meta.json                                     Status, started/completed, files, sourceCount
├── failed/
│   └── 2026-04-25-<topic-slug>.md                    Stub for SCOPE_UNCLEAR topics
└── flagged/
    └── 2026-04-25-<topic-slug>/                      Files that failed citation validation
```

`INDEX.md` is rewritten after every wave.

## State File

```
<state-dir>/marathon-research-state.json
```

Written via the **temp JS file pattern** — `Write` a JS file to `<temp-dir>/` then `Bash(node ...)`. Never use `node -e "..."` with inline template literals (Windows shell quoting breaks on backticks/apostrophes inside markdown content).

Schema:
```json
{
  "sessionId": "research-YYYY-MM-DDTHH-MM",
  "status": "running | paused | complete | aborted",
  "paused": false,
  "cronJobId": "cron_xxx",
  "startedAt": "ISO",
  "hoursCap": 8,
  "ramThresholdPct": 75,
  "queue": [
    { "slug": "topic-slug", "title": "Topic title verbatim", "framing": "optional body from queue file", "source": "arg | queueFile", "queuedAt": "ISO" }
  ],
  "currentWave": 0,
  "rotationIndex": 0,
  "waves": [
    {
      "waveNumber": 1,
      "slug": "topic-slug",
      "title": "Topic title",
      "startedAt": "ISO",
      "completedAt": "ISO",
      "status": "complete | failed-scope | failed-validation | in-progress",
      "scopeVerdict": "clear | unclear",
      "scopeReason": "...",
      "filesProduced": ["01-overview.md", "02-deep-dive.md", "sources.md"],
      "totalLines": 1247,
      "sourcesCount": 23,
      "claimsValidated": 89,
      "claimsFlagged": 0,
      "ramAtStartPct": 62,
      "ramAtEndPct": 71,
      "processesKilled": []
    }
  ],
  "totals": {
    "topicsCompleted": 0,
    "topicsFailed": 0,
    "filesWritten": 0,
    "sourcesCollected": 0
  }
}
```

---

<!-- STATIC BOUNDARY: everything above this line is stable across cron ticks. Everything below changes each tick. -->

## Workflow

### Phase 0: Invocation Parsing

- `--stop`: read state. Write `paused: true`, call `CronDelete(state.cronJobId)`, **delete `<state-dir>/scheduled_tasks.lock` if present**, print summary. Stop.
- `--status`: pretty-print queue depth, completed/failed counts, current wave, total sources. Stop.
- `--continue`: skip directly to Phase 3.
- `dry-run`: build queue, print plan, stop without writing state or registering cron.
- `--hours N`: override default 8h cap. Clamped to [1, 12].
- Positional args: each quoted argument is a topic title.
- `--queue <path>`: read the markdown queue file, parse `## ` headings as topics.
- **No state file exists**: fresh start, continue to Phase 1.
- **State file exists with `paused: false`**: cron re-entry, skip to Phase 3.

#### Phase 0.1: Stale state detection

1. **Lock file staleness**: If `<state-dir>/scheduled_tasks.lock` exists, check the PID. If dead OR lock more than 4 hours old, delete silently.
2. **Cron consistency**: If state has `status: "running"` and `cronJobId` not in `CronList()` AND state untouched >60 min, prompt to reset.
3. **Hours-cap hard abort**: If `startedAt` more than `state.hoursCap` hours ago (default 8), auto-abort.

---

### Phase 1: Fresh Start (user is present — the ONLY permission gate per HARD RULE #5)

**Step 1 — Build the queue**

Combine inline arg topics with `--queue` file topics. Slugify each title:
- Lowercase
- Replace non-alphanumeric runs with `-`
- Collapse repeated `-`
- Trim leading/trailing `-`
- Truncate to 60 chars

Add today's date prefix: `YYYY-MM-DD-<slug>`. If a slug collision occurs, append `-2`, `-3`, etc.

If queue empty AND no inline args AND no `--queue`: print usage and stop.

**Step 2 — Present the plan**

```
MARATHON RESEARCH PLAN
=======================
Queue ([N] topics, ~30-45 min each)
Hours cap: 8h (override with --hours N)
Cron interval: 30 minutes (fires at :18 and :48)
RAM threshold: 75% of system RAM

R&D folder: <research-root>/
State file: <state-dir>/marathon-research-state.json

Hard rules in effect:
  #1 Every claim cites a URL
  #2 Scope-unclear topics fail without spawning Opus
  #3 RAM monitored; stale processes killed at 75% threshold
  #4 Files split at 750 lines max
  #5 Zero permission prompts after launch

For dry-run: stop here.
```

**Step 3 — Pre-flight settings update (REQUIRED — HARD RULE #5)**

Update `~/.claude/settings.json` `permissions.allow`:

```
"Edit(<research-root>/**)"
"Write(<research-root>/**)"
"Edit(<state-dir>/marathon-research-state.json)"
"Write(<state-dir>/marathon-research-state.json)"
"Write(<temp-dir>/**)"
"Bash(node <temp-dir>/*)"
"WebFetch"
"WebSearch"
```

**Step 4 — Confirm**

Ask: "Ready to launch marathon research with [N] topics (~[N * 35] min, [hours]h cap)? [y/n]". THIS IS THE ONLY INTERACTIVE PROMPT IN THE ENTIRE RUN.

**Step 5 — Write initial state file**

Use the temp JS file pattern. Create the state directory and the research subfolders (`failed/`, `flagged/`).

**Step 6 — Initialize INDEX.md if missing**

Write a default INDEX.md with sections: Active Research, Completed Research, Failed / Out-of-Scope.

**Step 7 — Register the cron loop**

CronCreate:
- `cron`: `"18,48 * * * *"`
- `durable`: `true`
- `recurring`: `true`
- `prompt`:

```
This is an automated marathon-research loop tick.

RESOURCE DISCIPLINE — MANDATORY:
- WebSearch and WebFetch ARE permitted (this skill IS the reason they are allowed).
- Do NOT invoke mcp__chrome-devtools__* tools in this tick.
- Do NOT ask the user any questions. The session is unattended.
- Always run Phase 3a (self-heal / terminal-state check) FIRST.

WORKFLOW:
1. Read the state file at <state-dir>/marathon-research-state.json
2. Read the full marathon-research skill instructions
3. Execute Phase 3 (Wave Loop Tick).
```

Write the returned `cronJobId` into the state file.

**Step 8 — Launch Wave 1 immediately**

Go to Phase 2.

---

### Phase 2: Launch Wave (research one topic)

Read the state file. Pop `state.queue[state.rotationIndex]`.

**Step 1 — RAM precheck (HARD RULE #3)**

Run PowerShell:
```powershell
$mem = Get-CimInstance Win32_OperatingSystem
$totalKB = $mem.TotalVisibleMemorySize
$freeKB = $mem.FreePhysicalMemory
$usedPct = [math]::Round((($totalKB - $freeKB) / $totalKB) * 100, 1)
Write-Output "USED_PCT:$usedPct"
```

(On non-Windows hosts, swap in an OS-appropriate equivalent.)

If `usedPct >= 75`:
1. Find stale processes (>1GB working set, started >30 min ago).
2. Kill them.
3. Re-check. If still >= 75, abort the marathon.

Log RAM at start in the wave entry.

**Step 2 — Mark wave in-progress**

**Step 3 — Sonnet scope-check (front-runner) — HARD RULE #2 gate**

Spawn `Agent(subagent_type: general-purpose, model: sonnet)` with the prompt from "Sonnet Scope-Check Prompt Template" below. Parse for `SCOPE_BRIEF_START ... SCOPE_BRIEF_END` or `SCOPE_UNCLEAR_START ... SCOPE_UNCLEAR_END`.

**Step 4 — Handle scope failure (HARD RULE #2)**

If `SCOPE_UNCLEAR`:
1. Write `<research-root>/failed/<date>-<slug>.md` with a stub explaining the failure.
2. Update state wave entry: `status: "failed-scope"`, `scopeVerdict: "unclear"`, advance rotation.
3. Update INDEX.md.
4. Skip to wave-end report — do NOT spawn Opus.

**Step 5 — Write the brief**

Create `<research-root>/<date>-<slug>/00-brief.md` with the SCOPE_BRIEF block contents.

**Step 6 — Spawn Opus deep researcher**

Spawn `Agent(model: opus, subagent_type: general-purpose)`. Permissions on `<research-root>/**` and `<temp-dir>/**` were pre-approved. The agent uses WebSearch + WebFetch to gather sources, then writes:
- `01-overview.md`, `02-deep-dive.md`, etc. — split at 700 lines per HARD RULE #4
- `sources.md` — bibliography
- A `RESEARCH_MANIFEST_START ... END` block in its return text

**Step 7 — Citation validation pass (HARD RULE #1)**

Run a node validator over each produced markdown file (excluding `00-brief.md` and `sources.md`):

```js
// <temp-dir>/validate-N.js
const fs = require('fs');
const path = require('path');

const dir = '<research-root>/<date>-<slug>';
const sourcesPath = path.join(dir, 'sources.md');
const sourcesText = fs.existsSync(sourcesPath) ? fs.readFileSync(sourcesPath, 'utf8') : '';
const sourceFootnotes = new Set(
  [...sourcesText.matchAll(/^\[\^(\d+)\]:/gm)].map(m => m[1])
);

const META_PREFIXES = /^(Retrieved|Retrieval|See|Source:|Sources:|Note:|Notes:|Per|For more|Read more|Full bibliography|Citation|Citations)\b/i;

const targetFiles = fs.readdirSync(dir).filter(f => /^\d{2}-.*\.md$/.test(f) && f !== '00-brief.md');

let totalClaims = 0;
let flaggedClaims = 0;
const flaggedDetails = [];

for (const f of targetFiles) {
  const content = fs.readFileSync(path.join(dir, f), 'utf8');
  const stripped = content.replace(/```[\s\S]*?```/g, '');
  const lines = stripped.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    if (line.startsWith('#') || line.startsWith('>') || line.startsWith('|---') || line === '---') continue;
    if (META_PREFIXES.test(line)) continue;
    if (line.endsWith(':')) continue;
    const looksFactual = /\d|[A-Z][a-z]+ [A-Z][a-z]+|\b(is|are|was|were|has|have|costs?|reaches?|reports?|states?|claims?|grew|reached|sworn|elected|born|served|holds|conducted)\b/.test(line);
    if (!looksFactual) continue;
    totalClaims++;
    const lookahead = [line, lines[i+1] || '', lines[i+2] || '', lines[i+3] || ''].join(' ');
    const hasUrl = /https?:\/\/\S+/.test(lookahead);
    const fnMatch = lookahead.match(/\[\^(\d+)\]/);
    const hasValidFootnote = fnMatch && sourceFootnotes.has(fnMatch[1]);
    if (!hasUrl && !hasValidFootnote) {
      flaggedClaims++;
      flaggedDetails.push({ file: f, lineNumber: i + 1, line: line.slice(0, 200) });
    }
  }
}

const result = { totalClaims, flaggedClaims, flaggedDetails };
fs.writeFileSync('<temp-dir>/validate-N-result.json', JSON.stringify(result, null, 2));
console.log('CLAIMS:' + totalClaims + ' FLAGGED:' + flaggedClaims);
```

The validator skips meta-prefixes, list-intro lines ending with `:`, and uses a 3-line lookahead window so a topic sentence introducing a cited list passes when citations are in the bullets that follow.

If `flaggedClaims > 0`:
1. Move the entire topic folder to `<research-root>/flagged/<date>-<slug>/`.
2. Write `_validation-report.md` listing every flagged claim.
3. Mark wave `status: "failed-validation"`.
4. Skip to wave-end report.

**Step 8 — Line-count enforcement (HARD RULE #4)**

For each report file matching `\d{2}-.*\.md`, count lines. If >750, spawn a one-shot Sonnet split agent to split at the nearest `## H2` boundary. Re-run citation validation after split.

**Step 9 — Write meta.json**

```js
const meta = {
  slug: '<date>-<slug>',
  title: 'TITLE',
  status: 'complete',
  startedAt: 'ISO_START',
  completedAt: new Date().toISOString(),
  files,
  totalLines,
  sourceCount
};
```

**Step 10 — Update INDEX.md**

Rewrite INDEX.md by scanning `<research-root>/` for topic folders with `meta.json`, `failed/`, and `flagged/`. Sections: Active Research, Completed Research, Failed / Out-of-Scope, Flagged (citation validation failed).

**Step 11 — Update state file**

Push wave entry, advance rotation, update totals.

**Step 12 — Report wave results**

```
MARATHON RESEARCH WAVE [N] COMPLETE
=====================================
Topic: <title>
Status: <complete | failed-scope | failed-validation>
Files: [list]
Total lines: [N]
Sources cited: [N]
Claims validated: [N] (flagged: [N])
RAM: start [X]% -> end [Y]%

Topic folder: <research-root>/<date>-<slug>/
Rotation progress: [N]/[total]
Total this session: [completed]/[failed]/[total queued]
```

---

### Phase 3: Wave Loop Tick (cron re-entry)

**3a. Self-heal / terminal-state check (FIRST)**

Terminate with `CronDelete(state.cronJobId)` if ANY of:

- State file missing
- `state.status === "complete" | "failed" | "aborted"`
- `state.paused === true`
- `state.cronJobId` empty or mismatched
- `Date.now() - new Date(state.startedAt) > state.hoursCap * 3600 * 1000`
- `state.rotationIndex >= state.queue.length` (queue exhausted, go to Phase 4)

Delete lock file on termination.

WebSearch and WebFetch ARE permitted in this tick. Do NOT boot chrome-devtools-mcp. Do NOT ask the user questions.

**3b. In-progress check**

If last wave entry has `status: "in-progress"`: stop.

**3c. RAM precheck**

Same as Phase 2 Step 1.

**3d. Launch next wave**

Go to Phase 2.

---

### Phase 4: Marathon Complete

1. `CronDelete(state.cronJobId)`.
2. Update state to `status: "complete"`.
3. Cleanup: delete lock file, delete `<temp-dir>/` orchestration scripts (keep R&D outputs intact). **Preserve `validate-section.js`** — it is reused across runs and referenced by the validator-override memory.
4. Read final INDEX.md, inline it in the report.
5. **Distill completed marathons into summaries** (HARD WIRE per skill composition):
   - Invoke `Skill(skill: "distill")` with no args. Auto-detect mode picks up every just-completed marathon slug that has a `_(summary stub)_` placeholder in `<project-root>/research/_index.md`.
   - Distill runs Sonnet agents in parallel (one per topic). Typical wall-clock: ~3 min for 5 topics.
   - Distill writes `<project-root>/research/summaries/<topic-slug>.md` per marathon and updates `_index.md` to replace stubs.
   - If `/distill` reports any topic exceeded the 200-line cap after re-prompt: include that as a warning in the final report; the marathon still counts as complete.
6. Print final report:

```
MARATHON RESEARCH COMPLETE
===========================
Session: [sessionId]
Started / Completed / Duration

Topics processed: [N]
  Completed:        [N]
  Failed (scope):   [N]
  Failed (citation):[N]

Files written: [N]
Sources collected: [N]
Total lines of research: [N]

Summaries distilled: [N]
  [topic-slug]      [lines] lines
  ...

R&D folder: <research-root>/
Summaries:  <project-root>/research/summaries/
Index:      <project-root>/research/_index.md (stubs replaced)

== INDEX.md ==
[full INDEX.md content inlined here]
```

---

## Sonnet Scope-Check Prompt Template

```
You are a research scope-check front-runner. Your ONLY job is to either:
(a) emit a structured research brief that an Opus deep-research agent can execute against, OR
(b) declare the topic too unclear to research and refuse.

This is a HARD GATE. If you have ANY doubt about what the user is asking, return SCOPE_UNCLEAR.
The Opus agent that comes after you cannot ask the user clarifying questions. The user is unattended.

== TOPIC ==
[TOPIC_TITLE]

== FRAMING (from user, may be empty) ==
[FRAMING_BODY_FROM_QUEUE_FILE_OR_EMPTY]

== PROJECT CONTEXT (use only if topic is project-relevant) ==
[OPTIONAL: insert short project description and/or Read <project-md>]

== YOUR DECISION ==

If you understand the topic well enough to write a focused research brief: emit SCOPE_BRIEF.
If the topic is vague, ambiguous, missing context, contradictory, or unanswerable without further input: emit SCOPE_UNCLEAR.

Bias toward SCOPE_UNCLEAR when in doubt. A failed research run with bluffed claims is FAR worse than a failed scope-check that gets re-queued with sharper framing.

== OUTPUT FORMAT — pick exactly ONE block ==

If clear:

SCOPE_BRIEF_START
restated_topic: [one sentence]
sub_questions:
  - [question 1]
  - [question 2]
  - [question 3]
suggested_sources:
  - [authoritative domain or org]
expected_structure:
  - 01-overview.md: [what goes here]
  - 02-deep-dive.md: [if needed]
estimated_source_count: [integer]
notes: [one paragraph of guidance]
SCOPE_BRIEF_END

If unclear:

SCOPE_UNCLEAR_START
reason: [one paragraph explaining what is ambiguous and what clarifications would unlock this topic]
SCOPE_UNCLEAR_END

Output ONLY the chosen block. No preamble.
```

---

## Opus Deep Researcher Prompt Template

```
You are an Opus deep researcher. You have ONE job: produce a thoroughly cited markdown report on the assigned topic, using WebSearch and WebFetch to gather authoritative sources.

You have direct Edit and Write permission on:
  <research-root>/[DATE-SLUG]/
  <temp-dir>/

Write files directly. Do not produce diffs or snippets.

== TOPIC ==
[TOPIC_TITLE]

== SCOPE BRIEF (your contract for this run) ==
[FULL SCOPE_BRIEF BLOCK FROM SONNET]

== HARD RULES — INVIOLABLE ==

1. EVERY factual claim must carry a verifiable URL. If you cannot find a URL for a claim, drop it OR mark "Unsourced — DROP" and remove before final write. The orchestrator will run a citation validator; uncited claims will quarantine the entire topic.

2. If you discover the topic is unanswerable from public sources: STOP. Write a single 01-overview.md with a one-paragraph explanation. End with RESEARCH_MANIFEST_START block marking abandoned: true. Do not bluff. Do not invent sources.

3. Markdown files must stay under 750 lines. Self-monitor at line 700; close and start the next sequential file.

4. Citations: every assertion ends with either an inline link `([Source Title](https://url))` or a footnote reference `[^N]` whose target is defined in sources.md.

== SOURCES.MD FORMAT ==

Each source gets a numbered footnote:

[^1]: [Title of source](https://full.url) — Retrieved YYYY-MM-DD. Brief credibility note.
[^2]: [Another source](https://other.url) — Retrieved YYYY-MM-DD.

Number in order of first citation. Every footnote referenced in a report file must exist in sources.md. Every source must be cited at least once.

== PROCESS ==

Step 1: Read the scope brief. Plan which sub-questions go in which file.

Step 2: For each sub-question, do iterative WebSearch + WebFetch. Prefer primary sources: government data, official documentation, peer-reviewed papers, SEC filings, original press releases. Wikipedia is OK for navigation but cite primary sources, not the Wikipedia page itself.

Step 3: Write 01-overview.md (and 02+) and sources.md DIRECTLY using the Write tool. Watch line count. Split at ~700 lines.

Step 4: Self-validate before returning. Re-read each file. For each factual sentence, verify a URL or [^N] is present. For each [^N], confirm sources.md has the entry. For each entry, confirm at least one [^N] reference exists.

Step 5: Output the manifest block (last thing in your response):

RESEARCH_MANIFEST_START
slug: [DATE-SLUG]
files_written: [list]
total_lines: [sum across report files]
sources_count: [count of [^N] in sources.md]
claims_count: [estimate of factual assertions]
self_check_no_uncited_claims: true
abandoned: false
notes: [one sentence summary]
RESEARCH_MANIFEST_END

== TOOLING TIPS ==

- WebSearch is for discovery. Use iteratively.
- WebFetch returns rendered markdown. Cite specific facts, not whole pages.
- If WebFetch errors or hits a paywall, find an alternate source.
- Reasonable budget: 10-25 WebSearch + WebFetch calls combined per topic.

Begin.
```

---

## CronCreate Scheduling

```
cron: "18,48 * * * *"
durable: true               NO EFFECT — jobs are session-only (see note below)
recurring: true
```

**Session-only — read this before relying on the cron.** `CronCreate` jobs live only in this
Claude session. Nothing is written to disk, and the job is gone when Claude exits. The
`durable` param has **no effect**; there is no `.claude/scheduled_tasks.json` on disk.
Recurring jobs also auto-expire after 7 days, and fire only while the REPL is idle — never
mid-query.

That lifetime is **correct for this skill**: the cron watches the session it lives in, so if
that session dies there is nothing left for it to tick for. Full-crash recovery is a fresh
`--continue` invocation, not a timer. What the cron is actually for is the **timeout
watchdog** — a hung agent never completes and so never notifies, and that is the one thing
only a timer can catch.

30-minute interval is generous for most research topics (typical wave: 30-45 min). The in-progress check in Phase 3b prevents overlap if a wave runs long.

---

## Failure Modes

1. **Agent bluffs claims without URLs**: caught by the citation validator. Topic moves to `flagged/`.
2. **Topic unanswerable from public sources**: Opus writes a "could not be completed" file with `abandoned: true`. Orchestrator treats it as a successful-but-empty completion.
3. **Sonnet scope-check produces malformed brief**: orchestrator parses for the blocks. If neither found OR malformed: treat as `failed-scope`, advance.
4. **Opus produces a file > 750 lines**: split agent runs. If split fails twice, mark wave failed-validation.
5. **WebSearch / WebFetch unavailable**: Opus reports `abandoned: true`. Orchestrator continues.
6. **RAM exhaustion**: Phase 2 Step 1 detects, kills stale processes, retries once, aborts marathon if still over.
7. **Cron leak**: stale-state detection + self-heal recover on next invocation.
8. **State file corruption**: orchestrator catches JSON parse errors and prompts to reset.

---

## Important Notes

- **Research files are markdown** — apply your project's normal copy-style rules to them.
- **Each wave files 1 topic** — research is depth, not breadth.
- **Opus is the ONLY model that does deep research** — Sonnet is too shallow on synthesis across 15+ sources. Sonnet is used only for the cheap scope-check gate and the line-split agent.
- **The temp JS file pattern is mandatory** — never `node -e "..."` with template literals. Backticks in markdown content break Windows bash shell quoting.
- **Cron auto-expires after 7 days** — research marathons are designed for 4-8 hour runs anyway.
- **HARD RULE #5 has zero tolerance** — if you find yourself wanting to ask the user a question mid-run, the answer is to FAIL the topic into `failed/` and continue.
