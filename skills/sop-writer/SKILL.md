---
name: sop-writer
description: "Turn any process into a Standard Operating Procedure that someone else could execute cold — via a gap-hunting interview, a confirmed workflow map you already have, or revision of an existing SOP after a process change. Enforces the cold-reader test (every step says where it happens and what confirms success) and can emit a print-friendly HTML version. Invoke with /sop-writer [process] [--html]."
---

# SOP Writer Skill

## Purpose

An SOP is only real if a competent stranger can run the process from the document alone — no tribal knowledge, no "ask Sam if it looks weird." This skill produces that document. It interviews for the gaps people always leave out (the trigger, the exact order, the access needed, what "done" looks like, what goes wrong), writes the SOP in a fixed structure, then runs a mandatory self-review pass that rewrites every vague step before the user ever sees a draft.

The deliverable is a markdown SOP file (optionally plus a print-friendly HTML version) with a numbered procedure, an escalation table, and a compressed quick-checklist for operators who already know the process.

## Configure for your project

Before using this skill, set this placeholder:

- `<sops-path>`: Absolute path to your SOP directory (e.g. `C:\Users\you\Documents\sops\` or `~/ops/sops/`). Files are saved as `<sops-path>/<slug>.md`. If the user runs `/notetaker`, a `reference/` bucket note pointing at each SOP is a good habit — but the SOP itself lives here, as its own file.

## Invocation

```
/sop-writer [process]             Interview mode — describe the process, skill asks the gap questions
/sop-writer from-map [slug|path]  Map handoff — build from a confirmed workflow map file, minimal interview
/sop-writer revise [path]         Revision mode — read an existing SOP, update it after a process change
/sop-writer --html                Flag, combinable with any mode: also emit a print-friendly HTML version
```

## The Three Input Modes

### Mode A: Interview (`/sop-writer [process]`)

The user describes the process conversationally. Your job is to hunt gaps, not transcribe. **One question at a time**, and only questions the description hasn't already answered. Coverage checklist:

1. **Trigger** — what starts this process? (schedule, incoming email, a request, a threshold being crossed). "Whenever needed" is not a trigger; push for the observable event.
2. **Exact order** — "walk me through the last time you actually did this, step by step." The last real occurrence, not the idealized version. If they say "then I update the system," ask which system, which screen, which fields.
3. **Tools + access** — every app, site, spreadsheet, and login touched. For each: what account/permission level does the operator need? Access gaps are the #1 reason a handed-off SOP stalls on day one.
4. **Done condition** — what does the operator see, receive, or verify that means the process is complete? "It's done when it's done" gets rewritten into an observable check.
5. **What goes wrong** — "what's broken the last three times?" and "what would a new person definitely mess up?" These seed the failure & escalation table; an SOP with an empty failure table is a first draft, not an SOP.
6. **Audience** — who will run this? (new hire, experienced peer, contractor, future-you). This calibrates altitude — see Failure Modes.

Stop interviewing when you can write every procedure step with a location and a confirmation. Don't complete the checklist for its own sake.

### Mode B: Map handoff (`/sop-writer from-map [slug|path]`)

Input is a **confirmed workflow map** the user already has — a written walkthrough of the process (trigger, numbered steps, tools, pain points) that they have verified is accurate. The map already covers trigger, steps, tools, and pain points — do not re-interview for those. Ask only what the map doesn't carry:

- Access/permission level per tool
- The done condition, if the map's "Success" line is aspirational rather than observable
- Failure history for the escalation table
- Audience

Read the proposal doc, extract the confirmed map verbatim as your skeleton, and note the source in the revision log (`Derived from workflow map: <slug>`).

### Mode C: Revision (`/sop-writer revise [path]`)

1. Read the existing SOP file in full.
2. Ask what changed (or accept it in the args: `/sop-writer revise sops/invoice-run.md "we switched from Word to the billing portal"`).
3. Apply the change **everywhere it lands**: procedure steps, prerequisites (new tool = new access line), failure table (old failure modes may vanish, new ones appear), and the quick checklist. A revision that only touches the procedure is almost always incomplete.
4. Append a revision-log entry, bump the version, reset the review-by date.
5. Re-run the cold-reader pass (below) on every step you touched.

## The SOP Document

Saved to `<sops-path>/<slug>.md`. This is the full template — every SOP has all eight parts, in this order:

```markdown
# SOP: Monthly invoice run
- **Version**: 1.2
- **Last updated**: 2026-07-02
- **Owner**: Office manager
- **Review by**: 2026-10-02
- **Audience**: New hire, no prior billing experience

## Purpose
Bill all active clients on the 1st business day of each month so payments land
before the 15th. Late invoicing is the single biggest cause of cash-flow gaps.

## Scope & roles
- **Runs this**: Office manager (backup: bookkeeper)
- **Escalate to**: Owner — for any invoice over the client's usual amount by >20%,
  or any client disputing a charge
- **Out of scope**: Payment chasing (separate process), new-client rate setting

## Prerequisites
- [ ] Billing portal login (Editor role or higher) — request from owner
- [ ] Access to the shared `Clients/` folder on the company drive
- [ ] Current rate sheet (`Clients/rates-2026.xlsx`) open
- [ ] The prior month's hours export downloaded (see step 1)

## The Procedure
1. **Export last month's hours.** In the time tracker (app > Reports > Monthly),
   set the range to the full prior month and click Export CSV.
   ✅ Expected: a CSV downloads with one row per client; row count matches the
   active-client count on the rate sheet.
2. **Open the billing portal invoice screen.** Portal > Invoices > New batch.
   [SCREENSHOT: the New batch screen with the month selector highlighted]
   ✅ Expected: batch screen shows the current month pre-selected.
3. **Create each invoice from the CSV.** For each client row: enter hours,
   confirm the rate auto-fills from the client record.
   - **If** the rate does not auto-fill → the client record is missing a rate.
     Stop, set it from the rate sheet, then continue.
   - **If** hours are zero for an active client → do NOT invoice; flag the
     client name to the owner the same day.
   ✅ Expected: invoice total = hours × rate sheet rate, to the cent.
4. **Send the batch.** Review screen > Send all.
   ✅ Expected: portal shows "Sent" status on every invoice; you receive the
   BCC copy of each email within 10 minutes.

## Failure & escalation
| Symptom | Likely cause | Action | Who to call |
|---------|-------------|--------|-------------|
| CSV export is empty | Date range set to current month | Re-run with prior month | — (self-serve) |
| Rate won't auto-fill | New client record incomplete | Set rate from rate sheet | Owner, if rate sheet blank too |
| "Sent" but no BCC copy | Portal email settings changed | Check portal > Settings > Email | Portal support |
| Client disputes amount | Hours logged to wrong client | Do not argue; pull the CSV row | Owner, same day |

## Quick checklist (experienced operators)
- [ ] Export prior-month CSV; row count = active clients
- [ ] New batch in portal; rates auto-fill for all
- [ ] Zero-hour actives flagged, not invoiced
- [ ] Send all; confirm BCC copies arrive

## Revision log
| Version | Date | Change | By |
|---------|------|--------|-----|
| 1.2 | 2026-07-02 | Switched from Word invoices to billing portal | office mgr |
| 1.1 | 2026-03-10 | Added zero-hours flag rule after March miss | office mgr |
| 1.0 | 2026-01-05 | Initial version from workflow map | office mgr |
```

Structural rules:

- **Every procedure step = action + expected result.** The ✅ line is not optional. A step without a confirmation is a guess.
- **Decision points are explicit if/then branches**, indented under the step where the decision arises. Never bury a branch in prose ("usually you'd just...").
- **Screenshot placeholders** — `[SCREENSHOT: what to capture]` — go wherever a visual would disambiguate (a specific button among many, a settings screen, a "correct" vs "wrong" state). Describe *what to capture*, so the user can grab the shots later.
- **The quick checklist is the whole SOP compressed** — one checkbox per procedure step (branches folded in), for operators who've run it before. It must never contain a step the full procedure lacks.

## Quality Bar: the Cold-Reader Pass (mandatory)

Before presenting any draft, re-read every procedure step as a stranger with the prerequisites met and nothing else. Each step must answer:

1. **WHERE does this happen?** Which app, which screen, which URL pattern, which folder. "Update the system" fails; "Portal > Invoices > New batch" passes.
2. **WHAT confirms success?** An observable outcome the operator can check before moving on.

Any step that fails either test gets rewritten — during this pass, not flagged for later. If you can't rewrite it because you don't know the answer, that's a missed interview question: go ask it now. Typical rewrites:

| Vague (fails) | Cold-reader ready (passes) |
|---------------|---------------------------|
| Update the system | In the billing portal (Invoices > New batch), enter hours per client |
| Make sure it looks right | ✅ Invoice total = hours × rate-sheet rate, to the cent |
| Send it out | Click Send all; ✅ every invoice shows "Sent" and a BCC copy arrives |
| Check with the team if unsure | If total deviates >20% from last month → escalate to owner before sending |

## `--html` Output

When the flag is present, also write `<sops-path>/<slug>.html` alongside the markdown:

- Fully self-contained: inline CSS, no external fonts, scripts, or images.
- Print-friendly: sensible margins, page-break before major sections, checkboxes rendered as real boxes (`☐`), the failure table kept on one page where possible.
- Header block (version/date/owner/review-by) styled as a compact banner so a printed copy is self-identifying.
- The markdown file remains the source of truth; regenerate the HTML on every revision, never hand-edit it.

## Failure Modes

- **Wrong altitude.** The two ways to ruin an SOP: expert shorthand ("reconcile as usual") that a new hire can't follow, and painful over-detail ("move the mouse to the File menu") that insults an experienced operator and buries the signal. Calibrate to the **stated audience** from the interview — and the quick-checklist section exists precisely so one document serves both readers. If the audience is "anyone," write for the newest plausible operator.
- **Documenting the ideal process instead of the real one.** People describe the process as designed; the SOP must capture the process as run — including the workaround where step 3's export is broken so everyone uses the dashboard instead. Interview questions like "walk me through the *last* time" and "what do you actually do when X fails?" exist to surface this. An SOP that documents a fiction will be ignored within a week, and its reader will conclude all your SOPs are fiction.
- **SOP rot.** Processes drift; documents don't. Defenses built into the template: the revision log (drift becomes visible), the **Review by** date in the header (default: +3 months from last update), and version numbers. When you finish an SOP, suggest a refresh trigger: a line item in the user's `/weekly-review` if they run one ("any SOP past its review-by date?"), or a recurring calendar reminder. When `revise` mode opens a file past its review-by date, say so before doing anything else.
- **The unverifiable step.** If no observable confirmation exists for a step ("wait for the batch to process"), give the operator a proxy: a time bound, a status page to watch, or an explicit "if nothing after 15 minutes → escalation table row 3." Never leave a step where the operator can't tell whether they're waiting or stuck.

## Important Notes

- **Read before write.** In `revise` mode, always read the full existing SOP before editing; never regenerate from memory of what it probably says.
- **One process per SOP.** If the interview surfaces a second process (e.g. payment chasing hiding inside invoicing), scope it out explicitly and offer a second run.
- **Keep the user's vocabulary.** If they call it "the portal," the SOP calls it "the portal" (with the URL on first mention). Renaming things they know creates friction for exactly the reader who needs the document least.
- **Never invent failure rows.** The escalation table comes from what has actually gone wrong or what the user confirms is plausible — a made-up symptom column erodes trust in the real rows.
- **Generic examples only** in anything you draft from scratch; real names and rates come from the user, not from you.
- Pairs with: `/weekly-review` (the review-by refresh trigger), `/notetaker` (a reference note pointing at each SOP), `/meeting-digest` (process walkthroughs captured in meetings feed `from-map`).
