---
name: distill
description: "Convert marathon-research outputs into ≤200-line summaries/ cards with surgical @-references back to the marathon and canonical source files. Invoke with /distill (auto-detect new marathons) or /distill <slug> (just one). Auto-fired by marathon-research Phase 4 (step 5) after a marathon completes."
---

# Distill — Marathon → Summary Card

## Purpose

Turn raw marathon-research output (5,000-7,000 lines, 200+ sources, dense) into surgical summary cards (≤200 lines each) that work orders, CLAUDE.md cascades, and other skills can actually pull into context.

Each summary card is the **canonical entry point** for a topic: read the card first, descend into the marathon or canonical only when the card doesn't answer the question.

## When this fires

- **Manually** — user runs `/distill` (auto-detect) or `/distill <topic-slug>` (specific one).
- **Automatically** — `marathon-research` Phase 4 (step 5) invokes `/distill` after every marathon completion. Each completed marathon slug is converted to a summary card before the marathon report is finalized.

## Invocation

```
/distill                           Auto-detect: scan <project-root>/research/_index.md for stubs that need filling, distill them all in parallel
/distill <topic-slug>              Distill a specific summary (e.g. /distill qbo-integration). Slug = the basename of summaries/<slug>.md
/distill --slug <marathon-slug>    Distill a specific marathon (e.g. /distill --slug 2026-05-05-qbo-api-integration-...). Useful right after a single-topic marathon
/distill --dry-run                 Print the plan (which stubs would be filled, which marathons would be summarized) without spawning agents
/distill --refresh <topic-slug>    Re-distill an already-existing summary. Overwrites the prior file. Use when canonical/marathon material has changed
```

## Hard Rules

1. **≤200 lines per summary card.** Enforced by line-count check after the agent returns; if exceeded, agent is re-prompted with a "trim to 200 lines" instruction. Hard cap from `<project-root>/research/CLAUDE.md`.
2. **Surgical @-references.** Every non-obvious factual claim has a repo-relative `@research/...` reference. The card must NOT restate large blocks of canonical or marathon prose — it must point at them.
3. **Read order is preserved.** Card structure:
   - Audience+purpose intro (one paragraph)
   - Key Facts (the must-know numbers and policies)
   - Recommended Architecture / Decisions
   - Open Questions / [UNVERIFIED]
   - Action Items (consumable by `/backlog`)
   - Source Map (topic → @-ref)
4. **Don't bluff.** If the marathon is silent on a sub-question, the card is silent too. Don't invent claims to fill the structure.
5. **`_index.md` updates are atomic with the summary write.** When a summary is written, the corresponding `_(summary stub)_` line in `_index.md` is replaced with a one-line description in the same operation.

---

## Workflow

### Phase 0: Parse args

- `--dry-run`: build the plan, print it, stop. Do NOT spawn agents or write files.
- `--refresh <topic-slug>`: skip the "stub exists" check for this slug; treat as eligible.
- `--slug <marathon-slug>`: pin to one marathon directory; derive topic-slug from `_index.md`.
- `<topic-slug>` positional: target a specific summary filename (without `.md`).
- No args: auto-detect — every topic section in `_index.md` that has at least one marathon AND a `_(summary stub)_` placeholder is eligible.

### Phase 1: Build the work list

Read `<project-root>/research/_index.md`. The file is structured as `### <Topic>` sections, each containing:
- `- canonical/<file>` lines (background)
- `- marathons/<slug>/` lines (deep research)
- `_(summary stub)_ → summaries/<slug>.md` lines (the gap)
- `- summaries/<slug>.md — <description>` lines (already-distilled, skip in auto-detect)

For each eligible topic section, build:

```js
{
  topicHeading: "QBO Integration & Bookkeeping",
  summaryPath: "<project-root>/research/summaries/qbo-integration.md",
  marathonDirs: ["<project-root>/research/marathons/2026-05-05-qbo-api-..."],
  canonicalFiles: ["<project-root>/research/canonical/Streamlining...", ...],
  topicSlug: "qbo-integration",   // derived from summaries/<slug>.md
}
```

Skip topics that:
- Have no marathon line (nothing to distill from).
- Already have a non-stub `summaries/<slug>.md` line (unless `--refresh`).

### Phase 2: Present the plan

```
DISTILL PLAN
============
Eligible topics: [N]

  qbo-integration     ← marathons/2026-05-05-qbo-api-... + 8 canonical files
  tax-mapping         ← marathons/2026-05-05-automated-coa-... + 7 canonical files
  ...

Output: <project-root>/research/summaries/<topic-slug>.md
Index updates: <project-root>/research/_index.md (replace stubs in-place)

For dry-run: stop here.
```

### Phase 3: Spawn distill agents in parallel

For each eligible topic, spawn `Agent(subagent_type: general-purpose, model: sonnet)` with the prompt template below. Send all agents in a single message (parallel execution).

Sonnet is the right model — distillation is synthesis-light: re-organize and surgically reference, don't deeply re-reason. Opus would be overkill and slow.

### Phase 4: Validate each summary

For each returned agent:

1. **Line count.** Read the file; if `> 200`, send the agent a re-prompt: "Trim to ≤200 lines. The current file is N lines. Preserve all action items and the source map. Cut: extended prose, redundant restatements, anything not surgically @-referenced."
2. **@-reference presence.** Grep the file for `@research/`. If zero matches, send the agent a re-prompt: "Add at least one @research/ surgical reference per Key Fact and per Action Item."
3. **Index update.** The agent should already have replaced the `_(summary stub)_` line in `_index.md`. If not, do it now via Edit: replace `_(summary stub)_ → \`summaries/<slug>.md\`...` with `\`summaries/<slug>.md\` — <one-line description>`.

### Phase 5: Report

```
DISTILL COMPLETE
================
Summaries written: [N]
  qbo-integration       131 lines, 24 @-refs
  tax-mapping           156 lines, 31 @-refs
  ...

Index updated: <project-root>/research/_index.md
Read order is now: summary → marathon → canonical (per research/CLAUDE.md).
```

---

## Sonnet Distill Agent Prompt Template

```
Write a research summary card at <project-root>/research/summaries/<topic-slug>.md

Audience: senior engineers reading this BEFORE writing a backlog work order touching <topic area>.

Sources to read and synthesize:

MARATHON (priority — most current, supersedes canonical where they conflict):
<list each marathon file in the topic's marathon folder>

CANONICAL (longer-term context — supplement, don't restate):
<list each canonical file linked from this topic section in _index.md>

== HARD CONSTRAINTS ==
1. ≤200 lines (per <project-root>/research/CLAUDE.md).
2. Surgical @-references for every non-obvious claim. Format: @research/marathons/<slug>/<file>.md or @research/canonical/<filename> — repo-relative paths starting with @research/.
3. Don't restate canonical prose. Cite it and move on.
4. Mark anything the marathon flagged [UNVERIFIED] as such here too.
5. After writing the file, update <project-root>/research/_index.md to replace the _(summary stub)_ placeholder for this topic with: `summaries/<topic-slug>.md` — <one-line description ≤120 chars>.

== STRUCTURE (use these H1/H2 sections exactly) ==

# <Topic Display Name> — Summary

One-paragraph audience+purpose intro.

## Key Facts (the numbers and policies an engineer must know)
- Bullet per concrete fact, with @-ref.

## Recommended Architecture / Decisions
- The N things <package> should own. Reference architecture diagrams in ASCII if the marathon used one.

## Open Questions / [UNVERIFIED]
- Anything the marathon flagged as unverified or where official docs are absent.

## Action Items (consumable by /backlog)
- Numbered, ≤1 line each, each implies a near-term work order.

## Source Map
- Bulleted list of topic → @-ref.

== OUTPUT ==
Use the Write tool to write the summary file directly. Use the Edit tool to update _index.md. Then output one line: "WROTE <topic-slug>.md (N lines)" with the line count. No other commentary.

Begin.
```

---

## Wire-up with marathon-research

`marathon-research` Phase 4 (step 5) invokes `/distill` automatically after the marathon report is generated. The integration is:

```
Phase 4 (marathon-research): Marathon Complete
  → ... existing steps ...
  → CronDelete, mark state complete, write final report
  → Phase 4 (step 5): invoke /distill (auto-detect mode)
  → Distill runs in same Claude session, finishes typically in <3 min for 5 topics
  → Marathon's final report includes a "Summaries written:" section

Phase 4 (step 5) (distill): Auto-detect + parallel distill
  → Reads research/_index.md
  → Finds the just-completed marathon slugs (they have stubs)
  → Spawns N Sonnet agents in parallel
  → Updates _index.md and writes summaries/<slug>.md per topic
```

To invoke `/distill` from inside `marathon-research` Phase 4 (step 5), the running Claude calls `Skill(skill: "distill")`. No CLI shell-out, no hooks file — the wiring is a documented step in the marathon-research SKILL.md and a working Skill-tool call.

**Why a Skill-tool call and not a hooks-file hook?** Claude Code hooks (PreToolUse/PostToolUse/Stop) can run shell commands but cannot invoke Skills — Skills must be invoked by the running Claude. Skill-to-skill chaining via the Skill tool is the supported pattern for this kind of "fire X at end of Y" composition.

---

## Failure modes

1. **Summary exceeds 200 lines after re-prompt.** The agent has had two chances. Save the over-cap file with a `.draft.md` extension and write a `_distill-error.md` to the summaries directory noting the topic. Do NOT update `_index.md` for that topic — the stub stays.
2. **Marathon directory is missing a `meta.json`.** That topic was never finalized. Skip silently.
3. **Topic section in `_index.md` has multiple marathon lines.** The agent reads all of them — it's a multi-marathon topic. Common when a topic has had repeated research passes.
4. **`_index.md` parse fails.** The skill is index-driven; if the index is malformed, the skill prints the parse error and stops. Do not attempt to repair.

---

## Important notes

- **Sonnet, not Opus.** Distillation is light synthesis. Opus is overkill and 3-4× slower for this task. Reserve Opus for the deep-research phase.
- **Parallelism is intentional.** All eligible topics distill in parallel. Five topics finish in ~3 minutes wall-clock.
- **`_index.md` is the source of truth for topic groupings.** The skill is intentionally index-driven so that adding a new topic section to `_index.md` (with a marathon line + a stub) is the only change needed for a new topic to be picked up.
- **Use `--refresh` sparingly.** Summaries are stable artifacts; re-distilling churns the index and changes @-references that work orders may depend on.
