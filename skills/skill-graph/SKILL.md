---
name: skill-graph
description: "Builds and queries a machine-readable graph of your skill pack: every skill becomes a node with its invocation, triggers, and the artifacts it produces and consumes; Pairs-with lines and workflow text become edges. Answers routing questions (what consumes X, what runs after Y), lists interconnection debt with proposed fixes, and maintains the artifact contract registry that chain-running skills rely on. Invoke with /skill-graph [query|debt|registry] [args]."
---

# Skill Graph

## Purpose

A skill pack grows one skill at a time, but its value compounds only when skills hand off to each
other — and those handoffs live as prose (`Pairs with:` lines, "feed this to /X" sentences) that
no tool can traverse. The result: routing questions ("what should I run after a meeting digest?")
get answered from memory, new skills ship disconnected, and nobody notices which handoffs silently
broke when a skill's output format changed.

This skill mines every `SKILL.md` in the pack into a single machine-readable graph — nodes,
edges, and an artifact contract registry — plus a human-readable Mermaid view. It answers routing
queries from data instead of memory, measures interconnection debt, and generates (never applies)
the missing `Pairs with:` lines. The graph file is the source of truth for what CAN chain;
chain-library skills record what SHOULD chain and reference this registry for handoff formats.

## Configure for your project

Before using this skill, set these placeholders:

- `<skills-repo-path>`: Absolute path to the repo root containing `skills/` (e.g.
  `~/repos/my_claude_skills`). All mining happens under `<skills-repo-path>/skills/`.
- `<graph-path>`: Where the graph data file lives. Default and recommended:
  `<skills-repo-path>/skills/skill-graph/graph.json` — keeping it inside this skill's folder means
  the graph travels with the pack.
- `<proposals-path>`: Where debt mode writes proposed `Pairs with:` lines for human review.
  Default: `<skills-repo-path>/skills/skill-graph/pairs-with-proposals.md`.

## Invocation

```
/skill-graph                       -- build or refresh the graph; report what changed
/skill-graph query "<question>"    -- routing question answered from graph data
/skill-graph debt                  -- interconnection debt report + proposed Pairs-with lines
/skill-graph registry [artifact]   -- artifact contract registry (all, or one artifact)
```

## Mode 1: Build / Refresh (default)

### Step 1: Mine every skill into a node

Scan `<skills-repo-path>/skills/*/SKILL.md`. For each file, extract one node:

| Field | Source in SKILL.md |
|-------|--------------------|
| `name` | frontmatter `name:` |
| `invocation` | the `Invoke with /...` sentence in the description |
| `triggers` | trigger phrases / "use when" clauses in the description |
| `category` | best-guess label from description (audit, research, content, ops, finance, qa, meta) |
| `produces` | artifacts the workflow writes (files, reports, backlog items) + where |
| `consumes` | artifacts the workflow reads that another skill produces |
| `pairs_with` | skills named on the `Pairs with:` line, if present |

### Step 2: Classify every edge as declared or inferred

- **Declared** — the skill names the relationship explicitly (`Pairs with:` line, or workflow text
  that says "hand this to /X"). High confidence.
- **Inferred** — mining matched an artifact one skill writes to a path/format another skill reads,
  but neither file names the other. Real coupling, undeclared. These are the debt-mode raw material.

Every edge carries `{from, to, type, basis}` where `type` is one of `pairs_with | produces |
consumes | hands_off_to` and `basis` is `declared | inferred`.

### Step 3: Write the graph and diff against the previous one

Write `<graph-path>` (JSON). If a previous graph exists, report the delta — nodes added/removed,
edges added/removed, contract changes — instead of dumping the whole graph:

```
GRAPH REFRESH — 2026-07-06
Nodes: 130 (+2: skill-graph, power-chains)   Edges: 61 (+14 declared, +3 inferred)
Contract changes: 1 — "learnings note" gained consumer claude-md-doctor
Pairs-with coverage: 16/130 (was 14/128)
```

### Step 4: Render the human view

Write a Mermaid directed graph next to the data file (`graph.md`), clustered by category, edge
style distinguishing declared (solid) from inferred (dashed). For a richer rendered diagram, hand
the JSON to `/arch-diagram`.

### Graph data shape (fenced example, wave-1 edges shown as data)

