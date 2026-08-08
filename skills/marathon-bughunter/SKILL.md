---
name: marathon-bughunter
description: "Long-running walkaway session that drives a Chrome DevTools browser through your web app to hunt for new bugs introduced by recent code changes. Each wave walks a route or flow, inspects console/network/DOM/layout, and files concrete BUG entries to the backlog. Invoke with /marathon-bughunter [--stop] [--status] [--continue] [--since <ref>] [dry-run]."
---

# Marathon Bughunter Skill

## Configure for your project

Before using this skill, swap these placeholders for your project values:

- `<project-root>` — absolute path to your project root (e.g. the directory you run `git` in)
- `<backlog-dir>` — absolute path to the directory holding `bugs.md` (and friends)
- `<state-dir>` — absolute path where this skill writes its state JSON and lock file (commonly `<project-root>/.claude`)
- `<dev-url>` — your dev server URL (e.g. `http://localhost:5173`)
- `<src-pages-glob>` — glob for files that map to routes (e.g. `src/pages/**`, `apps/web/src/pages/**`)
- `<evidence-dir>` — temp directory for screenshots and DOM snapshots (e.g. `<project-root>/.tmp/bughunter`)

If your app requires login, use a dedicated test account; configure credentials via environment variables, not in this skill file.

## Purpose

Runs a sustained, unattended visual QA loop against a running dev server. Each wave:

1. Picks the next **hunt target** from a rotation queue (recent-commit routes + core pages + flows)
2. Navigates via Chrome DevTools MCP and captures evidence (screenshots, console, network, DOM snapshot)
3. Interacts with the UI (click, fill, scroll, resize) following target-specific steps
4. Detects bugs: console errors, failed requests, visual regressions, broken interactions, console floods, layout breaks, 404s, auth failures
5. **Files new BUG entries** to `<backlog-dir>/bugs.md` with concrete details and cited evidence
6. Loops via **CronCreate** every 30 minutes

Use `/marathon-bughunter` after (or during) a code-execution loop to catch regressions. It is designed to run in parallel with that loop: the executor ships code, bughunter finds what it broke, the next intake cycle picks those bugs up.

Unlike one-shot UI review skills, this skill runs unattended for hours and files bugs directly into the backlog.

## Invocation

```
/marathon-bughunter                    Start fresh, default rotation queue
/marathon-bughunter --since HEAD~10    Focus on routes touched in last 10 commits
/marathon-bughunter --since main@{1h}  Focus on what changed in the last hour
/marathon-bughunter core               Core pages only
/marathon-bughunter admin              Admin pages only
/marathon-bughunter --stop             Pause after current wave completes
/marathon-bughunter --status           Show current wave, routes covered, bugs filed
/marathon-bughunter --continue         Manual re-entry if cron misfired
/marathon-bughunter dry-run            Show rotation queue + recent-commit analysis, stop
```

## Prerequisites

- Dev server running at `<dev-url>`
- Chrome launched with `--remote-debugging-port=9222`
- Chrome DevTools MCP server connected
- A test account credential pair available via env vars (see "Configure for your project" above)

If any prerequisite is missing at launch time, Phase 1 runs preflight checks automatically and aborts with an actionable error.

## State File

```
<state-dir>/marathon-bughunter-state.json
```

Written via the temp JS file pattern.

Schema:
```json
{
  "sessionId": "bughunter-YYYY-MM-DDTHH-MM",
  "status": "running | paused | complete | aborted",
  "paused": false,
  "cronJobId": "cron_xxx",
  "startedAt": "ISO timestamp",
  "sinceRef": "HEAD~10 or null",
  "recentCommitRoutes": ["/route-a", "/route-b"],
  "currentWave": 0,
  "rotationQueue": [
    { "kind": "route",    "target": "/route-a",   "reason": "touched by commit abc in last 5 commits" },
    { "kind": "flow",     "target": "onboarding", "reason": "core onboarding flow" },
    { "kind": "viewport", "target": "/route-a@375", "reason": "mobile regression check" }
  ],
  "rotationIndex": 0,
  "waves": [
    {
      "waveNumber": 1,
      "kind": "route",
      "target": "/route-a",
      "startedAt": "ISO",
      "completedAt": "ISO",
      "status": "complete",
      "consoleErrorsFound": 3,
      "networkFailuresFound": 1,
      "visualIssuesFound": 2,
      "interactionFailuresFound": 0,
      "bugsFiled": 4,
      "bugIdsFiled": ["BUG-080", "BUG-081", "BUG-082", "BUG-083"],
      "evidenceDir": "<evidence-dir>/wave-1/"
    }
  ],
  "totalBugsFiled": 0,
  "screenshotsDir": "<evidence-dir>/"
}
```

