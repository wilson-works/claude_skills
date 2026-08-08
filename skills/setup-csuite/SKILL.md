---
name: setup-csuite
description: "Brief the 70-agent C-suite on a new codebase the agent-org skill was just installed into. Surveys the repo (monorepo layout, key directories, backlog, business-plan, SoT, project memory, hard rules, recent decisions), writes a project-tailored ORG-INDEX.md at .claude/ORG-INDEX.md so chiefs and EAs navigate by pointer instead of re-exploring every run, then runs a one-shot council with all seven chiefs (James, Elle, Mara, Amelia, Margot, Marisol, Everett) and Victor (VP-AI). Each chief reads the index, names beta-blockers from their lens, proposes new work orders, and asks one peer question. The skill synthesizes the council, files any approved WOs to the project backlog, and emits a marathon-org launch prompt for the next session. Invoke with /setup-csuite. Re-run with /setup-csuite --refresh after major org or codebase changes to update the index."
---

# setup-csuite Skill

The post-install brief for the 70-agent org. Run this once after `/agent-org` lands in a new codebase, and the C-suite goes from "blind on the repo" to "oriented + opinionated + filed WOs" in a single session.

## When to use

- **Immediately after `/agent-org` install** in a fresh codebase. The org exists but no chief knows what they're looking at.
- **After a major repo restructure** (monorepo split, branch reshuffle, new top-level dir like `business-plan/`).
- **After adding a new branch to the org** (e.g., going from CTO-only to CTO + CFO + COO).
- **When the existing `ORG-INDEX.md` feels stale** -- chiefs are re-grepping the codebase to orient. The index has a gap; refresh it.

## What it produces

Three artifacts under your project root:

1. `.claude/ORG-INDEX.md` -- the navigation map. Chiefs read this first; it points them to every file they need.
2. New work orders in your project's backlog (per the council output). The skill detects your backlog location from the project's `CLAUDE.md` (or asks once if not specified).
3. `prompts/setup-csuite-marathon.md` (or equivalent) -- a marathon-org launch prompt that uses the index + council output to set up the next deep-work session.

## How it runs

### Phase 1 -- Pre-flight (≤ 30 seconds)

1. **Detect agent-org install**: confirm `.claude/agents/cto-james.md` exists. If not, halt with "Run /agent-org install first."
2. **Detect project root + CLAUDE.md**: read the project's `CLAUDE.md`. Extract: product name, branch defaults, hard rules, backlog path, design spec path, business-plan path.
3. **Detect repo shape**: in parallel, `ls -la` the project root and one level into each top-level dir. Map: monorepo vs single-app; languages (`tsconfig.*`, `pyproject.toml`, `Gemfile`, `go.mod`, etc.); test framework; deploy artifacts (`firebase.json`, `vercel.json`, `Dockerfile`, etc.).
4. **Detect backlog**: look for the convention `<project-root>/.claude/projects/<slug>/backlog/` OR a `backlog/` dir at the root OR a value in `CLAUDE.md`. If none, ask the user once and remember (write to memory).
5. **Detect business-plan + SoT + memory**: look for `business-plan/`, `sot-audit/`, `docs/`, `research/` at project root; look for `~/.claude/projects/<slug>/memory/MEMORY.md`. Note presence/absence.

### Phase 2 -- Build the index (≤ 2 minutes)

Survey the codebase enough to write a useful index. **The index is a map, not a tour** -- pointers + one-line descriptions, never narrative.

Required sections in `.claude/ORG-INDEX.md`:

1. **Five-second product story** (3-4 sentences max). What it is, who buys, what's in beta.
2. **Canonical taxonomy lock** (if any). Verticals, products, segments -- whatever the project is "about" at the noun level. Pull from CLAUDE.md or SoT files; ask if ambiguous.
3. **Codebase map**. Top-level tree, two levels deep. One line per directory describing what lives there. If monorepo, name each package/app and what it owns.
4. **SoT files** (if present). Where canonical facts live; how to disambiguate when memory and code disagree.
5. **Business plan + investor materials** (if present). What's in `business-plan/`, where the deck lives, where the financial model lives. Skip if absent.
6. **Hard rules + design specs**. `CLAUDE.md` first, `DESIGN.md`/`STYLE.md`/`ARCHITECTURE.md` if they exist, security policies, pre-commit guards.
7. **Backlog**. Where the WOs live, format, prefixes (BUG-/FTR-/TDT-/DSN- or whatever this project uses), how to add an item.
8. **Project memory**. Where `MEMORY.md` lives; high-load entries.
9. **Agent-to-domain map**. The full 70-agent org table. Cross-branch consult channel. Path-guard hook status. How to post to the human CEO (the project's actual handle, not "ceo" -- check comms.py + ask if uncertain).
10. **Recent canonical decisions** (≤ 10 rows). Pulled from CLAUDE.md, memory, SoT, or last 30 days of git log. Date, lock, one-line.
11. **Beta/launch gate snapshot**. Top 10-15 open items blocking the nearest milestone. Pull from backlog; sort by stated priority.
12. **"If you're working on X, read Y" lookup table**. The 10-15 most common cross-cutting tasks and where to start. Build by inspecting the codebase for recurring patterns (auth, data layer, UI components, payment, etc.).
13. **How to use the index**. Six-line ops manual for the chiefs.
14. **What this file is NOT**. Anti-scope so chiefs don't put status/roadmap/decisions here.

**Write rules for the index**:
- Pointer first, description second. `path -- one-line description.` is the canonical row.
- Absolute paths where the chief will copy-paste into a Read tool. Relative paths fine in tree diagrams.
- No narrative paragraphs. No "we think" or "probably." Either a pointer exists or it does not.
- Maintained-by line at the bottom names the EA layer. Last-revised date.

### Phase 3 -- Brief the C-suite in parallel (≤ 5 minutes)

Spawn all seven chiefs in a single message, each via the Agent tool with their `subagent_type`. Each gets:

- The path to the newly-written `ORG-INDEX.md`.
- The path to `CLAUDE.md` (project rules).
- 2-4 chief-specific files to read (SoT entries in their domain, key backlog file tops, relevant memory entries).
- A "do NOT grep the codebase, trust the index" instruction.
- A 4-section response template (see below).
- A hard word cap (500-600 words depending on chief).

**Standard 4-section response template** every chief uses:

```
## 1. Orientation confirm
One sentence "I'm oriented to <...>." plus:
(a) what part of the codebase / org touches this chief's domain
(b) the live in-flight work they can see
(c) the one canonical decision they most need to defend

## 2. Beta-blocker top 3 (lens of this chief)
Pull from the backlog. ID + one-line title + reason it's a blocker + dept-head to route to. Specifics, not categories.

## 3. NEW work order proposals (max 3)
Things the org is missing right now from this lens. Proposed prefix, one-line title, 2-3 sentence why, owner. Specific enough that the EA layer can file them post-council.

## 4. Council question for peers
One question for another chief -- the most important cross-branch decision needed before the next marathon-org wave.
```

**Chief-by-chief brief prompts** (copy these into each Agent call):

- **James (CTO)** -- `subagent_type: cto-james`. Read: ORG-INDEX, CLAUDE.md, backlog top of bugs.md + features.md.
- **Elle (CFO)** -- `subagent_type: cfo-eleanor`. Read: ORG-INDEX, CLAUDE.md, financial model (if exists), pricing + currency SoT (if exists), backlog top of bugs + features.
- **Mara (COO)** -- `subagent_type: coo-mara`. Read: ORG-INDEX, CLAUDE.md (esp. Deploy Discipline + push-cadence), roadmap SoT, backlog top of bugs + tech-debt.
- **Amelia (CAO)** -- `subagent_type: cao-amelia`. Read: ORG-INDEX, CLAUDE.md, DESIGN.md + DESIGN-GAME.md if present, COPY-SPEC.md if present, copy-style memory entries.
- **Margot (CMO)** -- `subagent_type: cmo-margot`. Read: ORG-INDEX, CLAUDE.md, marketing SoT, pricing SoT, business-plan deck path (don't read the full HTML), positioning memory entries.
- **Marisol (DOR)** -- `subagent_type: dor-marisol`. Read: ORG-INDEX, CLAUDE.md. Brief reply (500 words) since most repos are advisory-only for this branch. Tell the chief explicitly whether the product touches their domain.
- **Everett (CAP)** -- `subagent_type: cap-everett`. Read: ORG-INDEX, CLAUDE.md, SECURITY.md if present, currency + pricing SoT. Brief reply (500 words) for the same reason.

If the project doesn't use a domain (e.g., a non-financial repo doesn't need Marisol or Everett), skip those briefs and note "branch advisory-only with no product surface" in the index.

### Phase 4 -- Synthesize + file new WOs (≤ 3 minutes)

1. **Collect** all seven replies into a single in-conversation synthesis (no Write yet).
2. **De-duplicate** proposals. When two chiefs propose the same WO with different framing, consolidate -- name both chiefs in the "Filed by" line.
3. **Confirm with user** (skip if `--auto` flag): show the consolidated WO list, ask which to file. Default = all.
4. **File approved WOs** to the backlog. Use the project's backlog format (read one existing item per file to mirror shape). On Windows, use Edit tool to prepend to the file (avoid heredoc per the CreDub project's hard rule). Use the next-available ID -- read the highest-numbered visible item, increment from there, don't trust stale "Next ID" comments.
5. **Capture council questions** as memory entries (one per question -- type: `project`, name slug: `council_question_YYYY_MM_DD_<n>.md`). These should not become WOs; they need founder adjudication and the memory entry surfaces them next session.