```json
{
  "generated": "2026-07-06",
  "nodes": [
    {
      "name": "extract-approach",
      "invocation": "/extract-approach [args]",
      "category": "meta",
      "produces": [{ "artifact": "learnings-note", "where": "notes/learnings/" }],
      "consumes": [],
      "pairs_with": ["retro", "notetaker", "distill", "claude-md-doctor", "harness-audit"]
    },
    {
      "name": "claude-md-doctor",
      "invocation": "/claude-md-doctor [audit|rewrite]",
      "category": "meta",
      "produces": [{ "artifact": "claude-md-rewrite", "where": "CLAUDE.md" }],
      "consumes": ["learnings-note", "decision-record", "harness-audit-findings"],
      "pairs_with": ["extract-approach", "decision-policy", "harness-audit", "rules-gate", "budget-mode", "skill-builder"]
    }
  ],
  "edges": [
    { "from": "extract-approach", "to": "claude-md-doctor", "type": "hands_off_to", "basis": "declared" },
    { "from": "harness-audit", "to": "backlog", "type": "hands_off_to", "basis": "declared" },
    { "from": "decision-policy", "to": "claude-md-doctor", "type": "hands_off_to", "basis": "declared" },
    { "from": "attack-surface", "to": "weekly-review", "type": "hands_off_to", "basis": "declared" }
  ],
  "registry": [
    {
      "artifact": "learnings-note",
      "produced_by": "extract-approach",
      "consumed_by": ["claude-md-doctor", "harness-audit", "retro"],
      "format": "one atomic note per file; frontmatter name/description; body states trigger + rule"
    },
    {
      "artifact": "backlog-item",
      "produced_by": "backlog",
      "consumed_by": ["work-orders", "council-rd", "harness-audit"],
      "format": "backlog item with category, priority, and status per the backlog skill's format"
    }
  ]
}
```

## Mode 2: Query

Answer routing questions from `<graph-path>` — never from memory of the pack. If the graph is
older than the newest SKILL.md mtime, refresh first. Supported question shapes:

- **"what consumes X?"** / **"what produces Y?"** — direct registry lookup.
- **"chain from artifact A to artifact B"** — shortest path over produces/consumes edges; list
  every intermediate skill and the artifact handed off at each hop.
- **"what should I run after /X?"** — every outbound `hands_off_to` and `pairs_with` edge from X,
  declared edges first.

```
QUERY: what should I run after /meeting-digest?
Declared: /weekly-review (digest feeds the weekly sweep)
Inferred: /backlog (digest action items match backlog's item format — edge undeclared)
Chain note: meeting-digest → weekly-review → monday-brief is a known 3-hop path.
```

## Mode 3: Debt

1. List every skill with **no** `Pairs with:` line (coverage was 14/128 at first measurement).
2. For each, generate a proposed line from its inferred edges — only edges with a concrete basis
   (matched artifact or named handoff in workflow text), never speculative pairings.
3. Write all proposals to `<proposals-path>`, grouped by confidence, each with its evidence line.

This mode **never edits other skills**. Applying proposals is a separate, human-approved step —
batch application needs its own explicit order/PR, because a wrong declared edge is worse than a
missing one.

```
DEBT REPORT — 2026-07-06
Coverage: 16/130 skills declare Pairs with (114 missing)
Proposals written: 41 high-confidence, 22 medium → pairs-with-proposals.md
Top orphans (no edges in or out at all): file-organizer, image, video
```

## Mode 4: Contract Registry

The registry section of the graph is the pack's artifact vocabulary: every named artifact, who
produces it, who consumes it, and the file/section format each consumer relies on. This is the
drift-protection layer — when a producer changes its output format, `registry <artifact>` shows
exactly which consumers must be checked. Chain-running skills (see `power-chains`) reference
registry entries for their handoffs instead of re-describing formats inline.

`/skill-graph registry learnings-note` prints that artifact's entry plus a staleness check: does
the producer's SKILL.md still describe the registered format? Mismatch → flag, don't guess.

## Failure Modes

- **Mining prose is heuristic.** `produces`/`consumes` extraction from workflow text will miss
  artifacts described obliquely and occasionally invent a match. That is why every inferred edge
  carries its evidence and debt proposals are review-gated — treat the graph as evidence, not truth.
- **Stale graph answering queries.** A query against a graph older than the pack's newest SKILL.md
  gives confidently wrong routing. The mtime check in Mode 2 is mandatory, not optional.
- **Registry drift.** A producer skill edits its output format without updating consumers. The
  registry staleness check catches format-description drift, but only when someone runs it — pair
  refreshes with your periodic skill audit (`/skill-stocktake`).
- **Debt proposals applied blindly.** A generated `Pairs with:` line that pairs the wrong skills
  actively misroutes future sessions. Proposals ship to a file for review, never directly into
  other skills' files.

## Important Notes

- **Regenerate, never hand-edit.** `graph.json` is derived data; fix the source SKILL.md and
  refresh. Hand edits are overwritten by the next build.
- **Declared beats inferred everywhere:** query answers rank declared edges first, and debt mode
  exists to convert good inferred edges into declared ones — through review.
- **New skills register at birth:** when authoring a skill, run a refresh afterward so the graph
  picks up its edges; the authoring skill's `Pairs with:` requirement is what makes this work.
- **Scope boundary:** this skill maps and proposes; it does not execute chains (that is the chain
  library's job) and does not edit other skills (debt proposals are review-gated by design).
- Pairs with: `/power-chains` (chains are authored from graph queries and reference the contract
  registry), `/skill-stocktake` (quality audit uses the graph to find orphans and overlap),
  `/bg-pipeline` (its Skill I/O Contracts table is a hand-kept ancestor of the registry),
  `/arch-diagram` (renders the graph JSON as a styled diagram).
