---
name: brainstorm
description: "A structured two-phase ideation session. DIVERGE: quantity-first rounds under deferred judgment, you and Claude generating in parallel — the format the group-creativity evidence actually favors — with named techniques rotated on demand (Osborn free-wheel, SCAMPER operators, silent brainwriting-style rounds, reversal, constraint shuffles). CONVERGE: affinity-cluster the pile, triage fast, then score the survivors against your stated criteria into a reasoned shortlist. Output files to your notes, backlog, or business brain by your choice; shortlists can hand off to deliberation skills. Invoke with /brainstorm [topic]."
---

# Brainstorm

## Purpose

The pack judges ideas well (`/llm-council`, `/premortem`) but nothing *generates* them with
discipline. And ideation folklore is largely wrong: the best-replicated finding in the field is
that people generating **in parallel, silently, then pooling** produce more and better ideas
than a group talking it out — the classic meeting-room brainstorm loses most of its output to
production blocking (one voice at a time while everyone else holds and loses their thoughts).
What survives from the tradition is the phase discipline: **defer judgment, go for quantity,
welcome wild ideas, build on what's there** — as rules for a *generation phase kept strictly
separate from evaluation*.

A human plus an AI partner is the parallel-silent structure by construction: both generate at
once, nobody waits for a turn, and the partner neither judges socially nor free-rides. This
skill runs that session in two phases and never repeats the debunked claims (it will not tell
you a bigger meeting means more ideas).

## Configure for your project

Before using this skill, set this placeholder:

- `<sessions-path>`: Where full session piles are archived (e.g. `ideas/`), so a shortlist's
  losing ideas aren't lost — today's cut is sometimes next quarter's winner. The *outputs* go
  wherever you choose at session end (notes, backlog, business brain); this is just the archive.

## Invocation

```
/brainstorm <topic>            -- full session: diverge → converge → file outputs
/brainstorm <topic> --diverge  -- generation only; converge later against the archived pile
```

## Phase 1: DIVERGE (quantity first, judgment deferred)

