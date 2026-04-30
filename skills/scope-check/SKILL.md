---
name: scope-check
description: "Compares original work item / plan scope against actual implementation to detect scope creep during long sessions or autonomous runs. Outputs a PASS/CONCERNS/FAIL verdict based on scope change percent. Invoke with /scope-check [phase|work-item-id|plan-file]."
---

# Scope Check Skill

## Purpose

Long sessions and autonomous runs sometimes drift. Work items get expanded mid-flight. Features balloon from "fix this bug" into "fix this bug and refactor the surrounding module." This skill catches that drift by comparing the original scope (from a backlog work item or a plan file) against the actual implementation (git diff). Returns a PASS / CONCERNS / FAIL verdict based on how much the scope grew.

## Configure for your project

Before first use, replace the following placeholders:

- `<project-root>` — absolute path to your project
- `<backlog-path>` — directory holding backlog markdown files (e.g. `docs/backlog/`, `<your-project-backlog-path>`)
- `<plans-path>` — directory holding plan/spec files (e.g. `docs/plans/`, `~/.claude/plans/`)
- `<work-item-id-pattern>` — your project's work item ID prefix style (e.g. `BUG-`, `FTR-`, `TASK-`, `JIRA-1234`)
- `<session-state-files>` — any session/run state files your workflow produces (optional)

## Invocation

```
/scope-check                              - auto-detect current run phase and check it
/scope-check BUG-096                      - check scope of a specific work item by ID
/scope-check FTR-272                      - check scope of a feature work item
/scope-check plan:my-plan-name            - check against a plan file
/scope-check --since HEAD~5               - check last 5 commits against their referenced work items
```

## Prerequisites

- File read access to `<project-root>` (for git)
- File read access to `<backlog-path>` (for work items)
- File read access to `<plans-path>` (for plan files)

## Workflow

### Step 1: Identify Scope Source

Based on arguments:

- **No argument**: Read `<session-state-files>` if present. Identify the currently-active phase and its work item. If no active run, fall back to the most recent merged feature commit.
- **Work item ID** (matching `<work-item-id-pattern>`): Grep `<backlog-path>` for the ID. Extract the full work item description (priority, details, context).
- **Plan file** (`plan:name`): Read from `<plans-path>/[name].md`.
- **--since <ref>**: Get all commits since `<ref>`; for each, parse the work item ID from the commit message and fetch the corresponding backlog entry.

### Step 2: Define Expected Scope

From the scope source, extract:
- **Stated objective**: What the work item / plan says it will do (one-liner)
- **Listed deliverables**: Specific items called out (files to change, features to add, bugs to fix)
- **Explicit out-of-scope**: Anything the work item said NOT to touch

If any of these are missing from the source, note the ambiguity. Unbounded work items are harder to scope-check.

### Step 3: Extract Actual Scope

Get the actual changeset:

- If checking a phase of a run: `git diff <phase-base>..HEAD --stat` plus list of changed files
- If checking a commit range: `git diff <ref>..HEAD --stat`
- If checking a plan: compare against the current working tree

Extract:
- Files changed (count, list)
- Lines added / removed
- New files created
- Files deleted
- Any commits not matching the work item ID (scope leakage via extra commits)

### Step 4: Compare and Classify

For each actual change, classify it as:

- **In-scope**: Directly fulfills a stated deliverable
- **Reasonable adjacent**: Imports, type updates, test stubs — required for the in-scope change to work
- **Scope creep**: Changes that aren't required but are adjacent improvements
- **Out-of-scope**: Changes in completely unrelated files or features

Compute:
- **Scope change percent** = (creep + out-of-scope files) / total changed files
- **Unrelated commits**: commits with work item IDs that don't match

### Step 5: Produce Verdict

**PASS** if:
- Scope change percent <= 10%
- No out-of-scope commits
- No violations of explicit "do not touch" directives

**CONCERNS** if:
- Scope change percent 10-25%
- OR 1-2 adjacent improvements that would be fine in a follow-up work item
- Advisory: note what could have been deferred

**FAIL** if:
- Scope change percent > 25%
- OR unrelated commits present
- OR violates explicit out-of-scope directives
- Blocking: recommend reverting the out-of-scope changes into separate work items before merging

### Step 6: Report

```markdown
# Scope Check: [scope source]

**Source:** [work item ID / plan name]
**Verdict:** PASS | CONCERNS | FAIL
**Scope change:** [X]%

## Stated Objective
[from work item]

## Deliverables
- [x] [deliverable 1 - completed as planned]
- [x] [deliverable 2 - completed]
- [ ] [deliverable 3 - NOT addressed]

## Changeset
- Files changed: [N]
- In-scope: [N] ([%])
- Adjacent: [N]
- Creep: [N]
- Out-of-scope: [N]

## Scope Creep (if any)
- [file 1]: [reason this is creep, e.g., "refactored helper that wasn't broken"]
- [file 2]: [...]

## Out-of-Scope (if any)
- [file 1]: [reason, e.g., "unrelated to bug fix, belongs in separate work item"]

## Recommendation
- PASS -> proceed to merge
- CONCERNS -> flag in PR, consider deferring adjacent improvements to follow-up
- FAIL -> revert out-of-scope changes before merge; file follow-up work items for the creep
```

### Step 7: Follow-Up

If verdict is CONCERNS or FAIL, offer to:
- File a follow-up backlog item for each out-of-scope change
- Run a retro after the run completes to analyze the creep pattern

## Principles

- **Discovered requirements are valid.** If a work item couldn't have been completed without touching file X, that's in-scope adjacent, not creep.
- **Creep isn't always bad.** CONCERNS is advisory, not blocking. Small opportunistic cleanups can be net-positive.
- **Out-of-scope is blocking.** Changes to unrelated features should be reverted and re-filed.
- **The test:** Every changed line should trace directly to the work item's stated deliverable.

## Anti-Patterns

- Do not scope-check a work item you're currently implementing. This is a post-hoc check.
- Do not classify ALL adjacent changes as creep. Imports, types, and test stubs are expected collateral.
- Do not auto-revert. Report findings; let the user decide what to revert.
