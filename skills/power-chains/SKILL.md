---
name: power-chains
description: "A library of named, versioned multi-skill playbook chains with a gated runner: each chain file declares its steps as skill invocations, the explicit artifact handoff between every step (what gets written where, and how the next step reads it), and a per-step gate — outward-facing or destructive steps always STOP for explicit user resume. Ships four canonical chains and an authoring mode that scaffolds new chains from skill-graph queries. Invoke with /power-chains [run|author|report] [chain]."
---

# Power Chains

## Purpose

The pack's skills compose — a meeting digest feeds the weekly review, research reports distill
into council-reviewed work orders — but the compositions live in users' heads. Every run of a
multi-skill playbook is reinvented: which skill first, where its output landed, what to hand the
next step. `bg-pipeline` can execute a sequence, but it has no library; nothing records the chains
that are known to work, their handoffs, or where a human must stay in the loop.

This skill is that library plus its runner. A chain is a named, versioned file: steps as skill
invocations, an explicit artifact handoff per step, and a per-step gate. The graph of what CAN
chain lives in `skill-graph`; this skill records what SHOULD chain and why. Handoff formats are
referenced from skill-graph's contract registry, never re-described inline — when a producer's
format changes, the registry flags every chain that depends on it instead of each chain drifting
separately.

## Configure for your project

Before using this skill, set these placeholders:

- `<chains-path>`: Directory holding one file per chain (e.g. `<project-root>/chains/`). The six
  canonical chains ship here on first run.
- `<project-root>`: Where completion reports are written (matches `bg-pipeline`'s results
  location so background and inline runs land reports in the same place).

## Invocation

```
/power-chains                      -- list chains with when-to-run triggers and last-run status
/power-chains run <chain>          -- execute a chain inline, honoring gates
/power-chains run <chain> --bg     -- execute via /bg-pipeline as background agents
/power-chains author "<goal>"      -- scaffold a new chain from a skill-graph query
/power-chains report [chain]       -- show the latest completion report
```

## Chain definition format

One file per chain in `<chains-path>`, named `<chain-name>.chain.md`. Format:

```markdown
# chain: launch-day  (v1)
when-to-run: shipping a launchable release and the launch date is set

steps:
  1. skill: /product-marketing-context
     writes: product context doc            -> registry: product-context
     next-step-reads: positioning + ICP sections
     gate: continue
  2. skill: /launch-strategy
     reads: product-context (step 1)
     writes: launch plan with channel list  -> registry: launch-plan
     gate: continue
  3. skill: /directory-submissions
     reads: launch-plan channel list (step 2)
     writes: submission tracker
     gate: STOP  -- submits to external directories; resume only on explicit user go
  4. skill: /social-content
     reads: launch-plan + product-context
     writes: launch posts + content calendar
     gate: STOP  -- publishing is outward-facing; drafts may proceed, posting may not
  5. skill: /analytics-tracking
     reads: launch-plan channel list
     writes: tracking plan (UTMs per channel)
     gate: continue
on-failure: halt chain, write partial completion report, list completed steps + artifacts
```

Rules the format enforces:

- **Every handoff is explicit.** Each step names what it writes, where, and what the next step
  reads from it. "Run A then B" without a named artifact between them is not a valid chain.
- **Registry references, not format descriptions.** Where an artifact has a contract registry
  entry (see `/skill-graph registry`), the step points to it (`-> registry: <artifact>`). The
  chain file never restates the format — drift protection lives in one place.
- **Gates are per-step:** `continue` (proceed automatically), `STOP` (halt; explicit user resume
  required), `detour: <chain>` (branch to another chain, then return).
- **Version on every change.** Editing a chain bumps its `(vN)` and notes what changed — a chain
  that silently mutates can't be trusted by the runs that reference it.

## Runner mode

1. Read the chain file; resolve every registry reference against `/skill-graph registry` — a
   missing or stale registry entry is a pre-flight failure, not a mid-run surprise.
2. Execute steps in order. Inline: invoke each skill directly. `--bg`: hand the step list to
   `/bg-pipeline` (sequential mode), preserving gate semantics — a STOP gate ends the background
   segment and notifies; the next segment launches only on user resume.
3. At each gate: `continue` proceeds; `STOP` halts with a summary of what the halted step will do
   once resumed; `detour` runs the named chain and returns.
