---
name: business-pass
description: Run a structured pass to grow the Business Model Canvas brain. Two modes - scan (autonomous codebase or app sweep that extracts new BMC evidence) and interview (short interactive Q&A to fill BMC gaps). Both modes write directly into the BMC brain via the same note schema as /business-notes. Invoke with /business-pass [scan|interview] [block?].
---

# Business Pass Skill

## Purpose

`/business-notes` is for capturing notes as they surface in conversation. `/business-pass` is for **proactively going hunting** — either by scanning the codebase or running app for new BMC evidence, or by interviewing the user to fill gaps in the business plan. Both modes write into the same brain and use the same note schema as `/business-notes`.

## Configure for your project

Set these placeholders to match your environment (same defaults as `/business-notes`):

| Placeholder | What it means | Example |
|-------------|---------------|---------|
| `<bmc-brain-path>` | Where the BMC brain lives on disk | `./business-plan/bmc-brain/` |
| `<note-id-prefix>` | Prefix used for note IDs | `NOTE` |
| `<project-root>` | Root of the product or codebase | `./` |
| `<src-path>` | Frontend source folder | `./src/` or `./apps/web/src/` |
| `<api-path>` | Backend / API source folder | `./api/` or `./functions/src/` |
| `<shared-path>` | Shared types / constants | `./packages/shared/` |
| `<config-path>` | App config (segments, tiers, plans) | `./config/` |
| `<billing-path>` | Billing / pricing code | `./api/billing/` |
| `<marketing-path>` | Marketing site / landing pages | `./apps/marketing/` or `./marketing/` |

The brain location is `<bmc-brain-path>`. NEVER duplicate an existing note — update in place. Note IDs continue from the highest existing id.

## Invocation

```
/business-pass                          Default: ask which mode to run
/business-pass scan                     Autonomous codebase + brain diff pass
/business-pass scan [block]             Scan focused on one BMC block
/business-pass interview                5-question interview, dynamic targeting of weakest blocks
/business-pass interview [block]        Interview focused on one BMC block
/business-pass interview --quick        3 questions only
/business-pass interview --deep         10 questions, branching follow-ups
```

## Mode 1: scan

Goal: find new BMC evidence the brain doesn't have yet, or correct stale entries.

Steps:
1. **Read the brain index.** Load every file in `<bmc-brain-path>` to know the current state. Track the highest note ID.
2. **Pick a focus.** If a block was passed, scan only for that block. Otherwise, identify the 2-3 weakest blocks (shortest notes, oldest dates, most "missing" gaps in dev-followups).
3. **Spawn an Explore agent** (subagent_type: Explore, thoroughness: medium) with a precise prompt: "Find evidence of {block} that is NOT already captured in {existing-note-summary}. Look at {specific dirs based on block}. Report concise file paths + 1-line descriptions."
   - For value-propositions / key-activities: scan `<src-path>`, core feature folders, top-level component directories
   - For customer-segments: scan `<config-path>`, anything that defines personas / segments / verticals / industry templates
   - For revenue-streams: scan `<billing-path>`, plan / tier definitions in `<shared-path>`, any in-app purchase code
   - For customer-relationships: scan onboarding flows, support / help components, social or community features
   - For channels: scan `<marketing-path>`, public landing pages, signup / referral / invite code
   - For key-partners / cost-structure: scan `package.json` / dependency manifests, infra config (`.env`, deploy configs), third-party SDK integrations
4. **Diff against the brain.** For each finding, decide: (a) new note, (b) update existing note, (c) already covered — skip.
5. **Write the changes.** Append/update notes with `Source: codebase-scan`, status `reviewed`, today's date, and tag `codebase-scan`.
6. **Mirror gaps.** Any new "missing" findings get bullets in `dev-followups.md`. Any unknowns get bullets in `open-questions.md`.
7. **Report.** Print a short summary: notes added, notes updated, blocks still under-covered.

