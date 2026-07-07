---
name: extract-approach
description: "Captures how a non-trivial engineering problem was solved, at the moment it is solved, as an atomic claim-titled approach note — recurrence trigger, failure symptom, checkable rule, counter-example — filed in a topic-indexed corpus that a future session (or a weaker model) can retrieve and apply when a similar problem appears. Includes index-first retrieval, a review/decay loop, and the CLAUDE.md-plus-hooks wiring that makes capture fire without being asked. Invoke with /extract-approach [find|review] [args]."
---

# Extract Approach

## Purpose

The knowledge inside a hard-won fix evaporates the moment the session ends; the next session —
often a cheaper model — re-derives it or repeats the mistake. Postmortem practice names the stakes:
without a formalized process of learning from incidents, they recur indefinitely. But capture
alone is not reuse — large lessons-learned repositories famously go unused because readers can't
find the applicable lesson in the pile. An unreviewed, unretrieved note might as well never have
existed.

This skill captures each solved problem as one atomic note optimized for *read time*: a claim
title that works as the retrieval key, an applies-when trigger so a future model knows the note is
relevant, a checkable rule it can apply and verify, and a counter-example that bounds the claim.
A capped index is the only thing that grows in always-loaded context; the corpus is read on
demand. `retro` scores a session, `notetaker` remembers a thought, `distill` compresses a report —
`extract-approach` captures how one engineering problem was solved, retrievably.

## Configure for your project

Before using this skill, set these placeholders:

- `<approach-notes-path>`: Directory for the note corpus, organized as one topic subfolder per
  concept area (e.g. `approaches/orm/`, `approaches/caching/`). Recommended: a dedicated area
  inside the project's existing memory/notes directory rather than a new parallel store.
- `<approach-index-path>`: The capped index file, default `<approach-notes-path>/APPROACHES.md`.
  One line per note (claim title · trigger · topic). Hard cap ~200 lines — mirroring the
  platform's own auto-memory index, where only the first 200 lines / 25KB of `MEMORY.md` are
  loaded at session start and everything else is fetched on demand.

## Invocation

```
/extract-approach                    -- capture: mine this session for the just-solved problem
/extract-approach find "<problem>"   -- retrieve: index-first lookup of applicable notes
/extract-approach review             -- maintain: merge duplicates, archive stale, promote winners
```

## What earns a note (capture gate)

Capture fires for a **non-trivial solved problem**: a bug fixed, a failure diagnosed, a
non-obvious approach that worked. Skip trivial or purely mechanical changes — capture-spam is how
an index dies. One insight per note; if the solve contained two insights, write two notes. If you
struggle to state the insight as one sharp declarative title, the thinking is still muddy or the
note conflates ideas — split it or keep digging before filing.

## Note schema

One file per solved problem: `<approach-notes-path>/<topic>/YYYY-MM-DD-<claim-slug>.md`. The
filename is self-indexing: absolute date for recency, claim slug as the retrieval key. Fields, in
order — every one exists to make the note executable by a weaker model with no context:

| Field | Why it's there |
|-------|----------------|
| Claim title (complete declarative sentence) | Retrieval key; forces one sharp insight; works "like an API" for the body |
| Date + source | Recency arbitration and provenance for a no-context future reader |
| Topic tags | Concept-keyed filing — by what the insight is about, never by ticket or session |
| Applies-when (trigger) | The recurrence signature: how a future model recognizes "this note is relevant now" |
| What went wrong / symptom | The observable failure signature, recognizable when it happens again |
| The approach (checkable rule) | The concrete corrective — specific enough to apply *and verify*, code-adjacent where possible |
| Counter-example / when NOT to apply | Bounds the claim; prevents over-generalization |
| Related | Links to neighbor notes, so one found note surfaces the others |

```markdown
# Webhook retries duplicate side effects unless handlers are idempotent by event key

- **Date**: 2026-03-14   **Source**: checkout-service session, double-refund bug
- **Topic**: webhooks, idempotency

## Applies-when (trigger)
Any handler that performs a side effect (payment, email, DB write) in response to a
webhook or queue message from a provider that retries on non-2xx or timeout.

## What went wrong / symptom
Customer refunded twice. Provider retried after our handler timed out post-commit —
the retry re-ran the refund. Logs show two deliveries of the same event id, 90s apart.

## The approach (checkable rule)
Before the side effect, upsert the provider event id into a processed-events table with
a unique constraint; on conflict, return 200 and skip. Check: replaying any delivery
twice must produce exactly one side effect and two 200s.

## Counter-example / when NOT to apply
Handlers that are already naturally idempotent (pure upserts of the event payload) —
adding the dedup table there is overhead without a failure mode to prevent.

## Related
- [[2026-02-02-timeouts-after-commit-look-like-failures-to-callers]]
```

## Capture workflow (`/extract-approach`)

1. Identify the just-solved problem from the session: what failed, what was tried, what worked.
2. Distill the one reusable insight and state it as a complete declarative claim title.
3. Fill every schema field — the counter-example is mandatory, not optional; a rule without
   bounds over-generalizes.
4. File under the concept topic (create a topic folder only when a real note needs it), synthetic
   or sanitized details only if the session touched sensitive data.
5. Append one line to `<approach-index-path>`: claim title · trigger phrase · topic. If the index
   would exceed its cap, run the review step before adding.
