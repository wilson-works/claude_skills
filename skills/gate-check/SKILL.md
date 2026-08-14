---
name: gate-check
description: "Formal milestone readiness validation. Checks required artifacts and acceptance criteria for each defined milestone gate (MVP, beta, vertical/segment launch, billing, GA) with multi-perspective review. Returns PASS/CONCERNS/FAIL. Invoke with /gate-check [milestone|--list]."
---

# Gate Check Skill

## Purpose

Before major milestones we want a formal "are we ready to advance?" check rather than gut feel. This skill validates readiness against defined acceptance criteria per milestone, runs a multi-perspective review (product, technical, economy/business), and returns PASS / CONCERNS / FAIL with specific blockers.

## Configure for your project

Before using this skill, set these placeholders:

- `<project-root>`: Absolute path to your project root (e.g. `d:/myproject/`).
- `<gate-output-dir>`: Where gate-check reports are saved (default: `<project-root>/docs/gate-checks/`).
- Edit the **Defined Milestone Gates** section below: replace the example artifacts and acceptance criteria with the ones that actually apply to your product.
- Edit the references to QA skills (`/qa-sweep`, `/validate`, `/economy-check`) so they match the skills your project has.

## Invocation

```
/gate-check              -- auto-detect current milestone, check readiness
/gate-check mvp          -- check MVP gate
/gate-check beta         -- check beta launch gate
/gate-check segment-launch -- check readiness for first market segment GA
/gate-check billing      -- check readiness to enable paid billing
/gate-check ga           -- check general availability gate
/gate-check --list       -- list all defined gates and their criteria
```

## Prerequisites

- File read access to `<project-root>`
- Access to any project memory or decision-log files referenced in your acceptance criteria

## Defined Milestone Gates

EDIT THIS SECTION for your project. The example below is a generic SaaS pattern - tune to fit.

### MVP
Required artifacts:
- Core loop works end-to-end (sign-up -> primary action -> visible result)
- At least 1 use-case / segment fully configured
- Auth + tenant creation + invite flow functional
- Role-gated pages don't leak data to lower-privilege users (server-side rules + client sanitizer)
- Cloud project provisioned, security rules deployed

Acceptance criteria:
- `/qa-sweep all` reports no critical bugs
- `/validate <default-segment>` passes
- Secrets guard clean (no server-only env values leaking into client bundles)
- Deploy script works (can push to prod environment)

### Beta Launch
Required artifacts: everything from MVP, plus...
- Primary engagement loop wired up with at least one configured cycle/season
- Recurring task/mission system live
- Catalog of unlockables populated to a usable minimum
- First-time user walkthrough completable
- Narrative / content arc at least one complete unit
- Landing page published
- Invite code system tested

Acceptance criteria:
- `/economy-check all` (or equivalent balance audit) returns PASS or CONCERNS (no FAIL)
- `/qa-sweep` reports no critical or high bugs
- Onboarding walkthrough completable end-to-end
- Support channel (email at minimum) set up

### Segment Launch (per-segment)
Required artifacts:
- Segment-specific config complete with terminology
- Segment-specific content templates
- Segment-specific theme / visuals
- Segment-specific admin onboarding content

Acceptance criteria:
- `/validate <segment>` passes
- `/qa-sweep --segment <segment>` reports no segment-specific issues
- Segment-specific onboarding flow tested

### Billing
Required artifacts:
- Payment provider integration live
- Plan limits enforced server-side (security rules + functions), not client-only
- Billing admin UI functional
- Dunning / failed-payment flow designed
- Cancellation flow preserves user data

Acceptance criteria:
- Server-side enforcement verified (attempt to exceed limits from client -> blocked)
- Webhook handler tested end-to-end
- At least one full payment cycle completed in test mode
- Referral / reward mechanics tested if applicable

### GA (General Availability)
Required artifacts:
- All targeted segments configured
- Marketing site live with pricing
- Self-service signup + payment
- Terms, privacy, and compliance documents live
- Support docs / help center populated

Acceptance criteria:
- All segment gate-checks PASS
- Billing gate PASS
- No critical bugs outstanding
- Retention analytics instrumented (D1, D7, D14, D30)

## Workflow