## Backlog Location

```
<backlog-dir>/bugs.md
```

All new bugs file here. The bughunter never modifies other backlog files.

---

## Workflow

### Phase 0: Invocation Parsing

Parse flags first:

- `--stop`: read state, mark `paused: true`, `CronDelete(state.cronJobId)`, delete lock file, print summary, stop.
- `--status`: read state, pretty-print wave progress, bugs filed per wave, total bugs filed. Stop.
- `--continue`: skip to Phase 3.
- `dry-run`: run Phase 1 through rotation queue build and recent-commit analysis, print plan, stop.
- `--since <ref>`: override recent-commit window.
- `core` / `admin` positional arg: restrict rotation queue to one section.
- No state file: fresh start, continue to Phase 1.
- State file with `paused: false`: cron re-entry, skip to Phase 3.

#### Phase 0.1: Stale state detection

1. **Lock file staleness**: Delete `<state-dir>/scheduled_tasks.lock` if PID dead or older than 4 hours.

2. **Cron consistency**: If state says `running` with a `cronJobId` and `CronList()` does not show it AND state has not been touched in >60 minutes, prompt:
   ```
   STALE BUGHUNTER MARATHON DETECTED
   ==================================
   State file says status=running but cron job [ID] is not scheduled.
   Last state update: [age] ago.
   Reset state to complete? [y/n]
   ```
   If y: write `status: "complete"`, `abortedBy: "stale detection"`. If n: stop.

3. **12-hour hard cap**: Auto-abort if `startedAt` > 12 hours ago.

---

### Phase 1: Fresh Start (user is present)

**Step 1 — Preflight**

Run inline checks:
- Dev server reachable at `<dev-url>`
- Chrome DevTools MCP responds to `mcp__chrome-devtools__list_pages`
- Test account can authenticate (soft check)

If any check fails: print a specific error and stop. Do not launch the cron.

**Step 2 — Analyze recent commits**

Build the recent-commit route list to prioritize routes touched by recent work:

```bash
git -C <project-root> log --format="%H %s" [SINCE_REF]..HEAD -- "<src-pages-glob>"
```

Default `SINCE_REF` if `--since` not provided: `HEAD~20` OR `main@{24 hours ago}`, whichever is more recent.

For each commit, extract:
- Modified files under `<src-pages-glob>`
- Map files to routes using your project's pages-to-routes table (see "Pages to Routes Map" section below — EDIT THIS for your project)
- The commit ID and one-line message

Deduplicate into `{ route, lastTouchedBy: "COMMIT_SHA title" }` entries.

**Step 3 — Build rotation queue**

Three kinds of hunt target:

1. **route** — a URL path. Load it, interact lightly, collect evidence.
2. **flow** — a named multi-step user journey. Follow a scripted sequence.
3. **viewport** — a URL path with a specific viewport size for mobile checks.

Default rotation:

```
Recent commit routes (highest priority):
  route   /route-a   touched by [commit]
  route   /route-b   touched by [commit]

Core routes (always included — EDIT THIS for your project):
  route   /          home
  route   /admin     admin (if applicable)
  ...

Core flows (EDIT THIS for your project):
  flow    onboarding   first-time user onboarding
  flow    primary-cta  the main happy-path action

Mobile viewport checks:
  viewport /@375
  viewport /<key-page>@375

Error path probes:
  route   /nonexistent-route    404 handling
  route   /admin (as non-admin) permission gate
```

Apply positional arg filters to trim the queue.

**Step 4 — Present the plan**