6. Add `Related` links to any existing note the new one touches — a note found by one path should
   surface its neighbors.

## Retrieval workflow (`/extract-approach find`)

1. Read `<approach-index-path>` first, always — never grep the corpus cold.
2. Match the current problem against trigger phrases and claim titles; open only the notes whose
   applies-when matches. Title + topic grep is the zero-infrastructure default; the schema's
   claim-title-as-key design leaves room for semantic (embedding) retrieval later without
   re-writing notes.
3. Apply the checkable rule and verify by its own check; if the counter-example matches instead,
   say so rather than forcing the note to fit.

## Review workflow (`/extract-approach review`)

Unbounded memory defeats itself — every durable system surveyed for this skill bounds or prunes.
Periodically (pair it with your weekly or retro cadence):

- **Merge** near-duplicate notes into the sharper claim.
- **Archive** notes whose trigger hasn't matched anything in months (move out of the index, keep
  the file).
- **Promote** a note retrieved repeatedly: its rule graduates into a CLAUDE.md instruction (keep
  it concrete and verifiable — specific instructions are followed more reliably than vague ones)
  or, if it has grown a workflow, a skill candidate for the pack.

## Wiring: make capture fire without being asked

Hooks cannot invoke Skills — only the running Claude can — so the wiring is two-layered:

1. **CLAUDE.md instruction (primary).** A few always-loaded lines, well under the official
   ~200-lines-per-file guidance: *"When you finish solving a non-trivial engineering problem,
   before ending your turn, capture it via /extract-approach. Skip trivial changes."* This is the
   layer that can actually invoke the skill.
2. **`Stop` hook (enforcing nudge).** `Stop` fires when Claude finishes responding and *can block
   the stop* (exit code 2 / `decision:"block"`) while injecting a reminder via
   `additionalContext`. Keep it advisory-toned to avoid capture-spam on trivial turns. For
   marathon or agent-org runs, the same nudge per work unit belongs on `SubagentStop`, matched to
   the worker agent type.
3. **`SessionStart` hook (retrieval side).** On startup/resume, inject the index (or a
   topic-filtered slice) via `additionalContext` so relevant past approaches are in front of the
   model *before* it re-solves a solved problem. Note the documented caveat: resumed sessions
   replay saved hook text rather than re-running the hook, so injected content can be stale.
4. **`PostToolUse` detector (optional).** Matched to `Bash`, it can notice a test command flipping
   fail→pass and inject "a problem was just solved — consider an approach note" as a signal into
   the Stop-time decision.

## Boundary: what this skill is not

| Sibling | Its unit | Stays its job |
|---------|----------|---------------|
| `retro` | one session/sprint | velocity, blockers, estimation, action items — it may *surface* a recurring pattern; the durable note for that pattern is filed here |
| `notetaker` | one thought, any domain | general decisions/ideas/people/reference; this skill is the typed, engineering-only sibling with an enforced executable schema |
| `distill` | one research marathon | many→one compression of an existing long report; this skill is event→one capture from a live session — no input document exists |

Handoffs: `retro` closes with "file recurring patterns as approach notes"; `claude-md-doctor`
consumes approach notes as evidence for instruction-file rules; `harness-audit`'s
memory-compounding lens reads this corpus's reuse rate; the note location and schema register as a
contract artifact in `skill-graph`'s registry so consumers track format changes.

## Failure Modes

- **Write-and-forget.** The NASA outcome: a repository exists, nobody retrieves from it. The
  `SessionStart` index injection and the find-before-solving habit are the countermeasures —
  capture without re-exposure is wasted work.
- **Capture-spam.** Noting trivial fixes buries the jewels and blows the index cap. The capture
  gate is a real gate; when in doubt on a trivial change, don't file.
- **Event-keyed notes.** Filing by ticket/session ("the Tuesday outage note") instead of by
  concept kills cross-situation reuse — the same insight won't be found from a different incident.
  Titles are claims; topics are concepts.
- **Rules without bounds.** A note missing its counter-example gets applied everywhere and
  poisons trust in the corpus. The field is mandatory at capture time.
- **Parallel-store sprawl.** Inventing a filing system beside the platform's memory directory and
  `notetaker`'s buckets duplicates infrastructure. This skill's value is the executable schema and
  the solve-time trigger — ride the existing index-plus-topic-files shape.

## Important Notes

- **The reader is a weaker model with no context.** Every schema field earns its place by that
  test: self-contained, concrete, checkable. If a note needs the session that produced it to make
  sense, it isn't done.
- **The index is the product.** The corpus can grow large (single-concept files stay browsable
  into the thousands of entries); the always-loaded index cannot. Guard the cap.
- **Promotion is the endgame:** a note that keeps getting retrieved should stop being a note and
  become a standing rule — that's the compounding loop, not note-hoarding.
- Pairs with: `/retro` (surfaces recurring patterns worth filing; its retros link the session's
  notes), `/notetaker` (general-knowledge sibling; non-engineering thoughts route there),
  `/distill` (report compression sibling), `/claude-md-doctor` (consumes notes as rule evidence),
  `/harness-audit` (reads note reuse rates for its memory-compounding lens), `/skill-graph`
  (the note schema registers as a contract artifact).
