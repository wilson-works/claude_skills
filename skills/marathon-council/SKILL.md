---
name: marathon-council
description: "Long-running walkaway session that rotates through focus areas, researches the codebase, convenes product councils, and files work orders to the backlog. Designed as the intake half of a continuous improvement loop -- marathon-council fills the backlog, marathon-orders executes it. Invoke with /marathon-council [--stop] [--status] [--continue] [dry-run]."
---

# Marathon Council Skill

## Configure for your project

Before using this skill, swap these placeholders for values that fit your environment:

- `<your-project-backlog-path>` -- absolute path to the directory holding `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, `completed.md`
- `<state-dir>` -- absolute path to the directory where the marathon state file should live (e.g. `<project-root>/.claude`)
- `<project-root>` -- absolute path to the repository root the skill operates against
- `<PRODUCT_DESCRIPTION>` -- a short paragraph describing your product (positioning, stack, data model, pricing tiers, hard rules) that gets injected into every council prompt

## Purpose

Runs a sustained, unattended council research loop over 4-8 hours. Each wave:

1. Picks the next **focus area** from a rotation queue
2. **Researches** the codebase to find real gaps (not hypothetical ones)
3. **Convenes** a 5-member product council with research findings injected as evidence
4. **Files** 25-30 work orders to the backlog with deduplication against prior waves
5. Loops via **CronCreate** every 45 minutes

This is the intake half of a continuous improvement loop:
- `/marathon-council` fills the backlog with well-researched, evidence-backed work orders
- `/marathon-orders` executes them with Opus agents

Use `/council-orders` for a single one-shot council session. Use `/marathon-council` when you want deep, rotating coverage across multiple focus areas while you walk away.

## Invocation

```
/marathon-council                     Start fresh, full rotation queue
/marathon-council [focus1,focus2,...]  Custom rotation (comma-separated focus areas)
/marathon-council --stop              Pause after current wave completes
/marathon-council --status            Show current wave, rotation progress, items filed
/marathon-council --continue          Manual re-entry if cron misfired
/marathon-council dry-run             Show rotation queue without launching
```

## Focus Area Rotation

Default rotation queue (one per wave, cycled in order):

```
0. user-feedback-triage      -- Debate real user feedback, promote valid items to dev proposals
1. enterprise-readiness      -- Fortune 500 demo-killer gaps (default council-orders framing)
2. security-hardening        -- SOC 2, pen-test, auth, data rules, PII
3. mobile-responsive         -- Mobile breakpoints, touch targets, responsive layouts
4. onboarding-retention      -- First-run experience, activation, empty states, email flows
5. feature-area-readiness    -- Per-feature-area gaps (cycles through your product's main feature areas)
6. design-polish             -- Visual consistency, token compliance, loading/error states, polish
7. platform-scale            -- Hot docs, cold starts, indexes, cost, idempotency, monitoring
8. admin-experience          -- Admin controls, reporting, team management, audit, provisioning
9. billing-monetization      -- Plan enforcement, upgrade flows, feature gating, payment edge cases
10. accessibility-compliance -- WCAG, ADA, keyboard nav, screen readers, DPA, opt-out rights
```

If the user provides a custom list (e.g., `/marathon-council security-hardening,mobile-responsive,design-polish`), only those focus areas run, in the order specified.

For `feature-area-readiness`, the wave cycles through one feature area per council. The skill uses a priority order configured for the product. On subsequent passes it continues the rotation.

## State File

```
<state-dir>/marathon-council-state.json
```

Written exclusively via `Bash(node -e ...)` to stay within pre-approved permissions.

Schema:
```json
{
  "sessionId": "council-marathon-YYYY-MM-DDTHH-MM",
  "status": "running | paused | complete",
  "paused": false,
  "cronJobId": "cron_xxx",
  "startedAt": "ISO timestamp",
  "currentWave": 0,
  "rotationQueue": ["enterprise-readiness", "security-hardening", ...],
  "rotationIndex": 0,
  "featureAreaIndex": 0,
  "waves": [
    {
      "waveNumber": 1,
      "focus": "enterprise-readiness",
      "startedAt": "ISO",
      "completedAt": "ISO",
      "status": "complete | in-progress | failed",
      "researchFindings": ["finding1", "finding2"],
      "itemsFiled": 28,
      "duplicatesSkipped": 2,
      "idRanges": { "FTR": "157-168", "BUG": "031-035", "DSN": "042-045", "TDT": "019-022" },
      "chairmanSynthesis": "brief text"
    }
  ],
  "totalItemsFiled": 0,
  "totalDuplicatesSkipped": 0
}
```

## Backlog Location

```
<your-project-backlog-path>
```

Files: `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, `completed.md`

---

## Workflow

### Phase 0: Invocation Parsing

Parse flags before doing anything else:

- `--stop` flag: read state file. If it exists, write `paused: true` via node, call `CronDelete(state.cronJobId)`, print summary. If no state file, print "No marathon council in progress." Stop.
- `--status` flag: read state file. Pretty-print: session ID, current wave, rotation progress, items filed per wave, total items filed, total duplicates skipped. Stop.
- `--continue` flag: skip to Phase 3 directly.
- `dry-run` argument: show rotation queue and estimated runtime. Stop.
- **No state file exists**: fresh start, continue to Phase 1.
- **State file exists and `paused: false`**: cron re-entry, skip to Phase 3.

### Phase 1: Fresh Start (user is present)

**Step 1 -- Parse rotation queue**

If user provided custom focus areas, parse them. Otherwise use the default 10-area rotation.

**Step 2 -- Present the plan**

```
MARATHON COUNCIL PLAN
======================
Rotation queue (one council per wave, ~45 min each):

 1. enterprise-readiness    -- Fortune 500 demo-killer gaps
 2. security-hardening      -- SOC 2 / pen-test / auth gaps
 3. mobile-responsive       -- Mobile breakpoints and touch UX
 ...

Estimated duration: ~[N * 45] minutes ([N] waves)
Cron interval: 45 minutes

For dry-run: stop here.
```

**Step 3 -- Pre-flight settings update (REQUIRED)**

Update `~/.claude/settings.json` to add these entries to `permissions.allow` if not already present:

```json
"Edit(<your-project-backlog-path>/**)",
"Write(<your-project-backlog-path>/**)",
"Edit(<state-dir>/marathon-council-state.json)",
"Write(<state-dir>/marathon-council-state.json)"
```

Tell the user: "Updating settings.json to pre-approve backlog writes for unattended operation."

**Step 4 -- Confirm**

Ask: "Ready to launch marathon council with [N] focus areas (~[N*45] min)? [y/n]"

If n: stop. If y: continue.

**Step 5 -- Write initial state file**

```bash
node -e "
const fs = require('fs');
const state = {
  sessionId: 'council-marathon-' + new Date().toISOString().slice(0, 16).replace(':', '-'),
  status: 'running',
  paused: false,
  cronJobId: '',
  startedAt: new Date().toISOString(),
  currentWave: 0,
  rotationQueue: ROTATION_QUEUE_JSON,
  rotationIndex: 0,
  featureAreaIndex: 0,
  waves: [],
  totalItemsFiled: 0,
  totalDuplicatesSkipped: 0
};
fs.mkdirSync('<state-dir>', { recursive: true });
fs.writeFileSync('<state-dir>/marathon-council-state.json', JSON.stringify(state, null, 2));
console.log('STATE_WRITTEN');
"
```

**Step 6 -- Register the cron loop**

Use CronCreate:
- `cron`: `3/45 * * * *` (fires at :03, :48 of every hour -- offset from marathon-orders' :07/:27/:47)
- `durable`: `true`
- `recurring`: `true`
- `prompt`:

```
This is an automated marathon-council loop tick.

1. Read the marathon council state file:
   <state-dir>/marathon-council-state.json

2. Read the full marathon-council skill instructions:
   ~/.claude/skills/marathon-council/SKILL.md

3. Execute Phase 3 (Wave Loop Tick) as documented in the skill.

The skill will check for paused state, determine if the current wave is complete, launch the next wave if ready, and handle marathon completion. Do not ask the user for confirmation.
```

Write the returned `cronJobId` into the state file via node.

**Step 7 -- Launch Wave 1 immediately**

Do not wait for the first cron tick. Go to Phase 2 now.

---

### Phase 2: Launch Wave

Read the state file. Determine the current focus area from `rotationQueue[rotationIndex]`.

**Step 1 -- Resolve focus framing**

Map the focus area to a council framing string:

| Focus area | Framing |
|---|---|
| user-feedback-triage | SPECIAL: see User Feedback Triage section below |
| enterprise-readiness | "Fortune 500 demo readiness. If a VP of HR, CTO, or Sales Ops director saw a 20-minute demo on Monday, what would kill the deal?" |
| security-hardening | "Enterprise security review. A staff security engineer is doing a pre-purchase audit. What fails SOC 2, pen-test, or compliance review?" |
| mobile-responsive | "Mobile-first audit. A user opens the product on their phone during a commute. What breaks, looks wrong, or is unusable on a 375px viewport?" |
| onboarding-retention | "First-run experience. A new user just signed up. What's confusing, empty, broken, or missing in their first 10 minutes? What makes them not come back tomorrow?" |
| feature-area-readiness | "Feature-area buyer demo: [FEATURE_AREA_NAME]. A buyer for that feature area is evaluating the product. What terminology, workflow, or feature gap makes them say 'this isn't built for us'?" |
| design-polish | "Design quality audit. A Principal Designer is reviewing every screen. What reads as 'side project' vs. 'funded product'? Focus on token compliance, consistency, loading/error/empty states, and polish." |
| platform-scale | "Scale readiness. 500 teams, 10K users, peak hours. What breaks first? Hot documents, cold starts, missing indexes, cost runaway, data integrity gaps?" |
| admin-experience | "Admin war room. A team owner with 50 members needs to manage their team. What's missing, broken, or buried in admin controls, reporting, provisioning, and audit?" |
| billing-monetization | "Monetization audit. A user on Free wants to upgrade. What's broken in plan enforcement, upgrade flows, feature gating, or payment edge cases? What leaks premium features to free users?" |
| accessibility-compliance | "Accessibility and compliance. An HR director with legal oversight is evaluating. What fails WCAG 2.1 AA, keyboard navigation, screen reader support, DPA requirements, or employee opt-out rights?" |

For `feature-area-readiness`, cycle through your product's feature areas using `state.featureAreaIndex`. Each area should have a buyer role attached so the framing reads naturally (e.g. "Operations Manager at a mid-size company").

**Step 2 -- Codebase research pass**

This is the key differentiator from plain `/council-orders`. Before convening the council, the orchestrator researches the actual codebase to find concrete evidence of gaps.

Run targeted research based on the focus area:

**For enterprise-readiness:**
- Grep for `admin`, `audit`, `role`, `provision`, `SSO`, `SCIM`, `export` across client and server source
- Check if admin panel exists and what controls it exposes
- Check audit log implementation completeness

**For security-hardening:**
- Read your data security rules (e.g. `firestore.rules`, IAM policies) in full
- Grep for `allow`, `request.auth`, `resource.data` in rules
- Grep for `any` type assertions in server code
- Check server-side authorization patterns
- Look for client-side-only security checks

**For mobile-responsive:**
- Grep for `@media`, `sm:`, `md:`, `lg:` breakpoint usage in components
- Check if touch targets exist (min 44px)
- Look for fixed widths that break on mobile

**For onboarding-retention:**
- Read walkthrough and onboarding components
- Check empty state handling across main views
- Look for first-run detection logic

**For feature-area-readiness:**
- Read your feature-area config module
- Check the target area's config completeness
- Grep for hardcoded terminology from other areas

**For design-polish:**
- Read your design system docs
- Grep for off-token color values (hex codes not in design system)
- Check loading/error state coverage in main components

**For platform-scale:**
- Check database index definitions
- Look for document fan-out patterns in server code
- Grep for missing error handling in async operations

**For admin-experience:**
- Read admin components
- Check what admin actions are available vs. missing
- Look for admin-only server functions

**For billing-monetization:**
- Read plan enforcement logic in your shared package
- Check if feature gating is server-side or client-side only
- Look for billing-related server functions

**For accessibility-compliance:**
- Grep for `aria-`, `role=`, `tabIndex` usage
- Check form label associations
- Look for keyboard event handlers

Compile findings into a **research brief** -- a bulleted list of 8-15 concrete findings with file paths and line numbers. This brief is injected into every advisor prompt so they argue from evidence, not theory.

**Step 3 -- Read current backlog state**

Read all four backlog files to get:
- Current `<!-- Next ID: N -->` values
- Last 30 items per file (to build dedup summary)
- Items filed by previous waves in this session (from state file)

Build a comprehensive "already filed" summary so advisors do not duplicate.

**Step 4 -- Spawn 5 advisors in parallel**

Use the Agent tool to spawn all 5 advisors simultaneously. Each advisor receives:

- Their lens identity (same 5 lenses as `/council-orders`)
- The product context block
- The **focus framing** for this wave
- The **research brief** from Step 2 (concrete evidence from the codebase)
- The dedup summary (existing backlog + items filed in prior waves this session)
- Instructions to produce exactly 5 work orders

**Advisor prompt template:**

```
You are [ADVISOR TITLE] on a product council.

Your lens: [LENS DESCRIPTION]

[PRODUCT CONTEXT BLOCK -- same as council-orders]

FOCUS FOR THIS SESSION: [FRAMING STRING FROM STEP 1]

CODEBASE RESEARCH FINDINGS (evidence from the actual code -- use these to ground your work orders in reality, not theory):

[RESEARCH BRIEF -- bulleted list of findings with file paths]

ALREADY IN THE BACKLOG (do NOT duplicate these):
[DEDUP SUMMARY -- IDs and titles of existing items + items from prior waves]

YOUR JOB: Produce exactly 5 work orders that a developer could execute. Each must:
- Be grounded in the research findings above (cite a specific file or gap when possible)
- Be a gap you would personally block a deal over from your lens
- Not duplicate anything in the "already filed" list
- Be actionable within a single focused work session (no multi-sprint epics)

Format each as:
[CATEGORY] Title
Priority: critical/high/medium/low
Details: 2-3 specific sentences. Name components, collections, functions, file paths.
Why it matters: one sentence on the failure mode or buyer objection this closes.

No preamble. Output exactly 5 work orders.
```

**Step 5 -- Collect and deduplicate**

After all 5 advisors return, collect work orders. Deduplicate:
- Against each other (merge overlapping items from different advisors)
- Against the existing backlog
- Against items filed in previous waves this session

**Step 6 -- Run the Chairman**

Same as `/council-orders` -- Chairman synthesizes, adds 5 gap items. Include the research brief in the Chairman prompt too.

**Step 7 -- File all work orders to the backlog**

Follow the same filing rules as `/council-orders`:
- Sequential IDs from current Next ID values
- Sorted by priority within each file
- `- **Council**: [Advisor Name] (marathon wave [N]: [focus])` tag on each item
- Update `<!-- Next ID: N -->` comments
- Section header: `<!-- MARATHON COUNCIL WAVE [N] -- [FOCUS] -- Filed [DATE] -->`

**Step 8 -- Update state file**

```bash
node -e "
const fs = require('fs');
const state = JSON.parse(fs.readFileSync('<state-dir>/marathon-council-state.json', 'utf8'));
state.currentWave = WAVE_NUM;
state.rotationIndex = (state.rotationIndex + 1) % state.rotationQueue.length;
// For feature-area-readiness, also advance featureAreaIndex
state.waves.push({
  waveNumber: WAVE_NUM,
  focus: 'FOCUS',
  startedAt: 'ISO',
  completedAt: new Date().toISOString(),
  status: 'complete',
  researchFindings: FINDINGS_ARRAY,
  itemsFiled: ITEMS_COUNT,
  duplicatesSkipped: DUPES_COUNT,
  idRanges: { FTR: 'X-Y', BUG: 'X-Y', DSN: 'X-Y', TDT: 'X-Y' },
  chairmanSynthesis: 'SYNTHESIS_TEXT'
});
state.totalItemsFiled += ITEMS_COUNT;
state.totalDuplicatesSkipped += DUPES_COUNT;
fs.writeFileSync('<state-dir>/marathon-council-state.json', JSON.stringify(state, null, 2));
"
```

**Step 9 -- Report wave results**

```
MARATHON COUNCIL WAVE [N] COMPLETE
====================================
Focus: [focus area] ([framing summary])
Research findings: [N] concrete gaps identified
Work orders filed: [N] ([N] FTR, [N] BUG, [N] DSN, [N] TDT)
Duplicates skipped: [N]
Chairman's take: [1-2 sentence synthesis]

Rotation progress: [N]/[total] focus areas completed
Total items filed this session: [N]
Next wave in ~45 min: [next focus area]
```

---

### Phase 3: Wave Loop Tick (cron re-entry)

Read the state file. Then:

**3a. Paused check**

If `state.paused === true`: call `CronDelete(state.cronJobId)`. Stop.

**3b. In-progress check**

If the last wave entry has `status: "in-progress"`: a prior tick is still running. Do nothing. Stop.

**3c. Launch next wave**

If `state.rotationIndex < state.rotationQueue.length` (more focus areas remain):
- Go to Phase 2 to launch the next wave.

**3d. Marathon complete check**

If `state.rotationIndex >= state.rotationQueue.length` (all focus areas covered):
- Go to Phase 4 (Marathon Complete).

---

### Phase 4: Marathon Complete

1. Call `CronDelete(state.cronJobId)`
2. Update state to `status: "complete"` via node
3. Print final report:

```
MARATHON COUNCIL COMPLETE
==========================
Session: [sessionId]
Started: [startedAt]
Completed: [now]
Waves completed: [N]

Wave Summary:
  Wave 1: enterprise-readiness -- 28 items filed
  Wave 2: security-hardening -- 26 items filed
  Wave 3: mobile-responsive -- 30 items filed
  ...

Total work orders filed: [N]
Total duplicates skipped: [N]
Backlog breakdown: [N] FTR, [N] BUG, [N] DSN, [N] TDT

The backlog is loaded. Run /marathon-orders to start executing.
```

---

## The Five Council Members

Same lenses as `/council-orders` -- kept identical so output is comparable across sessions:

1. **Enterprise Sales Engineer** -- Fortune 500 demo-killer gaps
2. **Staff Security Engineer** -- SOC 2, pen-test, compliance gaps
3. **Principal Product Designer** -- Visual/UX gaps that read as "startup prototype"
4. **Staff Platform Engineer** -- Scale embarrassments (hot docs, cold starts, cost)
5. **L&D / HR Tech Buyer** -- Manager reporting, fairness, accessibility, compliance

## Product Context Block

Same as `/council-orders` -- included in every advisor prompt:

```
PRODUCT: <PRODUCT_DESCRIPTION>
```

Replace `<PRODUCT_DESCRIPTION>` with a short paragraph describing your product: positioning, tech stack, data model highlights, pricing tiers, and any hard rules advisors must respect (style rules, terminology constraints, scope limits).

---

## CronCreate Scheduling

```
cron: "3/45 * * * *"       Fires at :03, :48 -- offset from marathon-orders' :07/:27/:47
durable: true               Persists to .claude/scheduled_tasks.json
recurring: true              Runs until deleted or 7-day auto-expiry
```

The 45-minute interval gives each council wave enough time to complete (research + 5 parallel advisors + chairman + filing typically takes 20-35 minutes).

---

## Deduplication Strategy

Deduplication is critical because running 10 councils back-to-back will surface overlapping gaps. The skill uses three layers:

1. **Intra-wave**: After all 5 advisors return, merge items that target the same component/feature/gap. Keep the most detailed version.
2. **Cross-wave**: Each wave reads the full current backlog (including items filed by prior waves). The dedup summary in advisor prompts grows each wave.
3. **Semantic**: The Chairman is explicitly told to flag if any of the 25 advisor items are near-duplicates of existing backlog items and to skip them.

If deduplication reduces a wave below 20 items, that is fine. Quality over quantity. The skill reports duplicates skipped so the user can see diminishing returns.

---

## Continuous Improvement Loop

The intended workflow across two sessions:

**Session A (walkaway, 4-8 hours):**
```
/marathon-council
```
Fills the backlog with 150-250 well-researched, evidence-backed work orders across 10 focus areas.

**Session B (walkaway, 4-8 hours):**
```
/marathon-orders all
```
Executes the highest-priority work orders from the backlog, one at a time, with Opus agents.

**Session C (repeat):**
```
/marathon-council
```
New council session picks up where the last left off. Research phase detects what was already fixed by marathon-orders, and councils focus on remaining and newly revealed gaps.

This creates a flywheel: research reveals gaps, councils prioritize them, Opus agents fix them, next research pass finds the gaps that fixing revealed.

---

## User Feedback Triage (Focus Area 0)

This focus area is fundamentally different from the other 10. Instead of researching the codebase for gaps, it processes real user feedback from a `devProposals` collection (or equivalent) and debates whether each item deserves a dev proposal.

### How It Works

**Research phase (replaces codebase grep):**

The agent reads user feedback from an internal Support page via Chrome DevTools MCP. The internal app must be running on localhost and Chrome must be open with `--remote-debugging-port=9222`.

1. Navigate to the internal Support page and filter to triaged items:
   ```
   mcp__chrome-devtools__navigate_page({ url: 'http://localhost:5174/support' })
   mcp__chrome-devtools__click({ selector: '[data-filter="triaged"]' })
   mcp__chrome-devtools__take_screenshot()
   ```

2. Read the summary line to check counts. If triaged count is 0, skip this wave entirely and advance the rotation index. Print: "No user feedback to triage. Advancing to next focus area."

3. Scrape triaged items from the page DOM:
   ```
   mcp__chrome-devtools__evaluate_script({ expression: `
     JSON.stringify(
       Array.from(document.querySelectorAll('[data-proposal-id][data-status="triaged"]')).map(el => ({
         id: el.dataset.proposalId,
         userName: el.querySelector('[data-field="user-name"]')?.textContent || '',
         sourceType: el.querySelector('[data-field="source-type"]')?.textContent || '',
         message: el.querySelector('[data-field="source-message"]')?.textContent || '',
       }))
     )
   `})
   ```

4. For each triaged item, grep the codebase for components/features mentioned in the user's message. Build a research brief mapping each feedback item to relevant code locations.

**Council phase:**

The 5 advisors each receive the batch of triaged feedback items (up to 15 per wave) and the research brief. Instead of producing 5 work orders, they:

1. Evaluate each feedback item independently: Is it valid? Is it already addressed in the codebase? Is it a real gap or user error?
2. For each item they consider valid, produce a work order proposal: title, category (bugs/design/features/tech-debt), priority, implementation details, rationale.
3. Vote: mark each item as VALID or SKIP with a one-line reason.

**Advisor prompt template for user-feedback-triage:**

```
You are [ADVISOR TITLE] on a product council.

[PRODUCT CONTEXT BLOCK]

USER FEEDBACK TRIAGE SESSION

Below are real feedback items submitted by beta users via the in-app feedback widget or team feedback form. For each item, you must:

1. VOTE: VALID or SKIP (with one-line reason)
2. If VALID, produce a work order proposal with: title, category, priority, details, rationale

[FEEDBACK ITEMS -- each with: id, sourceUserName, sourceMessage, sourceFeedbackType, codebase context]

CODEBASE CONTEXT (what we found near the reported areas):
[RESEARCH BRIEF]

Format your response as:

ITEM [id]:
VOTE: VALID | SKIP
REASON: [one line]
--- (if VALID) ---
TITLE: [work order title]
CATEGORY: bugs | design | features | tech-debt
PRIORITY: critical | high | medium | low
DETAILS: [2-3 implementation sentences with file paths]
RATIONALE: [one sentence on why this matters]
```

**Filing phase (replaces backlog filing):**

For each feedback item, count VALID votes across all 5 advisors:

- **3+ votes (consensus)**: Submit the dev proposal via your internal callable or app UI with the best proposal (pick the most detailed VALID response). This sets the item's status to `proposed`, making it appear in the Dev Requests tab for human review.
- **< 3 votes (no consensus)**: Auto-dismiss with reason `Council consensus below threshold (N/5 votes)`. This filters low-signal items before they reach the human.

The submission callable typically requires platform-admin auth; route through your internal app's authenticated session rather than embedding service-account credentials.

**Writing proposals via Chrome DevTools MCP:**

For each item the council approved (3+ votes), the agent interacts with the internal Support page to submit the proposal:

1. Click "Write Proposal" on the target card:
   ```
   mcp__chrome-devtools__click({ selector: '[data-action="write-proposal"][data-proposal-id="PROPOSAL_ID"]' })
   ```

2. Fill the form fields:
   ```
   mcp__chrome-devtools__fill({ selector: '[data-proposal-id="PROPOSAL_ID"] [data-field="title"]', value: 'TITLE' })
   mcp__chrome-devtools__fill({ selector: '[data-proposal-id="PROPOSAL_ID"] [data-field="details"]', value: 'DETAILS' })
   mcp__chrome-devtools__fill({ selector: '[data-proposal-id="PROPOSAL_ID"] [data-field="rationale"]', value: 'RATIONALE' })
   ```
   Select category and priority dropdowns, set votes count.

3. Click submit:
   ```
   mcp__chrome-devtools__click({ selector: '[data-action="submit-proposal"][data-proposal-id="PROPOSAL_ID"]' })
   ```

4. Verify the card status changed to "proposed" by taking a screenshot or checking the DOM.

For items the council rejected (< 3 votes), click "Dismiss":
```
mcp__chrome-devtools__click({ selector: '[data-action="auto-dismiss"][data-proposal-id="PROPOSAL_ID"]' })
```

No service-account credentials needed. The internal app handles writes through its authenticated session.

### Priority Trigger

On every cron tick (Phase 3), before checking the normal rotation queue:

1. Query `devProposals` for items with `status == 'triaged'`.
2. If any exist and the last `user-feedback-triage` wave was > 2 hours ago (or never), run a user-feedback-triage wave first, then continue with the normal rotation.

This ensures user feedback is processed promptly even mid-rotation.

---

## Approved Proposal Filing (Pre-Check on Every Tick)

On every cron tick (Phase 3), before the normal rotation, also check for approved proposals:

1. Navigate to the internal Support page and check for approved/corrected items:
   ```
   mcp__chrome-devtools__navigate_page({ url: 'http://localhost:5174/support' })
   mcp__chrome-devtools__evaluate_script({ expression: `
     JSON.stringify(
       Array.from(document.querySelectorAll('[data-status="approved"], [data-status="corrected"]')).map(el => ({
         id: el.dataset.proposalId,
         status: el.dataset.status,
         title: el.querySelector('[data-field="proposal-title"]')?.textContent || '',
         category: el.querySelector('[data-field="proposal-category"]')?.textContent?.replace(/[\[\]]/g, '') || '',
         priority: el.querySelector('[data-field="proposal-priority"]')?.textContent || '',
         details: el.querySelector('[data-field="proposal-details"]')?.textContent || '',
         message: el.querySelector('[data-field="source-message"]')?.textContent || '',
       }))
     )
   `})
   ```

2. For each approved/corrected proposal:
   a. Determine the target backlog file from the category.
   b. Read the current `<!-- Next ID: N -->` from the target file.
   c. Write the backlog item in standard format:
      ```
      ### [PREFIX-NNN] [Title]
      - **Added**: [today's date]
      - **Priority**: [priority]
      - **Council**: User Feedback Pipeline (dev proposal [proposal ID])
      - **Details**: [details]
      - **Context**: Promoted from dev proposal [proposal ID]. Original user message: "[sourceMessage excerpt]"
      ```
   d. Mark as filed on the internal Support page via the "Mark Filed" button:
      ```
      mcp__chrome-devtools__click({ selector: '[data-action="mark-filed"][data-proposal-id="PROPOSAL_ID"]' })
      ```
      Then enter the backlog item ID in the prompt dialog:
      ```
      mcp__chrome-devtools__handle_dialog({ accept: true, promptText: 'PREFIX-NNN' })
      ```

3. Report: "Filed N approved dev proposals to backlog: [list of IDs]"

This runs automatically on every tick. No human action is needed beyond the approval in the app UI. The filed items then get picked up by `/marathon-orders` like any other backlog item.

---

## Important Notes

- **Do not run simultaneously with `/marathon-orders`.** Both write to the backlog and read state files. Run them in separate sessions.
- **Each wave files 20-30 items.** A full 10-wave rotation produces 200-300 work orders. This is intentional -- the backlog is designed to be large and prioritized, with `/marathon-orders` cherry-picking the highest priority items.
- **Research quality degrades after ~6-8 waves** as diminishing returns set in. If duplicatesSkipped exceeds 40% of items in a wave, the skill should auto-complete early and report "diminishing returns detected."
- **The state file is separate from marathon-orders.** `marathon-council-state.json` vs `marathon-state.json`. Both can coexist on disk, just not run concurrently.
- **Advisors use Sonnet (default agent model)** -- councils are breadth work, not depth work. Save Opus for marathon-orders execution.
- **File writes during cron ticks use Bash (node -e) exclusively** -- same pattern as marathon-orders for permission consistency.
- **Cron auto-expires after 7 days.** Marathon council sessions are designed for 4-8 hours per run.
- **Early termination on diminishing returns**: If a wave's `duplicatesSkipped / (itemsFiled + duplicatesSkipped) > 0.4`, the skill prints a warning and auto-pauses. The user can resume with `--continue` if they want to push through.
