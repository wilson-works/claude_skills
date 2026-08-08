---
name: harness-audit
description: "Audits your entire Claude Code harness against its purpose: enumerates every configurable surface (settings scopes, permission rules and modes, sandboxing, hooks, CLAUDE.md/rules hierarchy, auto memory, skills, subagents, MCP servers), then judges it through five lenses — goal alignment, Bitter-Lesson overengineering, stale self-model, memory compounding, and autonomy calibration — producing severity-ranked findings with specific edits and a PASS/CONCERNS/FAIL verdict per lens. Invoke with /harness-audit [lens|surfaces]."
---

# Harness Audit

## Purpose

Narrow audits already exist — skill quality has `/skill-stocktake`, spec drift has
`/spec-audit` — but nothing reads the harness *as a whole* and
asks whether it still serves its owner's goal. Harnesses accrete: permission grants outlive their
reason, CLAUDE.md files describe a model that no longer exists, memory bloats past its load
window, and hand-built scaffolding keeps compensating for weaknesses the current model doesn't
have.

The audit's load-bearing mental model comes from the platform itself: **CLAUDE.md, memory, and
skills are context — they shape what Claude tries to do; permission rules, hooks, and sandboxing
are enforcement — they constrain what is allowed regardless of what Claude decides.** Official
docs state that instructions never change what Claude Code allows, and route any "must happen"
rule to hooks. An audit that treats a CLAUDE.md "always do X" line as a guarantee has
mis-classified a context surface as an enforcement surface — that single confusion underlies most
harness findings.

## Configure for your project

Before using this skill, set this placeholder:

