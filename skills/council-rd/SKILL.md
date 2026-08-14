---
name: council-rd
description: Convene one mini-council per R&D research folder. Each council reviews the research output and picks the TOP 2-3 work orders that come out of it, then files them to the backlog and emits an HTML review tool used to approve/review/disapprove each WO before they finalize. Invoke with /council-rd [research-root] or /council-rd reconcile <decisions> to apply decisions back to the backlog. Filesystem-safe alias for "Council R&D" (the conceptual name with the ampersand cannot be a CLI command).
---

# Council R&D Skill

## Configure for your project

Before using this skill, swap these placeholders for your project values:

- `<research-root>` — absolute path to the directory holding R&D topic folders (output of `/marathon-research`)
- `<backlog-dir>` — absolute path to the directory holding `bugs.md`, `features.md`, `design.md`, `tech-debt.md`
- `<memory-dir>` — optional path to a memory/context folder where lasting rules are stored
- `<project-md>` — optional path to your top-level project context file
- `<product-context>` — fill in the short product context block in the council agent prompt with your own product/tech summary (see "Step 3" below)
- `<lens-set>` — five-lens council frame; defaults are listed in the prompt template, but EDIT to fit your domain (e.g. swap "L&D / HR Tech Buyer" for a different buyer persona)

## Purpose

Take a directory of completed R&D research topics (output of `/marathon-research`) and turn each topic into 2-3 actionable work orders, applying a 5-lens product council frame.

This is the **research-driven** companion to a generic council-orders skill. Where a generic council-orders runs a single 5-advisor sweep with a fixed WO output, `/council-rd` runs one mini-council **per research folder** and produces a smaller, more targeted batch (typically 24-36 WOs across all topics, 2-3 per topic).

The skill has two phases:

1. **Generate** (default) — scan research root, spawn one mini-council per topic, file WOs, emit HTML review tool.
2. **Reconcile** — apply user decisions exported from the HTML review tool back to the backlog (annotate, shelve, edit, or remove WOs).

## Invocation

```
/council-rd                              Default: scan <research-root>
/council-rd <research-root-path>         Custom research root
/council-rd reconcile <decisions-md>     Apply user decisions back to backlog
/council-rd reconcile                    Paste decisions inline; skill will prompt
```

The conceptual command name is "Council R&D" but the CLI alias is `council-rd` because `&` is reserved in most shells.

## Why this exists (the workflow)

User runs `/marathon-research [topics...]`. That fills `<research-root>` with one folder per completed topic — each folder contains `00-brief.md` (Sonnet scope-check), numbered deep-research files, `sources.md` (cited bibliography), and `meta.json` (status/metrics).

Without `council-rd`, those research outputs sit there. Council-rd is the bridge: research -> ranked, council-vetted, immediately-actionable backlog items.

The HTML review tool lets a non-technical reviewer make approve/review/disapprove decisions per WO without reading raw markdown, with notes preserved. The reconcile phase then closes the loop — decisions become annotations or shelvings on the actual backlog files.

---

## Phase 1 — Generate

### Step 1 — Read backlog state

Read the four backlog files to capture current next IDs and a sample of recent items:

```
<backlog-dir>/features.md   (FTR-)
<backlog-dir>/bugs.md       (BUG-)
<backlog-dir>/design.md     (DSN-)
<backlog-dir>/tech-debt.md  (TDT-)
```

Capture each `<!-- Next ID: N -->` value. Grep the last 30 FTR titles plus the last 10 of each other category for the dedup summary.

### Step 2 — Enumerate research topics

List immediate child folders of `<research-root>` matching `YYYY-MM-DD-<slug>/`. Skip `failed/`, `flagged/`, and non-topic files (`INDEX.md`, etc.).

For each topic folder, identify:
- `00-brief.md` (always present — the Sonnet scope-check)
- The synthesis file (usually the highest-numbered `06-*.md` or `05-*.md`)
- Other numbered files for context

