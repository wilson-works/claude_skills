---
name: business-notes
description: "Capture business and strategy notes and auto-file them into a Business Model Canvas brain. Builds a living business plan in parallel with the product. Invoke with /business-notes [command] [args]."
---

# Business Notes Skill

## Purpose

Capture strategic, marketing, pricing, partnership, customer, and operational notes as they surface during day-to-day work, and file them into a Business Model Canvas (BMC) brain so the business plan grows alongside the product. When invoked without args, it summarizes what the brain says about: (1) the business plan, (2) software or operations work that falls out of notes, (3) deep-research questions that need external answers.

## Configure for your project

Before first use, set these placeholders to match your environment. Either edit this file directly, or keep the defaults and create the matching directories.

| Placeholder | What it means | Example |
|-------------|---------------|---------|
| `<bmc-brain-path>` | Where the BMC brain lives on disk | `./business-plan/bmc-brain/` |
| `<note-id-prefix>` | Prefix used for note IDs | `NOTE` (yields `NOTE-0001`) |
| `<project-root>` | Root of the product or codebase | `./` |

Defaults assumed in the rest of this document: `<bmc-brain-path>` = `./business-plan/bmc-brain/`, `<note-id-prefix>` = `NOTE`.

## Brain Location

```
<bmc-brain-path>
```

Files (one per BMC block, plus extras):

| File | BMC Block |
|------|-----------|
| `value-propositions.md` | Value Propositions |
| `customer-segments.md` | Customer Segments |
| `channels.md` | Channels |
| `customer-relationships.md` | Customer Relationships |
| `revenue-streams.md` | Revenue Streams |
| `key-resources.md` | Key Resources |
| `key-activities.md` | Key Activities |
| `key-partners.md` | Key Partners |
| `cost-structure.md` | Cost Structure |
| `marketing-campaigns.md` | (extra) campaign ideas + experiments |
| `open-questions.md` | (extra) deep research needed |
| `dev-followups.md` | (extra) software or operations work triggered by notes |
| `inbox.md` | unfiled notes awaiting triage |

Each note entry:

```markdown
## <note-id-prefix>-0023 — Short title
Date: 2026-04-29
Status: raw | reviewed | council-approved | locked
Block: value-propositions
Tags: marketing, virality
Source: conversation | user | council

Body of the note. Keep it short and actionable. Include any verbatim
user quotes that capture the spirit of the idea.

**Dev follow-ups:** (optional) bullets of software or operations work implied
**Research needed:** (optional) bullets of unknowns
```

## Invocation

```
/business-notes                         Summary: what goes to business plan / dev / research
/business-notes add [text]              Auto-file a new note into the right BMC block
/business-notes add --block=[block] [text]   Force a specific block
/business-notes list                    List all notes grouped by block
/business-notes list [block]            List notes for one block
/business-notes show <note-id-prefix>-0023   Print a single note
/business-notes edit <note-id-prefix>-0023   Update a note's body/status/tags
/business-notes plan                    Render a draft business plan from current BMC state
/business-notes export                  Emit a one-page BMC snapshot (markdown table)
```

## Triage rules for `add`

When the user adds a note without specifying a block, decide based on keywords:

- "pricing", "plan", "tier", "LTV", "ARPU", "subscription" -> `revenue-streams`
- "campaign", "viral", "meme", "launch", "ads", "PR", "content" -> `marketing-campaigns` AND link Channels
- "customer", "persona", "target user", "ICP", "segment" -> `customer-segments`
- "community", "support", "retention loop", "onboarding" -> `customer-relationships`
- "distribution", "social", "search", "directory", "marketplace" -> `channels`
- "feature", "product" tied to value -> `value-propositions`
- "hire", "co-founder", "team", "infra", "tooling" -> `key-resources` or `key-activities`
- "vendor", "integration", "reseller", "partner" -> `key-partners`
- "cost", "burn", "bill", "margin", "unit economics" -> `cost-structure`

If ambiguous, drop into `inbox.md` and flag it in the next summary.

Every note also gets scanned for:
- **Dev follow-ups** -> mirrored into `dev-followups.md` with a pointer to `<note-id-prefix>-xxxx` (these are candidates to promote to a real backlog later)
- **Research needed** -> mirrored into `open-questions.md`

## Default summary (`/business-notes` with no args)

Produce three sections:

1. **Business plan** — latest state of each BMC block, 1-3 bullets each, drawn from the most recent and highest-status notes.
2. **Software / ops queue** — open items from `dev-followups.md` not yet promoted. Recommend promoting concrete items into your real work backlog.
3. **Deep research queue** — open items from `open-questions.md`. Suggest which warrant a `/llm-council` run or external web research.

## Examples of good notes

- "Hypothesis: small marketing agencies are the right beachhead — they have 5-15 seats, feel pain from ad-hoc spreadsheets, and influence other agencies." -> `customer-segments`
- "Move pro tier from $15 to $19 and add an annual-only plan at $12/seat to anchor higher." -> `revenue-streams`
- "Partnership idea: integrate with the top three industry associations to get directory placement." -> `key-partners`
- "Launch viral moment: post-signup share card with the user's first-week stats — push to LinkedIn." -> `marketing-campaigns`

## Relationship to other skills

- `/business-roundtable <note-id-prefix>-xxxx` -> sends a note to the council, then writes the council verdict back into the note and promotes status to `council-approved`.
- `/business-pass` -> the proactive counterpart to this skill. It scans the codebase or interviews the user to fill BMC gaps, writing into the same brain and using the same note schema described here.
- `/llm-council` -> used under the hood by `/business-roundtable`.

## Bootstrap

If `<bmc-brain-path>` does not exist, create it and seed every file listed above with a short H1 header and an empty notes section. Do this automatically on first invocation. Note IDs continue from the highest existing ID across all files.