```
MARATHON BUGHUNTER PLAN
========================
Recent-commit window: HEAD~20 ([N] commits analyzed)
Routes touched by recent work: [N]

Rotation queue ([N] waves, ~10-15 min each):

 1. route    /route-a       [touched by commit]
 2. flow     onboarding     [core flow]
 3. viewport /key-page@375  [mobile regression check]
 ...

Estimated duration: ~[N * 20] minutes
Cron interval: 30 minutes (fires at :23, :53)

Dev server: <dev-url>
Evidence:   <evidence-dir>/wave-[N]/

For dry-run: stop here.
```

**Step 5 — Pre-flight settings update (REQUIRED)**

Update `~/.claude/settings.json` to add these entries to `permissions.allow` if not already present:

```json
"Edit(<backlog-dir>/bugs.md)",
"Write(<backlog-dir>/bugs.md)",
"Edit(<state-dir>/marathon-bughunter-state.json)",
"Write(<state-dir>/marathon-bughunter-state.json)",
"Write(<evidence-dir>/**)"
```

Tell the user: "Updating settings.json to pre-approve bug filings and evidence writes for unattended operation."

**Step 6 — Confirm**

Ask: "Ready to launch marathon bughunter with [N] hunt targets (~[N * 20] min)? [y/n]"

**Step 7 — Write initial state file**

Use the temp JS file pattern.

**Step 8 — Register the cron loop**

Use CronCreate:
- `cron`: `23,53 * * * *`
- `durable`: `true`
- `recurring`: `true`
- `prompt`: instructs the cron tick to read the state file, read this skill file, and execute Phase 3.

```
This is an automated marathon-bughunter loop tick.

RESOURCE DISCIPLINE — MANDATORY:
- Chrome DevTools MCP tools ARE permitted in this tick (this skill IS the reason the browser is running).
- Do NOT spawn new Agent() subagents. All browser work happens inline in the tick handler.
- Always run Phase 3a (self-heal / terminal-state check) FIRST. If any terminal condition is met, CronDelete and exit without touching the browser.

WORKFLOW:
1. Read the state file at <state-dir>/marathon-bughunter-state.json
2. Read the full marathon-bughunter skill instructions
3. Execute Phase 3 (Wave Loop Tick).

Do not ask the user for confirmation.
```

Write the returned `cronJobId` into the state file.

**Step 9 — Launch Wave 1 immediately**

Go to Phase 2 without waiting for the first cron tick.

---

### Phase 2: Launch Wave

Read the state file. Pop the next entry from `rotationQueue[rotationIndex]`.

**Step 1 — Ensure authenticated session**

First wave: navigate to `<dev-url>`. Check for a login screen. If present, fill credentials from environment variables and submit.

Subsequent waves: assume session persists. If a wave hits a login screen unexpectedly, re-auth and note it as an anomaly (worth filing as an auth regression bug if it recurs).

**Step 2 — Reset console + network log**

Before navigating to the target, clear stale state. If the MCP server does not support `clear`, take a baseline snapshot before navigation and diff against the post-navigation snapshot.

**Step 3 — Create evidence directory**

```bash
mkdir -p <evidence-dir>/wave-[N]/
```

**Step 4 — Execute the hunt (branch by kind)**

### Kind: route

```
1. mcp__chrome-devtools__navigate_page({ url: '<dev-url>[TARGET]' })
2. mcp__chrome-devtools__wait_for({ networkIdle: true, timeout: 10000 })
3. mcp__chrome-devtools__take_screenshot({ path: '<evidence-dir>/wave-[N]/initial.png', fullPage: true })
4. mcp__chrome-devtools__list_console_messages()
5. mcp__chrome-devtools__list_network_requests()
6. mcp__chrome-devtools__take_snapshot()
7. Lightweight interaction pass:
   - Scroll to bottom via evaluate_script
   - Click any visible button that looks safe (buttons with data-testid, NOT destructive actions like delete/logout/cancel)
   - If a modal opens, screenshot it and close via ESC
   - Hover over prominent cards
8. Take after-interaction screenshot
9. Re-collect console + network
```

### Kind: flow

Flows have scripted step sequences (see "Flow Scripts" below — EDIT THIS for your project). Each step is a nav + interaction + screenshot + console check. A flow runs 5-10 steps and captures evidence at each.

### Kind: viewport

