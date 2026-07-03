---
name: marathon-research-council
description: Condense N completed marathon-research outputs into a build-ready council summary. Convenes a 5-advisor LLM council that reviews the research collectively, peer-reviews each other anonymously, and produces a chairman synthesis plus a per-marathon "build-ready chunk" card. Designed to bridge the gap between raw R&D output (large, exploratory) and backlog work orders (small, executable). Invoke with `/marathon-research-council [marathon-slug ...]` or `/marathon-research-council --since YYYY-MM-DD`.
when_to_use: Use when 3+ marathon-research outputs have completed and need to be condensed before building, or when the user asks to "council the research", "review the marathons", or "turn marathons into work orders".
---

# Marathon-Research Council

A specialized variant of `/llm-council` tuned for **condensing R&D output into build-ready chunks**. Standard `/llm-council` answers a single decision question. This skill answers a different question:

> *"We just produced N marathons of research. Before we start building, what are the load-bearing decisions, where does the research actually disagree with itself or with our constraints, and what are the smallest build-ready chunks we should hand to the backlog?"*

## Configure for your project

Before using this skill, swap these placeholders for your project values:

- `<research-root>` — absolute path to the directory holding marathon-research output folders (e.g. `research/marathons/` or whatever your `/marathon-research` skill writes to)
- `<council-output-dir>` — absolute path where this skill writes the council summary, transcript, and HTML report (e.g. `research/council/`)
- `<research-index>` — optional path to a research index file you want updated with a one-line entry per council session (e.g. `research/_index.md`)
- `<backlog-drafts-dir>` — optional path where draft work-order files land when invoked with `--file-backlog` (e.g. `backlog/_council-drafts/`)
- `<project-context>` — optional path to your project context file (CLAUDE.md, README.md, etc.) — read for the "what we're building" line in the framed brief
- `<distill-skill-name>` — name of your per-marathon distillation skill if you have one (default: `distill`)

If you don't have a marathon-research skill yet, install one first — this skill consumes its output. The companion shape this skill expects:

```
<research-root>/<YYYY-MM-DD>-<slug>/
├── 00-brief.md           # scope brief
├── 01-*.md ... NN-*.md   # numbered deep-research files
├── meta.json             # status, file list, source count, validation
├── sources.md            # citation list
└── _validation-report.md # optional, validator output
```

## When to use this skill

- 3+ marathons have just completed and are sitting in `<research-root>`.
- You're about to start building features that the research informs.
- You need to translate sprawling research into a small number of actionable decisions.
- Future R&D batches will need the same treatment — this skill is meant to be **rerun** every time a new wave of marathons completes.

## When NOT to use this skill

