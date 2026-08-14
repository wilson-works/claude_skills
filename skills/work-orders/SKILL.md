---
name: work-orders
description: "Start a triage and execution session that reads the backlog, prioritizes items, and spawns Sonnet agents to process them. Invoke with /work-orders [category|all|dry-run]."
---

# Work Orders Skill

## Purpose

Process the work order backlog by triaging open items, presenting a prioritized run plan, and spawning Sonnet sub-agents to execute each item. This is the "do the work" counterpart to `/backlog` (which is just the notebook).

Designed to be invoked in a fresh session dedicated to processing queued work.

## Configure for your project

Edit these placeholders before running:

- `<your-project-backlog-path>`: directory holding your backlog files (e.g. `~/.claude/projects/<project>/backlog/`, or `docs/backlog/`).
- `<project-root>`: absolute path to your project's repo root (the working directory passed to spawned agents).
- `<project-claude-md>`: path to your project's `CLAUDE.md` (usually `<project-root>/CLAUDE.md`).
- `<build-command>`: one-shot build/test command an agent can run to verify its change (e.g. `npm run build`, `npx turbo build`, `cargo check`, `pytest -q`).
- `<project-rules-summary>`: 2-4 lines describing your project's hard rules so agents do not have to fully read CLAUDE.md to start (still required, but the summary primes them).

## Invocation

```
/work-orders                 Review all open items, prioritize, propose a run plan
/work-orders bugs            Process only bug fixes
/work-orders design          Process only design requests
/work-orders features        Process only feature requests
/work-orders tech-debt       Process only tech debt
/work-orders all             Process everything, highest priority first
/work-orders dry-run         Show what would be executed without doing anything
/work-orders [ID]            Process a single specific item (e.g., /work-orders BUG-003)
```

## Backlog Location

```
<your-project-backlog-path>
```

Files: `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, `completed.md`

<!-- STATIC BOUNDARY: everything above this line is stable across invocations and can be cached. Everything below is dynamic — backlog reads, prioritization, and flag handling change per invocation. -->

## Workflow

### Step 1: Read the Backlog

Read all backlog list files (or the filtered category). Parse each item to extract:
- ID, title, priority, details, context, acceptance
- Date added (for age sorting)

If the backlog is empty, report "No open work orders" and stop.

### Step 2: Build the Run Plan

Sort items by:
1. Priority: critical > high > medium > low
2. Age: oldest first within same priority
3. Category: bugs before design before features before tech debt (bugs are more likely to block other work)

Present the run plan to the user:

```
WORK ORDER RUN PLAN
====================

Ready to process 4 items:

1. [BUG-001] high -- Timer does not pause on tab switch
   Agent: Sonnet | Isolation: worktree | Est: bug fix in useSessionTimer

2. [BUG-002] medium -- Leaderboard flickers on load
   Agent: Sonnet | Isolation: worktree | Est: rendering optimization

3. [DSN-001] high -- Card needs more visual energy
   Agent: Sonnet | Isolation: worktree | Est: component restyle

4. [TDT-001] low -- Remove unused auth helpers
   Agent: Sonnet | Isolation: worktree | Est: dead code removal

Mode: Sequential (use --parallel for concurrent execution)

Proceed? (y/n)
```

For `/work-orders dry-run`, show the plan and stop. Do not ask to proceed.

### Step 2.5: Sonnet Context Brief (run before spawning execution agents)

For each item in the approved run plan, spawn a short-lived Sonnet context agent to gather codebase context before execution. This is the Sonnet-first pattern — execution agents start with a brief, not a cold start. Run these in parallel (one per item, all at once) before spawning any execution agents.

```
Agent(
  model: "sonnet",
  effort: "low",
  run_in_background: false,
  description: "CONTEXT: [ID] [title]",
  prompt: """
You are a Sonnet context agent. Research this work order and output a brief. Do NOT write any code or modify any files.

Work Order:
ID: [ID]
Title: [title]
Category: [category]
Details: [details]
Context: [context]
Working directory: <project-root>

Tasks:
1. Grep the codebase for the key symbols, component names, hook names, or data paths mentioned in the title/details
2. Read the 2-3 most relevant files
3. Check the last 10 entries of <your-project-backlog-path>/completed.md for prior art (similar patterns already solved)
4. Identify what could break if this change is done wrong (blast radius)

Output ONLY this block:
CONTEXT_BRIEF_START
hotspot_files:
  - [relative path]
  - [relative path]
prior_art: [one sentence or "None found"]
blast_radius: [files that could break]
approach: [2-3 sentence specific recommendation]
CONTEXT_BRIEF_END
"""
)
```

Wait for all context agents to return. Parse each `CONTEXT_BRIEF_START...CONTEXT_BRIEF_END` block and inject it into the corresponding execution agent prompt below.

If a context agent returns a malformed brief, proceed without it — do not block execution.

### Step 3: Execute Work Orders

For each item in the run plan, spawn a Sonnet sub-agent:

```
Agent tool call:
  model: "sonnet"
  isolation: "worktree"
  description: "[ID] short title"
  prompt: (see agent prompt template below)
