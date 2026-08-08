---
name: org-reference-packs
description: "The refresh mechanism for an agent organization's factual knowledge: per-department reference packs where every fact carries its source URL and as-of date, grouped by volatility tier with a named refresh trigger per volatile group. Build mode assembles packs exclusively from cited research output (this skill never authors a fact); refresh mode sweeps triggers and turns overdue ones into re-verification orders, notifying every agent that reads a changed pack; slim mode generates proposal-only de-fact-ed agent definitions. Design law: definitions carry judgment; packs carry facts; facts carry citations and dates. Invoke with /org-reference-packs [build|refresh|slim] [args]."
---

# Org Reference Packs

## Purpose

Agent definitions rot where they store facts: the annually-changing cap, the fee schedule, the
"October refresh" someone named in a file that nothing ever performs. `/org-knowledge-audit`
finds that debt; this skill is where the externalized facts go to live — and, critically, to
*stay alive*. A reference pack is a per-department knowledge file whose every fact carries its
source URL and as-of date, whose volatile sections carry named refresh triggers, and whose
readers are registered — so when a fact changes, the org knows exactly which agents were leaning
on it.

The design law, verbatim and load-bearing: **definitions carry judgment; packs carry facts;
facts carry citations and dates.** This skill is the mechanism, not the knowledge: it never
authors a fact. Pack content comes only from cited research output; an uncited fact cannot
enter a pack by construction.

## Configure for your project

Before using this skill, set these placeholders:

- `<packs-path>`: Directory for reference packs, beside the org (e.g. a `packs/` folder next to
  `org.config.json`). One
  file per department (or per agent where a role's knowledge is truly disjoint). Packs register
  as contract artifacts in `/skill-graph` — readers are consumers.
- `<slim-proposals-path>`: Where slim mode writes proposed definition rewrites (e.g.
  `<packs-path>/slim-proposals/`). Proposals only — application is a separate, human-gated step.

## Invocation

```
/org-reference-packs build <dept|agent>   -- assemble/extend a pack from audit findings or a charter
/org-reference-packs refresh              -- sweep all refresh triggers; dispatch overdue re-verifications
/org-reference-packs slim <agent>         -- propose a de-fact-ed definition (proposal file only)
```

## Pack format

Grouped by volatility tier (the audit's T1–T4); every fact one line-item with source + date;
every T1/T2 group headed by a named refresh trigger. Synthetic example (fictional
municipal-permits domain; citation format is illustrative):

```markdown
# Reference Pack: permits-dept  (v4)
readers: head-permits-dana, junior-permits-eli        # registered consumers
last-full-review: 2026-07-06

## T1 — scheduled-change figures
REFRESH TRIGGER: fee ordinance revision — adopted each budget cycle, expected September;
verify quarterly regardless.
- Expedited filing fee: $310 — [source: city fee schedule §4.2 URL] — as of 2026-07-06
- Standard review window: 30 days — [source: ordinance 12-401 URL] — as of 2026-07-06

## T2 — statistics
REFRESH TRIGGER: annual department report, expected February.
- Appeal success rate: 38% (2025 dept report) — [source URL] — as of 2026-03-01

## T3 — citations / precedents
- Notice-rule precedent: Harmon v. City Board (status: good law) — [source URL] — as of 2026-07-06

## T4 — structural facts
- Application form: PB-101 (renewal: PB-102) — [source URL] — as of 2026-07-06

## Change log
- v4 2026-07-06: expedited fee $290 → $310 per VQ-031 verification; readers notified
```

Agents consume packs by instruction, not by copy: a definition says "Read
`<packs-path>/permits-dept.md` for current figures" — never restates the figure.

## Build mode

Input is either an **EXTERNALIZE finding set** from `/org-knowledge-audit` or a **topic charter**
("what the permits department needs to know"). Then:

1. Convert each needed fact into a research order — `/quick-research` for single facts,
   `/marathon-research` for a batch or a whole charter. The orders carry the pack's required
   format: value, source URL, as-of date, volatility tier.
2. Assemble the pack **only from what the research returns, with its citations intact**. A fact
   the research couldn't source enters the pack as an explicit gap line ("fee amount:
   UNVERIFIED — research order VQ-044 open"), never as a remembered value. This is structural:
   build mode's only inputs are cited research files; there is no code path for the skill's own
   knowledge to enter a pack.
3. Name the refresh trigger for each T1/T2 group — a real-world event ("annual rate revision,
   expected October") plus a fallback interval ("verify quarterly regardless").
4. Register the pack and its readers in `/skill-graph`'s contract registry; long research
   reports distill to pack-sized entries via `/distill` rather than pasting report prose.

## Refresh mode

1. Sweep every pack's triggers: overdue (event passed, interval elapsed, or `as of` older than
   its group's cadence) → dispatch a re-verification research order per stale group.
2. Apply verified changes: update the fact, its source, its as-of date; bump the pack version;
   append the change log entry.
3. **Notify the readers:** every changed fact produces a notification entry naming each
   registered reader agent — a changed fact with unnotified readers is a silent regression.
4. Cadences surface through `/weekly-review`'s sweep (the same registration pattern as
   `/attack-surface`), so refresh debt appears in the weekly ritual instead of accumulating
   invisibly.

## Slim mode (proposal-only)

For an agent whose definition embeds pack-worthy facts:

1. Identify the embedded facts (usually straight from the audit's EXTERNALIZE findings).
2. Generate the proposed slimmed definition: judgment, workflow, and escalation rules stay;
   each fact block becomes a pack pointer ("Read `<packs-path>/<pack>` for current figures").
3. Write the proposal to `<slim-proposals-path>` with a before/after diff summary. **Never apply
   it** — definition edits are separate, human-gated orders. A proposal that also edited the
   file would bypass the very gate that makes the org auditable.

## Failure Modes

- **Authoring a fact.** The catastrophic failure: a "helpful" value from model memory entering a
  pack defeats the entire mechanism, because packs are trusted downstream precisely because they
  can't contain unsourced facts. Gaps stay gaps until research fills them.
- **Trigger rot.** A named trigger nobody sweeps is the same unperformed "October refresh" this
  skill exists to fix. Refresh mode plus the weekly-review registration are the mechanism; if
  neither runs, the packs are just better-formatted rot.
- **Unnotified readers.** Updating a fact without the reader notification turns a correct pack
  into a stealth behavior change for every agent that cached the old value in its outputs.
- **Pack bloat.** A pack that ingests whole research reports stops being loadable at runtime.
  Facts enter as line-items (via `/distill` for long sources); the report stays in the research
  folder, linked.
- **Slim mode applying itself.** Proposals only. The temptation to "just apply the obvious
  rewrite" is how audit gates die.

## Important Notes

- **The pack is the contract:** readers registered, format registered (`/skill-graph`), changes
  versioned and logged. That is what lets sixty-five agents share facts without sixty-five
  copies drifting independently.
- **Fictional example, real format:** the permits-dept pack above is synthetic; its shape —
  tiered groups, named triggers, per-fact source+date, change log, reader registry — is the
  specification.
- **Division of labor with the audit:** `/org-knowledge-audit` finds and classifies; this skill
  houses and refreshes. The audit's EXTERNALIZE findings are build mode's primary input; a
  build without an audit (charter mode) should be followed by one, so the pack and the
  definitions reconcile.
- **Model routing:** pack assembly, refresh sweeps, and change-log maintenance → sonnet
  (formatting, date math, and reader-notification lists are haiku-safe); charter scoping and
  slim-mode judgment (what is judgment vs. fact in a definition) → the session's strongest
  model; escalation: a verified fact that contradicts another pack's entry — reconcile via one
  adjudicated research order before either pack updates.
- Pairs with: `/org-knowledge-audit` (EXTERNALIZE findings feed build mode; the audit measures
  the debt this skill retires), `/quick-research` and `/marathon-research` (the only sources
  pack content can come from), `/distill` (long research → pack-sized entries),
  `/weekly-review` (refresh cadences surface in its sweep), `/skill-graph` (packs and readers
  register as contract artifacts).
