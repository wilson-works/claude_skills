---
name: retro
description: "Post-session/sprint retrospective. Analyzes completed work, velocity, blockers, estimation accuracy, and recurring patterns. Outputs 3-5 action items and saves to a retro log. Invoke with /retro [session|sprint|--since <ref>]."
---

# Retro Skill

## Purpose

After a long work session, sprint, or autonomous run, projects often have no structured way to assess what got done, what failed, estimation accuracy, recurring blockers, or process improvements. This skill reads git log, backlog state, any session-state files, and plan files to produce a structured retrospective with specific, measurable findings and a short list of action items for next time.

## Configure for your project

Before first use, replace the following placeholders:

- `<project-root>` — absolute path to your project (e.g. `/home/user/myproject`, `d:/work/myapp`)
- `<backlog-path>` — directory holding your backlog markdown files (e.g. `docs/backlog/`, `<your-project-backlog-path>`)
- `<plans-path>` — where plan/spec files live (e.g. `docs/plans/`, `~/.claude/plans/`)
- `<retros-path>` — where retro outputs are saved (e.g. `docs/retros/`)
- `<session-state-files>` — any session/run state files your workflow produces (e.g. `*-state.json` from autonomous runs); leave empty if you don't have any

## Invocation

```
/retro                        - retro on the most recent session (auto-detect)
/retro session                - retro on today's work session (today's commits + changes)
/retro sprint                 - retro on the most recent named sprint/run
/retro --since HEAD~10        - retro on last 10 commits
/retro --since 2026-04-10     - retro since a specific date
```

## Prerequisites

- File read access to `<project-root>` (for git history and any state files)
- File read access to `<backlog-path>` (for completed and open items)

## Workflow

### Step 1: Scope the Retro

Based on arguments:

- **No args**: Auto-detect. If `<session-state-files>` exist with a recent `completedAt`, scope to that run. Otherwise, default to today's commits.
- **`session`**: Today's commits only. `git log --since='today 00:00'`.
- **`sprint`**: The most recent named sprint/run identified in your state files or commit log.
- **`--since <ref>`**: User-specified commit range.

### Step 2: Collect Data

**Commits:** `git log --since=<start> --pretty='%h %s'` — commit count and any work item IDs referenced in messages.

**Work items completed:** Parse `<backlog-path>` for entries with a closed/done date in the retro window. Count by category if your backlog supports categories.

**Work items added:** Parse `<backlog-path>` for entries created in the window.

**Session state:** If retro scope is a structured run, read its state file for wave count, agents spawned, any failures or retries.

**Plan files:** Check `<plans-path>` for plans created or completed in the window.

**Git stats:** Lines added/removed, files changed, unique files touched.

### Step 3: Analyze

**Velocity:**
- Work items closed per day
- Commits per day
- Lines changed per day
- Compare against prior retros if any exist in `<retros-path>`

**Completion rate:**
- For a structured run: planned phases vs completed phases
- For work items: what percentage of opened items in the window got closed in the window

**What went well:**
- Data-backed observations only. E.g., "5 bugs closed, 0 regressions detected"
- Successes verified by tests or other tooling

**What went poorly:**
- Phase failures, agent timeouts, merge conflicts
- Work items that got reopened or needed rework
- Scope creep incidents

**Blockers:**
- Parse session state and commits for blocker language ("blocked by", "dependency on", "waiting for")
- External dependencies that delayed work
- Recurring blockers vs one-off blockers

**Estimation accuracy:**
- Compare work item descriptions (small/medium/large) vs actual diff sizes
- Flag systematic under/over-estimation

**Process patterns:**
- Recurring issues across multiple phases (e.g., "3 phases failed due to the same auth issue")
- Patterns that worked

### Step 4: Produce Retro Document

Save to `<retros-path>/retro-[YYYY-MM-DD]-[scope-name].md`:

```markdown
# Retro: [scope name]

Scope: [date range]
Commits: [N]
Work items closed: [N]
Work items added: [N]

## Metrics
| Metric | Value | vs Prior Retro |
|--------|-------|----------------|
| Commits/day | X | +/- Y |
| Items closed | N | +/- |
| Lines changed | N | +/- |
| Phase completion | X/Y | |
| Bug:Feature ratio | X:Y | |

## Velocity Trend
[one-paragraph comparison against prior retros]

## What Went Well
- [specific, data-backed observation]
- [another]

## What Went Poorly
- [specific issue with evidence]
- [another]

## Blockers
| Blocker | Resolution | Prevention |
|---------|------------|------------|
| [blocker] | [how resolved] | [how to avoid next time] |

## Estimation Accuracy
- [systematic pattern observed]

## Recurring Issues
- [pattern] - observed [N] times in this period
- [if a pattern appeared in prior retros too, flag it]

## Carryover
[work items still open that were expected to close]

## Tech Debt Delta
[added / resolved in the window]

## Action Items (max 5)
1. [specific, owned, dated action]
2. [...]

## Previous Action Item Follow-Up
[from prior retro: which got done, which didn't]
```

### Step 5: Follow-Up

Offer to:
- File any action items that require code changes as backlog entries
- Save a one-line summary to a long-running retro log (for cross-retro pattern detection)
- Run a systems/architecture review if the retro surfaced architectural concerns

## Principles

- **Data over anecdote.** Every observation must cite a specific commit, work item, or metric. No "it felt like we moved fast."
- **Systemic over individual.** Patterns across phases matter more than one-off incidents.
- **Five max.** More than 5 action items means nothing gets done. Prioritize ruthlessly.
- **Follow up on previous actions.** Unaddressed previous action items signal a process problem.
- **Retro once per run, not per phase.** Overuse kills the signal.

## Anti-Patterns

- Do not retro during an active session/run. Wait for completion.
- Do not blame agents or tools for failures when the cause is process/scope.
- Do not copy the same action items from retro to retro without explanation.
- Do not mark a retro "done" without committing or saving it.
