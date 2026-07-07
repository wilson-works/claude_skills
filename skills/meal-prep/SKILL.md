---
name: meal-prep
description: "Profile-driven weekly meal planning: a one-time interview captures your household size, user-supplied dietary rules, budget shape, cooking time and skill, equipment, and dislikes into a stored profile; each weekly run then produces a rotating meal plan honoring your rules, a consolidated grocery list ordered by store section, and a batch-cook schedule whose storage guidance carries sourced US food-safety figures. Corrections fold back into the profile. Strictly no nutrition or diet advice — dietary rules are inputs you supply; designing or changing a diet routes to a professional. Invoke with /meal-prep [setup|correct]."
---

# Meal Prep

## Purpose

Weekly meal planning is a canonical recurring head-loop: the same constraint-satisfaction puzzle
(who's home, what's in the fridge, what did we just eat, what's on sale) re-solved from scratch
every Sunday. This skill captures the constraints once, then makes the weekly run cheap: a plan
that honors your rules and rotates for variety, a grocery list consolidated and ordered for one
pass through the store, and a batch-cook schedule that handles the food-safety part correctly —
the one class of factual claims this skill carries, sourced from US federal guidance and stated
exactly, because getting a storage number wrong is a safety defect, not a style choice.

**Scope guard (hard):** this skill plans logistics around dietary rules *you supply*. It gives
zero nutrition or diet advice — no calorie or macro targets, no portion sizing for goals, no
"healthy" claims, no medical-diet design. This skill covers food-*safety* handling (storage,
reheating, batch-cook cooling), not nutrition or diet planning; for calorie, macro, allergy, or
medical-diet advice, consult a registered dietitian or your healthcare provider.

## Configure for your project

Before using this skill, set this placeholder:

- `<meal-profile-path>`: Where the profile and weekly plans live (e.g. `household/meals/`). The
  profile is one file; each weekly run appends a dated plan (which doubles as the rotation log).

## Invocation

```
/meal-prep           -- weekly run: plan + grocery list + batch-cook schedule
/meal-prep setup     -- one-time profile interview (or revisit it)
/meal-prep correct   -- fold feedback into the profile ("less pasta", "Tuesdays got busy")
```

## Setup: the profile (one-time, judgment-heavy)

One question at a time, plain language: household size and who eats what · dietary rules **as
you state them** (recorded verbatim as constraints, never evaluated or supplemented) · budget
shape · weeknight cooking time and honest skill level · equipment (slow cooker? freezer space?)
· hard dislikes · staple preferences · how much repetition is welcome. Stored as the profile
file; every future run reads it. Requests during setup to *design* a diet ("what should I eat to
lose weight?") get the scope-guard routing, warmly and without a lecture.

```markdown
# meal profile  (v6 — corrected 2026-06-28: "less pasta" → variety rule)
household: 2 adults + 1 kid (age 7, no spicy — retired 2026-06-28, now mild-ok)
dietary rules (user-supplied, verbatim): no shellfish · one vegetarian dinner/week
budget: normal weeks flexible; tight weeks flagged in the run
weeknights: ≤30 min (Tuesday ≤20 — evening class) · weekend: one real cook
equipment: slow cooker, full freezer drawer · skill: comfortable, no deep-frying
dislikes (hard): mushrooms (adult 2), fish at home
variety: no repeat within 2 weeks · ≤1 pasta dinner/week (v6)
staples always stocked: rice, eggs, frozen peas, tortillas
```

## The weekly run

1. **Inputs:** the profile + this week's calendar quirks + what's already in the fridge/pantry
   (listed or pasted).
2. **Plan:** one dinner slot per day (plus lunches if profiled), honoring every hard rule,
   rotating against the plan log for variety, and routing leftovers deliberately — a batch-cook
   dinner's surplus becomes a named lunch, not a fridge mystery.
3. **Grocery list:** consolidated across the week's recipes, minus what's on hand, grouped by
   store section. The section ordering is a shopping convenience, not a standard — no such
   standard exists. The one safety-adjacent ordering note, from FDA/FoodSafety.gov guidance:
   pick up perishables (meat, dairy, frozen) last, and refrigerate within 2 hours of purchase
   (1 hour if it's above 90 °F out).
4. **Batch-cook schedule:** what to prep when, with a storage plan per item using the safety
   table below.

```
WEEK OF 2026-07-06 — plan for profile v6 (2 adults + 1 kid, no shellfish, ≤30 min weeknights)
Mon  sheet-pan chicken + roasted veg      (new; batch: double the chicken)
Tue  leftover chicken → wraps             (≤20 min rule: Tuesday class)
Wed  black-bean chili (slow cooker AM)    (batch: freeze half in shallow containers)
...
GROCERY (minus on-hand)  Produce: ... · Dry goods: ... · Dairy: ... · Meat/frozen: LAST
BATCH-COOK Sunday: chili base + chicken · cool in shallow containers, fridge within 2 h
STORAGE: chicken (cooked) fridge 3–4 days → Tue/Wed lunches · chili half → freezer, label date
```

## The food-safety table (the skill's only factual claims — sourced, stated exactly)

US federal guidance (USDA FSIS · FoodSafety.gov · FDA), retrieved 2026-07-06:

| Rule | Figure | Source |
|------|--------|--------|
| Danger zone | 40–140 °F — bacteria can double in as little as 20 minutes | USDA FSIS |
| Two-hour rule | Perishables out of refrigeration max **2 hours** — **1 hour** if above 90 °F | USDA FSIS / FoodSafety.gov |
| Fridge / freezer targets | **40 °F (4 °C)** or below / **0 °F (−18 °C)** or below | FDA / FoodSafety.gov |
| Cooked leftovers | Fridge **3–4 days**; freezer 2–6 months for quality (safe indefinitely at 0 °F) | FoodSafety.gov / USDA FSIS |
| Reheating leftovers | To internal **165 °F**, checked with a food thermometer | USDA FSIS / FoodSafety.gov |
| Cooling large batches | Divide into **shallow containers**; refrigerate within 2 hours — hot food may go straight in | USDA FSIS |
| Thawing (only three safe ways) | Fridge (slow, safest) · cold water changed every 30 min (cook immediately) · microwave (cook immediately) — never on the counter | USDA FSIS |
| Refreezing | Fridge-thawed food may be refrozen uncooked (quality loss); water- or microwave-thawed must be **cooked first**; cooked food may be refrozen | USDA FSIS |

Per-item raw-ingredient windows (ground meat 1–2 days fridge, whole cuts 3–5 days, raw poultry
1–2 days, etc.) come from the FoodSafety.gov Cold Food Storage Chart — the skill consults it for
items outside this table rather than recalling figures.

**Jurisdiction caveat (stated whenever the table is used outside the US):** these figures follow
**US** guidance. National authorities differ materially — for example, the UK Food Standards
Agency (food.gov.uk) recommends eating cooked leftovers within **2 days** and a fridge of
**0–5 °C**. Outside the US, check your national food-safety authority.

## Correction loop (`/meal-prep correct`)

Feedback becomes profile, so no correction is ever made twice: "too much pasta" → a variety
rule; "Tuesdays got busy" → a weeknight time cap; "kid now eats spicy" → a constraint retired.
Each correction bumps the profile version with a dated note. If corrections accumulate into a
contradiction, that's the escalation below — not a silent judgment call.

## Failure Modes

- **Nutrition creep.** "Since you're planning meals anyway, how many calories should…" — the
  scope guard is absolute, however natural the segue. Route out, every time, including when the
  user's own dietary rules seem inconsistent (record what they said; suggest a professional if
  they ask whether the rules are *right*).
- **Safety figures from memory.** Any storage number not in the table above gets looked up from
  the official chart at run time, never recalled. A wrong day-count is a defect class of its
  own.
- **Rotation amnesia.** A plan that ignores the log serves chili three Wednesdays running. The
  plan log is an input to every run, same as the profile.
- **Fictional pantry.** Consolidating a grocery list against an assumed inventory buys
  duplicates; if the user doesn't supply what's on hand, the list says "assumes empty pantry."
- **Dressed-up conveniences.** Store-section ordering and pantry formats are claim-free UX —
  presenting them as standards manufactures authority that doesn't exist.

## Important Notes

- **Three content classes, never mixed:** sourced safety facts (the table — exact, cited);
  claim-free structure (plans, lists, schedules — convenience, no authority claimed); and
  routed-out territory (all nutrition/diet advice). Every sentence the skill produces belongs
  to exactly one.
- **Dietary rules are verbatim inputs:** the skill honors "no shellfish" without asking why and
  never adds rules the user didn't state ("you might also want to cut…" is nutrition creep).
- **This is a graduated life-loop:** the profile is the captured judgment; the weekly run is
  the cheap mechanical loop; `/life-loop`'s dinner-week example is this skill's little sibling.
- **Model routing:** profile capture and unsatisfiable-constraint resolution → opus; the weekly
  run → sonnet (grocery consolidation and list formatting are haiku-safe); named escalation:
  the constraint set becomes unsatisfiable — dietary rules × budget × time conflict — which is
  a re-interview with trade-offs made explicit, announced as such, never silently resolved.
- Pairs with: `/life-loop` (the pattern this skill graduates from; new food-adjacent
  micro-loops start there), `/weekly-review` (batch-cook day and recurring shop can register
  with its sweep), `/travel-plan` (the other graduated life-loop — trip weeks suspend the meal
  plan), `/notetaker` (recipe keepers and household notes file there).
