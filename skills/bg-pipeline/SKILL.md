---
name: bg-pipeline
description: "Runs a sequence of skills or prompts as background sub-agents, keeping your main session's context window clean. Use for long multi-step QA passes, full sweeps, or chained workflows. Invoke with /bg-pipeline [pipeline description or skill list]."
---

# Background Pipeline Skill

## Purpose

Launches long-running skill chains as background sub-agents so they don't consume your main conversation's context window. Each step runs in isolation, reports results to a shared output file, and the next step picks up where the last left off.

Use this when you want to run multiple QA passes, design audits, or improvement loops without watching each one execute in your active session.

## Configure for your project

Before using this skill, set these placeholders:

- `<project-root>`: Absolute path to your project root (e.g. `d:/myproject/`). Pipeline result files are written here.
- `<your-skill-list>`: The skills your project actually has. Adjust the Pre-built Pipelines section to reference skills that exist in your setup.
- `<default-vertical-or-flag>`: Any default flags your QA skills accept (e.g. environment, tenant, vertical). Optional.

## Invocation

```
/bg-pipeline full qa sweep across all sections
/bg-pipeline /qa-sweep section-a, /qa-sweep section-b, /qa-sweep section-c
/bg-pipeline /spec-audit all then /qa-sweep section-c
/bg-pipeline /review-ui then /ui-styling area-x then /review-ui
/bg-pipeline continuous: /qa-sweep all
```

**Modes:**
- **Sequential pipeline** -- Run a list of skills/prompts one after another. Each agent gets the previous agent's summary as context.
- **Parallel pipeline** -- Run multiple independent skills simultaneously as separate background agents.
- **Continuous mode** -- Run a single skill or pipeline repeatedly (like `/loop` but with full agent isolation per iteration).

<!-- STATIC BOUNDARY: everything above this line is stable across invocations and can be cached. Everything below is dynamic - pipeline description, step list, and output file paths change per invocation. -->

## Workflow

### Step 1: Parse the Pipeline

Interpret the user's request and build a pipeline plan:

```
Pipeline: Full QA Sweep
|-- Step 1: /preflight
|-- Step 2: /qa-sweep section-a          [background agent]
|-- Step 3: /qa-sweep section-b          [background agent]
|-- Step 4: /qa-sweep section-c          [background agent]
|-- Step 5: /spec-audit                  [background agent]
\-- Step 6: Aggregate results -> summary report
```

Present the plan to the user. Ask for confirmation before launching.

### Step 2: Create the Output File

Create a timestamped pipeline results file:

```
pipeline-results-YYYY-MM-DDTHH-MM.md
```

Location: `<project-root>`.

Write the header:

```markdown
# Pipeline Results -- [pipeline name]
Started: [timestamp]
Status: Running

## Steps
```

### Step 3: Launch Background Agents

For each step in the pipeline, spawn a sub-agent using the Agent tool with `run_in_background: true`.