### Phase 5 -- Emit the next marathon-org prompt (≤ 1 minute)

Write `prompts/setup-csuite-marathon.md` (or follow the project's numbered prompt convention -- check `prompts/` for existing patterns). Structure:

1. **Pre-flight** -- whatever the council surfaced as needing founder action before the next marathon (deploy debt, secrets, decisions outstanding).
2. **Launch prompt** -- a fenced block the founder pastes into a new session. Should call `/marathon-org` with category + wave size, then brief `cto-james` with the WO queue partitioned by file ownership.
3. **Expected output shape** -- what a successful marathon looks like (WOs closed, screenshots captured, push cadence respected, index updated).
4. **What this marathon does NOT do** -- explicit out-of-scope list so chiefs don't drift.
5. **What to run after** -- 2-4 follow-on marathon proposals.

### Phase 6 -- Final summary to the human

Single response. ≤ 400 words. Cover:
- The 4 files written (index + WOs filed + memory entries + next-marathon prompt).
- The 7 chiefs' headline takeaways (one bullet per chief).
- The 2-3 founder decisions still outstanding (council questions surfaced as memory).
- One line: "Next session: paste the launch prompt at `prompts/setup-csuite-marathon.md` to run the marathon."

## Invocation

```
/setup-csuite               -- run the full flow; ask before filing each batch
/setup-csuite --auto        -- run the full flow; file all proposed WOs without asking
/setup-csuite --refresh     -- only rebuild ORG-INDEX.md; skip the council
/setup-csuite --council     -- run only the council on an existing index
/setup-csuite --no-prompt   -- skip the next-marathon prompt emission
/setup-csuite --branches=cto,cfo,cao    -- only brief named branches (skip advisory-only)
```

## Hard rules

- **Never entangle adjacent entities.** The project lives in a repo path, the founder may have a day-job firm, the codebase may have been cloned from a prior internal tool. None of those make the prior entity an operator, co-owner, or compliance-liability surface of the current product. Before briefing chiefs, name the operating entity explicitly in the index ("X is the operator; Y is a warm-intro source / prior-art origin / unrelated firm of the founder"). When in doubt, ask the user -- do NOT import operator-entanglement framing into a chief's brief on your own initiative. This is especially important for CFO / CAP / DOR briefs where domain instincts will run toward "well if the founder also owns firm Y then surely..." -- no. Treat each entity as a discrete legal + operational island unless the user says otherwise.
- **Never re-explore what the index already maps.** If a chief asks "where is X" mid-council and the index has it, the answer is "in the index, section N." If the index doesn't have it, the index has a gap -- add the pointer, don't paper over it.
- **Pointers, not narrative.** The index is a map. Anything longer than 2-3 sentences per row belongs in `docs/` or `CLAUDE.md`, not here.
- **Trust CLAUDE.md.** If CLAUDE.md says no emojis / no em dashes / no anti-X framing / use Node not heredoc, the skill honors it -- in its own output, in the WOs it files, in the brief prompts it sends to the chiefs.
- **Read the backlog format before filing.** Mirror existing item shape per file. Use Edit (not Bash heredoc) to insert at the top.
- **Never invent backlog IDs.** Highest existing visible ID + 1, not whatever a stale "Next ID" comment claims.
- **Never spawn juniors.** This skill briefs chiefs only. The juniors run in the marathon that follows.
- **Single-pass orientation.** Each chief gets one shot to respond; no follow-up rounds. If they need more, they say so in their council question.
- **Confidence rating optional.** Chiefs may add a 1-5 confidence on their NEW WO proposals. The synthesizer uses it to tier the file order.
- **Update, don't append.** On `--refresh`, the skill rewrites the index whole. It does not "patch on top of" a stale version.

## What this skill does NOT do

- Does not write code or modify product files. Index + backlog + memory + prompt files only.
- Does not run a marathon. It produces the prompt to run one.
- Does not replace `/marathon-org`, `/work-orders`, or `/agent-org`. It complements them.
- Does not maintain the index after the session ends. Tim (CTO-EA) and the EA layer own ongoing maintenance; flag drift via a TDT when noticed.
- Does not require the project to be financial, gamified, or any specific shape. The branch composition flexes: if a project has no finance surface, Elle's brief returns "advisory-only, no live work" and that's a valid council seat.

## Diagnostic

`/setup-csuite --diagnose` prints:
- ORG-INDEX.md path + last-modified.
- Backlog path + counts per file.
- Which chiefs have brief files in `.claude/agents/` (sanity check: 7 chiefs + 1 VP-AI + 7 EAs + heads + juniors).
- Whether `comms.py` is present.
- Path-guard hook status.
- Last `/setup-csuite` run date (from memory).

Maintained by the EA layer (Tim primary; Soph/Jas/Elena/Anika/Juno/Rina contribute when their branch's index section drifts). Skill version 1.0 -- 2026-05-21.