### Step 1: Identify Target Milestone

If no argument: read current state to infer. Signals:
- Plan-limit enforcement absent -> still pre-MVP
- Engagement loop exists but billing doesn't -> beta-track
- Billing live but only 1 segment -> segment-launch track

If ambiguous, ask the user.

If `--list`: print all gates and their criteria, exit.

### Step 2: Artifact Inventory

For the target milestone, check each required artifact exists:
- File checks: does the path/module exist?
- Feature checks: is the feature reachable from the app?
- Content checks: is the catalog populated to minimum?

Each artifact: PRESENT / PARTIAL / MISSING.

### Step 3: Acceptance Criteria Validation

For each criterion, run the named skill or check:
- `/qa-sweep all` or `/qa-sweep --segment X` (invoke as a sub-task)
- `/validate <segment>` (invoke as sub-task)
- `/economy-check all` (invoke as sub-task) - if your project has one
- Deploy dry-run
- Secrets guard

Each criterion: PASS / CONCERNS / FAIL with the referenced skill's verdict.

### Step 4: Multi-Perspective Review

Spawn three parallel perspectives using sub-agents or inline analysis:

**Product perspective:**
- Does the critical user journey work end-to-end?
- Is onboarding completable by a new user?
- Does the core loop feel rewarding per design intent?

**Technical perspective:**
- Are there any known critical bugs in the backlog?
- Is code health acceptable (TODOs/FIXMEs under threshold)?
- Are security fundamentals in place (security rules, sanitizer, secrets guard)?

**Economy / business perspective:**
- Does the economy or pricing balance as designed?
- Do limits align with the tier structure?
- Will the free -> paid conversion path work?

Each perspective issues a verdict + up to 3 specific concerns.

### Step 5: Final Verdict

**PASS** if:
- All artifacts PRESENT
- All acceptance criteria PASS
- All perspectives agree on PASS

**CONCERNS** if:
- 1-2 artifacts PARTIAL (not MISSING)
- OR acceptance criteria return CONCERNS but not FAIL
- OR one perspective flags addressable concerns
- Advisory: issues are fixable pre-launch but should be prioritized

**FAIL** if:
- Any artifact MISSING
- Any acceptance criterion FAIL
- Any perspective marks blocker-level concerns

### Step 6: Report

Save to `<gate-output-dir>/gate-[milestone]-[YYYY-MM-DD].md`:

```markdown
# Gate Check: [milestone]

Date: [date]
Verdict: PASS | CONCERNS | FAIL

## Artifact Inventory
| Artifact | Status | Notes |
|----------|--------|-------|
| [artifact 1] | PRESENT | |
| [artifact 2] | PARTIAL | [what's missing] |

## Acceptance Criteria
| Criterion | Skill | Verdict | Notes |
|-----------|-------|---------|-------|
| /qa-sweep all | qa-sweep | PASS | |
| /validate default | validate | PASS | |

## Product Perspective
Verdict: [PASS/CONCERNS/FAIL]
- [concern 1]
- [concern 2]

## Technical Perspective
[same structure]

## Economy / Business Perspective
[same structure]

## Blockers (if FAIL)
1. [blocker + recommended fix]
2. [...]

## Recommendations (if CONCERNS)
1. [concern + suggested resolution timeline]

## Next Steps
- [if PASS: specific go-live checklist]
- [if CONCERNS: prioritized fix list]
- [if FAIL: blocker tracking + re-run timeline]
```

## Principles

- **Artifacts THEN criteria.** A missing artifact is an immediate FAIL; don't waste time running acceptance skills if the thing doesn't exist.
- **Multi-perspective catches blindspots.** A PASS on technical doesn't help if economy is broken.
- **PASS is binary.** CONCERNS can still ship with awareness; FAIL cannot.
- **Gate-check is advisory.** The decision-maker makes the go/no-go call. This provides evidence.

## Anti-Patterns

- Do not run this during active development. It's a pre-launch gate, not a continuous check.
- Do not invent acceptance criteria not listed in this skill. Gates are defined; expand them explicitly if needed.
- Do not PASS a gate when any required artifact is MISSING, regardless of how polished the rest is.
- Do not auto-fix blockers; this skill is read-only and produces a verdict.
