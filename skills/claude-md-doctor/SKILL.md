---
name: claude-md-doctor
description: "Audits and rewrites a project's instruction files — CLAUDE.md, folder-scoped files, path-scoped rules, AGENTS.md bridging — into an operating manual a weaker model can execute: a scored audit across seven dimensions (size budget, checkability, necessity, red-line mechanism fit, constraint concreteness, scoping hygiene, structure), then a rewrite that deletes the derivable, converts adjectives into checkable conditions, moves area rules to scoped files, and routes real red lines to hooks — because instructions are advisory and decay within a session, while hooks hold. Invoke with /claude-md-doctor [rewrite|<path>]."
---

# CLAUDE.md Doctor

## Purpose

Instruction files rot in a specific way: they grow (each incident adds a rule), they stay vague
("be careful with the database"), and they quietly claim powers they don't have. The official
docs are blunt about the first: bloated CLAUDE.md files cause Claude to ignore your actual
instructions, and the per-line test is "would removing this cause Claude to make mistakes? If
not, cut it." The deepest problem is the third: **CLAUDE.md is advisory context, not
enforcement** — and the strongest empirical finding on instruction-following is that adherence
decays *within* a session as generated output accumulates, regardless of how well the file was
shaped at the start. A rule that must hold on function #40 as reliably as on function #1 cannot
live in prose; it needs a deterministic gate.

So this skill does two jobs. **Audit mode** scores the full instruction-file surface against a
seven-dimension rubric. **Rewrite mode** turns the file into an operating manual a weaker model
can execute: every kept rule checkable, every red line routed to the mechanism that actually
holds, every area rule scoped to load only when relevant — which is also what makes
downgrading routine work to smaller models safe.

## Configure for your project

Before using this skill, set this placeholder:

- `<doctor-output-path>`: Where audit reports and rewrite proposals are written (e.g.
  `docs/audits/instructions/`). The instruction files themselves are discovered from their
  standard locations (managed → user → project → local, plus `.claude/rules/` and imports).

## Invocation

```
/claude-md-doctor              -- audit: score the full load path against the rubric
/claude-md-doctor <path>       -- audit one instruction file
/claude-md-doctor rewrite      -- audit, then produce the full rewrite as a reviewable diff
```

## The mechanics the doctor must get right

These platform facts drive every judgment below:

- **Everything in the load path stacks.** All CLAUDE.md/CLAUDE.local.md files from filesystem
  root down to cwd are concatenated, never overridden — a contradiction between two files is not
  resolved by precedence; it is handed to the model as conflicting text.
- **Subdirectory files load on demand** (when Claude reads files there); `.claude/rules/*.md`
  with `paths:` globs load only on matching files — the most surgical scoping mechanism.
- **Imports (`@file`, max depth 4) organize but don't economize** — imported files still load in
  full at launch.
- **Claude Code reads CLAUDE.md, not AGENTS.md.** Bridge with an `@AGENTS.md` import. And the
  two precedence models differ: CLAUDE.md concatenates up the tree; AGENTS.md is nearest-file-
  wins — never conflate them.