- `<audit-report-path>`: Where audit reports are written (e.g. `docs/audits/`). One timestamped
  report per run. All harness surfaces are read from their standard locations (`~/.claude/`, the
  project's `.claude/`, managed-policy directories) — no configuration needed for those.

## Invocation

```
/harness-audit              -- full audit: enumerate all surfaces, judge all five lenses
/harness-audit <lens>       -- one lens only (goal | bitter-lesson | self-model | memory | autonomy)
/harness-audit surfaces     -- Phase 1 inventory only, no judgments (fast; good before changes)
```

## Phase 1: Enumerate every surface

For each surface: list what exists, trace it to the scope/file it lives in, and note anything
that contradicts intent. Never judge from memory of your own config — read the files.

1. **settings.json scopes** — managed → CLI args → local (`.claude/settings.local.json`) →
   project (`.claude/settings.json`) → user (`~/.claude/settings.json`), highest first. Inventory
   every active key per scope; flag capability-granting settings sitting in a lower-precedence
   scope than intended, and stale `env`/`model` overrides. `/status` shows the active sources.
2. **Permission rules** — full allow/ask/deny inventory. Evaluation is deny → ask → allow, first
   match wins, across all scopes (a deny at any level beats an allow at any other). Flag: bare
   tool-name denies (removes the tool entirely) vs scoped denies; fragile argument-constraining
   Bash patterns (bypassable via option reordering, protocol swaps, redirects — official guidance
   is deny the binary and use `WebFetch(domain:)` or a `PreToolUse` hook); single-slash path
   anchors that bind to the settings source, not filesystem root.
3. **Permission mode + sandboxing** — which of the six modes (default, acceptEdits, plan, auto,
   dontAsk, bypassPermissions) is active per scope, and whether the unattended-run boundary is a
   real sandbox/container or just prose. Notes that matter: `auto`/`bypassPermissions`/`dontAsk`
   as `defaultMode` are ignored from project/local settings (a repo can't grant itself autonomy);
   protected paths are never auto-approved outside `bypassPermissions`; conversation-stated
   boundaries are re-read from the transcript and **can be dropped by compaction** — a durable
   boundary is a deny rule, not a sentence.
4. **Hooks** — every registered hook by event, in every scope plus plugin and frontmatter
   sources. Confirm each script still exists; flag hooks whose enforcement duplicates or
   contradicts a permission rule, and mid-session hooks whose injected values go stale on
   `--resume` (saved text replays; the hook does not re-run).
5. **CLAUDE.md / rules / AGENTS.md hierarchy** — every file in the load path (managed → user →
   project → local, concatenated not overridden; subdirectory files load on demand; imports
   expand at launch and don't reduce cost). Line counts vs the official under-200-lines-per-file
   target ("longer files consume more context and reduce adherence"); contradictions between
   files (docs: contradictory rules may be picked between arbitrarily); AGENTS.md bridged via
   `@AGENTS.md` import if cross-agent compat is wanted.
6. **Auto memory** — `MEMORY.md` size vs its load window (only the first 200 lines or 25 KB
   loads at session start; the tail silently never loads); staleness and contradictions against
   current CLAUDE.md; topic-file sprawl.
7. **Skills, subagents, MCP servers** — inventory with scope and tool surface. Skills load on
   demand (unlike CLAUDE.md) — flag CLAUDE.md sections that have grown into procedures and
   should become skills. Subagents: tools/model/permissionMode frontmatter vs intent (note: auto
   mode ignores subagent `permissionMode`). MCP: every server, its scope (local/project/user),
   and whether `mcp__server__*` permission rules match intent.

## Phase 2: The five lenses

Judge the enumerated harness. Each lens gets PASS / CONCERNS / FAIL with evidence.

### Lens A — Goal alignment
Does the harness have a defined "better"? Anthropic's eval guidance: define evals before
capabilities, draw ~20–50 simple tasks from real failures, and use them as the regression bank
that makes any later change judgeable.
- **PASS:** an articulated success metric + a real-failure eval bank (or a handoff to
  `/eval-harness` to create one, which this audit's report includes as a step).
- **CONCERNS:** a stated goal but no regression bank — changes can't be judged improvements.
- **FAIL:** no success criterion at all; every future change is unfalsifiable.

### Lens B — Bitter-Lesson overengineering
Sutton's essay: general methods that leverage computation win "by a large margin"; "building in
how we think we think does not work in the long run." Anthropic's agent guidance applies it at
harness level: simple composable patterns over frameworks; "add complexity only when it
demonstrably improves outcomes." The audit's test is *demonstrable*: scaffolding not backed by
an eval beating the simpler baseline is presumptively overengineering.
- **PASS:** simple scaffolding; complexity that exists is eval-backed.
- **CONCERNS:** elaborate scaffolding, unproven — might earn its keep, nothing shows it.
- **FAIL:** hard-coded process substituting for current model capability, underperforming or
  obscuring the loop.

### Lens C — Stale self-model
Official docs direct periodic review of CLAUDE.md and rules files to remove outdated or
conflicting instructions, and context-engineering guidance explains why bloat actively degrades:
finite attention budget, "context rot" (accuracy decreases as token volume grows), instructions
at the wrong "altitude."
- **PASS:** reviewed, non-contradictory, at-altitude, within size targets.
- **CONCERNS:** no recent review, mild bloat/redundancy, near size limits.
- **FAIL:** instructions contradict current behavior or each other, or hard-code workarounds for
  limitations the current model no longer has.

### Lens D — Memory compounding
Auto memory is designed to compound — but only the index's load window actually enters context.
- **PASS:** `MEMORY.md` is a lean, current index inside the 200-line/25 KB window; detail lives
  in on-demand topic files.
- **CONCERNS:** index approaching the window; mild staleness.
- **FAIL:** index past the window (tail silently unloaded) or stale/contradictory notes
  misleading every session.

### Lens E — Autonomy calibration
The official primitives already encode a risk × reversibility partition: auto-mode's classifier
blocks irreversible/high-blast actions (prod deploys, force-push, mass deletion, credential
grants) while allowing local reversible work; `bypassPermissions` is scoped to isolated
environments only and offers no injection protection; sandboxing is the boundary that holds even
if injection bypasses Claude's decision-making. The audit's citable test: **caps must be
enforced (deny rules, PreToolUse hooks, sandbox/container, subagent maxTurns) rather than
requested (CLAUDE.md lines, conversation promises that compaction can drop).**
- **PASS:** unattended caps enforced; irreversible actions blocked; boundary is not prose.
- **CONCERNS:** unattended work relying on the classifier alone or on conversation-stated
  boundaries; no sandbox.
- **FAIL:** `bypassPermissions` outside an isolated environment, or autonomy with
  high-blast-radius actions reachable and no enforced cap.

## Phase 3: Report

Write to `<audit-report-path>`, findings ranked most-severe first — autonomy findings by blast
radius × reversibility, context findings by context cost × contradiction risk. Every finding
carries a specific edit, not just a complaint:

```
HARNESS AUDIT — 2026-07-06
Lenses: goal CONCERNS · bitter-lesson PASS · self-model FAIL · memory CONCERNS · autonomy PASS

FINDINGS (most severe first)
1. [self-model / FAIL] user CLAUDE.md L34 and project CLAUDE.md L12 give contradictory
   test commands; docs warn contradictions resolve arbitrarily.
   EDIT: delete user L34; the project file is authoritative for this repo.
2. [autonomy / PASS-with-note] marathon runs rely on deny rules + sandbox (good); the
   "don't push" instruction in CLAUDE.md L58 duplicates an existing deny — remove the prose
   or mark it advisory; the deny rule is the guarantee.
3. [memory / CONCERNS] MEMORY.md at 187 lines, 9 entries reference a project archived in May.
   EDIT: prune the 9 stale entries; index drops to ~140 lines.
4. [goal / CONCERNS] no eval bank exists; "better" is undefined.
   HANDOFF: /eval-harness — seed 20–50 tasks from the failures listed in appendix A.

HANDOFFS
- Findings 1,3 → /claude-md-doctor (audit-mode input)   - Finding 4 → /eval-harness
- Actionable items filed → /backlog (category: tech debt)
UNRESOLVED DISCLOSURES: review cadence required but no official interval exists; see notes.
```

## Handoffs

- **All actionable findings** file to `/backlog` in its item format (category, priority, status).
- **Eval definitions** (Lens A's output) hand to `/eval-harness` — this audit defines *what*
  "better" means; that skill owns scoring it.
- **Instruction-file findings** (Lenses C, and B where the scaffolding is CLAUDE.md-shaped)
  become `/claude-md-doctor` audit-mode input.
- **Security-relevant permission findings** (injection exposure, over-broad grants to
  outward-facing tools) route to `/attack-surface` for its harness-input assessment.

## Failure Modes

- **Auditing from memory.** Asserting what a settings file says without reading it produces
  confident, wrong findings — the exact disease this skill treats. Every finding cites file+line.
- **Prose mistaken for enforcement.** The most common real finding: a CLAUDE.md rule doing a
  deny rule's job. Classify every "must" by which surface actually holds it.
- **Bitter-Lesson zealotry.** Lens B flags *unproven* complexity; it does not mandate deleting
  scaffolding that an eval shows is earning its keep. The test is evidence, in both directions.
- **Severity inflation.** A 210-line CLAUDE.md is CONCERNS, not FAIL. Reserve FAIL for actively
  unsafe or provably counter-productive states, or the report stops being trusted.
- **Fixing while auditing.** The audit reports and hands off; applying edits is the owner's (or
  the target skill's) move. An auditor that edits mid-audit destroys its own evidence.

## Important Notes

- **Routing smells:** when Phase 1 surfaces model/effort-routing issues, hand them to a
  dedicated routing lint if your pack has one, rather than re-implementing such checks here.
- **Two honest disclosures ship with every report:** (1) official docs direct *periodic* review
  of instruction files but name no interval — the audit requires a cadence without citing a
  number; (2) no official doc endorses the "pasted proof + hard caps" unattended-run pattern by
  name — the enforced-caps half is grounded in documented primitives; the pasted-proof half is
  an un-blessed design choice and is labeled as such.
- **Model routing:** surface enumeration (Phase 1) is mechanical → sonnet; lens judgments and
  the report (Phases 2–3) are the judgment steps → run at the session's strongest model;
  escalate only when findings conflict across lenses.
- Pairs with: `/backlog` (findings land as work items), `/eval-harness` (Lens A's eval
  definitions), `/claude-md-doctor` (instruction-file findings feed its audit mode),
  `/attack-surface` (security-relevant permission findings), `/extract-approach` (Lens D reads
  its note corpus's reuse rate as compounding evidence).