**Rules of the phase** (Osborn's, enforced as constraints): no evaluation of any idea until
Phase 2 — not even praise; quantity is the goal; wild ideas welcome (taming is easier than
invigorating); build and combine freely.

**Structure:** interleaved parallel rounds. You seed (whatever's already in your head — first,
so the partner doesn't anchor you); Claude generates a round in parallel; you react with builds
or new seeds; repeat. Each Claude round has a quota (default 8–12), because a fixed quota is
what keeps generation honest when inspiration dips.

**Named techniques, rotated when a round stalls** (announced by name so you learn the moves):

| Technique | The move |
|-----------|----------|
| **Free-wheel** (Osborn) | Unconstrained quantity round — the default |
| **SCAMPER** (Eberle, building on Osborn's question lists) | Force transformations of existing ideas: Substitute · Combine · Adapt · Modify/Magnify · Put to another use · Eliminate · Reverse |
| **Silent rounds** (brainwriting-style, after Rohrbach's 6-3-5) | Fixed quota per round, building on the previous round's written pile — the structure that removes the speaking-turn bottleneck entirely |
| **Reversal** | SCAMPER's R aimed at the whole problem: "how would we guarantee this fails?" — then invert the answers |
| **Constraint shuffle** | Add, remove, or swap one constraint per round ("no budget" / "must ship Friday" / "for one user only") and regenerate |

How a session opens (synthetic):

```
/brainstorm "make onboarding emails less generic"
DIVERGE · round 0 — your seeds first (whatever's in your head, unfiltered):
> user: personalize by company size; kill email 3 entirely; a video maybe?
round 1 (free-wheel, quota 10): trigger off first real action instead of the
  clock · plain-text founder note · reply-to goes to a human · one email, five
  sends worth of content · segment by signup source · ...
> user: "build on the founder note — what else breaks the template?"
round 2 (build): hand-drawn diagram attachment · subject line with no title
  case · send at an odd minute (:47) · ...
round 3 stalls → rotating: CONSTRAINT SHUFFLE — "no email at all: same goal,
  different channel." → in-app note · SMS opt-in · a mailed postcard · ...
[judgment deferred throughout — no idea evaluated, praised, or developed yet]
```

Divergent rounds run on cheap models by design, and fan-out across models is a legitimate
diversity lever — with one caveat the recent literature flags: multiple AI generators can
converge on similar outputs, so the partner's role is parallel generation *feeding your
judgment*, never an autonomous idea committee.

## Phase 2: CONVERGE (separate step, never mid-generation)

A graduated ladder — go only as far up as the stakes warrant:

1. **Affinity clustering** (KJ method, after Kawakita): group the pile bottom-up into emergent
   themes; de-duplicate; name the clusters from the ideas, not in advance.
2. **Fast triage:** dot-vote-style picks or the NUF pass (Gray) — score New · Useful · Feasible
   — to cut the pile to candidates.
3. **Criteria scoring** for the survivors: elicit *your* criteria first ("what matters — cost,
   speed, reversibility, joy?"), weight them, and score each candidate with one line of
   reasoning per cell (Pugh-style against a baseline where comparing beats absolute scores).

```
CONVERGE — "make onboarding emails less generic" (41 ideas → 3)
Clusters: personalization-by-data (11) · timing/trigger changes (9) · format breaks (8) ·
  kill-the-sequence-entirely (5) · wildcards (8)
Triage: 9 candidates → NUF pass → 5 survive
Criteria (user-stated, weighted): effort ×1 · expected lift ×2 · testable-in-a-week ×2

| Candidate                              | Effort | Lift | Testable | Score | One-line reasoning |
|----------------------------------------|--------|------|----------|-------|--------------------|
| Trigger email #2 off first real action | good   | high | yes      | 9     | behavior beats schedule; A/B ready |
| Plain-text founder note as email #1    | low    | med  | yes      | 8     | format break, zero build           |
| Segment sequence by signup source      | high   | high | no       | 6     | best ceiling, needs data work      |

SHORTLIST: top two now (testable next week); segmentation parked to backlog with a note.
Losing pile archived → ideas/2026-07-06-onboarding-emails.md
```

**Escalation (named):** when two candidates tie and the tie turns on stakes the criteria didn't
capture ("both score 8, but one risks the brand"), that's no longer scoring — surface it as a
decision and offer `/llm-council` or `/premortem` rather than silently re-weighting.

## Filing (user's choice, asked once at session end)

- **Ideas/themes worth keeping** → `/notetaker` (its buckets, its format).
- **Actionable shortlist items** → `/backlog` (as items with category and priority).
- **Business-model-shaped ideas** → `/business-notes` (into the BMC brain).
- **Shortlist needing judgment** → hand to `/llm-council` (multi-perspective) or `/premortem`
  (stress-test before commitment).
- The full pile always archives to `<sessions-path>` regardless of filing choices.

## Failure Modes

- **Converging mid-generation.** "Ooh, that one's good, let's develop it" in round two is the
  classic phase violation — it ends generation early and anchors everything after. Praise is
  evaluation; hold it.
- **The partner anchoring the human.** If Claude generates first, the user's seeds shrink
  toward it. User seeds always open the session.
- **Quota theater.** Twelve restatements of one idea meet the quota and defeat it. Builds are
  welcome; rephrases don't count, and the skill says so when it notices.
- **Folklore relapse.** Any output implying "get more people in a room" or "verbal group
  brainstorming multiplies creativity" contradicts the evidence this skill is built on. The
  parallel-silent structure *is* the method.
- **Shortlist without reasoning.** A ranked list with no per-cell reasoning is a vibe with a
  table around it. Every score carries its one line.

## Important Notes

- **Technique names are teaching:** announcing "this is a SCAMPER round" builds the user's own
  ideation vocabulary — the skill should make itself progressively less necessary.
- **Evidence honesty:** the techniques are prompting scaffolds with proper attributions; the
  *format* (parallel, silent, phase-separated) is what the research supports. Where this skill
  extrapolates lab findings to human+AI sessions, that's a mechanistic argument supported by
  early studies, not decades of replication — held as design rationale, not sold as proof.
- **Model routing:** divergent rounds → sonnet, with multi-model fan-out as a diversity lever
  (quota checks and pile formatting are haiku-safe); clustering, criteria scoring, and the
  shortlist → opus; escalate tie-breaks on uncaptured stakes to the deliberation skills, not to
  a re-run.
- Pairs with: `/notetaker` (idea filing), `/backlog` (actionable outputs), `/business-notes`
  (BMC-shaped ideas), `/llm-council` (shortlist deliberation), `/premortem` (stress-testing the
  winner before commitment), `/decision-policy` (a shortlist choice that recurs becomes a
  standing record there).
