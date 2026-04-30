---
name: backlog
description: "View, add, close, and manage work order backlog items across categories (bugs, design, features, tech debt). Invoke with /backlog [command] [args]."
---

# Backlog Management Skill

## Purpose

Manage a persistent work order backlog stored in your project's backlog directory. This is the read/write interface for the backlog -- use it to view open items, add new ones, mark items done, and prune old completions.

## Configure for your project

Before using this skill, set this placeholder:

- `<your-project-backlog-path>`: Absolute path to your backlog directory (e.g. `C:\Users\you\.claude\projects\my-project\backlog\` or `/path/to/repo/backlog/`).

The directory should contain:
- `bugs.md`, `design.md`, `features.md`, `tech-debt.md` (open items)
- `completed.md` (done items)

If the files do not exist yet, create them with an empty placeholder section and a `<!-- Next ID: 1 -->` comment.

## Invocation

```
/backlog                     Show all open items across categories
/backlog bugs                Show only bug fixes
/backlog design              Show only design requests
/backlog features            Show only future considerations
/backlog tech-debt           Show only tech debt
/backlog add [description]   Auto-triage and add to the right list
/backlog done [ID]           Move item to completed log (e.g., /backlog done BUG-003)
/backlog move [ID] [target]  Move item to a different category (e.g., /backlog move BUG-003 design)
/backlog prune               Remove completed items older than 30 days
/backlog stats               Count by category and priority
```

## Backlog Location

All files live at `<your-project-backlog-path>`.

| File | Prefix | Category |
|------|--------|----------|
| `bugs.md` | `BUG-` | Bug fixes, broken behavior, regressions |
| `design.md` | `DSN-` | UI/UX improvements, visual polish, layout |
| `features.md` | `FTR-` | New features, ideas, product enhancements |
| `tech-debt.md` | `TDT-` | Refactoring, cleanup, performance, DX |
| `completed.md` | (any) | Done items with completion metadata |

## Item Format

Every item follows this format:

```markdown
### [BUG-003] Short descriptive title
- **Added**: 2026-04-02
- **Priority**: high
- **Details**: Full description of what needs to be done. Name specific files, components, functions, or data collections where possible. Instructions should be executable - an agent reading this should know exactly what to build or fix without needing to guess scope.
- **Context**: Where this came from, why it matters, what breaks if this isn't done.
- **Acceptance**: Specific, verifiable done condition. What must be true for an agent to call this complete? State the observable outcome, not "it works".
```

**Optional fields** (add when relevant):

```markdown
- **Audit-First**: true - add when the work order requires investigation before coding (blank screen with unknown cause, "audit all X controls", "find every instance of Y"). Triggers a scout agent before the fix agent in any marathon-style runner.
- **Blocked on**: [ID] - add when this item cannot be executed until another item ships first. Marathon runners will skip blocked items until the blocker is resolved.
- **Note**: [free text] - add for subsumption ("will be resolved by BUG-133"), shelved status, or important constraints the executing agent must know.
```

Priority levels: `critical`, `high`, `medium`, `low`

## Workflow by Command

### `/backlog` (no args) or `/backlog [category]`

1. Read all list files (or the specified one) from the backlog directory
2. Present items grouped by category, sorted by priority (critical > high > medium > low), then by date added (oldest first)
3. Show a count summary at the bottom

Display format:
```
BACKLOG OVERVIEW
================

BUGS (2 open)
  [BUG-001] high   -- Timer doesn't pause on tab switch (2026-04-02)
  [BUG-002] medium -- Leaderboard flickers on load (2026-04-03)

DESIGN (1 open)
  [DSN-001] high   -- Card needs more visual energy (2026-04-02)

FEATURES (0 open)

TECH DEBT (0 open)

Total: 3 open items (1 critical, 2 high, 0 medium, 0 low)
```

### `/backlog add [description]`

1. Parse the user's description to determine:
   - **Category**: Is this a bug (broken behavior), design (visual/UX), feature (new capability), or tech debt (cleanup/refactor)?
   - **Priority**: Infer from urgency words. Default to `medium` if unclear.
   - **Title**: Extract a short title (under 60 chars)
2. Draft the **Details** field: make it executable. Name specific files, components, or data collections if inferable from the description. An agent should be able to start from Details alone.
3. Draft the **Acceptance** field: state the observable done condition. If the user's description implies a specific outcome ("the setting should save", "the blank screen should render content"), translate that into a verifiable check. If acceptance criteria is not clear from the description, ask before filing.
4. Detect optional tags:
   - If the description mentions auditing, investigating, finding all instances, or diagnosing an unknown root cause - add `**Audit-First**: true`
   - If the description mentions a dependency on another item - add `**Blocked on**: [ID]`
5. Read the target list file to get the next available ID from the `<!-- Next ID: N -->` comment
6. Append the new item to the file
7. Increment the Next ID comment
8. Remove the "No open ..." placeholder line if present
9. Confirm to the user: show the item ID, category it was filed under, and the formatted entry

If the category is ambiguous, ask the user before filing.

### `/backlog done [ID]`

1. Find the item by ID across all list files
2. Remove it from its source file
3. Append it to `completed.md` with additional fields:
   - **Completed**: today's date
   - **Completed by**: "manual session" (or agent name if running from a marathon/work-orders runner)
   - **Resolution**: Ask the user for a brief resolution note, or accept one if provided (e.g., `/backlog done BUG-003 Fixed in useSessionTimer`)
4. If the source file has no remaining items, re-add the "No open ..." placeholder
5. Remove the "No completed items." placeholder from completed.md if present
6. Confirm the move

### `/backlog move [ID] [target]`

1. Find the item by ID
2. Re-prefix the ID to match the target category (e.g., BUG-003 becomes DSN-004)
3. Remove from source, append to target with new ID
4. Confirm the move

### `/backlog prune`

1. Read `completed.md`
2. Parse each item's `**Completed**` date
3. Remove items where the completion date is more than 30 days ago
4. Report how many items were pruned

### `/backlog stats`

1. Read all list files
2. Count items by category and by priority
3. Display a summary table:

```
BACKLOG STATS
=============
| Category   | Critical | High | Medium | Low | Total |
|------------|----------|------|--------|-----|-------|
| Bugs       | 0        | 1    | 1      | 0   | 2     |
| Design     | 0        | 1    | 0      | 0   | 1     |
| Features   | 0        | 0    | 0      | 0   | 0     |
| Tech Debt  | 0        | 0    | 0      | 0   | 0     |
|------------|----------|------|--------|-----|-------|
| Total      | 0        | 2    | 1      | 0   | 3     |

Completed (last 30 days): 5
Oldest open item: BUG-001 (2026-04-02, 3 days ago)
```

## Auto-Triage Rules

When adding items, use these signals to determine category:

**Bugs** (BUG-): "broken", "doesn't work", "error", "crash", "wrong", "fails", "regression", "flicker", "stuck", "missing data"

**Design** (DSN-): "looks", "ugly", "layout", "spacing", "color", "font", "animation", "responsive", "mobile", "visual", "polish", "energy", "boring", "generic"

**Features** (FTR-): "add", "new", "implement", "support", "enable", "integrate", "want", "should have", "idea", "consider"

**Tech Debt** (TDT-): "refactor", "cleanup", "optimize", "performance", "slow", "duplicate", "hardcoded", "deprecated", "upgrade", "migrate", "DX"

When in doubt, ask. Don't guess on ambiguous items.

## Inline Triage Mode

When the user is in a conversation and describes something that sounds like a work order (bug report, design feedback, feature idea, refactoring need) without explicitly calling `/backlog add`, you should still recognize it and offer to add it:

> "That sounds like a bug. Want me to file it as BUG-004?"

This keeps the flow conversational - the user doesn't have to remember the command syntax.

## Important Notes

- Always read the file before editing to get the current state and next ID
- Never duplicate IDs - always check the Next ID comment
- Keep item descriptions concise but specific enough for an agent to act on
- The `**Context**` field is important - it helps future agents understand WHY this item matters
- When showing items, always include the ID so the user can reference it easily
