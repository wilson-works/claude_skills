---
name: team-conduct
description: A conduct reference pack for teams of humans and AI agents — ownership language, honest status reporting, blameless escalation, closed-loop handoffs, and human-AI trust calibration. Research-derived (Edmondson, Google SRE, CAIB, I-PASS, MAST, and ~250 more sources distilled into enforceable rules, each shipped with the forcing function that keeps it from becoming a poster). Load when writing status updates, incident reports, escalations, session handoffs, or agent-definition conduct guidelines; or invoke /team-conduct to audit a message or artifact against the pack.
---

# team-conduct Skill

A single reference pack that answers five questions any team of humans and AI agents has to
answer, with rules extracted from the primary research rather than vibes:

1. **How do you own an outcome without blaming a person?** Forward/backward ownership rule.
2. **How do you report status without lying?** Commitment-vs-forecast vocabulary, binary state,
   burden of proof on "on track."
3. **How do you escalate without politics?** A reversibility gate, a 6-step peer-vs-escalate rule,
   and a 9-field escalation artifact with no blame field.
4. **How do you hand off without dropping the thread?** Closed-loop etiquette, receiver synthesis,
   an S0–S8 session-handoff template, named terminal states.
5. **How should an AI teammate talk to a human?** Calibrated reliance: first-person uncertainty,
   per-claim confidence, admit-before-asked error disclosure — and a table of human norms that do
   NOT transfer to agent-to-agent traffic.

The full pack is at [references/team-conduct-pack.md](references/team-conduct-pack.md). It is
written to be read by agents (drop it in a system prompt reference line) and by humans (read it
once, then argue with specific section numbers).

## The design rule behind the whole pack

Published values carry roughly zero information about enacted behavior (MIT SMR/Glassdoor
Culture 500). A rule becomes real only as **tool + adoption forcing-function + inspection
cadence** — and inspection must sample *content*, never completion counts, because both people
and agents will populate any template perfectly (the Ontario surgical-checklist result: 90%+
reported compliance, no outcome movement). Every section of the pack therefore ends with a
FORCING FUNCTION / INSPECTION block. If you adopt a rule without its enforcement, you adopted
a poster.

## How to wire it into an agent org

Add one or two pointer lines to each agent definition, tiered by role. Suggested lines:

- **All agents:**
  `Conduct pack: <path>/team-conduct-pack.md — commitments first-person, active, dated; causal accounts system-subject, person-free; silence is never confirmation; status is binary against a written standard, never a percentage.`
- **Workers (report to a lead):** add
  `Conduct pack §2 + §3: status carries state (binary) / blocker (named) / date consequence / evidence; escalate to your lead with four things — trigger, what you tried, the options you see, the one question you want answered — never a complaint, and only after the time-box or a named trigger.`
- **Leads (review workers):** add
  `Conduct pack §3 + §6: you decide one-way doors inside your area and ties between your own reports; two-way doors are not escalated. Reviewer is never the author, and every action item you accept carries owner + tracking ID + a prevention, not a promise to be careful.`
- **Routers (EAs, dispatchers):** add
  `Conduct pack §3.1 + §4.3: you are a router, not a decider — route to the lowest common ancestor, dedupe, timestamp, chase, log, and bounce any escalation missing a required field. Close every thread you open with a named terminal state.`
- **Deciders (chiefs, owners):** add
  `Conduct pack §3.3 + §5: your escalation reply is a written decision — the rationale, the dissent preserved on the record, the consequences you are accepting, and the owner of the next action. Dissent is written down before the commitment, not after.`

Route mis-tiered agents to the **worker** line, not the decider line — an agent wrongly told
"you decide" is a worse failure than one wrongly told "escalate with an artifact."

Before calling the wiring done, run a before/after eval: hold out ~20 scenarios (status posts,
escalations, handoffs), score outputs on three binaries (status carries all four fields without a
percentage; escalation names its trigger and reversibility; handoff has no unowned action item),
and require a real delta. If behavior doesn't move, the lines are decoration — put the rules in a
hook or a validator instead of prompts.

## Enforcement honesty

Most comms layers cannot validate message bodies. Until yours does, every "bounce" and "expiry"
rule in the pack is a CONVENTION — the receiving agent chooses to bounce — and the pack labels
them so. The highest-leverage build if you want real enforcement: typed message kinds
(escalation / status / handoff) with server-side required-field validation, required terminal
states on claim release, and a status-freshness sweeper. A rule that claims machine enforcement
it doesn't have is worse than an honest convention, because nobody audits a guarantee.

## Using /team-conduct as an audit

Invoked with an argument (a message, a status post, a handoff doc, or a file path), audit the
artifact against the pack: identify which section applies, quote the offending line, and rewrite
it per the relevant table. Report the section number with every finding so the author can argue
with the rule rather than the reviewer.
