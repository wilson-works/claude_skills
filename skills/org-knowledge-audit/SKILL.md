---
name: org-knowledge-audit
description: "Knowledge-integrity audit for an agent organization: reads every agent definition, extracts the domain claims embedded in them, classifies each by volatility risk (annually-changing figures down to pure workflow), flags every uncited volatile claim into a verification queue for the research skills, and checks each agent's carried knowledge against its charter. Reports per agent with VERIFY/CORRECT/EXTERNALIZE/RUNTIME fix classes — it never verifies a claim from model memory and never edits an agent file. Invoke with /org-knowledge-audit [agent|dept] [scope]."
---

# Org Knowledge Audit

## Purpose

Agent definitions accumulate domain knowledge the way kitchens accumulate spices: a cap here, a
fee schedule there, a statistic someone needed once — most of it uncited, none of it dated, and
the annually-changing parts silently wrong within a year. An agent that confidently applies last
year's figure is worse than one that says "look it up": the org's work inherits the staleness
invisibly.

This skill audits the org's knowledge the way a linter reads code: read everything,
classify what's found, rank by risk, report with concrete fixes. Its one inviolable rule is the
audit's own honesty: **the auditor never verifies or corrects a claim from its own memory — an
auditor that "fixes" an uncited figure from recall is committing the exact offense it audits.**
Every flagged claim goes to the research skills, which carry the every-claim-has-a-URL
discipline; this skill classifies and routes, asserting no external facts of its own.

## Configure for your project

Before using this skill, set these placeholders:

- `<org-root>`: The agent organization's root (e.g. the directory holding `org.config.json` and
  `agents/*.md`). Discovery also sweeps the project's `.claude/agents/` if present.
- `<audit-output-path>`: Where per-agent reports and the verification queue are written (e.g.
  `docs/audits/knowledge/`).

## Invocation

```
/org-knowledge-audit                 -- full audit: every agent in the roster
/org-knowledge-audit agent <name>    -- one agent file
/org-knowledge-audit dept <dept>     -- one department's agents
```

## Step 1: Discover

Build the roster from `<org-root>`: the `org.config.json` roster, every `agents/*.md`, and
`.claude/agents/`. Report the count and any file the roster names that doesn't exist (an orphan
roster entry is itself a finding).

## Step 2: Extract and classify claims

Read each agent definition and pull out every statement of domain fact. Classify by volatility:

| Tier | What it is | Risk |
|------|------------|------|
| **T1** | Figures that change on a schedule — caps, fees, rates, thresholds, deadlines | Highest: silently wrong after the next cycle |
| **T2** | Statistics and empirical percentages | High: source and vintage unknown |
| **T3** | Case citations and named precedents | High: status can change; misquotes propagate |
| **T4** | Stable structural facts — statute/section architecture, form names, org charts | Low: verify once, revisit rarely |
| **T5** | Pure workflow and judgment — how to decide, when to escalate | Not a claim; this is what a definition is *for* |

Two classification rules: when in doubt between tiers, assign the more volatile one (the cost of
over-flagging is a cheap verification; the cost of under-flagging is a wrong figure in
production); and a claim's citation only counts if it has both a source reference *and* an as-of
date — "per the statute" with no section and no date is uncited.

## Step 3: Flag into the verification queue — never verify inline

Every uncited T1–T3 claim becomes a queue entry. The skill writes the orders; the research
skills do the verifying (that is where the citation discipline lives):

- **Single claim** → a `/quick-research` order.
- **An agent with many flagged claims** → one `/marathon-research` batch order for the agent.

Queue entry format (written to `<audit-output-path>/verification-queue.md`):

```markdown
## VQ-031: [T1] head-permits-dana.md L47 — "expedited filing fee is $310"
Verify: current fee amount + effective date, from the issuing authority's official schedule.
Fix class if confirmed: VERIFY (stamp as-of date + source)
Fix class if changed: CORRECT (order will carry the verified figure)
```

## Step 4: Purpose-fit check

Per agent, compare the charter (its stated role) against the knowledge it carries:

- **Missing:** reference material its charter clearly needs but the definition neither contains
  nor points to — flag as a gap (candidate for a reference pack, not for inline stuffing).
- **Scope creep:** knowledge outside the charter (the permits agent carrying payroll tables) —
  flag for removal or relocation.
- **Routing smells** (model/effort mismatches surfaced while reading) → hand to your
  routing-lint skill, if present; this audit doesn't re-implement such checks.

