---
name: meeting-digest
description: "Turn raw meeting material — pasted notes, a transcript file, a voice-memo transcription, or your from-memory recap right after a call — into a structured digest: TL;DR, decisions, action items, open questions, follow-ups. Meeting-type presets shift the emphasis; series mode keeps a rolling file for recurring meetings and carries unresolved action items forward. Invoke with /meeting-digest [source] [flags]."
---

# Meeting Digest Skill

## Purpose

Meetings produce two things: decisions and commitments. Both evaporate within 48 hours unless someone writes them down in a findable shape. This skill is that someone — feed it whatever survived the meeting (a transcript, scribbled notes, a voice memo transcription, or just your memory five minutes after hanging up) and it produces the same structured digest every time.

The digest is deliberately boring and consistent: six sections, always in the same order, so future-you (or `/weekly-review`, which reads these files) can scan a month of meetings in two minutes. The skill extracts — it never invents. Anything the source material doesn't actually say goes to Open questions, not into a fabricated decision.

## Configure for your project

Before using this skill, set this placeholder:

- `<meetings-path>`: Absolute path to your meeting digests directory (e.g. `C:\Users\you\Documents\notes\meetings\` or `~/notes/meetings/`). If you run `/notetaker`, point this at its `meetings/` bucket so digests land in your notes system automatically.

## Invocation

```
/meeting-digest [pasted material]        Digest pasted notes, a transcript, or a voice-memo transcription
/meeting-digest [path\to\file]           Digest a transcript/notes file from disk
/meeting-digest recap                    From-memory capture: short interview right after a call
/meeting-digest --type [preset]          Apply a meeting-type preset (client, 1on1, standup, interview, board)
/meeting-digest --series [name]          Recurring-meeting mode: rolling file, carries open items forward
/meeting-digest --file                   Write the digest to <meetings-path> instead of inline only
```

Flags combine: `/meeting-digest transcript.txt --type client --series acme-weekly --file`.

## Input Sources

| Source | How it arrives | Handling |
|--------|----------------|----------|
| Pasted notes | Text in the message | Digest as-is; bullets and fragments are fine |
| Transcript file | A path (`.txt`, `.md`, `.vtt`, `.srt`) | Read the file; strip timestamps; watch for speaker-label issues (see Failure Modes) |
| Voice-memo transcription | Pasted auto-transcription, often punctuation-poor | Digest as-is; flag garbled passages rather than guessing at them |
| From-memory recap | `/meeting-digest recap` | Short interview — **max 5 questions, one at a time**: who was there, what was decided, who owes what, what's unresolved, when's the next touch. Stop early once the digest is drawable. |

Digest from what you're given. Never ask the user to clean up, reformat, or re-export the material first — a messy transcript that gets digested beats a clean one that never arrives.

## Digest Structure

Every digest has these six sections, in this order:

1. **TL;DR** — three sentences maximum. What the meeting was, what changed, what happens next.
2. **Decisions made** — only things the material shows were actually decided. "We're going with X" is a decision; "we could do X" is not (that's an idea — Notable context, or Open questions if it needs an answer).
3. **Action items** — table: `Owner | Task | Due`. Owner and Due only when the source states them. Unattributed tasks get owner `(unassigned)`; undated tasks get due `—`.
4. **Open questions** — unresolved items, ambiguous ownership, decisions that were discussed but not closed. Each with a one-line note on why it's open.
5. **Notable context / quotes** — background worth keeping: constraints mentioned, sentiment, a quote that captures where someone stands. Quote verbatim or not at all.
6. **Next meeting / follow-up** — scheduled next touch if stated, otherwise the implied follow-up ("send proposal by Friday, then reconvene").

### The extraction hard rule

**Never invent owners, dates, or decisions that are not in the source material.** This is the one rule that outranks completeness:

- Task with no stated owner → owner `(unassigned)`, and add an Open question ("Who owns the vendor comparison?").
- "Sometime next week" → due `next week (no date given)`, never a fabricated `2026-07-10`.
- Something discussed enthusiastically but not closed → Open questions or Notable context, never Decisions.
- When the material is ambiguous about who said what, attribute to `(unclear)` rather than guessing a name.

A digest with six `(unassigned)` rows is honest and useful. A digest with six guessed names is a liability that misassigns work.

## Meeting-Type Presets

Presets don't change the six sections — they change what you dig hardest for and how you weight the TL;DR. Auto-detect the type from the material when no `--type` is given (say which preset you applied); fall back to the general digest when unsure.

| Preset | Emphasis |
|--------|----------|
| `client` | Commitments made **to** the client and **by** the client, each explicitly labeled in Action items ("we owe" / "they owe"). Scope changes and pricing mentions always make Decisions or Open questions. |
| `1on1` | Feedback given and received, growth items, morale signals. Action items are usually few; Notable context carries the weight. |
| `standup` | Blockers first. TL;DR leads with what's blocked and who's waiting. Skip Notable context if there's nothing notable — standups rarely have quotes worth keeping. |
| `interview` | Candidate signal: strengths, concerns, specific evidence for each. Decisions = advance/hold/pass if stated. Action items = who completes scorecards, who schedules next round. |
| `board` | Asks made of the board/advisors and their responses, follow-ups promised, concerns raised. Every ask gets a row in Action items even if the answer was "let me think about it." |

## Workflow

1. **Identify the source.** Pasted text, file path, or `recap` interview. Read the file if a path was given.
2. **Apply the preset.** Use `--type` if given; otherwise detect from content and state your pick ("Reading this as a client call — say otherwise if not.").
3. **Extract under the hard rule.** Build the six sections. Sort action items: dated items first (soonest due), then undated, then `(unassigned)`.
4. **Render inline** (default). Keep it to one screen where the material allows.
5. **Offer routing once** (see Routing Integration below) if `/backlog` or `/notetaker` are in use.
6. **Write the file** if `--file` or `--series` was given: `<meetings-path>/YYYY-MM-DD-<slug>.md` (slug from the meeting topic, ≤40 chars). Series mode writes to the rolling file instead — see Series Mode.

### Output example

```markdown
# Digest: Vendor selection sync — 2026-07-02
Type: general · Source: pasted notes · Attendees: Alex, Jordan, Sam

## TL;DR
Narrowed the CRM shortlist from five vendors to two (Northwind, Fabrikam) on
cost and API fit. Jordan runs a two-week trial of both starting Monday.
Budget ceiling confirmed at $400/mo; final pick targeted for the July 20 sync.

## Decisions made
- Shortlist is Northwind and Fabrikam; the other three are out (cost, no API).
- Budget ceiling: $400/mo, confirmed by Alex.

## Action items
| Owner        | Task                                      | Due                     |
|--------------|-------------------------------------------|-------------------------|
| Jordan       | Set up trial accounts for both vendors    | 2026-07-06              |
| Sam          | Draft migration checklist from current CRM| next week (no date given)|
| (unassigned) | Ask legal about the data-processing terms | —                       |

## Open questions
- Who owns the legal review of data-processing terms? Discussed, no owner named.
- Do we need SSO at this tier? Sam raised it; nobody answered.

## Notable context / quotes
- Alex: "If migration takes more than a weekend, we're not doing it this quarter."
- Current contract renews 2026-08-15 — soft deadline for the whole decision.

## Next meeting / follow-up
Next sync 2026-07-20 — trial results and final pick.
```

## Series Mode (`--series <name>`)

For recurring meetings (weekly ops sync, biweekly client check-in), series mode keeps one rolling file per series at `<meetings-path>/series-<name>.md` instead of scattered one-offs.

1. **Read the rolling file first.** The newest digest sits at the top; older ones below.
2. **Carry forward**: every action item from the previous digest that isn't marked done gets re-listed in the new digest under a `Carried forward` subheading of Action items — with its original date, so age is visible.
3. **Flag overdue**: carried items whose due date has passed get an `OVERDUE` marker. State it plainly, once — no lecture.
4. **Mark resolutions**: if the new material shows a carried item was completed ("Jordan finished the trials"), mark it `done 2026-07-16` in the previous digest's table rather than silently dropping it.
5. Prepend the new digest to the top of the rolling file.

```markdown
### Carried forward (from 2026-07-02)
| Owner        | Task                                       | Due            | Status  |
|--------------|--------------------------------------------|----------------|---------|
| Sam          | Draft migration checklist                  | 2026-07-09     | OVERDUE |
| (unassigned) | Ask legal about the data-processing terms  | —              | open    |
```

An item carried forward three digests in a row is a signal, not a nag — note it once ("third carry — worth deciding if this is real") and move on.

## Routing Integration

If the user runs `/backlog` or `/notetaker`, the digest's contents have better homes than a markdown file alone:

- **Action items** that are the *user's own tasks* → offer `/backlog add` for each (their words become the Details field; the digest file is the Context).
- **Decisions** → offer `/notetaker add ... to decisions`.
- **People context** (preferences, sentiment, "Alex hates surprise scope changes") → offer `/notetaker add ... to people`.
- The digest itself belongs in the notetaker `meetings/` bucket — pointing `<meetings-path>` there makes this automatic.

**Offer once, at the end of the digest, as a single batched question** ("File 2 action items to /backlog and the budget decision to /notetaker? y / pick / skip"). Never re-ask in the same session, and never route without confirmation. If neither skill is in use, skip the offer entirely — don't advertise.

## Failure Modes

| Failure | What it looks like | Guard |
|---------|--------------------|-------|
| Hallucinated attribution | A task gets an owner or due date the source never stated | The hard rule: `(unassigned)` and `—` exist precisely so you never fill gaps with plausible fiction |
| Speaker-label confusion | Transcript tools mislabel speakers ("Speaker 2" becomes three different people) | When labels look unreliable, attribute to `(unclear)` and add one Open question about ownership rather than propagating wrong names into commitments |
| Demanding cleanup | Refusing to digest a messy wall-of-text transcript until the user reformats it | Digest from the material given, always. Flag gaps in Open questions instead of bouncing the input back |
| Brainstorm-as-decision | "We could try usage-based pricing" lands under Decisions | Decisions need decision language ("we're going with", "agreed", "final"). Everything softer is context or an open question |
| Digest bloat | A 90-minute transcript becomes a 4-page digest | The TL;DR cap (3 sentences) and one-screen target force selection. If it doesn't change a decision, an action, or a relationship, it doesn't make the digest |

## Important Notes

- **Extraction, not creation.** Every line in Decisions and Action items must be traceable to the source material. When in doubt, demote to Open questions — that section exists to hold doubt honestly.
- **Consistency is the feature.** Same six sections, same order, every time. Resist the urge to restructure for an "interesting" meeting; scanability across months is worth more.
- **Recap mode degrades gracefully.** Memory-based digests are thinner — that's fine. A 60% digest captured in 3 minutes beats a 100% digest that never happens. Note `Source: from-memory recap` in the header so future readers calibrate trust.
- **Verbatim or nothing for quotes.** A paraphrase presented as a quote is a small lie that compounds when the digest gets shared.
- **Dates are absolute.** Write `2026-07-02`, never "today" — the reader is a future session with no context.
- Pairs with: `/backlog` (action items out), `/notetaker` (decisions and people-context out; hosts `<meetings-path>`), `/weekly-review` (reads the week's digests).
