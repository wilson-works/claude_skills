---
name: quick-design
description: "Lightweight spec for small feature/architecture changes (tuning, tweaks, additions) that don't warrant a full design council. Classifies the change, scans for cross-system conflicts, documents the decision, and files it. Invoke with /quick-design [change description]."
---

# Quick Design Skill

## Purpose

Not every change needs a heavyweight design review. Small tweaks (raise a rate-limit threshold, add a new toggle, change a default value, add a new enum variant) need a quick spec that classifies the change, checks for cross-system conflicts, documents the decision, and moves on. This skill is the lightweight counterpart to a full council/RFC process. Use it when the right answer is mostly clear but you still want the decision recorded.

## Configure for your project

Before first use, replace the following placeholders in this file (or fork it into a project copy):

- `<src-path>` — path to your primary source tree (e.g. `src/`, `apps/web/src/`, `lib/`)
- `<core-package-path>` — path to the package or module that owns business logic
- `<quick-specs-path>` — where short specs are saved (e.g. `docs/quick-specs/` or `design/quick-specs/`)
- `<design-doc-paths>` — paths to existing design/architecture docs (e.g. `DESIGN.md`, `ARCHITECTURE.md`)
- `<systems-map-skill>` — the skill name for your systems map (or remove references if you don't have one)
- `<council-skill>` — the slash command for your heavyweight design review (e.g. `/llm-council`, `/rfc`)

## Invocation

```
/quick-design raise default page size from 25 to 50
/quick-design add a new "draft" status to the workflow enum
/quick-design lower the password reset token TTL from 24h to 1h
/quick-design add an opt-in feature flag for compact mode
```

**Argument:** A one-sentence description of the change.

## When to use `/quick-design` vs `<council-skill>`

Use `/quick-design` when:
- The change is numerically bounded (tuning a value, not redesigning a system)
- The affected surface is 1-2 files
- You know roughly what the right answer is and want a sanity check, not a debate
- The change won't meaningfully shift architecture, public API, or user behavior

Use `<council-skill>` when:
- Multiple reasonable approaches exist
- The change affects 3+ systems or 3+ files
- It touches data model, security boundaries, or core algorithms
- You want a structured pressure-test with adversarial review

## Prerequisites

- File read access to `<core-package-path>` and `<src-path>`
- Write access to `<quick-specs-path>`

## Workflow

### Step 1: Classify the Change

Assign one of three types:

- **Tuning**: A number/string change within an existing system. Examples: raise a default, drop a cap, change a timeout.
- **Tweak**: A behavior change within an existing system. Examples: a setting now applies per-user instead of per-team; a job now runs at 6am local instead of 9am.
- **Addition**: A new option inside an existing system. Examples: a new enum variant, a new optional config key, an additional output format.

If the change is actually a new system (not fitting inside an existing one), stop and recommend `<council-skill>` instead.

### Step 2: Scan for Cross-System Conflicts

For each type, check specific files:

**Tuning:**
- Read the module that owns the value
- Read any systems-map or dependency docs to see downstream consumers
- Check `<design-doc-paths>` for documented targets the new value would violate
- Flag if the new value crosses a documented boundary

**Tweak:**
- Read the module's behavior code
- Check for hardcoded assumptions elsewhere (server-side jobs, timezone handling, cached views)
- Flag any UI components or docs that describe the old behavior explicitly

**Addition:**
- Check if the new option collides with an existing one (duplicate name, overlapping trigger)
- Check if the type system supports it without edits to shared types
- Flag any admin/config schema or migration that would need updating

### Step 3: Present Findings

In one concise response, output:

```
## Quick Design: [change description]

**Type:** Tuning | Tweak | Addition

**Affected files:**
- <core-package-path>/[file1] (primary)
- <src-path>/[file2] (UI / consumer, if applicable)

**Conflicts / Considerations:**
- [e.g., "New default crosses the documented limit in <design-doc>"]
- [e.g., "Existing config UI doesn't surface this value; add input field"]
- [or "No conflicts found."]

**Downstream systems to re-verify:**
- [e.g., "Re-run integration tests for the X consumer"]
- [or "None."]

**Recommendation:** PROCEED | PROCEED WITH NOTED FIXES | RECONSIDER (elevate to <council-skill>)
```

### Step 4: Document the Decision

After user confirms the change, save a short spec to `<quick-specs-path>/[YYYY-MM-DD]-[kebab-name].md`:

```markdown
---
change: [change description]
type: [Tuning|Tweak|Addition]
status: planned | implemented
date: [YYYY-MM-DD]
---

# [Change Name]

## What changed
[One paragraph: before -> after]

## Why
[One paragraph: rationale, reference any prior decision or target]

## Affected files
- [file 1]
- [file 2]

## Cross-system verification
- [check 1]
- [check 2]

## Follow-up
- [e.g., "Re-run perf benchmarks next week"]
```

Never overwrite an existing spec. If a previous quick-spec addressed the same area, reference it rather than replacing it.

### Step 5: Link to Implementation

Print the suggested next step:
- If the user wants to implement now: offer to file a work item or run the change directly (for trivial tuning, can edit the file directly with user confirmation)
- If the change needs more thought: offer to escalate via `<council-skill>`

## Principles

- **Quick should be quick.** This entire skill should complete in under 2 minutes of real time. If the analysis is taking longer, escalate.
- **Document the decision, not the debate.** Quick-specs record what changed and why, not the alternatives considered.
- **Link to the systems map.** When available, cite it to identify downstream verification needs.
- **Respect prior decisions.** If a prior ruling contradicts the proposed tuning, flag it and recommend elevation.

## Anti-Patterns

- Do not produce a multi-page spec. If the change needs that, it's not a quick-design.
- Do not silently skip cross-system checks even for "obvious" changes. The whole point is catching hidden conflicts.
- Do not edit code from this skill. Output the spec; the user decides when to implement.
- Do not create a quick-spec for a change that hasn't been decided yet.