4. Write the completion report to `<project-root>`:

```
CHAIN COMPLETE — weekly-ops (v1)             2026-07-06
| # | Skill            | Artifact produced          | Gate      |
|---|------------------|----------------------------|-----------|
| 1 | /meeting-digest  | digests/2026-07-06-ops.md  | continue  |
| 2 | /weekly-review   | reviews/2026-W27.md        | continue  |
Steps run: 2/2 · Gates tripped: none · Failures: none
```

## Shipped canonical chains

Four chains ship with the skill (full definitions in `<chains-path>`; `launch-day` shown in full
above). Handoff column names the artifact passed between consecutive steps:

| Chain | Steps | Key handoffs | STOP gates |
|-------|-------|--------------|------------|
| `launch-day` | product-marketing-context → launch-strategy → directory-submissions → social-content → analytics-tracking | product context → launch plan → channel list → posts/UTMs | directory submissions; social posting |
| `weekly-ops` | meeting-digest (sweep) → weekly-review | digests → weekly review w/ Top 3 | none (local files only) |
| `qa-gauntlet` | preflight → qa-sweep → test-flow → smoke-check → user-feedback | env status → findings → flow report → PASS/FAIL → triaged feedback | none (all read-only; feedback promotes to backlog via its own review log) |
| `research-to-shipped` | marathon-research → distill → council-rd → backlog → work-orders → retro | cited reports → summary cards → approved WOs → backlog items → completed work → retro log | work-orders (writes + commits); council-rd's own HTML approval is a built-in detour |

## Authoring mode

`/power-chains author "<goal>"` scaffolds a new chain instead of hand-writing one:

1. Query the graph: `/skill-graph query "chain from artifact <A> to artifact <B>"` (or "what
   should I run after /X") — the graph proposes the skill path and the artifact at each hop.
2. Convert each hop into a step: fill `writes`/`reads` from the registry entries the graph
   returned; leave a `TODO` on any hop whose artifact has no registry entry yet.
3. Default every step's gate conservatively: anything the graph or the step's own SKILL.md marks
   as outward-facing, destructive, or settings-mutating gets `STOP`; the author downgrades to
   `continue` deliberately, never by default.
4. Write `<chains-path>/<name>.chain.md` at `(v1)` and show it for review — a scaffolded chain is
   a draft until a human has read its gates.

## Failure Modes

- **Gate erosion.** The chain works, so someone flips its STOP gates to `continue` for speed —
  and the next run auto-submits to directories at 2 a.m. Gates on outward-facing/destructive
  steps are the skill's reason to exist; downgrading one requires a version bump and a stated
  justification in the chain file.
- **Handoff drift.** A producer skill changes its output format; chains referencing the old shape
  fail mid-run or, worse, feed the next step garbage. The pre-flight registry resolution catches
  registered artifacts; artifacts without registry entries are the residual risk — get them
  registered rather than describing them in the chain file.
- **Chain sprawl.** Twenty near-identical chains nobody remembers. Before authoring, list existing
  chains; extend or version an existing chain when overlap is substantial. The library earns its
  keep by being short enough to know.
- **Background gate bypass.** Running `--bg` must not turn STOP gates into notifications-after-
  the-fact. The runner splits background execution at every STOP; if `bg-pipeline` can't honor
  that split for a given chain, run it inline instead.

## Important Notes

- **Chains amplify power, so they must not amplify blast radius.** The conservative-gate default
  is deliberate: one skill misfiring is a mistake; a chain misfiring is five mistakes with
  momentum.
- **The library records judgment, not just sequence.** `when-to-run` and the gate rationale are
  as much the content as the step list — a chain file a new user can't read and trust is
  incomplete.
- **skill-graph is the source of truth for what CAN chain;** this library is the curated record
  of what SHOULD chain. Authoring mode is the bridge between the two.
- **Completion reports feed retros:** `research-to-shipped` and any long chain should end with
  `/retro`, and chain reports are input evidence for it.
- Pairs with: `/skill-graph` (contract registry backs every handoff; authoring mode starts from
  graph queries), `/bg-pipeline` (the background executor the runner delegates to),
  `/backlog` (chains that produce work land it as backlog items), `/retro` (chain completion
  reports are retro evidence).