## Step 5: Report

One report per agent plus an org summary, ranked by volatility tier then claim count. Every
finding carries a fix class:

| Fix class | Meaning |
|-----------|---------|
| **VERIFY** | Claim stands after research → stamp source + as-of date where it lives |
| **CORRECT** | Claim is wrong → a separate §11-gated correction order, armed with the verified fact |
| **EXTERNALIZE** | Fact belongs in a cited reference pack (`/org-reference-packs`) with the definition pointing to it |
| **RUNTIME** | Convert to a look-it-up-live instruction — right for facts too volatile for any pack cadence |

Synthetic example (fictional agent — a municipal-permits org):

```
KNOWLEDGE AUDIT — head-permits-dana.md            2026-07-06
Charter: routes permit applications; advises juniors on fee schedules and deadlines.

Claims: 19 total — T1: 6 · T2: 2 · T3: 1 · T4: 7 · T5: (workflow, not counted)
Cited with as-of date: 2 of 9 volatile (T1–T3) claims

FINDINGS (most volatile first)
1. [T1, uncited] L47 "expedited filing fee is $310" → VQ-031 (quick-research)
   Likely fix: EXTERNALIZE — fee schedule belongs in the permits reference pack
2. [T1, uncited] L52 "renewal window is 30 days" → VQ-032
   Likely fix: RUNTIME — window is set per-ordinance; instruct lookup, don't store
3. [T2, uncited] L88 "about 40% of appeals succeed" → VQ-033
   Likely fix: CORRECT or DELETE — no source, no vintage, decorates rather than decides
4. [T3, uncited] L91 cites "Harmon v. City Board" for the notice rule → VQ-034 (verify status)
PURPOSE-FIT: charter needs the current fee schedule (gap — pack candidate);
  L102-115 zoning variance tables are outside charter (scope creep — relocate).
QUEUE: 8 entries → 1 marathon-research batch (VQ-031..038)
Backlog: 3 items filed (pack candidate, scope-creep relocation, correction follow-up)
```

Findings file to `/backlog` in its item format; the queue entries dispatch to the research
skills; EXTERNALIZE sets feed `/org-reference-packs` build mode.

## Failure Modes

- **The auditor commits the audited offense.** Correcting an uncited claim from model memory —
  even an "obviously right" one — is the failure this skill exists to catch. Every fix routes
  through researched verification, no exceptions for confidence.
- **Editing agent files.** This skill reports; corrections are separate, human-gated orders
  armed with verified facts. An audit that edits mid-pass destroys its evidence and skips the
  gate.
- **Tier deflation.** Calling an annually-changing cap "T4 stable" to shrink the queue defeats
  the audit. When in doubt, the more volatile tier — the classification rule is asymmetric on
  purpose.
- **Flag-everything noise.** T5 workflow content and T4 structural facts with plausible
  stability are not queue candidates by default; drowning the queue in stable facts buries the
  six figures that actually rot. The tiers exist to spend verification where volatility lives.
- **Queue theater.** A verification queue nobody dispatches is inventory of known-unknowns.
  The report ends with the dispatch plan (which orders, which research skill), not just the list.

## Important Notes

- **Boundary vs `/skill-stocktake`:** that skill audits *skills* for quality and overlap; this
  one audits *agent definitions* for knowledge integrity. An agent whose problem is quality
  (vague charter, dead instructions) gets noted and routed there, not re-audited here.
- **This skill asserts zero external facts.** Its own text contains no figures, statutes, or
  statistics — the synthetic example is fictional. If drafting an audit ever seems to require
  stating a real-world fact, that fact belongs in a verification order, not in this skill.
- **The end-state is structural:** repeated EXTERNALIZE findings converge on the design law that
  definitions carry judgment and packs carry facts (see `/org-reference-packs`). The audit
  measures the distance to that state; the packs close it.
- **Model routing:** discovery, extraction, and classification → sonnet (queue formatting and
  counts are haiku-safe); purpose-fit judgment and the org summary → the session's strongest
  model; escalate when agents carry *contradictory* claims on the same fact — cross-agent
  contradictions need one adjudicated verification, not parallel ones.
- Pairs with: `/org-reference-packs` (EXTERNALIZE findings are its build input),
  `/quick-research` and `/marathon-research` (the verification delegates — citation discipline
  lives there), `/backlog`
  (findings land as work items), `/skill-stocktake` (the skills-side sibling — boundary above).