- For a single decision question (use `/llm-council`).
- For mid-marathon scope checks (use `/scope-check`).
- When marathons haven't finished (`meta.json` status != `complete`).
- For per-marathon ≤200-line summary cards (use `/distill` or your project's equivalent).

## Inputs

- A list of marathon slugs (folder names under `<research-root>`), OR
- `--since YYYY-MM-DD` to pick up all marathons completed since a date, OR
- `--all-pending` to pick up every marathon not yet referenced in a council summary.

Optional flags:
- `--file-backlog` — also write draft work-order files to `<backlog-drafts-dir>`.
- `--no-html` — skip HTML report generation (markdown only).

## Outputs

Three artifacts written to `<council-output-dir>`:

1. **`council-summary-<timestamp>.md`** — the canonical build-ready summary. One section per marathon with **Decision**, **Stack pick**, **Open questions**, **Build chunks (≤5)**, **Cross-marathon dependencies**. This is the file the user keeps.
2. **`council-transcript-<timestamp>.md`** — full transcript: framed brief, all 5 advisor responses, all 5 peer reviews (de-anonymized), chairman synthesis.
3. **`council-report-<timestamp>.html`** — visual scannable report (same shape as `/llm-council` but with marathon-aware sections).

## The five advisors (R&D-tuned variants)

Same five thinking lenses as `/llm-council`, but each is briefed on the **build-readiness** problem:

1. **The Contrarian** — what in this research is wrong, contradicted, outdated, or assumes things our codebase doesn't actually have? What load-bearing claim is one source thick?
2. **The First Principles Thinker** — strip the research back. What's the actual problem the research is trying to solve, and is the research solving the right problem? Is there a simpler shape that the marathons missed?
3. **The Expansionist** — what compounding upside is hiding in here? Which two marathons combine into a third capability nobody scoped? What R&D investment do we get for free if we sequence the build right?
4. **The Outsider** — read the research as someone who doesn't know your stack. Which marathons assume context that isn't on the page? Which decisions a fresh engineer would make differently? What's the curse of knowledge here?
5. **The Executor** — what's the smallest thing we can ship from each marathon? Which marathons can be turned into work orders today vs which need a design pass first? Where is the first PR?

## The session flow

### Step 1 — Gather the marathons

For each input slug, read:

- `meta.json` (title, file list, source count, validator verdict)
- `00-brief.md` (scope, sub-questions)
- The **synthesis / recommendations chapter** if present (filename pattern: `*synthesis*`, `*recommendations*`, or the highest-numbered chapter)
- The **anti-patterns / gotchas chapter** if present (filename pattern: `*antipatterns*`, `*gotchas*`, `*incidents*`)
- `_validation-report.md` if present (so the council knows where the research is weakest)

Skip any chapter that's >300 lines unless it's the synthesis chapter — the council does not need the full body, it needs the load-bearing claims.

### Step 2 — Build the context pack

Write a temporary file `<council-output-dir>/.tmp-context-pack-<timestamp>.md`. Structure:

```
# Council Context Pack — <timestamp>

## Marathons under review
- <slug 1> — <title>
- <slug 2> — <title>
…

## Per-marathon condensation

### <slug 1>
**Title:** …
**Source count / validator:** …
**Scope (from 00-brief):** …
**Synthesis (verbatim from synthesis chapter):** …
**Anti-patterns (top 3):** …
**Open questions / weak areas (from validator report):** …

### <slug 2>
…
```

Cap each marathon's section at ~150 lines. The total pack should fit comfortably in one advisor's context.

### Step 3 — Frame the brief

Compose a single framed brief that all 5 advisors will receive. Structure:

```
# Framed Brief

## What we're building
<3 lines from <project-context> mission + relevant memory>

## What just landed
<one-line description of each marathon and why it was queued>

## What the council must answer
1. For each marathon, what is the build-ready decision (or set of decisions) this research enables?
2. Which marathons depend on which? What's the right build sequence?
3. Where does the research conflict — between marathons, or with the project's stated constraints?
4. What is the smallest set of work orders that, if executed, would validate the research?
5. What R&D gap remains that requires another marathon (or a design pass) before we can build?

## What we are NOT asking
- Don't re-derive what's already in the synthesis chapters.
- Don't summarize. Critique, sequence, and decide.
- Don't propose new R&D unless an existing marathon is structurally incomplete.
```

### Step 4 — Convene the council (5 sub-agents in PARALLEL)

Spawn all 5 advisors simultaneously. Each receives:

1. Their advisor identity + thinking lens (R&D-tuned variant from above)
2. The framed brief
3. The context pack (passed as `@<council-output-dir>/.tmp-context-pack-<timestamp>.md` reference)
4. Word budget: 600-1000 words (longer than standard `/llm-council` — this is a multi-marathon review, not a single question)

**Sub-agent prompt template:**

```
You are [Advisor Name] on the Marathon-Research Council.

Your thinking lens: [R&D-tuned description from above]

The council is reviewing <N> completed marathons. Your job is to read the context pack and respond from your lens. Do not hedge. Do not try to be balanced. Lean fully into your assigned angle.

## Framed brief
[framed brief]

## Context pack
@<council-output-dir>/.tmp-context-pack-<timestamp>.md

## What to produce
Address every marathon, not just the ones easy from your lens. Structure your response as:

1. **Per-marathon take** — for each marathon, 2-4 sentences from your lens. What's the decision? What's wrong / right / missing?
2. **Cross-marathon insight** — at least one observation that only emerges by looking across all <N> marathons together.
3. **Build sequence verdict** — which 1-3 marathons should the team build from FIRST, and which should wait? Why?
4. **Your one strong claim** — the single thing you most want the chairman to weigh.

Word budget: 600-1000. No preamble. Be specific — name the marathon by short slug.
```

### Step 5 — Peer review (5 sub-agents in PARALLEL)

Anonymize the 5 advisor outputs as Response A through E (random mapping). Spawn 5 reviewers. Each sees all 5 anonymized responses and answers:

1. Which response identifies the highest-leverage build chunk? (pick one, justify)
2. Which response has the biggest blind spot about the project's actual constraints? (be specific)
3. What did ALL 5 responses miss about how these marathons interact?
4. Which marathon was treated most weakly across all responses (least scrutinized)?

Reviewer word budget: 250-400 words.

### Step 6 — Chairman synthesis

One agent receives: framed brief, context pack reference, all 5 de-anonymized advisor responses, all 5 peer reviews. The chairman produces the final **council summary**, structured as:

```
## Where the council agrees
<bullet list of high-confidence build decisions, each tagged with the marathons that support it>

## Where the council clashes
<bullet list of unresolved tensions, with both sides>

## Blind spots the peer review caught
<things only surfaced through reviewers>

## Per-marathon build-ready cards
For each marathon (use the slug as header):

### <slug>
- **Decision:** <1-2 sentences — what we're going to do based on this research>
- **Stack pick:** <library / pattern / approach name(s)>
- **Open questions:** <items that still need a decision before building>
- **Build chunks (≤5):** <list of small, ship-shaped work order candidates>
- **Depends on:** <other marathons or design passes>

## Cross-marathon dependency graph
<ascii or bullet — which marathons feed which>

## The first PR
<single concrete first pull request the team should open>

## What still needs an ADR
<list of decisions that warrant an architecture-decision-record entry before code>
```

### Step 7 — Write the artifacts

Write three files to `<council-output-dir>`:

1. **`council-summary-<timestamp>.md`** — just the chairman's "Per-marathon build-ready cards" + "Cross-marathon dependency graph" + "The first PR" + "What still needs an ADR". This is the file the user keeps.
2. **`council-transcript-<timestamp>.md`** — framed brief, context pack reference, all 5 advisor responses (de-anonymized headers), all 5 peer reviews, chairman synthesis (full).
3. **`council-report-<timestamp>.html`** — single self-contained HTML with inline CSS:
   - Header: "Marathon-Research Council Verdict — <date>"
   - Summary card: count of marathons reviewed, total source count, total lines of research condensed
   - Chairman verdict (collapsible sections for "Where council agrees / clashes / blind spots")
   - Marathon cards in a 2-column grid, each card showing Decision / Stack pick / Build chunks
   - Dependency mini-diagram (ASCII inside `<pre>`)
   - Collapsible advisor responses (collapsed by default)
   - Footer: timestamp, marathon slugs reviewed

Delete the temp context pack `.tmp-context-pack-<timestamp>.md` after the artifacts are written.

### Step 8 — Update the research index (optional)

If `<research-index>` is configured, add a one-line entry:

```
- [Council summary <date>](council/council-summary-<timestamp>.md) — N marathons condensed: <slug1>, <slug2>, …
```

### Step 9 — Optional: file backlog candidates

If the user passed `--file-backlog`, take each marathon card's "Build chunks" and write them as draft work order files under `<backlog-drafts-dir>`. Do NOT commit them to the live backlog — the user reviews and promotes them manually.

## Hard rules

- **All 5 advisors must run in parallel.** Sequential spawning lets earlier responses bleed into later ones (defeats the purpose).
- **Always anonymize for peer review.** The mapping from advisor → letter must be random.
- **Chairman can disagree with the majority.** If 4 advisors say one thing but one dissenter has the strongest reasoning, the chairman sides with the dissenter.
- **Never edit canonical research content.** This skill is read-only against the research module.
- **Cap context pack at one read window.** If the marathon list is too long to fit, batch into 2 council runs and merge summaries — do not silently truncate.
- **Cite by slug.** Every chairman claim should reference at least one marathon slug. Claims with no source are quarantined to "things we feel but can't show."

## Failure modes to watch

| Failure | Symptom | Fix |
|---|---|---|
| Advisors all agree | The verdict reads bland; no real tension | Re-spawn with sharper lens prompts; the brief was probably under-specified |
| One marathon was barely mentioned | Reviewer #4 flags it | Spawn a single follow-up advisor focused only on that marathon |
| Chairman says "it depends" | Synthesis is hedging | Re-prompt the chairman with the explicit instruction: pick a side |
| Build chunks are fuzzy | "Implement encryption" is not a chunk | Re-prompt: each chunk must be ≤1 day of work and have a clear acceptance test |
| Validator report ignored | Council recommends building from a weakly-cited claim | Always include `_validation-report.md` excerpts in the context pack |

## Example invocations

```
/marathon-research-council 2026-05-05-api-idempotency 2026-05-05-fastapi-multitenant
/marathon-research-council --since 2026-05-05
/marathon-research-council --all-pending --file-backlog
```

## What this skill does NOT do

- It does NOT pick one framework / library on behalf of the user. The chairman recommends; the user decides.
- It does NOT auto-create ADRs. It flags candidates in "What still needs an ADR" and the user (or `/quick-design`) drives the ADR.
- It does NOT promote work orders to the backlog. It writes drafts under `<backlog-drafts-dir>` only when `--file-backlog` is set.
- It does NOT replace `/distill`. `/distill` produces ≤200-line summaries per marathon for general consumption. This skill produces a **build-ready cross-cut** across multiple marathons. Use both: `/distill` for individual cards, this skill for the collective decision.

## Companion skills

- **`/marathon-research`** produces the input this skill consumes.
- **`/distill`** produces per-marathon summary cards (≤200 lines each); this skill produces the cross-marathon council verdict.
- **`/llm-council`** answers a single decision question; this skill answers "given this pile of research, what do we build?"
- **`/council-rd`** picks 2-3 work orders per research folder with one mini-council each; this skill runs ONE multi-marathon council and produces a build sequence across all of them.
- **`/quick-design`** drives the ADRs this skill flags.
- **`/marathon-orders`** executes the work orders this skill drafts.
