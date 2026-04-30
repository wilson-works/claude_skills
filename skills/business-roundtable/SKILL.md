---
name: business-roundtable
description: "Send a business note to the LLM council for review on whether to do it, how to implement it, and how to present it, finalize with the user, then lock it into the BMC brain. Invoke with /business-roundtable [NOTE-ID | free text]."
---

# Business Roundtable Skill

## Purpose

Take a business note (marketing idea, pricing move, positioning shift, partnership, campaign, customer-segment hypothesis) and run it through a structured review loop:

1. **Council review** — hand it to `/llm-council` for independent multi-advisor analysis.
2. **Implementation plan** — synthesize how to actually execute it (software + content + ops).
3. **Presentation plan** — how it should be pitched to users, investors, or the team.
4. **User finalization** — present everything to the user for final edits and sign-off.
5. **Lock into BMC brain** — write the finalized version back to the note, mark status `locked`, and file any derived dev work into `dev-followups.md` and the project's real backlog.

## Configure for your project

Set these placeholders (same defaults as `/business-notes` and `/business-pass`):

| Placeholder | What it means | Example |
|-------------|---------------|---------|
| `<bmc-brain-path>` | Where the BMC brain lives on disk | `./business-plan/bmc-brain/` |
| `<note-id-prefix>` | Prefix used for note IDs | `NOTE` |
| `<backlog-skill>` | Name of your real work-backlog skill | `/backlog` |

If you do not have a backlog skill yet, just append derived dev work to `<bmc-brain-path>/dev-followups.md` and skip the backlog step.

## Invocation

```
/business-roundtable <note-id-prefix>-0001    Review an existing note from the BMC brain
/business-roundtable [free text]              Create a new note first, then review it
/business-roundtable --last                   Review the most recently added note
```

## Default council lineup

When invoking `/llm-council`, request these five generic business advisors. They are role-shaped, not persona-shaped, so they apply to any business:

1. **Marketing Strategist** — positioning, messaging, channel fit, brand consistency.
2. **Pricing Analyst** — revenue impact, willingness-to-pay, packaging, plan ladder, unit economics.
3. **Customer Discovery Lead** — segment fit, ICP signal, jobs-to-be-done, evidence vs. assumption.
4. **Competitor Watcher** — what comparable products do, defensibility, market timing, table-stakes vs. differentiation.
5. **Operations Lead** — execution feasibility, sequencing, team capacity, risk, what breaks first.

If the note is heavily tilted toward one block, you can swap one advisor for a domain specialist (e.g. a Compliance / Trust advisor for security-sensitive moves), but keep the panel at five.

## Flow

### Step 1 — Load or create the note
- If given a note ID, read it from `<bmc-brain-path>`.
- If given free text, call `/business-notes add` first, then continue with the new note ID.

### Step 2 — Run the council
Invoke `/llm-council` with a prompt that includes:
- The raw note body
- A current BMC snapshot (from `/business-notes export` or by reading `<bmc-brain-path>` directly), so advisors see the full business context
- The five-advisor lineup above
- Three explicit questions the council must answer:
  1. **Should we do it?** (strategic fit, risk, expected impact, evidence quality)
  2. **How do we implement it?** (software changes, content, ops, sequencing, timeline)
  3. **How do we present it?** (audience, hook, channels, tone — respect the user's copy rules)

Save the council transcript path into the note.

### Step 3 — Synthesize
Produce three sections in the conversation:
- **Verdict** — go / no-go / modify, with the reasoning the council agreed on, plus any dissents worth flagging.
- **Implementation plan** — concrete steps, split into `dev`, `content`, `ops`. Each dev step should be phrased so it can be dropped straight into a real backlog as a single work order.
- **Presentation plan** — the pitch, the copy angles, the channels, and the first experiment to run (with a measurable signal).

### Step 4 — Finalize with the user
Ask the user (briefly) for edits, cuts, or a green light. Accept inline changes. Do not proceed to lock-in until the user explicitly approves.

### Step 5 — Lock into the BMC brain
Once approved:
- Append a `## Council Review — {date}` section to the note with verdict, implementation plan, presentation plan, and the council transcript link.
- Set the note status to `locked`.
- For each dev follow-up, append to `<bmc-brain-path>/dev-followups.md` AND call the project's `<backlog-skill>` so it enters the real work queue (skip if no backlog skill is configured).
- For each research question that came out of the discussion, append to `<bmc-brain-path>/open-questions.md`.
- If the note reshapes a BMC block (e.g. new revenue stream, new channel, new segment), update that block's file with a one-line summary pointing to the note ID.

## Rules

- Always use `/llm-council` for the review step. Never fake a council.
- Respect the user's copy rules in any generated copy or pitch (default: no emojis, no em dashes — adjust to match the user's stated style guide).
- Do not skip user finalization. The user must sign off before anything is locked or pushed to the backlog.
- Keep the summary terse. Lead with the verdict, then plans. The user reads the diff.

## Example

```
/business-roundtable <note-id-prefix>-0014
```

Loads a "raise pro tier from $15 to $19 and add annual-only $12 plan" pricing note, runs the council on whether to ship it, how to update billing + checkout + landing copy, and how to roll it out (grandfather existing customers, change-log post, in-app banner). Presents the synthesis to the user, accepts edits, then locks the note and files the dev work into the real backlog.

## Relationship to other skills

- `/business-notes` — captures notes; this skill reviews and locks them. Same note schema, same brain location.
- `/business-pass` — proactive counterpart to `/business-notes`; high-stakes notes from a pass are good candidates for a roundtable.
- `/llm-council` — the underlying multi-advisor engine this skill drives.
