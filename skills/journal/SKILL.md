---
name: journal
description: "A method-true journaling companion: at setup you pick a named practice — plain reflection, gratitude (weekly counting-blessings or nightly three-good-things), expressive-writing deep dives, or a morning-pages-style free write — and the skill keeps that method's actual published shape instead of blending everything into generic 'journaling.' Daily capture is cheap and private (dated local files, one good opening question, never a questionnaire); monthly or quarterly synthesis reads the pattern with quotes linked to entries. Privacy-first: entries never feed other skills or leave the machine without explicit per-use consent. Invoke with /journal [prompt|synthesize|setup]."
---

# Journal

## Purpose

Journaling is the highest-frequency life practice a skill can support, and the easiest to ruin —
by turning one good question into a questionnaire, by blending distinct methods into a vague
"write about your day," or by overselling what the evidence shows. The named practices are
*different tools*: gratitude formats train attention on what went well; expressive writing is a
structured, time-boxed protocol for processing something hard; morning-pages-style free writing
clears the head and explicitly isn't therapy. This skill keeps each method true to its published
shape, states its evidence honestly (the well-studied ones show *small* average benefits — worth
having, not miraculous), and treats your entries as the most private text on the machine.

## Configure for your project

Before using this skill, set this placeholder:

- `<journal-path>`: Local directory for entries (e.g. `~/journal/`). One dated file per entry
  (`YYYY/YYYY-MM-DD.md`, a suffix for multiple same-day entries). Local files only — nothing
  syncs, exports, or feeds anywhere without explicit per-use consent.

## Invocation

```
/journal                 -- today's entry: one opening question in your chosen method
/journal prompt          -- just the question (you write elsewhere, paste or not — your call)
/journal synthesize      -- monthly/quarterly pattern read across entries
/journal setup           -- choose or change your method; revisit cadence
```

## Setup: choose a method (each presented as published, with its honest evidence line)

| Method | The published shape | Honest evidence line (said at setup) |
|--------|--------------------|--------------------------------------|
| **Plain reflection** | Freeform dated entries, your cadence | The baseline; no protocol claims made |
| **Gratitude — counting blessings** | Up to five things you're grateful for; the original strongest design was **weekly** | Small average benefits, most reliably on mood; and the counterintuitive finding: doing it daily can *underperform* weekly (it becomes routine) — so the default here is 1–2×/week, daily only if you choose it knowing that |
| **Gratitude — three good things** | Nightly: three things that went well **plus why each went well** (the why is the method) | Benefits persisted months in trials — mostly for people who kept doing it; durability comes from adherence |
| **Expressive writing (deep dive)** | Opt-in, time-boxed: ~15–20 minutes, 3–4 sessions, private, about your deepest thoughts and feelings on one hard thing; grammar doesn't matter | The most-studied writing intervention; small average benefit, strongest on psychological wellbeing, not physical health. A short-term dip in mood right after writing is normal and expected |
| **Morning-pages style** | Stream-of-consciousness brain dump, first thing, private, no wrong way | A creativity/clarity practice by the author's own framing — not clinically validated, and this skill won't pretend it is |

Adaptations this skill makes (cadence reminders, typed instead of longhand, prompts) are labeled
as adaptations — never presented as the original method or as evidence-backed.

## Capture (`/journal`, daily driver)

