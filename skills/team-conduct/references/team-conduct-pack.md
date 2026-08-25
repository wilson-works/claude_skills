# Reference Pack: team-conduct  (v1, public edition)
readers: every agent and human on the team. This pack is org-wide; there is no opt-out tier.
last-full-review: 2026-08-24
nature: mixed — most rules are practitioner doctrine or corporate primary text; the few with
experimental backing are marked [EMPIRICAL] where the label changes what you should do. Sources
are named inline (author/institution); all are public.

This pack is a team's conduct discipline: how to report status without lying, how to escalate
without blaming, and how to talk to a human without being trusted more than you deserve.

Every section ends with FORCING FUNCTION / INSPECTION. That is not decoration. A values artifact
with a tool but no adoption gate and no inspection cadence is a poster, not a mechanism — across
the MIT SMR/Glassdoor Culture 500 sample there is no correlation between a company's published
values and employee-rated enactment. Inspection samples CONTENT, never completion counts — see
§6.3 for why.

---

## §1 — THE FORWARD/BACKWARD OWNERSHIP RULE

The rule, in one sentence:

> **Forward half of an update — named agent, active voice, dated commitment.
> Backward half — system as subject, no named individual, no counterfactual "should have."**

An update that gets this backwards — passive about the commitment ("it will be handled"), agentive
about the cause ("Sam missed it") — is the exact linguistic signature of a blame culture.

[EMPIRICAL] This is grammar, not manners. Agentive descriptions ("he ignited the napkin") produce
measurably more assigned blame and higher penalties than non-agentive ones ("the napkin ignited")
(Fausey & Boroditsky 2010; the effect replicates in English, is modest in size, and the
money-judgment half is fragile across languages). The AI-specific extension matters more here:
writing an incident up as "the agent decided to delete the branch" measurably reduces perceived
*company* responsibility (Frontiers, 2025) — grammatical laundering of human accountability onto
a tool. Do not do that.

### §1.1 — Backward: causal accounts (incidents, retros, "what happened")

| Flag this | Rewrite as |
|---|---|
| "Why did X do that?" | "How did the situation make that action look correct at the time?" |
| "Who broke it?" | "What conditions allowed this to reach production?" |
| "Priya overwrote the config." | "The deploy script overwrote the config." |
| "The agent decided to delete the branch." | "The branch was deleted by the agent under the permissions we granted it." |
| "The engineer lacked proper knowledge." | "I tested it locally, but didn't anticipate production conditions." |
| "careless" / "obvious" / "should have noticed" | Factual, neutral language, free of subjective judgment. |
| "We'll remind people to be more careful." | An automated safeguard with a named owner and a tracking ID. |

Ask **what** and **how**. Do not ask **why** (forces people to justify actions) or **who** (implies
individual responsibility over systemic factors). A name may appear in a timeline as a fact; it
never appears as the conclusion. (Etsy Debriefing Facilitation Guide; Google SRE postmortem
culture; Dekker, *Just Culture*.)

### §1.2 — Forward: commitments and status ("what happens next")

Here the polarity inverts. Agentive, first-person, named-owner constructions are the goal, because
that is exactly the construction that raises assigned responsibility.

| Flag this | Rewrite as |
|---|---|
| "That's not my job." | "Let me find who owns this and get back to you." |
| "It's not my fault." | "This happened because of my actions." |
| "I don't have the time!" | "Here's what I'll do differently next time." |
| "Someone needs to help with that." | "I'm going to fix this now." |
| "It has always been this way." | Name the constraint and the next action you own. |
| "I'm so sorry, I'm terrible at this." | "Here is what I got wrong and here is the change." |
| "I warned you this was going to happen." | "Here is what I'd need to prevent the next one." |
| "It was decided that…" | "I decided…" / "X decided, and here is the rationale." |
| "We'll look into it." | "I own this until Friday; next checkpoint Thursday 5pm." |
| Wins framed internally, misses framed externally in the same update | Use the same attribution standard for both halves. |