```
1. Parse target: "/key-page@375" -> url=/key-page, viewport=375
2. mcp__chrome-devtools__resize_page({ width: 375, height: 667 })
3. Navigate, wait, screenshot
4. Check for horizontal scroll via evaluate_script: document.documentElement.scrollWidth > window.innerWidth
5. Check for overflow-hidden elements hiding content
6. Check touch target sizes: query for button/a elements with computed size < 44x44
7. Scroll through the full page, screenshot every ~800px
8. Collect console + network
9. Resize back to 1280x800 after the wave
```

**Step 5 — Detect bugs**

A bug is worth filing if:

1. **Console error** — any message with `level: "error"` not on the ignore list.
2. **Network failure** — any non-asset request with status `>= 400` or `status: 0`. Exclude favicon, DevTools internals, expected-failing analytics endpoints.
3. **Console flood** — same error message appears >5 times on a single page load. File as high priority.
4. **Visual issue** — horizontal scroll on mobile when overflow-x should be hidden, text overflow, broken images, zero-dimension cards that claim data, modal stacking issues.
5. **Interaction failure** — a click on a button with a known testid did not produce a navigation, modal open, or DOM mutation within 2 seconds.
6. **Auth regression** — hitting a page forced an unexpected re-login.
7. **404 on expected route** — a route that worked yesterday now 404s.

For each detected bug, record category, severity, evidence (screenshot paths, message text, network details), route, the acceptance condition (the observable check that proves the bug is gone, e.g. "route /x loads with zero console errors at 375px"), and the recent commit that most likely caused it.

**Severity heuristic:**
- critical: console flood, auth regression, blank page, build crash visible in console
- high: unhandled console error on core route, network 500 on data fetch
- medium: visual issue visible on first paint, network 4xx on non-critical endpoint
- low: minor layout issues, console warnings, edge-case interaction failures

**Step 6 — Dedup against existing bugs**

Before filing, read `<backlog-dir>/bugs.md` and check for existing entries with overlapping route, error message substring, or symptom phrasing.

If a duplicate is found: do NOT file. Append a note to the existing bug:
```
- **Bughunter re-confirmed**: [DATE] wave [N] route [target] — still present
```

**Step 7 — File new bugs**

Append a new entry to `<backlog-dir>/bugs.md` using the temp JS file pattern. Use the file's `<!-- Next ID: N -->` counter to assign IDs.

```js
// <evidence-dir>/bughunter-wave-[N]-bug-[M].js
const fs = require('fs');
const p = '<backlog-dir>/bugs.md';
let content = fs.readFileSync(p, 'utf8');
const match = content.match(/<!-- Next ID: (\d+) -->/);
const nextId = parseInt(match[1], 10);
const newId = 'BUG-' + String(nextId).padStart(3, '0');
const entry = `
### [${newId}] ${TITLE}
- **Added**: ${TODAY}
- **Priority**: ${PRIORITY}
- **Source**: bughunter wave ${WAVE_NUM} route ${ROUTE}
- **Details**: ${DETAILS}
- **Acceptance**: ${ACCEPTANCE}
- **Evidence**: screenshot <evidence-dir>/wave-${WAVE_NUM}/[file].png. Console: "${CONSOLE_MSG}". Network: ${NETWORK_SUMMARY}.
- **Likely cause**: ${LIKELY_COMMIT} (${LIKELY_COMMIT_MSG})
- **Context**: Filed during marathon-bughunter run ${SESSION_ID}.
`;
content = content.replace(/<!-- Next ID: \d+ -->/, '<!-- Next ID: ' + (nextId + 1) + ' -->');
content = content.replace(/(<!-- Next ID: \d+ -->\n)/, '$1' + entry);
fs.writeFileSync(p, content);
console.log('FILED:' + newId);
```

**Step 8 — Update state file**

Push the wave entry into `state.waves`, advance `rotationIndex`, increment `totalBugsFiled`.

**Step 9 — Report wave results**