Optional: if Chrome DevTools MCP is connected and the dev server is running, also do a UI pass — screenshot the relevant section and confirm the feature actually renders, not just exists in code. Skip silently if MCP isn't connected.

## Mode 2: interview

Goal: extract knowledge that only lives in the user's head.

Steps:
1. **Read the brain index** to know what's already captured and what's thin.
2. **Pick targets.** If a block was passed, focus there. Otherwise, identify the 2-3 weakest blocks AND any open questions in `open-questions.md` that the user could answer in one sentence.
3. **Use AskUserQuestion** to ask 5 questions (3 for `--quick`, 10 for `--deep`). Ask them ONE AT A TIME, not all at once, so the user isn't overwhelmed and answers can branch follow-ups. Each question should:
   - Be specific and answerable in 1-3 sentences (no "tell me about your business")
   - Target a real gap in the brain, not something already captured
   - Offer 3-4 multiple-choice options when possible to make answering fast, plus an "other / let me explain" option
4. **After each answer**, file it immediately as a note in the right block. Use `Source: interview-YYYY-MM-DD` with today's date. Status `reviewed`. If the answer triggers a follow-up question, ask it next instead of moving on.
5. **Resolve open questions.** If any answer resolves a bullet in `open-questions.md`, remove that bullet and reference the resolving note ID.
6. **Report.** Print a summary of the new notes, which gaps are now filled, and which questions to revisit next time.

### Question bank by block (seed ideas — generate fresh ones based on actual gaps)

- **value-propositions**: "If you had to cut the product down to one feature for launch, which one keeps the user coming back?"
- **customer-segments**: "Out of the segments you've talked to, which has shown the strongest pull so far, and what's the second-best one?"
- **channels**: "Where will the first 100 users actually come from — paid ads, your personal network, communities, organic search, or referrals?"
- **customer-relationships**: "What's the one moment in the product where a user should feel 'I cannot quit this'?"
- **revenue-streams**: "What price would feel like a no-brainer for the entry tier, and where would you set the ceiling tier?"
- **key-resources**: "What is the single most important capability you do not yet have on the team?"
- **key-activities**: "Which weekly activity, if you stopped doing it, would the business slow down the fastest?"
- **key-partners**: "Are there any partnerships you are already exploring that could deliver users or distribution?"
- **cost-structure**: "What's your monthly burn ceiling before you'd need to raise or pause?"
- **marketing-campaigns**: "What's a launch moment you'd want to engineer — a viral asset, a directory push, a niche-community campaign?"

## Note schema (unchanged from /business-notes)

```markdown
## <note-id-prefix>-xxxx — Title
Date: 2026-04-29
Status: reviewed | raw | council-approved | locked
Block: <block-name>
Tags: codebase-scan|interview, get|keep|grow, ...
Source: codebase-scan | interview-YYYY-MM-DD | user

Body. Keep it short and actionable. Quote the user verbatim where it captures spirit.

**Dev follow-ups:** (optional) bullets
**Research needed:** (optional) bullets
```

## Hard rules

- NEVER invent user quotes. If you didn't get a verbatim answer, paraphrase and tag `Source: codebase-scan` not `interview`.
- NEVER duplicate an existing note. Update in place when the same fact appears.
- NEVER ask more than one question at a time in interview mode.
- NEVER ask questions whose answers are already in the brain — re-read first.
- Code changes are out of scope. This skill only writes to `<bmc-brain-path>`. Dev follow-ups go to `dev-followups.md`, not the actual codebase.
- After every pass, the brain should be strictly bigger or more accurate, never smaller (unless explicitly removing stale notes the user corrects).

## Relationship to other skills

- `/business-notes` — capture in flow; this skill is the proactive counterpart and uses the same note schema and brain location described there.
- `/business-roundtable <note-id-prefix>-xxxx` — promote a high-stakes note from this pass to the LLM council.
- `/llm-council` — answer items in `open-questions.md` that need external reasoning, not user input.

## First run

If `<bmc-brain-path>` doesn't exist, bootstrap it the same way `/business-notes` does (one file per block + extras), then proceed.