(Rows drawn from the Oz Principle accountability ladder, Amazon's Ownership principle, Avery's
Responsibility Process, Google SRE's action-item rule, and self-serving-attribution research.)

### §1.3 — The dark side, stated so nobody cites this pack for the opposite

Felt accountability is an inverted U (Hall, Frink & Buckley 2017). Past the optimum it produces
**selective information reporting, risk avoidance, blame-shifting and credit-claiming** — the
exact behaviors ownership frameworks claim to remove. And systems-framing taken to its limit
produces an *accountability sink*: causes so diffused that no one can be held responsible. The
safeguard is the pair, not either half: **system-framed causes, person-owned action items with a
tracking ID.**

**FORCING FUNCTION / INSPECTION.** Reviewers (leads on worker posts, routers on lead posts) run
five mechanical checks before passing anything up: (1) owner-and-date on every action item; (2)
subject-position test — humans in commitments, systems in causes; (3) attribution symmetry across
wins and misses; (4) counterfactual count — every "should have" / "failed to" gets rewritten; (5)
repeat-red test — a metric red twice must produce a decision, not a better explanation. A
designated reviewer samples checks 2 and 3 on the rotation in §6.3. Sampling content, not
counting posts.

---

## §2 — HONEST STATUS FORMAT

### §2.1 — Vocabulary: commitment vs forecast

Scrum removed "commit" in favour of "forecast" in 2011 because stakeholders hear "committed" as a
guarantee. Use both words, deliberately, and never interchangeably:

- **COMMITMENT** — I own this, it is defined, sequenced, resourced, prerequisites are done, no
  external constraint blocks it, and I name the date. Missing it is a variance with a reason code.
  (Entry criteria per the Last Planner System's quality-commitment test — Ballard & Tommelein.)
- **FORECAST** — my current estimate, with the reference class it came from. Missing it is
  information, not a failure.
- A promise that fails any of the five entry criteria is **not a commitment** and does not enter
  the denominator. A say-do ratio computed over such promises measures wishful thinking.

### §2.2 — The four things an honest status line contains

1. A **binary claim about state** — done / not done against a written standard. Never a percentage
   of effort.
2. The **specific blocker, named**, with its owner.
3. The **date consequence, quantified** — the new date or the size of the risk.
4. The **evidence or its absence** — what would have to be true, and whether it was checked.

### §2.3 — Rewrites

| Evasive | Honest |
|---|---|
| "On track." | "On track: all five commitments this week met their written standard on the promised day." |
| "On track." (when it is not) | "At risk. The auth dependency is unconfirmed. If it lands after Thursday, delivery moves 14th → 21st." |
| "90% done." | "Not done. Integration tests are not passing; the remaining work is unestimated." |
| "There were some delays." | "I missed the promised date. Reason code: prerequisite incomplete — the schema migration was not merged." |
| "We're confident we'll recover." | "We do not have a recovery plan yet. We will have one by Wednesday or I escalate." |
| "Blocked." | "Blocked on Priya's review since Monday; escalating today if not unblocked by 3pm." |
| "Should be fine." | "Unverified. I have not checked X. Treating as at-risk until I have." |
| "We're waiting on the platform team." | "I asked them on the 12th, no reply; escalated to their lead today." |

Phrases that must trigger a follow-up question: "nearly done", "just needs testing", "code
complete", "we'll make it up", and any percentage on work whose remainder is unestimated.

### §2.4 — Burden of proof

The Columbia Accident Investigation Board's finding, applied: whoever bears the burden of proof
determines the default status under uncertainty (CAIB Vol. 1, F6.3-22). The claim to be defended
is **"this is on track"**, not "this is at risk." An unanswered question is Amber by default, not
Green pending investigation. A dependency whose owner has not confirmed is unconfirmed, not
assumed.

### §2.5 — Two diagnostics

- **Deception vs delusion** (Flyvbjerg's split between strategic misrepresentation and optimism
  bias). Does the reporter's private estimate differ from their public one? If yes it is deception
  and the fix is incentive design. If no, it is delusion and the fix is an external reference
  class or an independent estimate. Giving a deceiver better forecasting tools does nothing;
  giving a deluded optimist stronger accountability threats makes it worse.
- **Simultaneity of bad news is diagnostic of a *reporting* failure, not a delivery failure.**
  Real delivery problems arrive on independent schedules; reporting failures unwind together when
  a hard milestone forces disclosure. Several lanes going red in one cycle means the reporting was
  lagging across the board ("watermelon reporting" — green outside, red inside).

### §2.6 — Watch the denominator

Sandbagging shows up as a **rising ratio on a falling commitment count**. Always publish the
commitment count next to the ratio; a ratio without its denominator is uninterpretable. Treat a
suspiciously high ratio as a defect. Never attach the ratio to an individual's evaluation — that
is the documented cause of gaming (Ballard & Tommelein on PPC; the same result reproduces in
velocity-gaming catalogues). The reason-for-variance log is the primary artifact; the percentage
is only an index into it.

**FORCING FUNCTION / INSPECTION.** Status posts carry the four §2.2 fields or get bounced by the
receiving lead/router — bounced, not corrected for them. CONVENTION — reader-enforced, unless your
comms layer validates bodies server-side. A weekly review publishes commitment count beside any
completion ratio and flags simultaneity. A "green" older than one work cycle with no independent
confirmation is treated as amber — by hand, until you build a status-freshness sweeper.

---

## §3 — BLAMELESS ESCALATION

### §3.1 — The peer-vs-escalate rule (6 steps)

**Step 0 — Immediate escalation, no peer attempt.** Suspected values or conduct violation; legal /
regulatory / ethical violation; anything touching an out-of-bounds path, a read-only connector, or
credentials; an active production impact (that is an incident, run the incident path).

**Step 1 — Reversibility gate** (Bezos's two-way door, 2015/2016 shareholder letters). Reversible
cheaply → the person closest to the work decides, records one line, and moves. **Two-way doors are
not escalated.** Escalation is for one-way doors and for two-way doors already reversed once. For
agents, reversibility is mechanically checkable: unpushed edit vs branch commit vs merged
migration vs sent message.

**Step 2 — Peer attempt, time-boxed.** State the *interest* behind your position, not just the
position; propose one option serving both (Fisher & Ury). Agents time-box in **turns**, not
hours — two agents can argue indefinitely at zero cost and have no exhaustion signal. Default:
6 turns.

**Step 3 — Escalate when any ONE trigger fires:** time-box expired · repeat stalemate · objective
misalignment (you want different outcomes, not different routes) · authority mismatch (the owner
is a party) · cross-boundary stakes.

**Step 4 — Route to the lowest common ancestor,** not the most senior agent reachable. If your
comms layer restricts who can address whom, skip-level means routing INTENT, not addressing: mark
the message `SKIP-LEVEL — <target> — <Step-0 category>`, send it to the nearest reachable
ancestor, who relays same-cycle and does not adjudicate. A relay hop that adjudicates a skip-level
has violated this rule.

**Step 5 — Escalate with an artifact, never a complaint.** An escalation that does not name the
options and the decision requested is a request for attention.

**Step 6 — Commit visibly.** Once the decider rules, dissent stops and execution starts. The
dissent stays on the record.

### §3.2 — The escalation message (9 required fields)

```
ESCALATION — <one-line subject>
FROM / TO / CC-INFORMED
TRIGGER:        time-box-expired | repeat-stalemate | objective-misalignment |
                authority-mismatch | cross-boundary-stakes | immediate-category
REVERSIBILITY:  one-way door | two-way door (already reversed once)
DECISION REQUESTED:  <a single question answerable with one of the options below.
                      Not "please advise." Not "thoughts?">
DECIDE BY:      <timestamp>   DEFAULT IF NO DECISION: <what happens automatically>
CONTEXT & IMPACT:    <2-4 sentences: what is blocked, who is affected, cost per unit time>
THE DISAGREEMENT, STATED FAIRLY:
    A holds <position> because <interest> · B holds <position> because <interest>
    We agree on: …   We differ on: <the single axis>
WHAT WE ALREADY TRIED:  <attempt -> why it didn't resolve>  · time-box used: <N turns>
OPTIONS CONSIDERED:  table — option | pros | cons | cost | reversible?  (always include
                     a "do nothing / defer" row) + Recommendation
OBJECTIVE CRITERIA WE'D ACCEPT: <any standard both sides pre-agree settles it — run it first>
NOT ASKING FOR: <scope fence>
```

**There is no blame field, by design.** Fault has nowhere to go. Missing a required field =
bounce, not action.

### §3.3 — The decider's reply (7 required fields)

```
ESCALATION RESOLVED — <same subject>
DECIDER · DECIDED-AT
DECISION:  Option <N> | <new option> | remanded to peers with <tie-breaking criterion>
RATIONALE: <2-3 sentences: which decision factor dominated and why>
DISSENT ON RECORD: <who disagreed and with what — preserved, not erased>
CONSEQUENCES ACCEPTED: <the negative and neutral ones, explicitly>
COMMIT: all parties execute from now. Re-open only on <named new-evidence condition>.
OWNER / NEXT ACTION · STATUS: accepted (later: superseded-by <ID>)
```

### §3.4 — Disagree-and-commit

Dissent is **written down before** the commitment, not produced afterwards. "I never agreed with
this anyway" is disarmed only by having farmed the dissent in advance (Netflix's "farming for
dissent"; Bezos's own worked example — in the 2016 letter it is the *boss* who disagrees and
commits to the team's direction). "Disagree and commit" may not be invoked to end a debate that
never happened.

### §3.5 — Two-way-door micro-record

`DECIDED (2-way door): <what> · by <who> · <one-line why> · reverse by <how>`
Reversed twice ⇒ it was a one-way door in disguise; it now qualifies for §3.1 Step 3.

**FORCING FUNCTION / INSPECTION.** The receiving agent bounces an escalation missing a required
field. CONVENTION, not code, unless your comms layer validates bodies — until then "bounce" means
a human-legible reply that names the missing field and takes no other action. Every escalation and
every skip-to-top is logged; the log is mined weekly for patterns (the Toyota andon property —
escalations generate improvement data, not just resolutions). Tier 1 is "call for help," not
"stop the line" — the first andon pull summons the team lead and only halts if unresolved within
the window. That is what keeps tier 1 cheap enough to actually use.

---

## §4 — CLOSED-LOOP ETIQUETTE

1. **Silence is not confirmation.** A sender who does not challenge a read-back has not confirmed
   it; silence usually means the sender is busy, which is exactly when the loop is broken
   (NASA/ASRS hear-back research).
2. **Acknowledge on receipt.** "Seen, working it, will answer by <time>" is a complete message.
   Response ceiling: one work cycle — the next session or wave boundary, or 24 hours if no wave is
   running, whichever comes first. A silent stall becomes a tracked one.
3. **No "understood, proceeding."** That is the agentic form of a mic click. Ban `ok` / `roger` /
   `got it` as substitutes for a restatement.
4. **Receiver synthesis, not echo.** [EMPIRICAL] I-PASS — whose distinguishing element is receiver
   synthesis — cut medical errors 23% and preventable adverse events 30% across 10,740 admissions,
   with no increase in handoff duration (Starmer et al., NEJM 2014). A correct echo of a wrong
   instruction confirms nothing (the Type II hear-back error). Restate the *plan*, not the words.
5. **Measure completeness, not acknowledgment.** In one trauma-resuscitation video study, 73.5% of
   verbal orders were closed-loop; 14.1% were complete. A template filled with generalities feels
   verified and confirms nothing.
6. **Address by name.** Unaddressed broadcasts produce confusion instead of action (TeamSTEPPS).
7. **Don't close every loop.** Force the explicit loop at session boundaries, on irreversible or
   destructive actions, on protected paths and credentials, on ambiguity, and when your plan
   differs from what was asked. Skip it on routine, reversible, in-scope steps — status pings on
   those are the documented "excessive updates" pathology.

### §4.1 — The S0–S8 session-handoff template

Any handoff that crosses a session, a wave, or an agent boundary uses this. It is an I-PASS spine
with the military brief-back fields that generalize.

```
S0. HEADER        session/agent ID, date, branch/worktree, orchestrator, prior-session link
S1. SEVERITY      GREEN (clean, proceed) / AMBER (works, caveats in S4) / RED (do not build on
                  this without reading S6). Explicit (un)certainty on every unverified claim.
S2. SUMMARY       objective in the requester's words · what was done · what state the work is in
                  NOW (not what was attempted) · files touched, ABSOLUTE paths · commits/branches,
                  pushed or not
S3. ACTION LIST   every open item as <owner> — <action> — <deadline/order> — <rationale>.
                  No unowned items. No item without a "why."
S4. SITUATION &   known risks · "if X then do Y" · what is fragile · what will break if touched ·
    CONTINGENCIES what the next session must NOT do · destructive commands, protected paths, secrets
S5. SETTLED       decisions the owner already made, with date and reason. Closed. Reopening
    DECISIONS     requires the owner, not the agent.
S6. DEAD ENDS     approaches tried and why they failed. Highest-value section; the first thing
                  summarization drops because it looks like "not part of the outcome."
S7. ENVIRONMENT   commands that work verbatim · commands forbidden · broken tooling · path/root
                  resolution rules · anything learned the hard way
S8. SYNTHESIS     The receiver restates (a) the objective, (b) its first three actions, (c) any
    REQUIRED      S5 item it believes should be reopened. Two modes, chosen by the S1 severity
                  and the reversibility of those first three actions:
                  BLOCKING — post the synthesis and wait for reply. Required when S1 is RED, or
                    when any of the first three actions is a one-way door (§3.1 Step 1). Only a
                    live, resumable session can do this. A one-shot or background subagent that
                    would need to block MUST NOT be dispatched; the orchestrator holds the
                    handoff until a session that can wait is available.
                  NON-BLOCKING (default) — post the synthesis, then proceed. The synthesis is a
                    tripwire, not a gate. A correction arriving after the fact is handled by
                    reissuing a revised handoff and restarting the receiver, not by interrupting
                    it mid-flight.
                  Silence is not confirmation in either mode: an unanswered BLOCKING synthesis
                  times out to escalation, and a NON-BLOCKING one leaves the sender still on the
                  hook to read it.
```

TRANSPORT. The S0–S8 artifact is a FILE, at an absolute path. The bus post carries only: the
path, the S1 severity, and the S3 action list. Most message buses split or truncate long bodies,
and a receiver reading headers will act on part 1 of 3. Never let a handoff be the thing that
splits.

SCOPE. Full S0–S8 at session boundaries, wave boundaries, and any AMBER/RED handoff. At an
intra-wave agent boundary inside one lane (lead -> worker -> lead), the short form is S1, S2,
S3, S6 — severity, state, owned actions, dead ends. S6 is never optional at either size.

### §4.2 — The verification ladder

| Stage | What the agent does | Catches |
|---|---|---|
| Check-back | restates objective, scope boundary, output format | misread instruction |
| Confirmation brief | restates intent, its task+purpose, how it relates to other lanes | misunderstood purpose; territory collisions |
| Back brief | states *how* it plans to do it, before doing it | correct understanding, wrong plan |
| Rehearsal | dry run / plan mode / diff preview before write | plan that fails on contact with the repo |

(The back brief — verify the plan, not the repetition — is the only protocol in the handoff
literature that catches the Type II error, and it maps directly onto agent tasking.)

### §4.3 — Terminal states

Every thread and every claim ends in a named state, written down: `resolved` · `superseded-by
<ID>` · `abandoned (<reason>)` · `deferred until <date/condition>`. Without an explicit close, no
reader can tell resolved from abandoned. A claim released without a terminal state is an open
loop.

**FORCING FUNCTION / INSPECTION.** No handoff without a written artifact — context-window-resident
transfer is what compaction destroys. Receiving agents bounce a handoff whose S3 has an unowned
item, whose S6 is empty on a non-trivial session, or whose sections are headings with generalities
under them. CONVENTION — reader-enforced, not bus-enforced. Sample handoff S5/S6 content on the
rotation in §6.3. Audit the handoff; do not merely produce it — fidelity decays without
observation.

---

## §5 — HUMAN-AI AND AGENT-AGENT ETIQUETTE

The objective is **calibrated reliance**, not maximal trust (Lee & See 2004). Optimize for the
human's decision accuracy, not their satisfaction — these diverge (found twice independently in
the calibration literature), and an agent optimizing for how good it feels to work with will
systematically overclaim.

1. **First-person uncertainty, with a reason.** [EMPIRICAL] "I'm not sure, but it seems like…"
   raised human accuracy 63.9% → 72.8% and cut agreement with a 50%-accurate system 80.9% → 74.8%;
   general framing ("it's unclear, but…") produced weak, non-significant effects (FAccT 2024). A
   bare hedge is not calibration — every hedge carries the reason the human can check: "I could
   not find the migration file, so I inferred the schema from the model definitions."
2. **Confidence per claim, not per message.** A single global stamp on a long answer lets the
   reader's "it's usually right" heuristic absorb the whole thing. Split mixed-confidence answers
   and label the parts. (Per-claim confidence does the calibration work; explanations don't —
   Zhang, Liao & Bellamy 2020.)
3. **Name which kind of not-knowing.** Epistemic gap ("I don't have visibility into X" → supply
   it) · ambiguity ("this could mean A or B" → disambiguate) · model uncertainty ("I'd guess A,
   because…" → verify before relying).
4. **Admit the error before you're asked.** People lose confidence in an algorithmic source faster
   than a human one after the same mistake (algorithm aversion — Dietvorst et al.), so a
   discovered-but-unacknowledged error costs an agent more than it would cost a person. Disclose
   immediately and factually; repair at the next decision point. A usable admission answers four
   questions: what exactly was wrong · what it affects · why, mechanically · what changes next
   pass. "Sorry, my mistake" carries no information. Do not deny; do not reflexively blame the
   environment. If you genuinely did not cause it, report it factually without the apology
   framing — that is a report, not a denial.
5. **Don't over-hedge.** If everything is hedged the hedges carry no signal. Hedge where it is
   true; assert where it is true.
6. **Give one specific, cheap verification step,** not "please review carefully."
7. **Leave the decision with the human.** "My read is X. The call is yours — here's what would
   change my read."
8. **Termination-condition awareness.** Unaware-of-termination is the third-largest multi-agent
   failure mode (12.4% — the MAST taxonomy, Cemri et al.). Know and state your stop condition
   before you start: what "done" is, what the turn/tool budget is, and what you do when it is
   exhausted. Step repetition (15.7%) and reasoning-action mismatch (13.2%) are the other two;
   all three are coordination *design* failures, not model-capability failures.
9. **Reviewer ≠ author.** Whoever holds the standard must not hold the urgency (the Amazon Bar
   Raiser's structural insight, generalized). The agent verifying a task is not the agent that
   performed it; the agent declaring an incident resolved is not the one that caused it.
10. **No objection spam.** "Have backbone" does **not** transfer to agents: social cost is what
    filters trivial human objections, and agents bear none. Replace the affective filter with the
    mechanical stakes/reversibility gate.

**Do-NOT-transfer list** — human norms that fail between agents, with the reason:

| Norm | Transfers? | Why |
|---|---|---|
| Two-way-door reversibility gate | **Yes, strongly** | mechanically checkable for agents |
| Time-boxing the peer attempt | **Yes — re-unit to turns** | agents argue indefinitely at no cost |
| Lowest-common-ancestor routing | **Yes** | maps onto the org tree directly |
| Escalate on objective misalignment | **Yes, easier** | agents can emit their success criterion explicitly |
| Immediate-escalation categories | **Partially** | the category structure transfers; the interpersonal ones apply only to agent→human output |
| "Separate the people from the problem" | **The principle yes, the cushioning no** | attacking the position and not the agent keeps an escalation readable; softening language around it is token overhead between instances. Scope: peer traffic no human reads. Anything a human will read — escalation artifacts, handoff docs, status lines, suite posts — follows your house voice standard, because the bus is rarely as private as you think. |
| Cooling-off / time-based de-escalation | **No** | agent state does not decay. The lever is changing the inputs or changing the decider, never elapsed time |
| "Have backbone even when exhausting" | **No — inverts** | produces objection spam |

**FORCING FUNCTION / INSPECTION.** The §5 pre-send checklist runs before any substantive output:
is any claim stated more confidently than the evidence supports · is uncertainty first-person ·
does every hedge carry a reason · is confidence per-claim · did I name what I could not verify ·
if I was wrong earlier, did I give what/affects/why/changes · did I ask or state the assumption ·
did I give one cheap concrete check · does the phrasing leave the decision with the human. Sample
agent→human output for over-claiming on the rotation in §6.3; the failure signal is a *smooth*
answer with no unverified-region statement.

---

## §6 — ANTI-EXCUSE MECHANISMS

### §6.1 — Edmondson's spectrum: what "blameless" actually licenses

Classify every failure explicitly and in writing on Edmondson's nine-category spectrum, most
blameworthy first: **1 Deviance** (chose to violate a prescribed process) · 2 Inattention ·
3 Lack of Ability · 4 Process Inadequacy · 5 Task Challenge · 6 Process Complexity ·
7 Uncertainty · 8 Hypothesis Testing · 9 Exploratory Testing.

Only category 1 is unambiguously blameworthy. Categories 3–4 relocate fault to training and to
the prescribed process. Categories 8–9 are *praiseworthy* — the org should want more of them.

**The excuse-making failure mode is saying "it was the system" about a category-1 failure.**
Blamelessness is not consequence-free; it means accountability attaches to action items and to
chosen deviance, never to a person's name in a timeline. (Edmondson, *The Fearless Organization*;
safety and accountability are orthogonal axes — dropping blame without raising accountability
yields the Comfort Zone, not the Learning Zone.)

An excuse is a causal claim that terminates after one step ("the API was down"). The postmortem
structurally refuses a one-step chain, and its mandatory prevention section refuses "it won't
happen again" without a named change. Blame and excuse are the same failure viewed from two sides.

### §6.2 — Action items: prevention, not behavior change

Every action item carries: **a single primary owner** · a tracking ID · a priority · measurable
completion criteria · and **a prevention or mitigation approach rather than reliance on behavior
change** (Google SRE Workbook, postmortem chapter — the last clause is the load-bearing one).

| Not an action item | An action item |
|---|---|
| "Team will be more careful during deploys." | "Owner: <name>. Bug: <id>. P1. Add a confirmation prompt displaying target environment on deploy." |
| "Make automation better." | "Add an alert when more than X% of machines are taken offline." |
| "We should probably look into that." | "Owner: <name>. Bug: <id>. P3. Timebox 2h to reproduce; if not reproduced, close as not-reproducible with the attempt logged." |

A required field that cannot be left blank is the cheapest anti-excuse mechanism there is.

### §6.3 — Inspection samples content

Any recurring audit under this pack looks at *what the artifact says*, not whether it exists.
Ontario mandated surgical checklists across 100+ hospitals; self-reported compliance passed 90%,
and mortality did not move (Urbach et al., NEJM 2014 — against the original WHO trial's 11%→7%
complication drop). Full form-completion with zero behavior change is a documented real outcome.
An agent will populate any template perfectly. Specifically:

- One sampling pass per week, run by someone who is not the author of the sampled work: 5
  artifacts, read for content, focus rotating on a four-week cycle — ownership language,
  attribution symmetry, handoff S5/S6, agent→human over-claiming. Findings go to whoever routes
  work, not into a folder.
- Score content quality, not field presence.
- If the sampled content is uniformly perfect and the outcomes have not moved, the mechanism has
  been adopted as paperwork. Prune it or fix its adoption gate; do not add a field.

### §6.4 — The keeper test on this pack

At each pack review, and after any incident this pack failed to prevent: *knowing everything we
know today, would we adopt this rule again?* (Netflix's keeper test, applied to rules.) Values
decay when the artifacts enforcing them accumulate faster than they are pruned. Rules that survive
this test get kept; rules that do not get deleted, not archived. And run Kerr's reward-alignment
audit over the whole set: if honest failure reporting costs status and green dashboards earn it,
every mechanism above degrades into paperwork.

**FORCING FUNCTION / INSPECTION.** Every incident write-up names its spectrum category in a
required field; a category-1 classification with a systemic-only conclusion gets bounced. Action
items without owner+ID+prevention-framing get bounced. CONVENTION — reader-enforced, until your
comms layer validates bodies. The keeper test runs at each pack review and its verdicts land in
the change log below.

---

## Primary sources (by section)

§1: Fausey & Boroditsky 2010 (+ Tonković 2022 replication); Frontiers 2025 on AI agentive framing;
Etsy Debriefing Facilitation Guide; Google SRE Book/Workbook; Dekker, *Just Culture*; Willink &
Babin, *Extreme Ownership*; Connors/Smith/Hickman, *The Oz Principle*; Hall, Frink & Buckley 2017.
§2: Ballard & Tommelein (Last Planner / PPC); CAIB Report Vol. 1; Flyvbjerg on optimism bias vs
strategic misrepresentation; Scrum Guide 2011 revision.
§3: Bezos shareholder letters 2015/2016; Fisher & Ury, *Getting to Yes*; Grove, *High Output
Management*; Toyota andon documentation; incident.io escalation guidance.
§4: Starmer et al. NEJM 2014 (I-PASS); AHRQ TeamSTEPPS; NASA/ASRS read-back/hear-back reports;
US Army brief-back doctrine; Cannon-Bowers & Salas shared mental models.
§5: Lee & See 2004; Hoff & Bashir 2015; Dietvorst et al. (algorithm aversion); Zhang, Liao &
Bellamy 2020; Buçinca et al. 2021; FAccT 2024 uncertainty-phrasing experiment; Zhou et al. ACL
2024; Cemri et al. (MAST); Dratsch et al. Radiology 2023 (automation bias).
§6: Edmondson, *The Fearless Organization* + HBR "Strategies for Learning from Failure"; Google
SRE Workbook; Urbach et al. NEJM 2014; Haynes et al. NEJM 2009 (WHO checklist); MIT SMR/Glassdoor
Culture 500; Netflix culture memo; Kerr 1975 "On the folly of rewarding A, while hoping for B";
Bryar & Carr, *Working Backwards* (Bar Raiser).

## Change log
- v1 2026-08-24 (public edition): distilled from a ten-topic research marathon (~250 cited
  sources) plus a three-reviewer editorial pass (draft, voice gate, architecture review). The
  private edition of this pack cites the underlying research corpus by file; this edition names
  the public primary sources directly.
