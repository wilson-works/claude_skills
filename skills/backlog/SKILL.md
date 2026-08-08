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
/backlog                          Show all open items across categories
/backlog bugs                     Show only bug fixes
/backlog design                   Show only design requests
/backlog features                 Show only future considerations
/backlog tech-debt                Show only tech debt
/backlog add [description]        Auto-triage and add to the right list
/backlog set [ID] [field=value]   Set or update execution-routing fields on an item
                                  (e.g., /backlog set BUG-003 lane=B owner=marcus effort=M gate=alpha)
/backlog done [ID]                Move item to completed log (e.g., /backlog done BUG-003)
/backlog move [ID] [target]       Move item to a different category (e.g., /backlog move BUG-003 design)
/backlog prune                    Remove completed items older than 30 days
/backlog stats                    Count by category and priority
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

Every item has a **required core** that any executor can act on, plus optional **execution-routing fields** that let downstream skills (`/work-orders`, `/marathon-orders`, `/work-orders-org`, `/marathon-org`, `/workday`) pick the item up without re-planning.

### Required core (always present)

```markdown
### [BUG-003] Short descriptive title
- **Added**: 2026-04-02
- **Priority**: high
- **Details**: Full description of what needs to be done. Name specific files, components, functions, or data collections where possible. Instructions should be executable -- an agent reading this should know exactly what to build or fix without needing to guess scope.
- **Context**: Where this came from, why it matters, what breaks if this isn't done.
- **Acceptance**: Specific, verifiable done condition. What must be true for an agent to call this complete? State the observable outcome, not "it works".
```

Priority levels: `critical`, `high`, `medium`, `low`.

### Execution-routing fields (optional, add when known)

These let the WO be picked up by lane-parallel and org-routed runners without further triage. Fill them when you know them; leave them off when you don't — `/backlog add` will offer to fill them in, and `/backlog set` can add them later.

```markdown
- **Effort**: M
- **Lane**: B
- **Owner**: marcus
- **Reviewer**: cindy
- **Gate**: alpha
- **Depends on**: [BUG-001, FTR-014]
```

| Field | Values | Purpose |
|-------|--------|---------|
| **Effort** | `S` (≤2h) `M` (≤half day) `L` (≤full day) `XL` (split before filing) | Lets runners batch sensibly and reject XLs at intake. |
| **Lane** | Project-defined key | Which lane picks this up in a lane-parallel runner. Lane keys are defined by your `/workday` (or equivalent) skill — e.g. `A=db`, `B=backend`, `C=frontend`, `D=api`. Omit for non-parallel runs. |
| **Owner** | Agent name from your org-config | The named agent who implements. Used by org-routed runners (`/work-orders-org`, `/marathon-org`). Omit for direct (non-org) runners. |
| **Reviewer** | Agent name from your org-config | The named agent who reviews the diff before merge. Typically a department head. Omit to let the org runner pick by department. |
| **Gate** | Free-text milestone tag (e.g. `alpha`, `beta`, `v1`, `mvp-week-1`) | Lets you filter the backlog to a release scope. Multiple WOs can share a gate. |
| **Depends on** | List of WO IDs | Soft sequencing. Lane-parallel runners use it to order WOs within a lane and to flag cross-lane dependencies. Differs from **Blocked on** (hard skip). |

### Other optional fields

```markdown
- **Audit-First**: true -- the work order requires investigation before coding (blank screen with unknown cause, "audit all X controls", "find every instance of Y"). Triggers a scout agent before the fix agent in any marathon-style runner.
- **Blocked on**: [ID] -- hard block: this item cannot be executed until another item ships first. Marathon runners skip blocked items until the blocker is resolved. (Use **Depends on** for soft sequencing.)
- **Note**: [free text] -- subsumption ("will be resolved by BUG-133"), shelved status, or important constraints the executing agent must know.
```

### Which fields each runner uses

| Runner | Required | Uses if present | Ignored |
|--------|----------|-----------------|---------|
| `/backlog` (view) | core | all | none |
| `/work-orders` (Sonnet batch) | core | Effort, Gate, Depends on | Lane, Owner, Reviewer |
| `/marathon-orders` (Opus loop) | core | Effort, Gate, Depends on, Audit-First, Blocked on | Lane, Owner, Reviewer |
| `/work-orders-org` (org single) | core | Effort, Owner, Reviewer, Gate, Depends on | Lane |
| `/marathon-org` (org loop) | core | Effort, Owner, Reviewer, Gate, Depends on, Audit-First, Blocked on | Lane |
| `/workday` (4-lane parallel) | core + **Lane** | Effort, Owner, Reviewer, Gate, Depends on | none |

