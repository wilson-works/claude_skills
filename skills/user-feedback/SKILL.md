---
name: user-feedback
description: "Manage public user feedback from your app. Items land in a dev review log for triage before being promoted to the backlog. Invoke with /user-feedback [command]."
---

# User Feedback Skill

## Purpose

Handle feedback submitted by real users of your app. Unlike internal work orders (which go directly to the backlog), user feedback lands in a **dev review log** first. During periodic review sessions, you triage feedback items — promoting actionable ones to the backlog or dismissing noise.

This creates a buffer between raw user input and the development pipeline.

## Configure for your project

Edit these placeholders before running:

- `<your-project-backlog-path>`: directory holding your backlog files (e.g. `~/.claude/projects/<project>/backlog/`, or `docs/backlog/`).
- Backlog category files inside that path: `bugs.md`, `design.md`, `features.md`, `tech-debt.md`. Adjust to match what `/backlog` uses in your setup.
- `<feedback-source-options>`: the channels you actually receive feedback from (e.g. in-app widget, support email, app store review, social media).

## Invocation

```
/user-feedback                      Show all pending feedback awaiting review
/user-feedback add [description]    Log a new feedback item from a user
/user-feedback review               Start an interactive review session
/user-feedback promote [ID]         Move item to the backlog (auto-triage category)
/user-feedback promote [ID] [cat]   Move item to a specific backlog category (bugs/design/features/tech-debt)
/user-feedback dismiss [ID]         Archive item as not actionable
/user-feedback dismiss [ID] [note]  Archive with a reason
/user-feedback merge [ID] [ID]      Consolidate duplicate reports (see Merge Behavior)
/user-feedback stats                Count pending vs reviewed vs promoted
/user-feedback prune                Remove archived items older than 30 days
```

## File Locations

```
<your-project-backlog-path>
```

| File | Purpose |
|------|---------|
| `user-feedback.md` | Pending feedback awaiting dev review |
| `feedback-archived.md` | Dismissed/reviewed items (pruned after 30 days) |

Promoted items move to `bugs.md`, `design.md`, `features.md`, or `tech-debt.md` via the `/backlog` system.

## Item Format

```markdown
### [UFB-012] "The timer is confusing when I switch between tasks"
- **Added**: 2026-04-10
- **Source**: in-app feedback widget
- **User context**: Free tier, 2 weeks active
- **Sentiment**: frustrated
- **Details**: User reports the timer does not clearly show which task is being tracked when switching between items
- **Tags**: timer, UX, confusion
```

Fields:
- **Source**: where the feedback came from (one of `<feedback-source-options>`)
- **User context**: any available context about the user (plan tier, tenure, team size). Helps prioritize.
- **Sentiment**: positive, neutral, frustrated, angry. Inferred from tone.
- **Tags**: freeform keywords for grouping related feedback.

## Workflow by Command

### `/user-feedback` (no args)

1. Read `user-feedback.md`
2. Display all pending items, sorted by date (newest first)
3. Show count summary

Display format:
```
USER FEEDBACK -- DEV REVIEW LOG
================================

12 items pending review

[UFB-012] frustrated -- "The timer is confusing when I switch between tasks" (2026-04-10)
  Source: in-app widget | Tags: timer, UX, confusion

[UFB-011] positive -- "Love the campaign feature, wish I could create my own" (2026-04-09)
  Source: in-app widget | Tags: campaigns, feature-request

[UFB-010] neutral -- "How do I see my team's total hours?" (2026-04-08)
  Source: support email | Tags: reporting, hours

...
```

### `/user-feedback add [description]`

1. Parse the feedback description
2. Infer sentiment from tone
3. Extract tags from keywords
4. Read `user-feedback.md` to get the next available ID
5. Append the new item
6. Remove the "No pending feedback." placeholder if present
7. Confirm: show the formatted entry

If the user provides additional context (source, user tier, etc.), include it. Otherwise use defaults:
- Source: "manual entry"
- User context: "unknown"
- Sentiment: "neutral"

### `/user-feedback review`

Start an interactive triage session. For each pending item:

1. Display the item in full
2. Present options:
   - **promote** -- Send to backlog (auto-triage or specify category)
   - **dismiss** -- Archive as not actionable
   - **skip** -- Leave for later
   - **merge [ID]** -- Combine with another feedback item (multiple users reporting the same thing)
3. After each decision, immediately update the files
4. At the end, show a summary:
   ```
   Review complete: 8 items reviewed
     Promoted: 3 (2 bugs, 1 feature)
     Dismissed: 4
     Skipped: 1
     Remaining: 4 items pending
   ```

### `/user-feedback promote [ID] [category?]`

1. Find the item by ID in `user-feedback.md`
2. Determine the backlog category:
   - If category provided, use it
   - Otherwise auto-triage using the same rules as `/backlog add`
3. Create a new backlog item in the appropriate list file:
   - Title comes from the feedback
   - Priority defaults to `medium` (you can adjust later)
   - Context includes "Promoted from user feedback UFB-XXX"
   - Details include the original user feedback text
   - Acceptance states the observable done condition (required by the `/backlog` item format) — derive it from the feedback, or ask if unclear
4. Move the feedback item to `feedback-archived.md` with:
   - **Reviewed**: today's date
   - **Action**: promoted to [category] as [new ID]
5. Confirm: show the new backlog item ID and category

### `/user-feedback dismiss [ID] [note?]`

1. Find the item by ID
2. Move to `feedback-archived.md` with:
   - **Reviewed**: today's date
   - **Action**: dismissed
   - **Reason**: provided note, or "Not actionable"
3. Confirm the dismissal

### `/user-feedback stats`

```
USER FEEDBACK STATS
====================
Pending review: 12
Archived (last 30 days): 45
  - Promoted to backlog: 18
  - Dismissed: 27

Top tags (pending): timer (4), campaigns (3), UX (3), mobile (2)
Sentiment breakdown (pending): positive 3, neutral 5, frustrated 3, angry 1
Oldest pending: UFB-003 (2026-03-28, 5 days ago)
```

### `/user-feedback prune`

Remove archived items older than 30 days from `feedback-archived.md`.

## Merge Behavior

When multiple users report the same issue, use merge to consolidate:

```
/user-feedback merge UFB-015 UFB-012
```

1. Keep the older item (UFB-012) as the primary
2. Append the newer item's details as an additional report:
   ```
   - **Also reported by**: UFB-015 (2026-04-12) -- "Same timer issue, I lose track of time"
   ```
3. Remove UFB-015 from the pending list
4. Increment a `**Reports**` count on the primary item (signals priority)

Items with multiple reports should be considered higher priority during review.

## How Feedback Enters the System

Feedback can come from:

1. **Manual entry**: You read an email/review/DM and run `/user-feedback add`
2. **In-app widget**: A feedback form in your app writes to your backend, which formats and appends to `user-feedback.md` (or calls the skill via API)
3. **QA sweeps**: When a QA / test-flow skill identifies a user-facing issue, it can suggest filing as user feedback
4. **This conversation**: If you describe something a user reported, offer to file it

## Important Notes

- User feedback NEVER goes directly to the backlog -- it always passes through the review log first
- This prevents noise, duplicates, and non-actionable feedback from cluttering the development pipeline
- The review session is the quality gate -- only you decide what becomes a work order
- Sentiment and report count help prioritize during review but do not auto-promote
- Tags help spot patterns (e.g., 5 users complaining about "timer" = high priority signal)
- When promoting, always include the original user's words in the backlog item context -- it grounds the work order in real user pain