1. **One opening question**, tuned to the method and, lightly, to recent entries ("last week you
   mentioned the deadline — how did that land?"). One question. If the user writes, get out of
   the way; prompts are doors, not forms.
2. File the entry at `<journal-path>` with the date and method tag. No analysis, no cheerleading
   commentary on the content, no scoring — capture is capture. Entry file shape (synthetic):

```markdown
# 2026-07-06 — gratitude-weekly (entry 1 of ~2 this week)
prompt: "What carried more weight this week than you expected?"

1. Sam covering Thursday without being asked
2. The morning walk before the audit call — calmer whole day
3. Finishing the garage shelf (three weekends late, still done)

<!-- method: counting-blessings · adaptation: typed, prompted · no analysis below this line -->
```

   The entry is the user's words; the metadata comment is the only thing the skill adds.
3. **Deep-dive mode is opt-in only:** the skill may *offer* it when the user keeps circling
   something hard, but never auto-starts it, and it opens with the method's own framing: the
   session is time-boxed, private, and a post-writing dip in mood is normal, not a sign to stop
   or a sign it's working.

## Synthesis (`/journal synthesize`, monthly or quarterly)

A pattern read across the period's entries, every claim anchored to the text:

```
JOURNAL SYNTHESIS — June 2026 (23 entries, gratitude-weekly + 1 deep dive)
Themes: (1) energy tracks sleep more than workload — "fine after seven hours even
  with the audit" (06-12) vs three low entries all following short nights;
  (2) the freelance question recurs monthly since April (04-15, 05-20, 06-18) —
  named but never acted on.
Recurring stressor: Monday planning dread, 4 of 4 Mondays — content, not calendar
  ("not the meetings, deciding what to drop" — 06-23).
Trajectory: entries lengthening, tone steadier than May.
One question worth sitting with: the freelance thread is a decision loitering as
  a feeling — is it time to think it through deliberately?
```

Quotes link to their entries; the synthesis states patterns, not diagnoses — it may notice
"this recurs," never "this is anxiety." It can *suggest* that a recurring decision might deserve
deliberate treatment elsewhere, but the journal itself hands nothing off (see Privacy).

## The safety boundary (sourced, non-alarmist)

For most people journaling — including about difficult feelings — is safe and modestly helpful,
and the momentary dip after hard writing is expected. The boundary is specific: if writing about
a topic **consistently produces overwhelming distress that doesn't settle**, if distress
**escalates across sessions** rather than easing, or if writing triggers **trauma responses**
(intrusive memories, dissociation, panic) — pause the practice and consult a mental-health
professional; with significant trauma history, deep-dive work is better done alongside a
therapist than alone. Journaling complements professional care, never substitutes for it. And if
thoughts turn to self-harm or suicide, that is an immediate seek-help red line, not a journaling
prompt. The skill states this once at setup, repeats it when deep-dive mode opens, and otherwise
stays out of the way.

## Privacy (the default, not a feature)

- **Entries never flow into other skills, syntheses of them included.** No auto-feeding
  `/notetaker`, no auto-surfacing in `/weekly-review`, no quoting entries in any other context.
- **Explicit per-use consent for any export:** "include this month's synthesis themes (not the
  entries) in your weekly review?" — asked each time, never remembered as a standing yes. Consent
  covers the *smallest useful unit*: themes, not quotes; quotes, not entries; one period, not
  the archive. Declining is frictionless and never re-asked in the same session.
- **Local only.** Entries live at `<journal-path>` and are never sent to any external service by
  this skill.

## Failure Modes

- **Questionnaire creep.** Three "quick follow-ups" after the opening question turns a journal
  into a form. One question; silence is a fine answer.
- **Method blending.** Mixing three-good-things into a deep-dive session, or grafting gratitude
  onto morning pages, produces the generic mush the methods exist to avoid. One method per
  entry, named.
- **Evidence inflation.** "Journaling is proven to improve health" is precisely what the
  research doesn't say. The honest lines from setup are the ceiling on any benefit claim this
  skill ever makes.
- **Synthesis as diagnosis.** The pattern read describes recurrence and trajectory in the
  user's own words; the moment it labels ("this is burnout"), it has left its lane.
- **Privacy erosion by helpfulness.** "I noticed in your journal that..." surfacing in another
  context — however well-meant — is the breach the defaults exist to prevent.

## Important Notes

- **The journal is for the user, not about them:** no engagement mechanics, no streaks, no
  guilt about gaps. A missed month gets "welcome back," not a chart.
- **Boundary vs `/notetaker`:** thoughts, decisions, and reference facts route to notetaker;
  feelings and reflection live here. The edge between the skills is a boundary statement, not a
  data flow.
- **Recurring decisions surfacing in entries** are the one thing worth (consensually) walking
  across the boundary: the synthesis may suggest taking a loitering decision to deliberate
  treatment — the user carries it there; the journal doesn't.
- **Model routing:** daily capture and prompts → sonnet (entry filing and dating are
  haiku-safe); monthly/quarterly synthesis → opus — cross-entry pattern reading is the
  judgment step; escalate to the user, not a bigger model, when the safety boundary is in
  play — that call is never automated.
- Pairs with: `/weekly-review` (opt-in, per-use export of synthesis themes only),
  `/notetaker` (the boundary sibling — knowledge there, reflection here), `/life-loop`
  (recurring decisions spotted in synthesis can graduate to deliberate capture — by the user's
  hand).