```
MARATHON BUGHUNTER WAVE [N] COMPLETE
======================================
Hunt: [kind] [target]
Console errors:      [N]
Network failures:    [N]
Visual issues:       [N]
Interaction fails:   [N]
Bugs filed:          [N] ([BUG-080, ...])
Duplicates skipped:  [N]
Evidence:            <evidence-dir>/wave-[N]/

Rotation progress: [N]/[total] targets swept
Total bugs filed this session: [N]
Next wave in ~30 min: [next target]
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
- `state.rotationIndex >= state.rotationQueue.length` (queue exhausted, go to Phase 4)

On termination, delete `<state-dir>/scheduled_tasks.lock` if present. Do NOT tear down the chrome-devtools-mcp session explicitly.

**3b. In-progress check**

If the last wave entry has `status: "in-progress"`: a prior tick is still running. Stop.

**3c. Browser health check**

Call `mcp__chrome-devtools__list_pages`. If it fails or returns empty, the browser has crashed. Set `status: "aborted"`, `abortedBy: "browser unavailable"`, delete cron, print recovery message, stop.

**3d. Launch next wave**

Go to Phase 2.

---

### Phase 4: Marathon Complete

1. `CronDelete(state.cronJobId)`
2. Update state to `status: "complete"`.
3. Cleanup: delete `<state-dir>/scheduled_tasks.lock` if present. Do NOT delete the evidence directory.
4. Print final report:

```
MARATHON BUGHUNTER COMPLETE
============================
Session: [sessionId]
Started: [startedAt]
Completed: [now]
Waves completed: [N]
Routes swept: [N]
Flows swept: [N]
Mobile viewports checked: [N]

Bugs filed: [N] total
  critical: [N]
  high:     [N]
  medium:   [N]
  low:      [N]

Evidence: <evidence-dir>/ ([N] screenshots, [N] DOM snapshots)
```

---

## Pages to Routes Map (EDIT THIS for your project)

Translate modified files into routes to hunt. Example shape:

```
src/pages/HomePage.tsx           -> /
src/pages/AdminPage.tsx          -> /admin
src/components/onboarding/**     -> flow:onboarding
```

When a commit touches a file not in the table, add the file path as informational but do not route-map it.

## Flow Scripts (EDIT THIS for your project)

Each flow is a scripted multi-step journey. Examples below — replace with the flows that matter for your app.

### onboarding

```
1. navigate /onboarding (or trigger via the onboarding entry point)
2. wait_for the first step
3. screenshot
4. Click through each step:
   - At each step: screenshot, list_console_messages, check for stuck states
   - If a step is stuck (>10 sec with no DOM mutation), record interaction failure
5. Verify expected post-onboarding state
6. Exit
7. Navigate back to home, confirm persistence
```

### primary-cta

```
1. navigate to the page hosting the main happy-path action
2. Find the CTA (DOM query for data-testid)
3. Click it
4. Verify the expected modal/route/state change
5. Complete the action (do NOT trigger destructive variants)
6. Verify success state
7. Check console for errors during the success cascade
```

---

## CronCreate Scheduling

```
cron: "23,53 * * * *"
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

30-minute interval gives breathing room for the browser to stabilize between hunts.

---

## Dedup Strategy

Three layers:

1. **Against existing backlog**: before filing, read `bugs.md` and check every new bug against every existing bug by (route + error message substring).
2. **Within session**: track filed `bugIdsFiled` per wave.
3. **Re-confirm append**: when a duplicate is found, append a re-confirmed line to the existing entry so age and persistence are visible.

---

## Evidence Retention

All screenshots and DOM snapshots land under `<evidence-dir>/wave-[N]/`. The skill does not clean these up automatically. The user can manually clear `<evidence-dir>/` between marathons. Add a pre-flight cleanup step if disk space becomes an issue.

---

## Failure Modes

1. **Browser crashes mid-session**: Phase 3c catches this and aborts cleanly.
2. **Auth regression forces re-login every wave**: the auth check handles it but flags it. If recurring, file a critical auth bug.
3. **Flood of low-quality bugs**: if a single console message appears on >60% of routes in one session, file ONE high-severity bug covering all routes rather than spamming.
4. **False positives from dev-only warnings**: maintain an ignore list for HMR noise, favicon 404, expected dev overrides.
5. **Cron leak**: stale detection + self-heal in Phase 3a.
6. **Evidence directory grows unbounded**: documented behavior; user-managed cleanup.