If a topic has no synthesis file, log it and skip — do not invent recommendations from a half-built research folder.

### Step 3 — Spawn one mini-council agent per topic (parallel)

Spawn N agents in parallel — one per topic — using `subagent_type: general-purpose`, `model: sonnet`. Each agent receives:

- The exact research folder path
- A read order: 00-brief first, synthesis file second, others as needed
- The product context block (EDIT for your project)
- The recent backlog tail
- Topic-specific lens weighting
- Output format: exactly 2 or 3 work orders, no padding

**Agent prompt template** (replace bracketed placeholders per topic):

```
You are a 5-lens product council reviewing one R&D research topic. Your job is to extract the TOP 2-3 work orders that come out of this research — items the team should ship next based on the research findings.

RESEARCH FOLDER TO REVIEW:
[FULL_PATH_TO_TOPIC_FOLDER]

Read in this order:
1. 00-brief.md (scope-check)
2. [SYNTHESIS_FILE_NAME] (synthesis — most actionable)
3. Skim other numbered files only as needed

PRODUCT CONTEXT (EDIT for your project):
- [Short product description: what it is, target market, core value prop]
- [Tech stack: framework, backend, deployment]
- [Hard rules / non-negotiables: anything an advisor should not violate]
- [Any current product memory pointers, e.g. "see <project-md> for full context if needed via Read tool"]

5-LENS COUNCIL FRAME (apply all five — EDIT for your domain):
1. Enterprise Sales Engineer — what closes a F500 demo objection?
2. Staff Security Engineer — what closes a SOC2/security review?
3. Principal Product Designer — what makes UX feel funded vs side-project?
4. Staff Platform Engineer — what prevents production embarrassment at scale?
5. L&D / HR Tech Buyer — what makes a buyer say "bring this in?"

[OPTIONAL: TOPIC-SPECIFIC LENS WEIGHTING — e.g., "Mobile/offline relevance is particularly load-bearing for this topic; weight Platform Engineer heavily."]

RECENT BACKLOG TAIL (do NOT duplicate; cross-reference if related):
[INJECT: recent FTR titles + relevant BUG/DSN/TDT items]

YOUR TASK:
Pick the TOP 2-3 work orders the council unanimously believes are highest-leverage from this research. For each:

- CATEGORY: FTR / BUG / DSN / TDT
- TITLE: short, specific
- PRIORITY: critical / high / medium / low
- DETAILS: 3-5 sentences. Name files, components, data collections, or core packages. Cite the research file/section that supports the choice.
- WHY IT MATTERS: 1 sentence on the buyer/user objection or failure mode this closes.
- LEAD ADVISOR LENS: Sales / Security / Design / Platform / HR Buyer

OUTPUT FORMAT (no preamble, no markdown headers above each item):

WORK ORDER 1
CATEGORY: FTR
TITLE: ...
PRIORITY: high
DETAILS: ...
WHY IT MATTERS: ...
LEAD ADVISOR LENS: ...

WORK ORDER 2
...

Output exactly 2 or 3 work orders. Pick 3 only if the research has three clearly separate high-leverage gaps; pick 2 if only two stand out. Do not pad.
```

### Step 4 — Collect, dedupe, assign IDs

After all parallel agents return:

1. Bucket items by category (FTR, DSN, TDT, BUG).
2. Scan for cross-topic duplicates. Common overlaps:
   - SSO/SCIM gets flagged by Sales + HR lenses
   - Integration items appear across multiple topics
   - Per-domain config items appear in every domain-specific topic — these are NOT duplicates
3. When you do merge, take the more comprehensive of the two and note both source topics.
4. Sort within each category by priority (critical -> high -> medium -> low).
5. Assign sequential IDs starting from each file's `<!-- Next ID: N -->` value.

### Step 5 — File to backlog

Append to each backlog file. Entry format:

```markdown
### [FTR-XXX] Title
- **Added**: YYYY-MM-DD
- **Priority**: critical/high/medium/low
- **Council**: [Topic name] R&D — Lead lens: [Advisor]
- **Source**: research/[folder]/[file] §X
- **Details**: ...full details from advisor
- **Why**: ...one-sentence why-it-matters
```

Wrap each filed batch with a section header comment:

```html
<!-- =============================================================
     COUNCIL R&D SWEEP — Filed YYYY-MM-DD
     N research folders reviewed; council picked top 2-3 per topic.
     Source: [research-root-path]
     ============================================================= -->
```

Update the `<!-- Next ID: N -->` comment in each modified file.

### Step 6 — Emit HTML review tool

Generate a self-contained HTML review tool at `<research-root>/<YYYY-MM-DD>-council-rd-review.html`.

If your project has a prior council review HTML you want to mirror, point this skill at it once as the canonical example, then generate a fresh file following the same structure.

**Requirements (must-haves):**
- Sticky header with title, date, and live-updating stat counters (Total / Approved / Review / Disapproved / Pending)
- Filter chips: All, Critical, High, Medium, Pending, Approved, Review, Disapproved
- One section per R&D topic
- Per-WO card showing: ID, priority badge, title, lead lens, source citation, full details, "Why" line
- Three action buttons per card (Approve / Review / Disapprove) plus Clear
- Optional note input per card
- Decisions persist to `localStorage` (key: `council-rd-review-<YYYY-MM-DD>`) so refreshes don't wipe progress
- "Export decisions" button copies a structured markdown summary to clipboard (sections: APPROVED / REVIEW / DISAPPROVED / PENDING)
- "Reset all" button with confirm dialog
- Dark theme (suggested: navy bg `#0a0e1a`, surface `#131826`, accent `#06b6d4`, priority colors: critical red `#ef4444`, high amber `#f59e0b`, medium blue `#3b82f6`) — adjust to match your product palette
- Self-contained — no CDN deps, vanilla CSS/JS only
- All data embedded as a JSON array in the script

**Copy rules for the HTML chrome (UI text):**
- No emojis
- No em dashes — use commas, periods, parentheses, or `&middot;`
- Action button labels are plain text: "Approve" / "Review" / "Disapprove" / "Clear"
- Stat labels uppercase letterspaced: "TOTAL", "APPROVED", "REVIEW", "DISAPPROVED", "PENDING"
- Topic section header: short title + folder path + WO count

**Note on em dashes inside WO content**: WO details rendered inside the cards may legitimately contain em dashes (authored by advisors). Render them verbatim — only the UI chrome must be em-dash-free.

### Step 7 — Report to user

Output a structured summary:

1. **Chairman's synthesis brief** — under 200 words. Convergence (themes across multiple topics), divergence (topic-specific outliers), single most critical finding.
2. **Filed items table** — grouped by category, showing ID, priority, title, source topic.
3. **Priority breakdown** — count of critical/high/medium/low across all filed items.
4. **Top 3 chairman picks** — three most urgent items regardless of source topic.
5. **HTML review tool path** — clickable link, with one-sentence instruction: "Open this, mark Approve/Review/Disapprove on each card, then click Export decisions and paste the markdown back. I'll reconcile."

---

## Phase 2 — Reconcile

Triggered by `/council-rd reconcile <decisions-md>` or `/council-rd reconcile` (then paste).

The decisions markdown comes from the HTML review tool's "Export decisions" output and looks like:

```markdown
# Council R&D Review Decisions — YYYY-MM-DD

## APPROVED (N)
- **FTR-XXX** [priority] Title — NOTE: optional note

## REVIEW (N)
...

## DISAPPROVED (N)
...

## PENDING (N)
...
```

### Reconciliation rules

For each item in the decisions doc:

- **APPROVED with no note** — leave the WO unchanged.
- **APPROVED with a note** — translate the note into a structured edit on the WO. Common note shapes:
  - **Clarification** ("just to be clear that X means Y") — add a `**Reviewer rule:**` or `**Reviewer framing:**` line at the top of Details and modify prose to match.
  - **Spec change** ("change X to Y" / "we want N not M") — edit Details directly, add a `**Reviewer spec:**` line citing the override and a source-of-truth pointer.
  - **Sequencing** ("defer until X ships" / "use Y skill first") — add a `**Sequencing:**` line. Don't shelve unless the reviewer said shelve.
  - **Question** ("isn't this what X is for?") — add a `**Reviewer note:**` line that names the related artifact and clarifies the scope difference; do NOT silently delete the WO just because there's overlap.
  - **Cross-reference** ("see file Z") — add a `**Reviewer note:**` line citing the file path. If the file is load-bearing, also update the `**Source:**` line.

- **REVIEW** — leave in the backlog but add a `**Status: NEEDS REVIEW (YYYY-MM-DD)**` line at the top with the reviewer's note (if any). Tell the user explicitly which items need follow-up before they should be pulled into a marathon wave.

- **DISAPPROVED** — remove the WO entirely. Update `<!-- Next ID: N -->` only if the disapproved item was the highest-numbered (otherwise the next ID stays as-is and the gap is intentional). Print a confirmation line per removed WO.

- **PENDING** — leave alone. Note in the report which items the reviewer didn't decide on yet.

### Cross-WO ripple effects

Reconcile must also handle ripple effects:

- **"Shelf domain X"** — if an entire domain is shelved, find ALL WOs tied to that domain and mark them with a uniform `[SHELVED]` status header. Do NOT delete shelved items — they remain reactivation specs.

- **"Replace X with Y"** — update the displaced item's WOs to shelved status and add an explicit `**Reviewer decision:**` note on the replacement item's config WO confirming the swap. Update relevant memory.

- **"Override research-default value to N"** — if the override is structurally important (trial length, currency cap, cadence), create or update a memory file capturing the rule so future agents don't drift.

- **"Use skill /X for this work"** — add a `**Sequencing:**` line on the WO referencing the skill path. Don't invoke the skill yet; just route future work through it.

### Memory updates after reconciliation

After reconcile, scan the notes for any rule that should outlive this conversation:

- New product rules -> write a new `<memory-dir>/project_<topic>.md` and add to the memory index.
- Schedule overrides -> write a project memory.
- Domain-slate changes -> update the corresponding memory file.
- Cross-WO architectural decisions -> add a feedback memory.

Don't write memories for one-off WO edits or transient notes. The bar is: would a future agent in a different conversation make the wrong choice without this memory?

### Reconcile output

End the reconcile run with a summary:

- N approved (M unchanged, K annotated)
- N review (list IDs + the open question)
- N disapproved (list IDs removed)
- N pending (list IDs awaiting decision)
- M memories created/updated
- M cross-WO ripples applied (list)

---

## Notes

- **Always read the backlog BEFORE spawning advisors** so they have current dedup context.
- **Never spawn a council that hasn't read its research.** If you can't find a synthesis file, skip the topic and report the gap.
- **Parallel matters here**: 12 topics × 1 sonnet agent each = ~10 minutes of wall time. Do NOT serialize.
- **Don't invent topics**. The skill operates on whatever folders exist under `<research-root>`. If you want more topics, run `/marathon-research` first.
- **The HTML tool is the user-facing artifact**. The terminal report is for the loop logs.
- **Reconcile is non-destructive by default for everything except DISAPPROVED**. Even REVIEW items stay in the backlog with a status flag. Only DISAPPROVED items get deleted.
- **Keep lens descriptions stable across runs** so output is comparable.

## Custom invocation examples

```
/council-rd                              Default research root, full sweep
/council-rd <other-research-root>        Custom research root
/council-rd reconcile                    Paste decisions inline
/council-rd reconcile <path-to-md>       Read decisions from file
```

## Related skills

- `/marathon-research` — fills the research folder this skill consumes.
- `/llm-council` — for single decisions, not WO production.
- Backlog execution skills (e.g. `/work-orders`, `/marathon-orders`) — execute filed WOs after approval.
