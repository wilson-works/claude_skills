---
name: decision-policy
description: "Stops recurring decisions from being re-litigated: mines your notes, backlog, and session history for decisions made repeatedly, surfaces the latent rule behind each, triages by reversibility × stakes (one-way-door decisions never become rules), and files each as a standing record — ADR-style for technical decisions, terse standing policies for business/ops — in a maintained log future sessions consult before re-deciding. Also the filing destination for conclusions from your deliberation skills. Invoke with /decision-policy [file|consult|review] [args]."
---

# Decision Policy

## Purpose

The pack deliberates well — `/premortem`, `/llm-council`, `/business-roundtable`, `/quick-design`
all produce careful conclusions — and then records nothing. The same decision resurfaces a month
later and gets re-litigated from scratch. The cost is the one Nygard named when he invented the
architecture decision record: without the recorded "why," a future reader faces blind acceptance
(perpetuating a decision whose context changed) or blind reversal (undoing one that still
matters). And when the *same kind* of decision is decided repeatedly, variability creeps in —
what the decision-hygiene literature calls noise — which a standing rule collapses.

This skill maintains the decision log: it mines for recurring decisions, triages every candidate
by reversibility × stakes, and files two kinds of records — immutable ADRs for technical
decisions, terse standing policies for recurring business/ops calls. The triage is also the
guardrail: consequential one-way-door decisions are recorded and deliberated *every time*, never
converted into an auto-applied rule.

## Configure for your project

Before using this skill, set this placeholder:

- `<decision-log-path>`: Root of the decision log (e.g. `docs/decisions/`), kept in the repo —
  in-repo plain markdown is the strongest documented predictor of a decision practice surviving
  (versioned with the code, discoverable by grep, reviewed in PRs). Contains `adr/` (technical
  records, `NNNN-title-with-dashes.md` per the MADR convention), `policies/` (one file per
  standing policy), and `POLICIES.md` — the terse index future sessions load first.

## Invocation

```
/decision-policy                     -- mine notes/backlog/history for recurring decisions → triage → draft
/decision-policy file "<decision>"   -- file one decision now (e.g. a deliberation skill's conclusion)
/decision-policy consult "<situation>" -- check the log before deciding; cite the record or say none exists
/decision-policy review              -- maintenance pass: stale records, drift, supersession
```

## The triage (every candidate passes through this)

Reversibility × stakes, from the Type 1 / Type 2 framework: irreversible, consequential
decisions are one-way doors that deserve slow, deliberate treatment; most decisions are two-way
doors that should be decided lightly — around 70% of the information you wish you had — and the
documented failure mode is applying the heavy process to reversible calls.

| | Low stakes | High stakes |
|---|---|---|
| **Reversible** | Decide fast; at most a one-line log entry | **Standing-policy candidate** (if recurring) |
| **Irreversible** | ADR, decided locally but deliberately | **Type 1: ADR + full deliberation, every time — never a policy** |

Then the four gates, in order — a candidate becomes a standing policy only if all pass:

1. **Recurred ≥3 times** with similar inputs and outcome? No → one-off ADR, don't policy-fy.
2. **Reversible?** No → Type 1: route to deliberation (`/llm-council` for multi-perspective),
   record as ADR each time.
3. **Stakes bounded** if the default is occasionally wrong? No → keep case-by-case; a checklist,
   not a rule.
