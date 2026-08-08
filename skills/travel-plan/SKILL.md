---
name: travel-plan
description: "Plans a trip end to end without pretending to know the world: a capture interview for dates, party, budget, pace, and constraints; a day-by-day itinerary skeleton with one anchor per day; a run-time research discipline where every destination fact is fetched fresh with its source URL attached and visa/entry/health/safety facts come only from official government sources flagged MUST-VERIFY; reusable trip-type packing lists that improve after every trip; and a logistics checklist ordered by lead time. Plans only — never books, emails, or purchases. Invoke with /travel-plan [pack|checklist] [trip]."
---

# Travel Plan

## Purpose

Trip planning is a high-stakes recurring head-loop: dozens of small decisions, a few genuinely
unforgiving facts (entry rules, booking deadlines), and the same packing debates every time. The
failure mode of asking a model to plan a trip is confident staleness — visa rules, opening days,
and prices change, and a plan built on remembered facts fails at the airport.

This skill plans trips the honest way. The plan's *structure* — capture interview, anchor/flex
itinerary, packing lists, lead-time checklist — is durable and lives here. The plan's *facts* are
never baked in: every destination fact is researched at run time, carries its source URL in the
plan, and the facts that can ruin a trip (visa/entry, health requirements, safety advisories) are
taken only from official government sources and still flagged for the user to re-verify before
booking. The skill plans; it never books, emails, or purchases anything.

## Configure for your project

Before using this skill, set this placeholder:

- `<trips-path>`: Directory for trip plans and reusable packing lists (e.g. a `trips/` bucket
  beside your notes). One folder per trip; packing lists live in `<trips-path>/packing/` as one
  file per trip type.

## Invocation

```
/travel-plan                    -- new trip: capture interview → research → itinerary + checklist
/travel-plan pack <trip-type>   -- packing list only (beach, city, hiking, business, ...)
/travel-plan checklist <trip>   -- show an existing trip's logistics checklist with deadlines
```

## Part 1: Trip capture (interview)

One question at a time, plain language, 6–10 questions:

1. **Where and when** — destination(s), dates, and how flexible each is.
2. **The party** — who's going: ages, mobility, energy levels, veto-holders.
3. **Budget shape** — not a number interrogation: "splurge on food, save on rooms?" tiers.
4. **Pace** — packed days or slow mornings? (Be honest back: a packed plan with toddlers is a
   fiction — reflect the stated party in the pace you accept.)
5. **Interests** — what would make this trip *theirs*: food, hiking, museums, doing nothing.
6. **Constraints** — dietary, accessibility, dates that must hold, things already booked.
7. **Trip type** — beach / city / hiking / business / family-visit / mixed (selects the packing
   list and itinerary defaults).

Play the capture back and confirm before researching anything.

## Part 2: Run-time research discipline (the core rule)

This skill ships with **zero destination facts**. Everything factual is fetched at planning time
via web search, and every fact lands in the plan with its source URL beside it. Two tiers:

- **MUST-VERIFY tier** — visa/entry rules, health-entry requirements, safety advisories:
  researched **only from official government sources** (the traveler's own government's travel
  advisory service and the destination's official immigration/health authority). These are never
  asserted as settled: each carries its source URL, its retrieved date, and a `MUST-VERIFY before
  booking` flag. If an official source can't be reached at planning time, the plan says exactly
  that — a gap, never a guess.
- **Standard tier** — seasons/weather patterns, opening days, typical prices, transit options:
  researched from the best available source, URL noted, phrased as "as of <retrieved date>" so a
  reader knows the shelf life.

If any fact can't be sourced at run time, it enters the plan as an open question with a research
note — the skill never fills gaps from memory.

## Part 3: Itinerary skeleton

Day-by-day structure, built to survive contact with reality:

- **One anchor per day** — the single booked-or-important thing; everything else is flex.
- **Flex slots** around the anchor, chosen from the interests list, each with a bad-weather or
  low-energy alternate.
- **Travel days are travel days** — arrival/departure days get logistics and one gentle flex
  item, never an anchor.
- **Downtime honesty** — the stated pace and party set a hard ceiling on scheduled items; the
  skeleton shows empty slots as *planned* rest, not failure.

Synthetic example (fictional destination; bracketed items show where run-time research attaches —
this is the structure, not real-world advice):

```markdown
# Trip: Port Salina — Oct 12–16 (party: 2 adults, pace: slow mornings)

Entry: [MUST-VERIFY before booking — entry rules for your nationality:
  <official government source URL> — retrieved 2026-07-06]
Season note: [typical mid-October conditions: <source URL> — as of 2026-07-06]

## Day 1 (Sun) — travel day
- Arrive ~15:00; transit to old town [options + fares: <source URL>]
- Flex: harbor walk (alternate if raining: covered market)

## Day 2 (Mon) — ANCHOR: boat tour (book ahead ~2 weeks)
  [operating days + booking lead time: <source URL> — as of 2026-07-06]
- Morning: slow start (stated pace)
- Flex: fish market lunch · alternate: maritime museum
  [museum closed Mondays? verify: <source URL>]

## Day 3 (Tue) — open day (planned rest — party voted for one empty day)
```

## Part 4: Packing lists

Reusable per **trip type**, stored in `<trips-path>/packing/`, party-aware (each traveler gets a
tailored copy — kids' lists differ from adults'), and improved by a two-question debrief after
each trip: *"What did you pack and not use? What did you buy there?"* Unused items get a strike
count; three strikes → moved to an "only if..." section. Bought-there items join the list.

```markdown
# Packing: city trip (v4)
## Everyone
- [ ] Passport/ID — see trip plan's MUST-VERIFY entry row first
- [ ] Meds + copies of prescriptions
- [ ] One dressy outfit ("bought there 2025-11" — added v3)
## Only if... (struck out 3+ trips running)
- Travel iron (0 uses / 4 trips)
```

## Part 5: Logistics checklist

Everything bookable or expirable, ordered by **lead time**, longest first — documents and
entry requirements at the top (their lead times come from the MUST-VERIFY research, not from
assumptions), then bookings that sell out, then week-before and day-before items. Each row:
what, deadline, status, and the plan's source URL where one applies. On request, recurring
pre-trip dates (e.g. "check in online," "arrange pet care") register with `/weekly-review`'s
sweep so they surface in the weekly ritual.

## Failure Modes

- **Confident staleness.** Any destination fact stated without a fetched source is a defect —
  including in this file's own examples, which is why the example destination is fictional. If
  research fails, the plan shows the gap.
- **MUST-VERIFY erosion.** Summarizing entry rules from a blog or aggregator because the official
  source was slow to load defeats the tier's purpose. Official source or an explicit gap — no
  third option.
- **The over-stuffed itinerary.** Three anchors a day reads impressive and ruins the trip. One
  anchor is a rule, not a suggestion; push back using the user's own stated pace.
- **Packing list rot.** A list that never loses items grows until nobody reads it. The
  post-trip debrief and strike counts are the pruning mechanism — run them.
- **Scope creep into booking.** "Want me to book it?" is outside this skill by design — nothing
  outward-facing. The plan hands the user links and deadlines; the user does the booking.

## Important Notes

- **The skill's knowledge is structure, not geography.** It knows how to plan a trip; it looks up
  the world fresh every time. This is what keeps it safe to run years from now.
- **Re-research on reuse:** reopening a plan after weeks re-fetches the MUST-VERIFY tier —
  retrieved dates in the plan make staleness visible.
- **This is a captured life-loop, graduated:** trip planning is the worked example of a
  recurring personal decision turned into a stored, rerunnable structure — and a natural future
  `/power-chains` chain (capture → research → itinerary → checklist).
- **Model routing:** itinerary drafting and run-time research → sonnet (packing-list assembly
  and checklist date-ordering are haiku-safe); escalate to opus when the trip has ≥3 hard
  constraints in tension or multi-city routing optimization; the escalation is announced, not
  silent.
- Pairs with: `/life-loop` (this skill is a graduated loop; new recurring travel sub-decisions
  route there first), `/weekly-review` (pre-trip deadlines register with its sweep),
  `/notetaker` (trip notes and debrief answers file to its buckets).