```

**Sequential mode** (default): Run one agent at a time. Wait for completion before starting the next. This avoids merge conflicts.

**Parallel mode** (`--parallel`): Launch up to 3 agents simultaneously. Only use when items touch different files/areas.

### Step 4: Process Results

After each agent completes:

1. **If successful**:
   - Read the agent's result summary
   - Move the item from its backlog list to `completed.md` with:
     - **Completed**: today's date
     - **Completed by**: work-orders agent (Sonnet)
     - **Resolution**: summary of what the agent did
   - Report success to the user

2. **If failed**:
   - Keep the item in its backlog list
   - Append a `**Last attempt**` field to the item:
     ```
     - **Last attempt**: 2026-04-05 -- [brief description of what went wrong]
     ```
   - Report the failure and reason to the user

### Step 5: Summary Report

After all items are processed, present a summary:

```
WORK ORDER RESULTS
===================

Completed: 3/4
Failed: 1/4

COMPLETED:
  [BUG-001] Timer does not pause on tab switch
    Resolution: Added visibilitychange listener in useSessionTimer.ts

  [DSN-001] Card needs more visual energy
    Resolution: Rewrote Card with gradient borders and rank-based glow

  [TDT-001] Remove unused auth helpers
    Resolution: Deleted 3 unused functions from authUtils.ts

FAILED:
  [BUG-002] Leaderboard flickers on load
    Reason: Could not reproduce -- leaderboard renders correctly in test
    Action: Item remains in backlog with attempt note

Worktree branches created:
  - work-orders/BUG-001 (ready to merge)
  - work-orders/DSN-001 (ready to merge)
  - work-orders/TDT-001 (ready to merge)
```

## Agent Prompt Template

Each Sonnet execution agent receives this prompt (filled in per item, including context brief from Step 2.5):

```
You are a Sonnet agent processing a work order.

## Project Context
- <project-rules-summary>
- Working directory: <project-root>
- Read <project-claude-md> for full project rules before starting

## Work Order
- **ID**: [ID]
- **Category**: [bug|design|feature|tech-debt]
- **Title**: [title]
- **Priority**: [priority]
- **Details**: [details]
- **Context**: [context]
- **Acceptance**: [acceptance — the verifiable done condition]

## Context Brief (from Sonnet pre-analysis — start here, do not ignore)
[If context brief was returned, paste the full CONTEXT_BRIEF block here. If not available, write "No brief available — explore from CLAUDE.md."]

Hotspot files (read these first):
[hotspot_files from brief, one per line — or "See CLAUDE.md to orient"]

Prior art: [prior_art from brief]
Blast radius (files that could break): [blast_radius from brief]
Suggested approach: [approach from brief — treat as directional, trust the code if it conflicts]

## Instructions

1. Read <project-claude-md> first to understand project rules and constraints
2. Start with the hotspot files from the context brief above — they are pre-researched starting points
3. Implement the fix/change described in the work order
4. Verify your changes compile / pass: run `<build-command>`
5. If browser tools are available and this is a visual change, take a screenshot to verify

## Rules
- Follow all project rules in <project-claude-md> strictly
- Make minimal, focused changes -- only what the work order describes
- Do not refactor surrounding code or add unrelated improvements
- Do not create new files unless absolutely necessary
- If you cannot complete the work order, explain why clearly

## Output
When done, provide:
1. A one-line summary of what you changed
2. List of files modified
3. Whether the build passed
4. Any concerns or follow-up items
```

## Auto-Prune on Start

Every time `/work-orders` is invoked, automatically prune completed items older than 30 days from `completed.md` before presenting the run plan. Report how many were pruned (if any).

## Important Notes

- Always use `model: "sonnet"` for cost efficiency -- these are execution tasks, not design decisions. Context-brief agents additionally run `effort: "low"` (read-and-summarize work; the default reasoning budget is wasted there).
- **Escalation rule**: if an item fails on Sonnet (agent reports blocked, tests stay red, or the diff misses the acceptance criteria), do not re-spawn the same prompt on Sonnet — re-queue it once with `model: "opus"` and the failure summary prepended, or hand it to `/marathon-orders`. One Sonnet failure is signal, two is waste. (See docs/MODELS.md.)
- Always use `isolation: "worktree"` so each agent works on an isolated copy
- The user must approve the run plan before any agents are spawned
- Failed items stay in the backlog -- they are never silently dropped
- Each agent is self-contained -- it reads the project's CLAUDE.md and explores the code independently
- Worktree branches follow the naming pattern `work-orders/[ID]` for easy identification
- After all agents complete, the user decides which branches to merge