**Each agent's prompt includes:**
1. The specific skill instructions (read from the skill's SKILL.md file)
2. The arguments/flags for this step
3. Instructions to write findings to the shared output file
4. Context from previous steps (if sequential)

**Model routing per step** (see docs/MODELS.md): pass `model` on each Agent call —
- `read-only` QA/audit steps → `model: "sonnet"` (pattern-matching against a rubric; Sonnet 5 is the right tier and runs 5-way parallel cheaply)
- `write` steps (ui-styling, work-orders) → `model: "sonnet"`, escalate a step to `"opus"` only if it failed on Sonnet in a previous iteration
- purely mechanical steps (log collation, result formatting) → `model: "haiku"`
- the final aggregation/summary runs in the main session (inherits its model) — it's the judgment step

On Claude Code v2.1.145+, prefer preloading the skill via the agent's `skills:` frontmatter (or spawning a subagent type that declares it) over pasting the full SKILL.md into the prompt — same content, cached once instead of re-sent per step.

**Concurrency classification (determines launch strategy):**

Before launching, classify each step as one of:
- `read-only` - the step only reads files, code, or browser state (grep, screenshot, audit). Safe to run in parallel with any other read-only step.
- `write` - the step modifies files, code, or backlog entries. Must run serially - never in parallel with another write step.
- `sequential` - the step explicitly depends on output from the prior step (e.g., review-ui runs first, then ui-styling uses its findings). Run after the prior step completes.

Apply this rule: **if all pending steps are `read-only`, launch them all simultaneously in a single message as concurrent Agent tool calls.** If the next step is `write` or `sequential`, wait for all prior steps to complete first.

Most QA skills (qa-sweep, spec-audit, audit-page, perf-trace, review-ui) are read-only - they can run in parallel. Most write skills (ui-styling, work-orders, deploy) are write - run them serial.

**For sequential pipelines:**
- Wait for each agent to complete before launching the next
- Pass the previous agent's summary as context to the next agent

**For parallel pipelines (read-only steps only):**
- Launch all read-only agents simultaneously in a single message with multiple Agent tool calls
- Collect results as they complete
- Then proceed to any write or sequential steps serially

**Agent prompt template:**
```
You are running step [N] of a background QA pipeline.

Your task: Run the equivalent of [skill invocation] against the running app.

[Paste the full SKILL.md content here]

Arguments: [flags, target, etc.]

Previous step findings (if any):
[Summary from previous agent]

IMPORTANT:
- Complete the full skill workflow as described
- Be thorough - you have the full context window to work with
- Write your findings in plain language
- At the end, write a concise summary (under 500 words) of your findings
- Do NOT modify code unless explicitly told to fix issues
```

### Step 4: Collect and Aggregate Results

As each background agent completes:
1. Read its output
2. Append a formatted section to the pipeline results file
3. Update the status

### Step 5: Generate Summary Report

After all steps complete, write a final summary to the pipeline results file:

```markdown
## Pipeline Summary
Completed: [timestamp]
Duration: [total time]

### Results by Step
| Step | Skill | Critical | Warnings | Friction | Score |
|------|-------|----------|----------|----------|-------|
| 1 | /qa-sweep section-a | 0 | 1 | 2 | 85% |
| 2 | /qa-sweep section-b | 1 | 0 | 1 | 70% |
| ... | ... | ... | ... | ... | ... |

### Top Priorities (across all steps)
1. [Most critical finding from any step]
2. [Second most critical]
3. [Third most critical]

### Overall Verdict: [SHIP / NEEDS WORK / NOT READY]
[One paragraph plain-language assessment]
```

Notify the user that the pipeline is complete and point them to the results file.

---

## Skill I/O Contracts

Skill concurrency classification for pipeline planning. Skills not listed here are assumed `read-only` unless their name includes "styling", "orders", or "deploy".

EDIT THIS TABLE for your project's skill set.

| Skill | Concurrency | Outputs |
|---|---|---|
| qa-sweep | read-only | findings report |
| audit-page | read-only | lighthouse scores |
| perf-trace | read-only | perf trace report |
| review-ui | read-only | screenshot + findings |
| spec-audit | read-only | drift report |
| smoke-check | read-only | PASS/FAIL verdict |
| preflight | read-only | env status |
| test-flow | read-only | flow report |
| ui-styling | write | modified component files |
| work-orders | write | backlog updates + commits |
| deploy | write | git push |

---

## Pre-built Pipelines

EDIT THIS SECTION for your project. The defaults below are illustrative.

### `full-qa`
```
/bg-pipeline full-qa
```
Runs: preflight -> [qa-sweep section-a + qa-sweep section-b + qa-sweep section-c + spec-audit] (parallel, all read-only) -> summary

### `pre-deploy`
```
/bg-pipeline pre-deploy
```
Runs: preflight -> [qa-sweep section-a + qa-sweep section-b + review-ui + audit-page] (parallel, all read-only) -> summary

### `design-pass`
```
/bg-pipeline design-pass
```
Runs: review-ui (read-only) -> ui-styling area-a (write, serial) -> ui-styling area-b (write, serial) -> review-ui (read-only, re-verify) -> summary

### `friction-sweep`
```
/bg-pipeline friction-sweep
```
Runs: test-flow for each major user flow with --friction flag (all read-only, launch in parallel). Replace these flows with the ones that matter for your app:
1. Complete onboarding as new user
2. Navigate primary tabs
3. Complete the core action loop
4. Admin / privileged action
5. Social / collaboration action

---

## Continuous Mode

When invoked with `continuous:` prefix:

```
/bg-pipeline continuous: /qa-sweep all
```

1. Run the pipeline once as a background agent
2. When it completes, wait 15 minutes (or user-specified interval)
3. Launch a fresh background agent for the next iteration
4. Each iteration appends to the same results file with a timestamped section
5. Continues until the user says stop or the session ends

Each iteration starts fresh (clean context window) but references the previous iteration's findings to highlight what changed.

---

## Failure Modes

- **Step timeout** -- a background agent that has produced nothing well past its expected window (default assumption: ~30 minutes per step) is timed out. Mark the step `TIMEOUT` in the results file, retry it at most once, and keep launching steps that don't depend on it. Never block the whole pipeline waiting on one silent agent.
- **Partial results file** -- an agent that dies mid-write leaves its section truncated. Treat any step section missing its closing summary as `FAILED (partial)`: keep what landed, and have the aggregation step flag those findings as incomplete rather than silently averaging them into the scores.
- **Two steps writing the same file** -- never allowed. At plan time, require disjoint outputs: each write step's output paths (see the Skill I/O Contracts table) must not overlap with any other step's in the same pipeline. If the requested pipeline would violate this, serialize the conflicting steps or split their output files before launching. (The shared pipeline results file is the known exception -- appends to it are serialized through the orchestrator; parallel agents must never write it directly at the same time.)

---

## Important Notes

- Each background agent gets a full, clean context window - that's the whole point
- The main session stays responsive while agents work in the background
- Results accumulate in the pipeline results file, not in your conversation
- If an agent fails or times out, note it in the results and continue with the next step
- For pipelines that modify code (e.g., ui-styling), use `isolation: "worktree"` to prevent conflicts between parallel agents
- The user will be notified as each background agent completes
- Keep agent prompts self-contained - each agent knows nothing about the main conversation
