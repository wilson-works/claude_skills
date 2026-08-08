---
name: weekly-review
description: "A guided 15–20 minute weekly review ritual — GTD-flavored but tool-agnostic — that closes the loop on the week and produces next week's focus. Gathers from your notes, backlog, and meeting digests when present, asks you for the rest, walks wins/loose-ends/lessons, forces a Top 3 for next week, and writes a one-page review file with a running streak. Invoke with /weekly-review [flags]."
---

# Weekly Review Skill

## Purpose

The weekly review is the highest-leverage 20 minutes in a knowledge worker's week, and almost nobody does it because it has no forcing function. This skill is the forcing function: a guided ritual with four timeboxed phases that always ends in a written one-page file. Gather what happened, name what worked, close (or consciously park) what didn't, and pick exactly three things that matter next week.

Two design commitments do the work. **The Top 3 is a forced ranking of exactly three items** — the discipline of cutting to three *is* the product; a Top 7 is just a to-do list wearing a costume. And **the review isn't done until it's written** — an unwritten review evaporates by Tuesday, while a written one compounds: next week's Gather phase starts by reading it.

GTD-flavored, tool-agnostic: it reads from `/notetaker`, `/backlog`, and `/meeting-digest` when those are in use, and works fine from a plain conversation when they aren't.

## Configure for your project

Before using this skill, set these placeholders:

- `<reviews-path>`: Absolute path to your reviews directory (e.g. `C:\Users\you\Documents\notes\reviews\` or `~/notes/reviews/`). If you run `/notetaker`, a `reviews/` bucket there is the natural home.
- `<meetings-path>` *(optional)*: Your `/meeting-digest` output directory, if you use that skill — Gather reads this week's digests from it.

## Invocation

```
/weekly-review              Full ritual: Gather → Review → Plan → Write (~15–20 min)
/weekly-review --quick      5-minute version: wins, Top 3, write, done
/weekly-review last         Show the most recent review file and current streak (no ritual)
```

## The Ritual

Four phases, strictly in order, each timeboxed. Announce the phase as you enter it. Timeboxes are enforced by *you*: when a phase is full, summarize and move on — depth goes in next week's review, not this one's overtime.

### Phase 1: Gather (~5 min)

Collect the raw material, automated sources first. **Say what you're reading as you read it** — the user should know exactly what the review is built from:

1. `/notetaker` in use → run its `digest week` view and check inbox count. ("Reading your notes digest — 6 notes this week, 2 unfiled.")
2. `/backlog` in use → run `stats`; note items completed this week and the oldest open item.
3. `<meetings-path>` configured → read this week's digest files (`YYYY-MM-DD-*.md` within the last 7 days); pull open action items and decisions.
4. Last week's review file → read it; its Top 3 and "Not doing" list are this week's scorecard.

Then ask the user for what no file can hold — **one question at a time, max 4 total**, skipping any already answered by the files:

- "What were the calendar highlights — anything big that happened that isn't in the notes?"
- "Any win from this week you're proud of?"
- "What's nagging at you — the thing you keep remembering at odd hours?"
- "Anything you dropped that someone is waiting on?"

No sources and a quiet user? Proceed anyway — a review built from four answers is still a review.

### Phase 2: Review (~7 min)

Walk three passes, in order:

1. **Wins — name 3.** Exactly three, even in a rough week ("kept the streak alive" counts). Wins from the files count too — surface completed backlog items the user forgot they shipped.
2. **Loose ends.** Open action items from meeting digests, stale notes ending in open questions, unanswered messages the user remembers. List them; for each, tag it `carry` (goes to next week's plan), `park` (goes to Not doing), or `drop` (consciously released). Don't resolve them now — this is triage, not work.
3. **Lessons.** One question, honestly answered: "What took longer than expected this week, and why?" One or two lessons max, stated as a mechanism ("estimates ignore review latency"), not a resolution ("be faster").

Score last week's Top 3 while you're here: done / partial / untouched. No commentary on untouched beyond one line — the data speaks for itself over weeks.

### Phase 3: Plan (~5 min)

1. **Draft candidates** from loose ends tagged `carry`, the nagging item, and anything the user names.
2. **Force the ranking.** The user picks a Top 3 — exactly three. If they offer five, make them cut two: "Which two hurt least to push a week?" If they offer two, that's fine — a Top 2 is allowed; a Top 4 is not.
3. **Build the "Not doing" list.** Everything explicitly deferred, written down so it stops nagging. This list is a feature, not an afterthought — naming what you're *not* doing is what makes the Top 3 believable.
4. Each Top 3 item gets one line on *what done looks like* by next review.

### Phase 4: Write (~2 min)

Write the file — no confirmation step, the ritual ends in a file by definition:

1. Compute the ISO week and filename: `<reviews-path>/YYYY-'W'ww.md` (e.g. `2026-W27.md`).
2. Compute the streak: read the most recent existing review file. If it's the immediately preceding ISO week, streak = its streak + 1; otherwise streak = 1. No gap commentary either way.
3. Write the template below, filled in. Confirm with one line: `Written to 2026-W27.md — streak: 4 weeks.`

## Review File Template

```markdown
# Weekly Review — 2026-W27 (Jun 29 – Jul 5)
- **Date written**: 2026-07-03
- **Streak**: 4 weeks
- **Mode**: full            <!-- full | quick -->
- **Sources**: notetaker digest, backlog stats, 2 meeting digests, last week's review

## Last week's Top 3 — scorecard
1. Ship the pricing page update — **done**
2. Clear the proposal backlog (3 open) — **partial** (2 of 3 sent)
3. Fix the invoice template bug — **untouched**

## Wins (3)
1. Pricing page shipped a day early
2. Landed the Northwind renewal on the first call
3. Inbox zero twice — new personal record

## Loose ends
- [carry] Third proposal (waiting on scope answer from client)
- [park]  CRM migration research — parked until vendor trial ends
- [drop]  Conference talk submission — deadline passed, releasing it

## Lessons
- Proposals stall on *my* open questions, not client silence — ask scope
  questions in the first call, not by email afterward.

## Next week's Top 3
1. Send the third proposal — done = in the client's inbox by Wednesday
2. Fix the invoice template bug — done = next invoice renders correctly
3. Vendor trial checkpoint — done = trial notes written, lean recorded

## Not doing (deferred on purpose)
- CRM migration work (until trial verdict)
- Website copy refresh (revisit 2026-W29)
- New lead-magnet idea — noted, not started

## Notes
Energy dipped Thursday; two of three untouched-item weeks were Thursday-heavy.
Watch it.
```

The template is fixed. Same sections, same order, every week — the value of month twelve's archive depends on week one's format.

## Quick Mode (`--quick`)

Five minutes, three moves, same file:

1. **Wins** — name 3 (one question).
2. **Top 3** — forced ranking (one question, cut to three).
3. **Write** — same filename and template with `Mode: quick`; unused sections get a single `— (quick week)` line rather than being deleted, so the file shape stays constant.

Quick weeks extend the streak — a quick review is a review. Offer `--quick` proactively when the user sounds rushed; never guilt them into the full ritual.

## Failure Modes

| Failure | What it looks like | Guard |
|---------|--------------------|-------|
| Therapy-session drift | Phase 2 becomes an hour of processing one bad meeting | Timebox and move on. Acknowledge in one sentence, capture a note ("worth a longer conversation — not now"), continue. The review is a loop-closer, not a couch |
| Top 3 becomes Top 9 | "These are all critical" | Hold the line: exactly three. Everything else goes to Not doing — visibly kept, deliberately deferred. If nothing can be cut, that inability *is* the week's lesson |
| Skipping the write | "I've got it in my head, we're good" | The write is Phase 4 of 4, not an optional export. An unwritten review evaporates; write the file, then end |
| Streak guilt | "You broke your 11-week streak!" | Never. Streaks reset without ceremony: new streak = 1, zero commentary on the gap. The streak rewards showing up; it must never punish coming back |
| Gather rabbit-hole | Re-reading a month of notes "for context" | Gather reads this week plus last week's review only. Older material is `/notetaker recall` territory, on demand |

## Important Notes

- **The write step is non-negotiable.** Every path through this skill — full, quick, even a review that gets interrupted — ends with the file written from whatever was captured. A partial file beats no file.
- **Exactly three.** The forced ranking is the entire point; defend it politely and absolutely. The "Not doing" list is where the pressure goes.
- **One question at a time, max 4 in Gather.** This is a ritual, not an intake form. If the automated sources answered a question, don't ask it again.
- **Read before write.** Always read the most recent review before writing the new one — the streak, scorecard, and carried items depend on it.
- **Tone: colleague, not coach.** No pep talks, no productivity-guru voice, no judgment on untouched items or broken streaks. The user showed up; that's the ritual working.
- **Dates are absolute.** ISO week in the filename, real dates in the header — the reader is a future session with no context.
- Pairs with: `/notetaker` (Gather reads its digest; hosts `<reviews-path>`), `/backlog` (stats in, deferred items can be filed out), `/meeting-digest` (the week's digests feed Gather), `/sop-writer` (a recurring loose end may deserve a standing procedure).