`/workday` is the only runner where Lane is effectively required — without it, the planner has to bucket the WO by reading its file paths, which is slower and error-prone. Set Lane explicitly on any WO you intend to ship through a workday session.

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
5. **Infer execution-routing fields** from the description (auto-fill what you can; leave the rest blank for the operator to confirm):
   - **Effort**: detect size hints. "quick fix", "one-line", "typo" → `S`. "spike", "investigate", "refactor across N files" → `L`. "build the X system" → `XL` (and warn the user it should be split). Default to `M`.
   - **Lane**: if the description names a file path or domain that maps to a known lane in the project's lane configuration (where one exists), suggest it. Otherwise leave blank.
   - **Owner / Reviewer**: only auto-fill if the description explicitly names an agent ("have ava do X"). Otherwise leave blank; the org-routed runner will pick at dispatch time.
   - **Gate**: if the description references a milestone ("for alpha", "v1 must-have", "post-launch polish"), capture it. Otherwise leave blank.
6. **Confirm execution fields with the user before filing** (skip this in non-interactive contexts):

   ```
   Filing as [CATEGORY-NNN] "title". Suggested execution metadata:
     Effort:   M    Lane:   (none)    Owner:  (none)    Reviewer: (none)    Gate: alpha

   Edit any of these now? (y / skip) -- skip is fine, /backlog set can add them later.
   ```

   On `y`, accept inline overrides like `effort=L lane=B owner=marcus`. On `skip` or no response in non-interactive mode, file with what you have. Never block on this — execution fields are always optional at file time.
7. Read the target list file to get the next available ID from the `<!-- Next ID: N -->` comment
8. Append the new item to the file using the format in **Item Format** above (core fields always; execution-routing fields only when set)
9. Increment the Next ID comment
10. Remove the "No open ..." placeholder line if present
11. Confirm to the user: show the item ID, category it was filed under, and the formatted entry

If the category is ambiguous, ask the user before filing.

### `/backlog set [ID] [field=value]...`

Set or update execution-routing fields on an existing WO. Use this to promote a quick-filed WO to org-routed or workday-ready without re-typing the body.

```
/backlog set BUG-003 effort=M lane=B owner=marcus reviewer=cindy gate=alpha
/backlog set FTR-014 depends-on=BUG-003,FTR-012
/backlog set TDT-021 lane=                              # blank value clears the field
```

1. Find the item by ID across all list files.
2. Parse `field=value` pairs from the args. Accepted fields: `effort`, `lane`, `owner`, `reviewer`, `gate`, `depends-on`, `blocked-on`, `audit-first`, `note`, `priority`. Hyphenated names map to the corresponding bold field (e.g. `depends-on` → `**Depends on**`).
3. Validate values:
   - `effort` must be one of `S | M | L | XL`
   - `priority` must be one of `critical | high | medium | low`
   - `audit-first` must be `true` or `false` (false removes the field)
   - `depends-on` and `blocked-on` accept comma-separated WO IDs
4. Edit the WO block in place: insert each field if absent, replace if present, remove if value is blank.
5. Confirm by re-displaying the updated item.

Refuses to modify an item already in `completed.md` — re-open it via `/backlog move` first if needed.

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

Effort-hint signals for the **Effort** field:

- `S` (≤2h): "quick", "one-line", "typo", "rename", "tiny", "trivial"
- `M` (≤half day): default; most bug fixes and small features
- `L` (≤full day): "spike", "investigate", "audit across", "refactor", "rework"
- `XL` (split first): "build the X system", "rewrite", "migrate the whole", "across the entire codebase" — when you detect XL, propose a split before filing rather than filing one giant WO

Gate-hint signals for the **Gate** field: explicit mentions like "for alpha", "must-have for v1", "post-launch", "MVP", "beta blocker". If a milestone term appears in the description, capture it verbatim as the gate.

When in doubt, ask. Don't guess on ambiguous items.

## Inline Triage Mode

When the user is in a conversation and describes something that sounds like a work order (bug report, design feedback, feature idea, refactoring need) without explicitly calling `/backlog add`, you should still recognize it and offer to add it:

> "That sounds like a bug. Want me to file it as BUG-004?"

This keeps the flow conversational - the user doesn't have to remember the command syntax.

## Important Notes

- Always read the file before editing to get the current state and next ID
- Never duplicate IDs — always check the Next ID comment
- Keep item descriptions concise but specific enough for an agent to act on
- The `**Context**` field is important — it helps future agents understand WHY this item matters
- When showing items, always include the ID so the user can reference it easily
- Execution-routing fields (Effort, Lane, Owner, Reviewer, Gate, Depends on) are **optional at file time** — never block on them. They make the WO pickup-ready for advanced runners (`/marathon-org`, `/workday`), but a WO without them is still valid for `/work-orders` and `/marathon-orders`.
- `/workday`-bound WOs are the exception: set **Lane** explicitly, because the workday planner uses it to partition the queue across parallel sessions. A workday-bound WO without Lane forces the planner to infer from file paths, which is slower and error-prone.
- Lane keys, agent names, and gate values are **project-defined**, not skill-defined. This skill validates field presence and format, not value semantics — the consuming runner (`/workday`, `/marathon-org`, etc.) defines the valid value set.
