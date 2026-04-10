---
name: marathon-council
description: "Long-running walkaway session that rotates through focus areas, researches the codebase, convenes product councils, and files work orders to the backlog. Intake half of a continuous improvement loop -- fills the backlog, then /marathon-orders executes it. Invoke with /marathon-council [--stop] [--status] [--continue] [dry-run]."
---

# Marathon Council Skill

## Purpose

Sustained, unattended council research loop (4-8 hours). Each wave:
1. Picks next **focus area** from rotation queue
2. **Researches** the codebase for real gaps (not hypothetical)
3. **Convenes** 5-member product council with research evidence
4. **Files** 25-30 work orders to backlog with dedup
5. Loops via **CronCreate** every 45 minutes

Intake half of continuous improvement loop:
- `/marathon-council` fills backlog with researched, evidence-backed work orders
- `/marathon-orders` executes them

Use `/council-orders` for single one-shot council. Use this for multi-wave rotating coverage.

## Invocation

```
/marathon-council                     Full rotation, wave size 1
/marathon-council [focus1,focus2,...]  Custom rotation (comma-separated)
/marathon-council --stop              Pause after current wave
/marathon-council --status            Show progress
/marathon-council --continue          Manual re-entry
/marathon-council dry-run             Show rotation queue only
```

## Configuration (EDIT THESE)

Before using, update these paths and values for your project:

```
PROJECT_DIR: [your project root]                    # e.g., /home/user/myapp
STATE_FILE: [PROJECT_DIR]/.claude/marathon-council-state.json
BACKLOG_DIR: [your backlog directory]               # e.g., ~/.claude/projects/myproject/backlog/
SETTINGS_FILE: ~/.claude/settings.json
PRODUCT_CONTEXT: [see Product Context Block below]
```

## Focus Area Rotation

Default rotation (one per wave):

```
1. enterprise-readiness    -- Demo-killer gaps for enterprise buyers
2. security-hardening      -- Auth, rules, PII, compliance
3. mobile-responsive       -- Breakpoints, touch targets, responsive
4. onboarding-retention    -- First-run, activation, empty states
5. vertical-readiness      -- Per-vertical/persona gaps (cycles through your verticals)
6. design-polish           -- Visual consistency, loading/error states
7. platform-scale          -- Hot paths, indexes, cost, idempotency
8. admin-experience        -- Admin controls, reporting, provisioning
9. billing-monetization    -- Plan enforcement, upgrade flows, gating
10. accessibility-compliance -- WCAG, keyboard nav, screen readers
```

Custom list: `/marathon-council security-hardening,mobile-responsive,design-polish`

## State File Schema

```json
{
  "sessionId": "council-marathon-YYYY-MM-DDTHH-MM",
  "status": "running | paused | complete",
  "paused": false,
  "cronJobId": "",
  "startedAt": "ISO",
  "currentWave": 0,
  "rotationQueue": [],
  "rotationIndex": 0,
  "waves": [
    {
      "waveNumber": 1,
      "focus": "enterprise-readiness",
      "startedAt": "ISO",
      "completedAt": "ISO",
      "status": "complete | in-progress | failed",
      "itemsFiled": 28,
      "duplicatesSkipped": 2,
      "chairmanSynthesis": "brief"
    }
  ],
  "totalItemsFiled": 0,
  "totalDuplicatesSkipped": 0
}
```

Written exclusively via `Bash(node -e ...)` for permission consistency during unattended cron ticks.

---

## Workflow

### Phase 0: Invocation Parsing

- `--stop`: read state, set `paused: true`, `CronDelete(cronJobId)`, print summary. Stop.
- `--status`: read state, pretty-print progress. Stop.
- `--continue`: skip to Phase 3.
- `dry-run`: show rotation queue, stop.
- **No state file**: fresh start, Phase 1.
- **State exists, not paused**: cron re-entry, Phase 3.

### Phase 1: Fresh Start

**1.1 -- Parse rotation queue.** Custom or default.

**1.2 -- Present plan.**
```
MARATHON COUNCIL PLAN
======================
Rotation: [N] focus areas, ~45 min each
Estimated: ~[N*45] min
```

**1.3 -- Pre-flight settings.** Add to `permissions.allow` in settings.json:
```json
"Edit([BACKLOG_DIR]/**)",
"Write([BACKLOG_DIR]/**)",
"Edit([STATE_FILE])",
"Write([STATE_FILE])"
```