4. **Input pattern stable** (the rule won't drown in exceptions)? No → file as a guideline,
   softer than a policy.

Encoding a one-way-door decision as a standing rule is the precise failure this table exists to
prevent — a policy that auto-resolves Type 1 calls erodes exactly the optionality the framework
protects.

## Record schemas

**Technical ADR** (`adr/NNNN-title-with-dashes.md`) — the Nygard/MADR shape: Title (short noun
phrase) · Status (proposed → accepted → deprecated / superseded-by-N) · Context (the forces in
tension) · Decision (full sentences, active voice) · Consequences (all of them, good and bad) ·
Confirmation (how compliance is checked, where applicable). One to two pages, prose over
fragments. **Accepted ADRs are immutable** — typo and link fixes only; a changed conclusion is a
*new* ADR that references and re-statuses the old one.

**Standing policy** (`policies/<slug>.md`) — terser, built to be loaded and applied by an agent:

```markdown
# POL-007: Refund requests under $50 are approved without escalation  (v2, active)
- **Trigger:** customer requests a refund and the amount is below $50
- **Rule:** approve same-day; log amount + reason code; no approval chain
- **Triage basis:** recurring (14×/quarter), reversible (refund can be re-billed on fraud),
  stakes bounded (worst case $50 + goodwill)
- **Escalate-if:** same customer 3rd refund in 90 days · suspected fraud · amount ≥ $50
- **Provenance:** business-roundtable conclusion 2026-05-12; superseded POL-007 v1 (raised
  limit from $25 after zero abuse in two quarters)
- **Status:** active · **Last reviewed:** 2026-07-06
```

The `Escalate-if` field is the guardrail made mechanical: the policy self-limits to its
bounded-stakes envelope and kicks everything else back to human deliberation.

`POLICIES.md` carries one line per active policy (ID · trigger · rule, ~1 line each) so an agent
consults the index without loading the archive. Supersede and retire aggressively — the index's
value is inversely proportional to its length.

## Mining (`/decision-policy` with no args)

Honesty first: literature on detecting recurring decisions in free-form corpora is thin — this
is a heuristic pass, not proven automation. Three steps, with the human confirming at the end:

1. **Phrase-pattern sweep** over notes, backlog, meeting digests, and available session history:
   commitment language ("we decided to…", "let's go with…", "the plan is…", "same as last
   time"). Deliberation-skill outputs are the highest-signal corpus — check them first.
2. **Cluster by topic** and count recurrences; a cluster of ≥3 similar decisions is a candidate.
3. **Triage each candidate** through the gates above and present the found-rule for
   confirmation: "You've decided this the same way 4 times; here's the latent rule — file it?"

Never auto-file from mining alone. The mine surfaces; the human (or the ratifying deliberation
skill) accepts.

## Consult (`/decision-policy consult`)

The other half of the loop — the log only pays when it's read before deciding:

1. Load `POLICIES.md`; match the situation against triggers.
2. Hit → cite the policy by ID, apply its rule, honor its `Escalate-if` clauses.
3. Miss → say plainly that no record exists, decide fresh, and offer to `file` the outcome.
4. Drift signal: if the user overrides a matching policy, log the override — repeated overrides
   are the revision trigger (see Review).

Long-running sessions (marathons, org runs) should consult at the start of any wave that makes
recurring-shaped calls — that is this log's whole reason to exist.

## Review (`/decision-policy review`)

The documented failure trajectory is structural: records rot because the people who see them
lack the context to update them, and the collection "slowly fills with stale Accepted" records
until trust erodes. The documented countermeasure is a short periodic review (the quarterly
one-hour pattern), which is also the natural moment to re-run mining:

- **Stale check** — records whose context has visibly changed; supersede, never edit in place.
- **Drift check** — policies increasingly decided *against* (override log from Consult): revise
  the rule or retire it; drift is the retirement trigger.
- **Repeated-decision harvest** — the review's own byproduct: decisions that recurred since last
  review and deserve minting.
- **Index diet** — retire and archive aggressively; `POLICIES.md` must stay loadable at a glance.

## Handoffs

- **Filing destination for the deliberation skills:** `/quick-design` resolutions,
  `/business-roundtable` ratified conclusions, and `/llm-council` verdicts file here via
  `file` — each skill's outcome becomes a record instead of a chat memory.
- **`/premortem` stress-tests proposed policies:** before a policy goes active, a premortem on
  "this policy failed — why?" probes the `Escalate-if` envelope for Type 1 leakage.
- **`/llm-council` receives what the triage rejects:** candidates that fail the reversibility or
  stakes gates are exactly the decisions worth multi-perspective deliberation.
- **`/claude-md-doctor` consumes accepted policies:** a policy that binds *model behavior*
  (rather than business process) graduates into a CLAUDE.md rule during its rewrites.
- **Registry:** the two record schemas register as contract artifacts in `/skill-graph` so
  consumers track format changes.

## Failure Modes

- **Policy-fying a one-way door.** The catastrophic failure. The triage's gate 2 is absolute:
  irreversible → deliberation every time, whatever the recurrence count.
- **Write-only log.** Records nobody consults are Nygard's problem restated. Consult is wired
  into deciding (and into marathon/org-run starts) — if the log isn't being read, fix that
  before minting more records.
- **Editing accepted records.** Rewriting history breaks the trust the log exists to provide.
  Supersede with a new record; the old one keeps its status pointer.
- **Mining over-claim.** The phrase-pattern sweep will miss decisions and hallucinate clusters;
  it proposes, never files. Treating it as reliable automation is unsupported by the evidence.
- **Index bloat.** A 300-line `POLICIES.md` stops being consulted, which kills the loop. Retire
  aggressively; the archive keeps everything, the index keeps only what's active.

## Important Notes

- **Two record types on purpose:** ADRs optimize for rationale a future human can trust
  (immutable, prose, consequences); policies optimize for a rule an agent can apply (trigger,
  rule, escalate-if, one-line index entry). Collapsing them loses one of the two audiences.
- **The 70% rule travels with the policy:** reversible decisions ship at ~70% confidence with a
  light process — a policy that demands more certainty than its stakes warrant recreates the
  slowness the framework warns about.
- **Provenance matters:** every record names where it came from (deliberation skill, mining
  pass, direct filing) and its supersession chain — that history is what makes the next review
  cheap.
- **Model routing:** mining sweeps and index formatting → sonnet (date math and index rebuilds
  are haiku-safe); triage judgments, policy drafting, and reviews → the session's strongest
  model; escalate to full deliberation (`/llm-council`) when triage rejects a candidate as
  Type 1.
- Pairs with: `/premortem` (stress-tests proposed policies), `/llm-council` (receives Type 1
  candidates; its verdicts file here), `/business-roundtable` (authors and ratifies business
  policies; quarterly review venue), `/quick-design` (its resolutions file here; it cites
  standing records instead of re-deriving), `/claude-md-doctor` (accepted behavior-binding
  policies graduate into CLAUDE.md rules), `/notetaker` (general thoughts route there; decisions
  route here), `/skill-graph` (record schemas register as contract artifacts).
