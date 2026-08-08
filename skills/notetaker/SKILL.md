---
name: notetaker
description: "Persistent personal notes system — like the backlog, but for your work and thinking instead of work orders. Captures notes and thoughts into topic buckets that grow with you over time, so any future Claude session can recall them. Invoke with /notetaker [command] [args]."
---

# Notetaker Skill

## Purpose

Give chat-first users the thing they're missing: **a memory that outlives the session.** Many people run everything in one-off Claude conversations and lose context every time the tab closes. Notetaker is the fix — a plain-markdown notes system on disk, organized into buckets that fit *your* work, that any future session can read.

It is deliberately shaped like the `/backlog` skill: same command feel, same "capture fast, organize automatically" discipline. Backlog holds **work orders** (things to do); notetaker holds **knowledge** (things to remember — decisions, ideas, people, meetings, reference facts, half-formed thoughts).

The system grows with the user. It starts with a few buckets from a 2-minute setup interview and proposes new buckets as recurring themes show up. You never have to design a filing system up front — that's the skill's job.

## Configure for your project

Before using this skill, set this placeholder:

- `<your-notes-path>`: Absolute path to your notes directory (e.g. `C:\Users\you\Documents\notes\` or `~/notes/`). Pick somewhere synced/backed up if you can (OneDrive, Dropbox, a git repo). `/notetaker setup` will create it.

## Invocation

```
/notetaker                        Overview: buckets, note counts, 5 most recent notes
/notetaker setup                  First-run interview — creates the folder + starter buckets
/notetaker add [text]             Capture a note; auto-routed to the right bucket
/notetaker add [text] to [bucket] Capture into a specific bucket
/notetaker find [query]           Search all notes; returns matches with bucket + date
/notetaker recall [topic]         Synthesized answer from your notes ("what did we decide about pricing?")
/notetaker buckets                List buckets with descriptions and counts
/notetaker bucket new [name]      Create a bucket (asks for a one-line routing description)
/notetaker bucket merge [a] [b]   Merge bucket a into bucket b
/notetaker review                 Weekly-ish tidy: triage inbox, propose new buckets, surface stale threads
/notetaker digest [period]        Summary of everything captured this week/month
```

## Folder Layout

```
<your-notes-path>/
├── NOTES.md                      Index: bucket table + routing hints. Read this FIRST, always.
├── inbox.md                      Quick captures that didn't match a bucket yet
├── decisions/
│   ├── _bucket.md                What belongs here + routing keywords
│   └── 2026-07-02-pricing-tiers.md
├── ideas/
├── people/
├── meetings/
├── reference/
└── projects/
    └── <project-name>/           Buckets can nest one level for active projects
```

Every note is its own file: `YYYY-MM-DD-<slug>.md`. One thought per file — small files are easy to find, easy to link, and never collide.

### NOTES.md (the index)

```markdown
# Notes Index
Last reviewed: 2026-07-02

| Bucket | What goes here | Notes |
|--------|----------------|-------|
| decisions/ | Choices made and why — anything you'd hate to re-litigate | 14 |
| ideas/ | Raw ideas, someday/maybe, shower thoughts | 22 |
| people/ | One file per person — context, preferences, history | 8 |
| meetings/ | Meeting notes, calls, 1:1s | 31 |
| reference/ | Facts, how-tos, links, account details (non-secret) | 12 |
| projects/website-redesign/ | Active project — scoped notes | 9 |

Inbox: 3 unfiled
```

### Note format

```markdown
# Pricing tiers decision
- **Date**: 2026-07-02
- **Bucket**: decisions
- **Tags**: pricing, saas
- **Source**: call with Dana

We're going three tiers ($29/$79/$199), annual-only on the top tier.
Rejected usage-based pricing because support load doesn't scale with usage.
Revisit if enterprise deals exceed 3/quarter.

Related: [[2026-06-20-pricing-research]]
```

Required: title, Date, Bucket. Everything else optional. `[[filename]]` links connect related notes — write them even if the target doesn't exist yet; it marks a note worth taking.

### _bucket.md (per-bucket routing card)

```markdown
# decisions
One note per decision: what was chosen, what was rejected, and why.
Route here: "we decided", "going with", "chose X over Y", trade-off talk.
Do NOT route here: open questions (→ inbox), ideas not yet chosen (→ ideas).
```

## Workflow by Command

### `/notetaker setup` (first run)

1. Ask where notes should live if `<your-notes-path>` isn't set. Suggest a synced location.
2. Run a short interview — **max 4 questions, one at a time**:
   - "What kind of work will these notes mostly cover?" (job, business, personal, mix)
   - "What do you most often lose track of?" (decisions, ideas, people-context, meeting outcomes, how-tos)
   - "Any active projects that deserve their own space?"
   - "Anything you explicitly DON'T want stored here?" (record exclusions in NOTES.md)
3. Propose 4–6 starter buckets based on answers. Sensible default set: `decisions`, `ideas`, `people`, `meetings`, `reference`. Confirm before creating.
4. Create the folder tree, `NOTES.md`, `inbox.md`, and a `_bucket.md` per bucket.
5. Tell the user the two commands that matter day-to-day: `/notetaker add` and `/notetaker find`.

### `/notetaker add [text]`

1. Read `NOTES.md` for the bucket table and routing hints.
2. Route: match the note against each bucket's `_bucket.md` routing card. Confident match → file it. No confident match → append to `inbox.md` (never ask a filing question at capture time; capture must be frictionless).
3. Draft the note file: title (≤60 chars), Date, Bucket, Tags (1–3, lowercase), body. Keep the user's words — tighten, don't rewrite their thinking.
4. Add `[[links]]` to obviously related existing notes (check the bucket folder for matching slugs).
5. Confirm in one line: `Filed to decisions/ as 2026-07-02-pricing-tiers.md` or `Inboxed — /notetaker review will sort it.`

### `/notetaker find [query]` / `/notetaker recall [topic]`

- **find**: Grep across `<your-notes-path>` (filenames, tags, body). Return a compact hit list: `bucket/file — date — one-line context`. No hit → say so and offer the nearest bucket to browse.
- **recall**: find, then read the top matches and answer the question directly, citing which notes it came from (`per decisions/2026-07-02-pricing-tiers.md`). If notes conflict, surface the conflict with dates — newest is usually, not always, right.

### `/notetaker review`

The growth mechanic. Run weekly-ish, or whenever inbox > 10.

1. **Triage inbox**: propose a bucket for each unfiled note. User confirms in batch ("all yes", or "2 to ideas, rest yes").
2. **Propose new buckets**: if ≥3 notes across the system share a theme no bucket covers, propose one (with a draft `_bucket.md`). This is how the system grows — buckets are earned by evidence, never invented speculatively.
3. **Propose merges**: any bucket with <3 notes and no additions in 60 days gets a merge suggestion.
4. **Surface stale threads**: notes ending in open questions or "revisit if/when" older than 30 days — list them, ask keep/close/act.
5. Update `NOTES.md` (counts, `Last reviewed` date).

### `/notetaker digest [week|month]`

Read everything captured in the period; produce a one-page summary grouped by bucket: decisions made, ideas captured, people-context added, open threads. End with "the three notes most worth re-reading."

## Inline Capture Mode

Like backlog's inline triage: when the user says something in conversation that is clearly worth keeping — a decision, a preference, an idea, a fact they'll need again — offer to capture it:

> "That's a decision worth keeping. Want me to note it? (`/notetaker add`)"

Offer, don't auto-file. Never nag — at most one offer per conversation topic.

## Session-Start Habit

For chat-first users this is the whole payoff: **at the start of any session that touches ongoing work, read `NOTES.md` and skim relevant buckets before answering.** Recommend users put a line in their `CLAUDE.md` (or Project instructions):

```
My notes live at <your-notes-path>. Read NOTES.md and any relevant bucket
before working on anything ongoing. Capture new decisions via /notetaker.
```

## Boundaries — what notetaker is NOT

| Looks like a note, but isn't | Route instead |
|------------------------------|---------------|
| A task, bug, or to-do ("fix the login flow") | `/backlog add` — work orders live there |
| A secret (password, API key, SSN) | Refuse to store; point to a password manager |
| A whole document (contract, spec, report) | Store the file elsewhere; note its **location + one-line summary** in `reference/` |
| Meeting **transcript** (raw, long) | Summarize into a meetings/ note; don't paste walls of text |

If both a task and a decision are in one utterance, split them: decision → notetaker, task → backlog.

## Important Notes

- **Read before write.** Always read `NOTES.md` before filing; always read a note before editing it.
- **Capture beats filing.** A note in inbox.md is worth ten thoughts lost to a closed tab. Never block a capture on a filing question.
- **Never rewrite the user's thinking.** Tighten grammar, keep their framing. These are their notes, not your prose.
- **One thought per file.** If an add contains two unrelated thoughts, file two notes.
- **Buckets are earned.** New buckets come from `/notetaker review` evidence (≥3 orphan notes on a theme), not from speculation at setup.
- **Dates are absolute.** Write `2026-07-02`, never "today" or "last Tuesday" — the reader is a future session with no context.
- **Privacy**: everything stays on the user's disk. If asked to store something that looks like a credential, decline and say why.
- Plays well with: `/backlog` (tasks out), `/meeting-digest` (meeting notes in), `/weekly-review` (reads digests), `/handoff` (session context out).