**1.4 -- Confirm.** Ask user: "Ready to launch? [y/n]"

**1.5 -- Write initial state.** Via `node -e` to state file.

**1.6 -- Register cron.**
- `cron`: `3/45 * * * *` (offset from marathon-orders)
- `durable`: `true`, `recurring`: `true`
- Prompt:
```
Automated marathon-council tick.
1. Read state: [STATE_FILE]
2. Read skill: [path to this SKILL.md]
3. Execute Phase 3.
Do not ask user for confirmation.
```
Write `cronJobId` to state via node.

**1.7 -- Launch Wave 1.** Go to Phase 2.

---

### Phase 2: Launch Wave

**2.1 -- Resolve focus.** Map `rotationQueue[rotationIndex]` to framing string:

| Focus | Framing |
|---|---|
| enterprise-readiness | "Enterprise buyer demo. What kills the deal in the first 20 minutes?" |
| security-hardening | "Security audit. What fails SOC 2 or pen-test?" |
| mobile-responsive | "Mobile-first. What breaks on 375px?" |
| onboarding-retention | "New user first 10 minutes. What's confusing or empty?" |
| vertical-readiness | "Vertical buyer: [NAME]. What makes them say 'not built for us'?" |
| design-polish | "Design review. What reads as side project vs. funded product?" |
| platform-scale | "500 teams, 10K users, peak hours. What breaks first?" |
| admin-experience | "Admin with 50 members. What's missing in controls?" |
| billing-monetization | "Free user upgrading. What's broken in gating or payment?" |
| accessibility-compliance | "Compliance review. What fails WCAG 2.1 AA?" |

**2.2 -- Codebase research. TOKEN OPTIMIZATION: Use `output_mode: "files_with_matches"` and `head_limit: 10` on all Grep calls. Read only the 3-5 most relevant files, not everything.**

Research targets by focus (run only the searches for the current focus, not all):

- **enterprise-readiness**: grep `admin|audit|role|provision|SSO|export`
- **security-hardening**: read auth rules file, grep `allow|any` in server code
- **mobile-responsive**: grep `@media|sm:|md:|lg:` in components
- **onboarding-retention**: read onboarding/walkthrough components, check empty states
- **vertical-readiness**: read vertical config, grep for hardcoded terminology
- **design-polish**: read design system files, grep for off-token hex values
- **platform-scale**: check indexes, grep for fan-out patterns
- **admin-experience**: read admin components
- **billing-monetization**: read plan enforcement logic, check feature gating
- **accessibility-compliance**: grep `aria-|role=|tabIndex`

Compile into **research brief**: 8-15 bullets with file paths. Keep brief under 500 words (token budget).

**2.3 -- Read backlog state.** Get Next IDs, last 30 items per file. Build dedup summary (IDs + titles only, not full details -- saves tokens).

**2.4 -- Spawn 5 advisors in parallel.** Each gets:
- Lens identity
- Product context block (compact -- see below)
- Focus framing
- Research brief
- Dedup summary (titles only)

**TOKEN OPTIMIZATION**: Use `model: "sonnet"` for all advisor agents. Councils are breadth work; save Opus for execution.

**Advisor prompt template:**
```
You are [TITLE] on a product council for [APP_NAME].
Lens: [LENS -- 2 sentences max]

[COMPACT PRODUCT CONTEXT -- see below]

FOCUS: [FRAMING]

CODEBASE EVIDENCE:
[RESEARCH BRIEF -- bullets with paths]

ALREADY FILED (skip these):
[IDs + titles, one per line]

Produce exactly 5 work orders. Each grounded in evidence above.
Format:
[CATEGORY] Title
Priority: critical/high/medium/low
Details: 2-3 sentences. Name files/functions.
Why: one sentence.

No preamble. 5 items only.
```

**2.5 -- Collect and deduplicate.** Merge overlapping items across advisors and against backlog.

**2.6 -- Chairman.** Single agent, receives all ~25 items + research brief. Adds 5 gap items.

**TOKEN OPTIMIZATION**: Chairman prompt is under 800 words. Include only the 25 work order titles+details, not full advisor prompts.

**2.7 -- File to backlog.** Sequential IDs, priority-sorted, tagged:
```markdown
### [FTR-XXX] Title
- **Added**: YYYY-MM-DD
- **Priority**: critical/high/medium/low
- **Council**: [Advisor] (marathon wave [N]: [focus])
- **Details**: ...
- **Context**: ...
```

