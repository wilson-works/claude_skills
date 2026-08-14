---
name: life-loop
description: "Captures a recurring personal mental loop — what's for dinner, packing, gifts, workouts, weekend plans, chores — through a zero-jargon interview, converts it into a stored personal loop file with your actual decision rules, and proves the file works via a test-drive gate before calling it captured. From then on the loop runs cheaply on demand, learns from your corrections, and can graduate into a full skill. Invoke with /life-loop [run|list|promote] [name]."
---

# Life Loop

## Purpose

Everyone carries recurring head-loops: the same small decision re-made from scratch every week —
what's for dinner, what to pack, what to get whom, which chores this weekend. Each rerun burns the
same attention answering the same questions, because the personal rules that decide it ("never
repeat a dinner within two weeks," "always aisle-order the list") live only in your head.

This skill captures one loop through a short plain-language interview, writes those rules into a
personal loop file, and — the part that makes it real — refuses to call the loop captured until a
fresh, cheaper model given *only the file* produces output you accept. After that, running the
loop costs a fraction of re-deciding it, and every correction you make teaches the file.

**Boundary:** `life-loop` captures a *personal decision loop* and generates its runnable file
directly. If the interview reveals apps, handoffs, and other people — that's a multi-tool work
process, out of scope here; map it separately. If mapping a workflow reveals it is really one
person's recurring decision — it belongs here.

## Configure for your project

Before using this skill, set this placeholder (the operator sets it once; the person being
interviewed never sees a file path):

- `<loops-path>`: Directory for stored loop files and their run logs (e.g. a `loops/` bucket
  beside your notes). One file per loop, `<loops-path>/<loop-name>.loop.md`; run log appended
  inside the file.

## Invocation

```
/life-loop                    -- capture a new loop: interview → generate → test-drive gate
/life-loop run <name>         -- execute a stored loop; log corrections back into it
/life-loop list               -- stored loops, cadence, last run, correction count
/life-loop promote <name>     -- graduate a proven loop (see Promote mode)
```

## Mode 1: Capture (interview)

Rules of engagement — the interviewee may be a complete beginner:

- **One question at a time.** Never a questionnaire wall.
- **Zero jargon.** "I'll remember your rules so you don't have to re-explain" — never "preference
  profile," "loop file," or any path on screen.
- **Follow the pain.** Friction words ("every single week," "I always forget") get the next
  question.
- **Concrete beats general.** "Walk me through last week's version of this" beats "how do you
  usually do it."
- **8–12 questions**, then stop. Cover:

1. **The loop** — which recurring decision are we capturing? If unsure: "What small decision do
   you re-make most often and enjoy least?"
2. **Trigger & cadence** — what makes it come up, and how often?
3. **Last real occurrence** — walk through it start to finish; this becomes the worked example.
4. **Inputs** — what do you check or need in front of you? (calendar, fridge, budget, weather)
5. **Your actual rules** — the decisions inside the decision. Push past "it depends": "Last
   Tuesday you picked pasta — why pasta and not the chicken?" Extract every rule stated or
   revealed ("weeknights ≤30 min," "no repeat within 2 weeks").
6. **Hard constraints vs. preferences** — which rules are unbreakable, which are tie-breakers?
7. **What good output looks like** — the exact shape they want handed back, confirmed against
   the last-occurrence example.

Close with a playback in the user's own words and get an explicit yes before generating. The
confirmed playback is the contract.

## Mode 2: Generate (the loop file)

Write `<loops-path>/<loop-name>.loop.md`. Everything a RUN needs must be *in the file* — a run
step that says "use your judgment" is not done; go back and capture the rule. Format, shown as a
complete synthetic example (`/meal-prep` is this loop's graduated big sibling — full grocery and
batch-cook planning; this loop only decides the week's dinners):

```markdown
# loop: dinner-week  (v3)
cadence: weekly — Sunday afternoon, before the grocery run
inputs: this week's calendar; what's already in the fridge (user pastes or lists)

## Rules (hard)
- No dinner repeats within 14 days (check the run log below)
- Tuesday is always ≤20 minutes (evening class)
- Friday is takeout — never plan a cooked dinner for Friday

## Rules (preferences / tie-breakers)
- Use up listed perishables early in the week
- At most two pasta dinners per week ("too much pasta" — corrected 2026-06-15)
- One new-to-us recipe per week is welcome, never two

## RUN steps
1. Ask for the two inputs if not provided. [haiku-safe]
2. Draft Mon–Thu + Sat–Sun dinners (Friday = takeout) satisfying every hard rule;
   check each pick against the last 14 days in the run log. [sonnet]
3. Apply tie-breakers; note which preference decided any close call. [sonnet]
4. Output in the format below; append the picks + date to the run log. [haiku-safe]

## Output format
| Day | Dinner | Why this pick |
(one row per day, "why" only where a rule or tie-breaker decided it)

## Run log
- 2026-06-29: tacos, stir-fry, sheet-pan gnocchi, leftovers, takeout, curry, roast
- correction 2026-06-15: "too much pasta" → added ≤2-pasta preference (v2→v3)
```

## Mode 3: Test-drive gate (hard step — the loop is not captured without it)

1. Spawn a **fresh Sonnet-class agent** whose entire context is the loop file plus sample inputs
   from the interview's last-real-occurrence. No conversation memory, no interview transcript.
2. Show the user its output: "This is what future runs will look like. Would you accept this?"
3. **Accepted** → the loop is captured; record the test-drive pass in the file.
4. **Rejected** → every gap is a missing or wrong rule, not a model failure. Ask what's wrong,
   fold the answer into the rules, regenerate, re-test. A loop that fails the test-drive twice
   after rule fixes escalates: regenerate the file at a higher-effort model pass, then re-test on
   Sonnet again — the file must still *run* cheaply.

This gate is the whole trick: judgment is spent once at capture, then stored; runs are mechanical.

## Mode 4: Run

`/life-loop run dinner-week`: load the file, execute the RUN steps exactly, append to the run
log. When the user corrects an output ("too much pasta"), convert the correction into a rule or
tie-breaker, bump the loop's version, and note the correction with its date — the file learns, so
the same correction never needs making twice. Prune run-log entries older than the longest
look-back any rule uses (correction lines stay — they are the loop's version history).

## Mode 5: Promote

Two graduation paths, both stated to the user when the pattern appears:

- **Proven universal** — the loop would serve people who aren't you (three+ months of clean runs,
  rules with no personal secrets): graduate the loop file into a full skill in your pack.
- **Actually a work process** — runs keep touching multiple tools, other people, or handoffs:
  map it separately as a full workflow; that is outside this skill's scope.

## Failure Modes

- **Solutioning during the interview.** Proposing dinner plans in question 4 is this skill's
  version of the classic interview failure. Capture first; the playback confirmation is the gate.
- **Rules that live in the model, not the file.** If a test-drive pass depends on anything the
  interviewer remembers but didn't write down, the next run regresses. The fresh-agent test-drive
  exists precisely to catch this.
- **Correction amnesia.** Fixing an output in chat without folding the correction into the file
  means re-correcting forever. Every accepted correction becomes a versioned rule.
- **Loop sprawl.** Ten captured loops nobody runs. `list` shows last-run dates; a loop unused for
  months is a candidate to archive or merge, not to keep polishing.
- **Scope creep into siblings.** Groceries and batch-cooking belong to `/meal-prep`; trip
  logistics to `/travel-plan`; reflection to `/journal`. A loop drifting into a sibling's scope
  should reference it, not reimplement it.

## Important Notes

- **The interviewee never manages storage.** Paths, files, and versions are the skill's business;
  the user only ever sees questions, playbacks, and outputs.
- **Judgment up front, mechanics forever after.** The capture interview and file generation are
  the expensive, careful steps; they exist so that every future run is cheap and reproducible.
- **The run log is part of the ruleset** — "no repeats within 14 days" is only checkable because
  runs are logged in the file.
- **Model routing:** capture interview, loop generation, and regeneration after failed
  test-drives → opus-tier; test-drive execution and all `run` invocations → sonnet, with steps
  marked `[haiku-safe]` in the loop file runnable on haiku; escalate (regenerate at higher
  effort) when a loop fails its test-drive twice after rule fixes.
- Pairs with: `/notetaker` (loop storage follows its one-file-per-thing conventions),
  `/meal-prep` and `/travel-plan` (graduated worked examples of captured loops), `/journal`
  (reflection sibling — feelings are not rules).