- **Size ceiling:** official guidance targets under 200 lines per file ("longer files consume
  more context and reduce adherence"); practitioner corpus data puts the well-performing core
  nearer 80–100 lines. Files load in full regardless of length.
- **Instructions are advisory; hooks are deterministic.** The docs route anything that "must
  run at a specific point" to hooks; a PreToolUse hook exiting 2 blocks, prose merely asks.

## Audit mode: the rubric

Score each dimension 0–2 (fail / concern / pass). **A, B, and D are gating** — overall PASS
requires all three at pass plus a total ≥ 11/14 — because they map to the strongest evidence:
size-vs-adherence, unverifiable rules, and advisory decay.

| Dim | What it checks | Pass looks like |
|-----|----------------|-----------------|
| **A. Size & budget** | Root file line count vs the 200-line ceiling and ~80–100-line target | Lean always-loaded core; bulk pushed to scoped files/skills |
| **B. Checkability** | Fraction of rules a fresh reader could mark pass/fail without judgment | No naked adjectives ("clean," "proper," "carefully," "appropriate") — every imperative names an observable condition or a runnable check |
| **C. Necessity** | The removal test, per line | Nothing derivable from code, standard conventions, or linter-enforced rules |
| **D. Red-line mechanism fit** | Are unrecoverable/destructive prohibitions enforced by hooks, or just requested in prose? | Every real red line has a deterministic gate; prose versions marked advisory |
| **E. Constraint concreteness** | "Never/avoid" rules name the specific action | An Always-do / Ask-first / Never-do structure with named actions |
| **F. Scoping hygiene** | Broad rules in root; area rules in folder files or path-scoped rules; no cross-file contradictions; AGENTS.md bridged if present | Load path inventoried, contradiction-free, scoped correctly |
| **G. Structure & altitude** | High-signal imperative bullets; killer rules at the top, not buried mid-file; emphasis reserved for genuinely load-bearing items | Reads like an operating manual, not a diary |

```
INSTRUCTION AUDIT — 2026-07-06
Load path: ~/.claude/CLAUDE.md (61) · ./CLAUDE.md (214) · ./.claude/rules/db.md (18, path-scoped)
Verdict: FAIL  (A fail · B concern · C concern · D FAIL · E pass · F concern · G pass — 7/14)

GATING FINDINGS
[D] ./CLAUDE.md L102 "NEVER run destructive migrations on prod" exists only as prose.
    An advisory sentence cannot hold late in a session. FIX: PreToolUse hook (exit 2) matching
    the migration command; keep one line of prose marked "(advisory reminder; hook enforces)".
[A] ./CLAUDE.md at 214 lines exceeds the 200-line ceiling; est. 90 lines pass the removal test.
SAMPLE LINE FINDINGS
[B] L34 "write clean, well-structured code" — no observable condition → DELETE (model default)
[C] L57 "components live in src/components/" — derivable from the tree → DELETE
[F] L120-160 API-layer rules apply only to src/api/** → MOVE to .claude/rules/api.md (paths glob)
Full line-by-line classification: <doctor-output-path>/2026-07-06-audit.md
```

## Rewrite mode: the procedure

1. **Inventory the load path** — every file that loads, root-down, plus imports and any
   AGENTS.md; record line counts; flag cross-file contradictions (they stack, remember).
2. **Gather the evidence** before touching a line: approach notes from `/extract-approach`
   (documented mistakes and their preventive rules), accepted behavior-binding records from
   `/decision-policy`, and any `/harness-audit` instruction-file findings — rewrites grounded in
   observed failures beat rewrites from taste.
3. **Classify every line** — delete (derivable / model default) · keep-as-concrete-imperative ·
   move-to-scoped-file · convert-to-hook (unrecoverable or must-hold-late) · promote-to-skill
   (it grew into a procedure).
4. **Rewrite the kept lines to checkable form:** strip the adjective, state the observable
   condition and the check. "Verify code quality" → "run `pnpm typecheck` before reporting done
   and paste the result." The acceptance-criteria test: observable, no ambiguous terms,
   pass/fail decidable by a stranger.
5. **Pair failure modes with rules:** each recurring mistake gets the *weakest sufficient
   mechanism* — delete if unprompted behavior is fine, concrete rule, emphasis (`IMPORTANT`)
   only for the inconsistently-followed, scoped rule if localized, hook if unrecoverable,
   skill if procedural. Escalate only as far as needed.
6. **Structure constraints** as Always-do / Ask-first / Never-do, each Never naming a specific
   action; add explicit escalation rules for uncertainty ("if X is ambiguous, ask; don't
   guess") — an operating manual tells the reader when *not* to proceed.
7. **Order for attention:** killer rules first (buried-middle content is measurably weakest);
   budget the root to the ~80–100-line core; bridge AGENTS.md via import if cross-tool
   compatibility is wanted.
8. **Ship as a diff, apply on approval, then test in the real world:** watch whether behavior
   actually shifts. A rule still ignored after the rewrite is either buried (reorder/prune) or a
   red line that needed a hook — first drafts fall apart, and instruction files are code.

## Handoffs

- **Rewritten rules re-arm any rules-acknowledgment gate** your harness uses, if present.
- **Post-rewrite, trial a model downgrade:** a checkable, failure-mode-paired instruction file
  is what makes routing routine work to smaller models safe.
- **Hook conversions** are proposed as settings snippets for the user to apply — this skill
  edits instruction files (on approval), never permission/hook config.
- **Procedures promoted to skills** move into your skill-authoring workflow with the extracted
  steps as intake.

## Failure Modes

- **Rewriting from taste instead of evidence.** A shorter, prettier file that drops the one rule
  preventing last month's incident is a regression. Step 2's evidence gathering (approach notes,
  decision records, audit findings) is mandatory, not decorative.
- **Prose theater on red lines.** Leaving "NEVER touch prod" as a beautifully-rewritten sentence
  is still dimension-D failure — the sentence decays; the hook doesn't. The doctor's most
  valuable output is the routing decision, not the prose.
- **Deleting the non-obvious.** The removal test cuts what the model already does — not what it
  does *now on a good day*. When evidence shows a past failure, the rule stays (or becomes a
  hook), however obvious it reads.
- **Scoping as exile.** Moving rules to folder files to hit the root budget, when they actually
  apply broadly, just hides them from the sessions that need them. Scope by applicability, not
  by line-count pressure.
- **One-shot doctoring.** Behavior drift and new failure modes accumulate; the audit is cheap —
  re-run it on a cadence (officially: review instruction files periodically; no official
  interval exists, so set one and keep it).

## Important Notes

- **The reader is a weaker model** — the same bar as an approach note: conventions it can
  follow mechanically, failure modes paired with preventive rules, quality bars it can check,
  escalation rules for what it can't decide. If a rule needs the author present to interpret,
  it isn't finished.
- **The three-channel model is the skill's spine:** always-loaded prose (small, advisory,
  checkable) · on-demand context (scoped files, rules, skills) · deterministic gates (hooks).
  Every line belongs to exactly one channel, chosen by consequence and required reliability.
- **Honest limits, disclosed in every report:** adherence numbers are practitioner estimates
  and single-study findings, not guarantees — the direction (advisory decays; deterministic
  holds; bloat suppresses) is well-supported even where exact figures aren't.
- **Model routing:** load-path inventory and line classification → sonnet (line counts and
  flag-lists are haiku-safe); rewrite judgments, mechanism routing, and the final diff → the
  session's strongest model; escalate when two instruction files contradict on a load-bearing
  rule — that's an adjudication, not a rewrite.
- Pairs with: `/extract-approach` (approach notes are rewrite evidence), `/decision-policy`
  (accepted behavior-binding policies graduate into rules here), `/harness-audit` (its
  instruction-file findings are audit-mode input).