**2.8 -- Update state.** Advance `rotationIndex`, record wave results.

**2.9 -- Report.**
```
WAVE [N] COMPLETE: [focus]
Filed: [N] items | Dupes skipped: [N]
Chairman: [1 sentence]
Next: [focus] in ~45 min | Progress: [N]/[total]
```

---

### Phase 3: Wave Loop Tick (cron)

1. **Paused?** CronDelete, stop.
2. **In-progress?** Prior tick still running, stop.
3. **More focus areas?** Phase 2.
4. **All done?** Phase 4.

---

### Phase 4: Marathon Complete

1. `CronDelete(cronJobId)`
2. State `status: "complete"`
3. Report:
```
MARATHON COUNCIL COMPLETE
==========================
Waves: [N] | Items filed: [N] | Dupes skipped: [N]
Run /marathon-orders to start executing.
```

---

## Token Optimization Summary

These choices keep marathon-council economical over 10 waves:

| Technique | Savings |
|---|---|
| Sonnet agents (not Opus) for advisors | ~60% per agent |
| Research brief capped at 500 words | Prevents prompt bloat |
| Dedup summary is titles-only (no details) | ~70% smaller than full items |
| Grep uses `files_with_matches` + `head_limit: 10` | Avoids dumping file contents |
| Read only 3-5 hotspot files per wave | Bounded input |
| Chairman gets titles+details only | ~50% smaller than full advisor outputs |
| Compact product context block (~150 words) | vs. ~300 in full version |
| Wave reports are terse (3 lines) | Minimal context accumulation |
| State file via node (not Write tool) | No approval overhead |
| Early termination on >40% dupe rate | Stops wasting waves |

Estimated token cost per wave: ~50K input + ~15K output across 7 agent calls (5 advisors + chairman + research).
10-wave session: ~500K input + ~150K output total.

---

## The Five Council Members

Fixed lenses (customize for your domain):

1. **Enterprise Sales Engineer** -- "Ran Fortune 500 demos for 10 years. What question kills the deal? Admin controls, audit, SSO, provisioning, HRIS export."
2. **Staff Security Engineer** -- "Reviewed dozens of SaaS products. What fails SOC 2, pen-test, compliance? Auth, rules, PII, rate limiting, idempotency."
3. **Principal Product Designer** -- "Shipped enterprise design systems. What reads as side project? Empty/loading/error states, typography, mobile, transitions."
4. **Staff Platform Engineer** -- "Ran infra from 0 to millions. What breaks first? Hot docs, cold starts, indexes, fan-out, cost, monitoring."
5. **L&D / HR Tech Buyer** -- "Evaluated 20+ HR tools. What makes you say 'not yet'? Reporting, HRIS, accessibility, fairness, opt-out, DPA."

---

## Compact Product Context Block

Edit this for your project. Keep under 150 words:

```
PRODUCT: [App Name] -- [one-line description].
[2-3 sentence product summary with key features].
Tech: [stack summary].
Key collections/models: [list].
Pricing: [tiers].
Hard rules: [list any absolute constraints].
```

---

## Continuous Improvement Loop

```
Session A: /marathon-council     --> fills backlog (150-250 items)
Session B: /marathon-orders all  --> executes highest priority items
Session C: /marathon-council     --> research finds new gaps revealed by fixes
Session D: /marathon-orders all  --> executes next batch
...repeat...
```

---

## Setup Checklist

1. Copy `skills/marathon-council/` into `~/.claude/skills/`
2. Copy `skills/council-orders/` into `~/.claude/skills/` (dependency)
3. Edit the Configuration section with your project paths
4. Edit the Product Context Block for your product
5. Edit the 5 advisor lenses if your domain differs from SaaS
6. Create your backlog directory with `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, `completed.md`
7. Each backlog file needs a `<!-- Next ID: 001 -->` comment at the top
8. Run `/marathon-council dry-run` to verify

## Notes

- Do not run simultaneously with `/marathon-orders` (both write to backlog)
- Each wave files 20-30 items; full rotation produces 200-300 work orders
- Early termination if >40% dupe rate in a wave (diminishing returns)
- Cron auto-expires after 7 days (CronCreate hard limit)
- State file separate from marathon-orders (`marathon-council-state.json`)
