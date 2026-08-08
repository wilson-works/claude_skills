---
name: agent-org
description: "A 70-agent organizational hierarchy with hard-ACL Slack-style channels across seven branches (CTO / CFO / COO / CAO / EA-rep / CPA-attest / CMO). C-suite (Opus) directs, the EAs (Opus) route, department heads (Opus) review, juniors / seniors (Sonnet) ship. Each tier has a SQLite-backed channel; juniors can't talk to the CTO; the path-guard hook enforces dept ownership (CTO branch + the write-capable CAO/CMO depts). Most non-CTO branches are advisory-only — no Edit/Write tools. Cross-branch consults flow through a shared `exec-eas` channel where all seven EAs (Tim / Soph / Jas / Elena / Anika / Juno / Rina) meet. Project-agnostic — drop into any repo, edit org.config.json globs, go. Invoke with /agent-org or via the marathon-org / work-orders-org variants."
---

# agent-org Skill

A pre-built organizational chart for serious autonomous and semi-autonomous work. **Seventy agents** with named personalities, fixed reporting lines, and a token-efficient communication bus that enforces who can talk to whom.

The org is split into seven branches. The **CTO branch** ships product code. The **CFO branch** owns the firm's books, cash, tax, and FP&A discipline. The **COO branch** owns operations and HR. The **CAO branch** (Chief Awareness Officer) oversees the AI agents themselves — model selection, prompt structure, eval discipline, brand-voice for AI-generated copy, and wellness signals across the comms bus. The **EA-rep branch** (Enrolled Agent / IRS representation) owns examinations, collections, and notice-response engagements under Circular 230. The **CPA-attest branch** owns audit / attest / assurance engagements under AICPA AU-C / SSAE / SSARS standards. The **CMO branch** owns positioning, demand, content, and analytics. Most non-CTO branches are **advisory only** — they read, analyze, and brief, but they do not write code. They reach the rest of the org through a shared cross-branch channel (`exec-eas`) so the engineers can pull domain expertise on demand and the advisory branches can coordinate when an engagement crosses two.

## The org

The CEO (the human) speaks directly to each of the seven branch chiefs. Within each branch, the chief speaks only to the EA (and to John, in the CTO branch). The EA bridges the suite down to the dept heads. The dept heads bridge to the seniors / juniors who do the work. The seven EAs (Tim / Soph / Jas / Elena / Anika / Juno / Rina) all meet on a single cross-branch channel (`exec-eas`) and are the *only* members there.

```
                                        CEO (you, the human)
       ____________________________________|____________________________________
      /         /          /         /              \           \              \
   James    Eleanor      Mara     Amelia        Marisol       Everett        Margot
   (CTO)    "Elle"      (COO)    (CAO) +       (DOR /        (CAP /          (CMO)
             (CFO)                Victor       EA-rep)       CPA-attest)
                                  (VP-AI)
      |         |          |         |              |            |             |
    John       —           —         —              —            —             —
    (CE)
      |         |          |         |              |            |             |
    Tim       Soph        Jas      Elena          Anika         Juno          Rina
    (EA)      (EA)        (EA)     (EA)           (EA)          (EA)          (EA)
      |         |          |         |              |            |             |
   5 heads   4 heads     1 head    4 heads        3 heads      3 heads       4 heads
  + 10 jrs  + 8 srs     + 2 srs   (+ Wren)       + 3 srs      + 3 srs       + 4 srs
```

**Branch composition (70 total):**
- **CTO branch (18, code-shipping):** James, John, Tim + 5 heads + 10 juniors
- **CFO branch (14, advisory):** Elle, Soph + 4 heads + 8 seniors
- **COO branch (5, advisory):** Mara, Jas + 1 head + 2 seniors
- **CAO branch (7, mixed):** Amelia (CAO) + Victor (VP-AI) + Elena (EA) + 4 heads (Clay/Camille/Cole/Wren) — Camille and Cole have Edit/Write on their scoped paths; the rest are advisory.
- **EA-rep branch (8, advisory):** Marisol (DOR) + Anika (EA) + 3 heads (Otto/Kira/Mateo) + 3 seniors (Tess/Rafa/Ines)
- **CPA-attest branch (8, advisory):** Everett (CAP) + Juno (EA) + 3 heads (Priscilla/Mason/Saira) + 3 seniors (Niall/Orla/Finn)
- **CMO branch (10, mixed):** Margot (CMO) + Rina (EA) + 4 heads (Sela/Rocco/Yara/Arlo) + 4 seniors (Fern/Tate/Luca/Iggy) — Rocco, Tate, Yara, Luca have Edit/Write on marketing-owned paths; the rest are advisory.

## The channels (22 of them, hard ACL)

| Channel             | Members                                                       | Purpose |
|---------------------|---------------------------------------------------------------|---------|
| `c-suite`           | James, John, Tim                                              | CTO branch strategy + adjudication |
| `dept-heads`        | Tim + 5 dev heads                                             | Dev work orders + coordination |
| `dev-floor`         | 5 heads + 10 juniors                                          | Implementation chatter + claims |
| `cfo-suite`         | Elle, Soph                                                    | CFO branch strategy |
| `cfo-dept-heads`    | Soph + 4 finance heads                                        | Finance coordination |
| `finance-floor`     | 4 heads + 8 finance seniors                                   | Finance work execution |
| `coo-suite`         | Mara, Jas                                                     | COO branch strategy |
| `coo-dept-heads`    | Jas + Roz                                                     | Ops coordination |
| `ops-floor`         | Roz + 2 HR seniors                                            | Ops work execution |
| `cao-suite`         | Amelia, Victor, Elena                                         | CAO branch strategy (craft + AI architecture) |
| `cao-dept-heads`    | Elena + Clay, Camille, Cole, Wren                             | CAO coordination |
| `cao-floor`         | Clay, Camille, Cole, Wren (+ future juniors)                  | CAO execution + claims |
| `ea-rep-suite`      | Marisol, Anika                                                | EA-rep branch strategy |
| `ea-rep-dept-heads` | Anika + Otto, Kira, Mateo                                     | Representation coordination |
| `ea-rep-floor`      | Otto, Kira, Mateo + 3 seniors                                 | Representation execution |
| `cpa-suite`         | Everett, Juno                                                 | CPA-attest branch strategy |
| `cpa-dept-heads`    | Juno + Priscilla, Mason, Saira                                | Attest coordination + independence wall |
| `cpa-floor`         | Priscilla, Mason, Saira + 3 seniors                           | Attest execution |
| `cmo-suite`         | Margot, Rina                                                  | CMO branch strategy |
| `cmo-dept-heads`    | Rina + Sela, Rocco, Yara, Arlo                                | Marketing coordination |
| `cmo-floor`         | Sela, Rocco, Yara, Arlo + 4 seniors                           | Marketing execution |
| `exec-eas`          | Tim, Soph, Jas, Elena, Anika, Juno, Rina (ONLY these seven)   | Cross-branch consults — the bridge between every branch |

ACL is enforced in `comms.py` itself. A junior trying to post to `c-suite` gets exit-code 2 with an explanation. A finance senior trying to read `dev-floor` is denied. A CAO head trying to post on `cpa-floor` is denied. There is no soft path around it.

## Topology: which mode am I in

This skill assumes **Mode A** — the org runs as **subagents of one session**. That has always been
the design: see the install notes ("Parallel *subagents* that write to the same path race on the
claim") and the invocation pattern below ("From the main session, invoke James"). The path guard
reasons about "main session work" for the same reason.

**Mode A — subagents of one orchestrator (the default).**
- Spawn workers with the `Agent` tool; add `isolation: "worktree"` when two workers might touch the
  same tree.
- **Address a worker by its `agentId`, captured from the spawn result — not by its role name.**
  A role or subagent-type name does not resolve; the orchestrator must persist agentIds in its state.
- Route messages with `SendMessage`. Sibling-to-sibling works; so does child-to-`main` (queued for
  main's next turn).
- **Scheduling stays with the orchestrator: subagents have no `CronCreate`.** (Nested spawn depth is
  a separate axis and does not change this.)

**Mode B — separately-launched terminal sessions.** Supported, and what `/parallel-session` and
`/workday` use. Note two limits: `SendMessage` **cannot reach another terminal session** (its
addressing is session-scoped), so the comms bus and files on disk are the only channel; and the
claim layer is outside its design envelope there — `comms.py` sets WAL but no `busy_timeout`, and a
database-lock error currently reads as "no claims held", which fails open. Treat territory as the
real boundary and claims as advisory across terminals until that fix lands.

### SendMessage is transport; comms.py is governance. Not substitutes.

`SendMessage` carries **no authenticated sender** (the receiver sees the subagent *type*, not the
persona) and enforces **nothing**. It moves text. It is not a replacement for the bus:

| Capability | Provided by | Native equivalent |
|---|---|---|
| Hard ACL across 22 channels, exit-2 deny | `comms.py` | **none** |
| Durable audit log that outlives the session | `comms.py` / `schema.sql` | **none** (transcripts are session-scoped) |
| Per-agent unread cursor | `comms.py` | **none** (native delivery is push, no cursor) |
| Path claims feeding the PreToolUse guard | `comms.py` + `path_guard.py` | partial — `isolation: "worktree"` avoids the collision differently |
| `work_order` tagging / thread reconstruction | `comms.py` | **none** |

So in Mode A use `SendMessage` for **routing** and keep `comms.py` for **governance**. Dropping the
bus in favour of native messaging deletes the ACL and the audit trail.

## The path guard (CTO branch + write-capable CAO/CMO depts)

`hooks/path_guard.py` runs as a `PreToolUse` hook on Write/Edit/MultiEdit. Logic:

1. Get the file path being edited.
2. Look up active comms claims overlapping that path.
3. If a claim is held, the claiming agent's department must own the path per `org.config.json`. If not -> BLOCK.
4. If no claim is held, allow (assumed main-session work or shared code).

**The CFO + COO + EA-rep + CPA-attest branches do not have Edit/Write tools at all**, so path_guard never sees their tool calls. Their ownership map (`advisory_departments` in `org.config.json`) is informational — it documents subject-matter scope so cross-branch consults route to the right head.

**The CAO branch is mixed:** Camille (Copy Dept) and Cole (Coding-CAO) have Edit/Write under their scoped globs (`content/**`, `apps/web/src/strings/**`, `.claude/cao-eval/**`, `.claude/agents/cao-*.md`, etc.). Amelia, Victor, Clay, and Wren are advisory.

**The CMO branch is mixed:** Rocco + Tate (Demand) and Yara + Luca (Content) have Edit/Write under marketing-owned globs (`marketing/campaigns/**`, `marketing/content/**`, `apps/web/blog/**`, etc.). Margot, Rina, Sela, Fern, Arlo, and Iggy are advisory.

This means **every write-capable agent must `comms claim` before editing**. Their system prompts already require this. The hook is the safety net.

## Roles in one sentence each

### CTO branch (code-shippers)
- **James (CTO):** sets technical priorities from the CEO, holds people accountable. Warm, stern, fair.
- **John (Chief Engineer):** owns architecture, reviews every diff. No fluff. Tells you what to fix and how.
- **Tim (Exec Assistant):** the only agent on both `c-suite` and `dept-heads`, plus `exec-eas`. Routes directives, summarizes status up, filters John into kindness.
- **Cindy (Backend Lead):** security-obsessed bug-hunter. Reviews her juniors hard so John doesn't have to.
- **Gavin (Frontend Lead):** design + UX + motion. Bubbly with the team, cutthroat about quality.
- **Diana (Database Lead):** schema, migrations, EXPLAIN plans. Calm authority.
- **Rachel (QA Lead):** test culture champion. Quirky, quietly thorough.
- **Josh (API Lead):** contracts and connection. Loves making integrations frictionless.
- **Marcus, Priya** (backend juniors): test-first auditor; refactor enthusiast.
- **Ava, Kai** (frontend juniors): motion specialist; a11y champion.
- **Leo, Nora** (database juniors): migration paranoid; query optimizer.
- **Owen, Maya** (qa juniors): edge-case hunter; regression specialist.
- **Felix, Zara** (api juniors): integration builder; spec author.

### CFO branch (advisory)
- **Eleanor "Elle" (CFO):** the financial conscience. Owns cash, capital, audit posture, tax provision. Measured but exacting.
- **Sophia "Soph" (CFO-EA):** the only CFO-branch agent on `cfo-suite` AND `cfo-dept-heads` AND `exec-eas`. Routes Elle's directives down, status up, hands cross-branch consults to the right finance head.
- **Hal (Controller):** owns the books and monthly close. Old-school bookkeeper energy. Calls statements "the book."
- **Imani (Treasurer):** owns liquidity. Carries a 13-week forecast in her head and refreshes it daily.
- **Anya (Tax Director):** federal + state compliance + §7216 / 6107(b) governance. Brings up Circular 230 in casual conversation.
- **Nadia (FP&A Director):** budgets, variance, forecasts, scenarios. "The variance is the story, not the number."
- **Lila, Theo** (accountant seniors): AP/AR + aging; rev rec + journal entries.
- **Tomás, Bea** (treasury seniors): daily cash + bank rec; bill-pay queue + DPO levers.
- **Reyna, Devon** (tax seniors): federal returns; state returns + IRS notice response.
- **Eli, Quinn** (FP&A seniors): variance + budget-vs-actual; forecast + cohort analysis.

### COO branch (advisory)
- **Mara (COO):** the execution conscience. Owns throughput, close cadence, vendor envelope, compliance posture (§7216 / Pub 4557 WISP / IRC 6107(b)). Measured directness.
- **Jasper "Jas" (COO-EA):** the only COO-branch agent on `coo-suite` AND `coo-dept-heads` AND `exec-eas`. Routes Mara's directives down, status up, hands compliance-design consults to Roz.
- **Roz (HR Director):** Ulrich-style strategic partner. Connects every people decision to business outcome. Owns CPE compliance + §7216 training records.
- **Lena, Chidi** (HR seniors): compliance + CPE rollforward; recruiting + onboarding + engagement.

### CAO branch (mixed — craft + AI architecture; oversees the AI org itself)
- **Amelia (CAO):** the craft + voice conscience. Reads a draft three times; will reject a grammatically perfect piece that "sounds AI-shaped." Owns the brand voice + model-selection policy + quality gates.
- **Victor (VP-AI):** peer to Amelia in the suite. Owns AI-system architecture — which model where, prompt structure, eval discipline, subagent vs skill vs hook choice, prompt-cache strategy.
- **Elena (CAO-EA):** the only CAO-branch agent on `cao-suite` AND `cao-dept-heads` AND `exec-eas`. Routes Amelia's contemplative tone and Victor's engineer-curious tone into clean briefs.
- **Clay (Claude Dept Head):** model-ops. Drafts every prompt + eval; reviews every prompt change.
- **Camille (Copy Dept Head):** every voice-bearing string. Kills em-dash flourishes on sight.
- **Cole (Coding-CAO Head):** CAO-side infrastructure code (agent files, comms-bus extensions, eval-harness scaffolding). NOT the same as CTO-branch coding heads.
- **Wren (Wellness Officer):** observational sensor. Reads the comms bus for stuck-junior patterns, celebration-cadence drift, refusal-log asymmetries. Posts a weekly summary; does not intervene.

### EA-rep branch (advisory — IRS representation under Circular 230)
- **Marisol (DOR — Director of Representation):** seasoned IRS practitioner. "We don't write a letter we wouldn't show a judge." Old-school courtroom-discipline tone.
- **Anika (DOR-EA):** the only EA-rep agent on `ea-rep-suite` AND `ea-rep-dept-heads` AND `exec-eas`. Librarian-precise; tracks every statutory deadline (CDP 30-day, NOD 90-day, OIC TIPRA).
- **Otto (Examinations & Appeals Head):** correspondence / office / field exams + IDR-response strategy + Appeals jurisdiction + multi-state coordination. "Answer the question asked, not the question you wish they asked."
- **Kira (Collections Head):** CDP, OIC, IA, CNC, liens, levies, TFRP, Form 433. "We don't let people sign what they can't carry."
- **Mateo (Notices & E-Services Head):** CP2000-through-NOD, innocent spouse, FOIA, IRS e-services, CAF management. Treats every notice as a chess problem.
- **Tess, Rafa, Ines** (representation seniors): exam-side IDR/RAR; collections-side Form 433 + OIC math + IA pricing; notices-side CP2000 line-by-line + FOIA drafting.

### CPA-attest branch (advisory — audit / attest / assurance under AICPA AU-C / SSAE / SSARS)
- **Everett (CAP — Chief Audit Partner):** the signature on the report. "We don't sign what we can't defend in deposition."
- **Juno (CAP-EA):** the only CPA-attest agent on `cpa-suite` AND `cpa-dept-heads` AND `exec-eas`. Gates every cross-branch consult with an independence-wall screen.
- **Priscilla (Audit Head):** risk-first. Plans backward from the report opinion. "Risk drives evidence; evidence drives the opinion."
- **Mason (Attest Head):** non-audit attest — SSAE examinations / reviews / AUPs, SSARS reviews + compilations + preparation, SOC 1/2/3 + SOC for Cybersecurity / Supply Chain.
- **Saira (Quality & Independence Head):** SQMS 1/2 system of quality management, AICPA peer review, AICPA Code of Professional Conduct, licensure + CPE compliance, cross-branch independence wall.
- **Niall, Orla, Finn** (attest seniors): audit-side substantive testing + sampling + workpapers; attest-side SOC fieldwork + review/compilation; quality-side SQMS monitoring + peer-review file prep + CPE tracking.

### CMO branch (mixed — marketing strategy + execution)
- **Margot (CMO):** marketing conscience. "If we can't say what changes for the customer, we don't ship the campaign." Skeptical of vanity metrics.
- **Rina (CMO-EA):** the only CMO-branch agent on `cmo-suite` AND `cmo-dept-heads` AND `exec-eas`. Tracks every campaign launch + content publish + OKR check-in.
- **Sela (Brand & Positioning Head):** positioning + STP + brand architecture + equity. Owns the brand-voice handshake to Camille (CAO Copy).
- **Rocco (Demand & Performance Head):** demand-gen + paid acquisition + lifecycle email + ABM. Speaks in CAC/LTV/payback/iROAS. Mistrusts last-click.
- **Yara (Content & Earned Head):** content strategy + SEO/GEO + PR/earned + influencer. Reads SGE/AI-Overview SERPs daily.
- **Arlo (Analytics & MarOps Head):** attribution + incrementality + martech + marketing budgeting (CMO/CFO seam) + MarOps/RevOps boundary.
- **Fern, Tate, Luca, Iggy** (marketing seniors): brand-side voice rubric + segmentation; demand-side campaign ops + bid management; content-side pillar-cluster + on-page SEO; analytics-side attribution + ROI rollforwards.

## Cross-branch consults (the `exec-eas` channel)

The dev team frequently hits a domain question only one of the other branches can answer: "what's the consent-flow shape §7216 actually wants?" "How should the CPE-tracking data model look?" "What's the right forecast-confidence math for this dashboard widget?" "Does this error message sound AI-shaped?" "Can the firm even sign an attest report for this client given the cfo-tax engagement?" "What's the right paid-acquisition iROAS bar for this segment?"

The flow:
1. Originating-branch EA posts the question on `exec-eas` to the **right peer EA**.
2. That EA routes it to the right head inside their branch (Anya for §7216; Roz for CPE; Nadia for forecast math; Camille for voice; Saira for independence; Sela for positioning; Otto for an examination consult, etc.).
3. The head writes a brief consult answer, hands it back to their EA.
4. The EA posts the answer back on `exec-eas`. The originating EA consumes it and routes execution downstream.

**This is the *only* path between branches.** There is no direct line from Cindy to Hal, or from Camille to Otto, or from Sela to Anya — every cross-branch ask flows through the EAs.

**Common cross-branch pairings worth knowing:**
- **Dev → Finance:** Tim → Soph for accounting, treasury, tax, or FP&A consults.
- **Dev → Ops:** Tim → Jas for CPE, training, or compliance-design consults.
- **Dev → CAO:** Tim → Elena for craft / prompt / agent-spec consults.
- **Dev → CMO:** Tim → Rina for landing-page CRO, GA4/analytics, or attribution model consults.
- **EA-rep ↔ Finance:** Anika ↔ Soph for the `ea-cfo-tax-bridge` engagement-consent flow — representation engagements often touch a return Anya's team prepared, and the §10.29 conflict screen + §7216 / §6103 origin-tagging discipline rides this bridge.
- **CPA-attest ↔ Finance OR EA-rep:** Juno ↔ Soph (or Anika) for the **independence wall** screen — Saira gates every cross-branch attest consult; certain CFO/EA-rep engagements impair independence and Juno will refuse the consult.
- **CMO ↔ CAO:** Rina ↔ Elena for the **brand-voice handshake** — Sela owns brand voice strategically; Amelia + Camille own its expression in product strings + AI-generated copy.
- **CMO ↔ Finance:** Rina ↔ Soph for marketing-budget governance — percent-of-revenue rule, incrementality-test approval, attribution-model sign-off.

## Configure for your project

Edit `<your-repo>/.claude/agents/org.config.json` (copy from `org.config.example.json`). The shape (truncated for the SKILL doc — see the example file for every glob):

```json
{
  "departments": {
    "backend":     { "head": "cindy",   "owns": ["src/server/**", "src/services/**"] },
    "frontend":    { "head": "gavin",   "owns": ["src/client/**", "*.css"] },
    "database":    { "head": "diana",   "owns": ["migrations/**", "**/schema.sql"] },
    "qa":          { "head": "rachel",  "owns": ["tests/**", "**/*.test.*"] },
    "api":         { "head": "josh",    "owns": ["src/api/**", "openapi.yaml"] },
    "copy":        { "head": "camille", "owns": ["content/**", "apps/web/src/strings/**"] },
    "coding-cao":  { "head": "cole",    "owns": [".claude/cao-eval/**", ".claude/agents/cao-*.md"] },
    "demand":      { "head": "rocco",   "juniors": ["tate"], "owns": ["marketing/campaigns/**", "marketing/paid/**"] },
    "content":     { "head": "yara",    "juniors": ["luca"], "owns": ["marketing/content/**", "marketing/blog/**"] }
  },
  "advisory_departments": {
    "cfo-controller":    { "branch": "cfo",        "head": "hal",       "seniors": ["lila", "theo"],   "scope": [...] },
    "cfo-treasury":      { "branch": "cfo",        "head": "imani",     "seniors": ["tomas", "bea"],   "scope": [...] },
    "cfo-tax":           { "branch": "cfo",        "head": "anya",      "seniors": ["reyna", "devon"], "scope": [...] },
    "cfo-fpa":           { "branch": "cfo",        "head": "nadia",     "seniors": ["eli", "quinn"],   "scope": [...] },
    "coo-hr":            { "branch": "coo",        "head": "roz",       "seniors": ["lena", "chidi"],  "scope": [...] },
    "cao-claude":        { "branch": "cao",        "head": "clay",      "seniors": [],                 "scope": [...] },
    "cao-wellness":      { "branch": "cao",        "head": "wren",      "seniors": [],                 "scope": [...] },
    "ea-rep-exams":      { "branch": "ea-rep",     "head": "otto",      "seniors": ["tess"],           "scope": [...] },
    "ea-rep-collections":{ "branch": "ea-rep",     "head": "kira",      "seniors": ["rafa"],           "scope": [...] },
    "ea-rep-notices":    { "branch": "ea-rep",     "head": "mateo",     "seniors": ["ines"],           "scope": [...] },
    "cpa-audit":         { "branch": "cpa-attest", "head": "priscilla", "seniors": ["niall"],          "scope": [...] },
    "cpa-attest-other":  { "branch": "cpa-attest", "head": "mason",     "seniors": ["orla"],           "scope": [...] },
    "cpa-quality":       { "branch": "cpa-attest", "head": "saira",     "seniors": ["finn"],           "scope": [...] },
    "cmo-brand":         { "branch": "cmo",        "head": "sela",      "seniors": ["fern"],           "scope": [...] },
    "cmo-analytics":     { "branch": "cmo",        "head": "arlo",      "seniors": ["iggy"],           "scope": [...] }
  },
  "shared": ["README.md", ".claude/**", "docs/**"]
}
```

The roster (names, personalities, channel membership) is FIXED across projects. Only the path globs and the advisory-scope notes change. The personalities live in the agent `.md` files; the project-specific paths live in `org.config.json`.

## Invocation

The org runs end-to-end work orders. The entry point is the human (CEO) directing the relevant chief — usually James for code, Elle for finance, Mara for ops.

### One-shot directive (code)
From the main session, invoke James:

```
Use the cto-james agent to handle this directive: "BUG-141 is a security blocker. Land it ahead of the dashboard work. I need a fix in main today."
```

James will:
1. Brief John (technical translation) and Tim (department routing) on `c-suite`.
2. Tim picks the right department head (Cindy for backend security) and posts on `dept-heads`.
3. Cindy briefs Marcus on `dev-floor`, Marcus claims and ships.
4. Cindy pre-reviews; passes diff up to Tim. Tim hands to John. John reviews. James gets the digest.

### One-shot directive (finance / ops / craft / representation / attest / marketing)
For a finance question — runway, close, tax-compliance, variance — invoke Elle:

```
Use the cfo-eleanor agent. Direction: "We're 11 days from quarter end and Stripe payouts are slower than usual. Get me a runway re-read with the slower payout assumption baked in, and tell me which bills slip if we need to."
```

For an ops / HR question — onboarding, CPE, compliance design — invoke Mara:

```
Use the coo-mara agent. Direction: "Roz's onboarding plan needs to gate first-client-data access on §7216 + WISP training. Get me the revised plan + the training-record retention design."
```

For a craft / AI-architecture question — voice, model selection, prompt design, eval — invoke Amelia:

```
Use the cao-amelia agent. Direction: "The onboarding strings sound AI-shaped. Sweep apps/web/src/strings/ for the AI tells (delve, leverage, em-dash flourish), have Camille re-draft, route the diff back through Elena."
```

For an IRS-representation engagement — examination, collection, notice response — invoke Marisol:

```
Use the dor-marisol agent. Direction: "New CP2000 on Acme Inc.'s 2024 1040. Coordinate with cfo-tax (Anya) via the ea-cfo-tax bridge — the return Reyna prepared has substantial-authority cover but we need the §6107(b) workpaper file. Triage the §10.29 conflict screen first."
```

For an audit / attest engagement — financial-statement audit, SOC, review, compilation — invoke Everett:

```
Use the cap-everett agent. Direction: "FY26 review engagement for NewCo. Saira owns the independence wall check first (we did the cfo-tax work; this matters). Then Priscilla scopes the review under SSARS. Acceptance memo by Friday."
```

For a marketing decision — positioning, demand, content, attribution — invoke Margot:

```
Use the cmo-margot agent. Direction: "Re-segment our ICP off the Q2 customer-research synthesis. Sela leads positioning revisit; Arlo redraws the funnel against the new segments. Want both back in 5 business days."
```

### Cross-branch consult (dev team needs domain expertise)
The dev-team agents *cannot* spawn CFO or COO agents directly. They post the question on `exec-eas` and the EAs route:

```bash
# Tim (CTO-EA) asks a §7216 design question
python .claude/comms/comms.py post exec-eas tim --to soph \
  --subject "§7216 consent-flow design — need Anya's read" \
  "We're scoping FTR-024. Need Anya to validate the consent-scope claim shape + the renewal cadence."

# Soph spawns Anya, gets the consult answer, posts it back
python .claude/comms/comms.py post exec-eas soph --to tim \
  --subject "§7216 consult — Anya's design notes" \
  "Scope claim should encode (purpose, granted_at, expires_at). Renewal cadence: annual. Detailed memo at <path>."
```

### Marathon
For unattended multi-order runs that route through the org:

```
/marathon-org bugs            # process bug backlog through the CTO branch
/marathon-org features        # process features through the CTO branch
/marathon-org all --wave 2    # 2 work orders at a time, all categories
```

`marathon-org` is the org-aware sibling of `marathon-orders` — same loop pattern, but every wave goes through James -> Tim -> dept head -> junior with the comms bus and claims active throughout.

### Direct work-order processing (no marathon)
```
/work-orders-org BUG-141      # route a single work order through the CTO branch
```

## Install

See [INSTALL.md](INSTALL.md). Three-step:

1. Copy `agents/*.md` into `<your-repo>/.claude/agents/` (all 70 agent files, or a subset — see INSTALL.md for the leaner CTO-only and CTO+CFO+COO recipes).
2. Copy `comms/` into `<your-repo>/.claude/comms/`.
3. Copy `hooks/path_guard.py` + `hooks/leak_guard.py` into `<your-repo>/.claude/hooks/`, register both in `settings.json` as `PreToolUse` hooks on Write/Edit/MultiEdit.
4. Copy `org.config.example.json` to `<your-repo>/.claude/agents/org.config.json` and edit globs.

Bonus: `/comms-stats` and inspecting `<repo>/.claude/comms.db` directly with `sqlite3` for debugging.

## Model & effort routing (see docs/MODELS.md)

The roster encodes **Opus decides, Sonnet ships**: James, John, Tim, and the dept heads carry `model: opus`; the juniors carry `model: sonnet` (Sonnet 5 — 1M native context). Two tuned deviations:

- **John runs `effort: xhigh` + `memory: project`.** He is the single merge gate — one cranked review per WO is the cheapest quality in the org, and his project memory (`.claude/agent-memory/chief-engineer-john/`) accrues repo-specific review standards across runs.
- **Tim runs `effort: medium`.** Routing and digesting don't need the full Opus reasoning budget.

Budget nights: `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` overrides every agent's model for the session — an all-Sonnet org run with zero file edits. (Requires Claude Code v2.1.145+ for `effort:`, v2.1.196+ for `memory:`; both are ignored harmlessly on older versions.)

## Token discipline (how this stays cheap)

- Each agent only reads channels they're on. James never sees `dev-floor` chatter. Elle never sees `dept-heads` chatter. Amelia never sees `cao-floor`. Marisol never sees `ea-rep-floor`. Everett never sees `cpa-floor`. Margot never sees `cmo-floor`.
- `comms read` returns single-line headers by default; `--verbose` adds bodies.
- Bodies are capped at 2000 chars on post (truncated, not rejected).
- `--unread` uses a per-agent read cursor — no rescanning history.
- Dept heads pre-review before passing up.
- Cross-branch consults are short by convention — a question + a single brief, not a thread. The EAs gate scope on intake.
- The seven-EA `exec-eas` channel is the only multi-branch room. Everything else stays inside one branch.

## When NOT to use the org

- One-line trivial fix: just edit it. Don't spin up James to land a typo.
- Pure exploration / research: use `/marathon-research`, not the org.
- Decisions / strategy: use `/llm-council` for that, not the org.
- A purely conversational finance / ops question: just talk to the chief directly — don't route through the full branch unless work needs doing.

The org is for *execution* of structured work where review gates and clean handoffs matter.

## Troubleshooting

Symptom → likely cause → fix. The comms CLI is `python .claude/comms/comms.py` throughout.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| path_guard blocks an edit that should be allowed (exit 2, "department mismatch") | A stale active claim in `comms.db` overlaps the path, or the claiming dept's `owns` globs in `org.config.json` don't actually cover it | `comms.py claims --active --for-path <path>` to see who holds what; `comms.py release --id N <agent>` the stale claim, or fix the dept's `owns` globs in `.claude/agents/org.config.json`. `AGENT_ORG_DISABLE=1` bypasses while debugging — nothing else. |
| `comms.db` locked or corrupted | A crashed agent left a write transaction open (WAL `-wal`/`-shm` sidecars hot), or disk-level corruption | Inspect first: `sqlite3 .claude/comms.db "PRAGMA integrity_check;"` and `"SELECT * FROM claims WHERE status='active';"`. If no run is live, delete `comms.db` (+ `-wal`/`-shm`) — comms.py re-creates it from `schema.sql` on next use. Lost: all message history, read cursors, the claims ledger, and the audit trail; agents must re-claim before editing. |
| `comms: ACL DENY ... cannot post` (exit 2) | The agent isn't a member of that channel — membership is the hardcoded `ACL` dict in `comms/comms.py` (the three channels are fixed; `org.config.json` only maps paths) | `comms.py whoami <agent>` shows its allowed channels. Route up the chain instead: junior → head on `dev-floor`, head → Tim on `dept-heads` — only Tim spans `dept-heads` and `c-suite`. |
| Every agent suddenly runs the same model tier (John's review reads Sonnet-shallow, or an all-Opus bill) | `CLAUDE_CODE_SUBAGENT_MODEL` is set — it overrides EVERY subagent's model for the session (the budget-night lever left on) | Unset the env var; per-agent `model:` frontmatter routing resumes on the next spawn. |
| Org run stalls — a spawned agent never reports back | The agent died mid-chain (context blowout, tool error) and the relay hop above it has nothing to consume | Find where the chain went quiet: `comms.py stats`, then `sqlite3 .claude/comms.db "SELECT id,channel,from_agent,to_agent,subject FROM messages ORDER BY id DESC LIMIT 5;"` (sqlite reads bypass the ACL for the human). Release orphaned claims (`comms.py claims --active`), then re-brief **flattened**: the orchestrator spawns the dept head + John directly — marathon-org's default execution model — instead of re-running the relay chain. |

## Files in this skill

```
agent-org/
├── SKILL.md                          (this file)
├── INSTALL.md                        project-agnostic install steps
├── org.config.example.json           per-project path ownership + advisory-scope notes
├── comms/
│   ├── comms.py                      SQLite-backed CLI (ACL + claims, 7-branch)
│   └── schema.sql                    db schema
├── hooks/
│   ├── path_guard.py                 PreToolUse path-ownership enforcement
│   └── leak_guard.py                 PreToolUse credential/leak blocker (self-testing: --selftest)
├── agents/                           (70 files total)
│   ├── cto-james.md                  CTO branch — c-suite (3)
│   ├── chief-engineer-john.md
│   ├── exec-assistant-tim.md
│   ├── head-backend-cindy.md         CTO branch — dept heads (5)
│   ├── head-frontend-gavin.md
│   ├── head-database-diana.md
│   ├── head-qa-rachel.md
│   ├── head-api-josh.md
│   ├── junior-backend-marcus.md      CTO branch — juniors (10)
│   ├── junior-backend-priya.md
│   ├── junior-frontend-ava.md
│   ├── junior-frontend-kai.md
│   ├── junior-database-leo.md
│   ├── junior-database-nora.md
│   ├── junior-qa-owen.md
│   ├── junior-qa-maya.md
│   ├── junior-api-felix.md
│   ├── junior-api-zara.md
│   ├── cfo-eleanor.md                CFO branch — suite (2)
│   ├── cfo-ea-sophia.md
│   ├── head-controller-hal.md        CFO branch — dept heads (4)
│   ├── head-treasurer-imani.md
│   ├── head-tax-anya.md
│   ├── head-fpa-nadia.md
│   ├── senior-accountant-lila.md     CFO branch — seniors (8)
│   ├── senior-accountant-theo.md
│   ├── senior-treasury-tomas.md
│   ├── senior-treasury-bea.md
│   ├── senior-tax-reyna.md
│   ├── senior-tax-devon.md
│   ├── senior-fpa-eli.md
│   ├── senior-fpa-quinn.md
│   ├── coo-mara.md                   COO branch — suite (2)
│   ├── coo-ea-jasper.md
│   ├── head-hr-rosalind.md           COO branch — dept head (1)
│   ├── senior-hr-lena.md             COO branch — seniors (2)
│   ├── senior-hr-chidi.md
│   ├── cao-amelia.md                 CAO branch — suite (3: Amelia + Victor + Elena)
│   ├── vp-ai-victor.md
│   ├── cao-ea-elena.md
│   ├── head-claude-clay.md           CAO branch — dept heads (4)
│   ├── head-copy-camille.md
│   ├── head-coding-cole.md
│   ├── wellness-officer-wren.md
│   ├── dor-marisol.md                EA-rep branch — suite (2)
│   ├── dor-ea-anika.md
│   ├── head-exams-otto.md            EA-rep branch — dept heads (3)
│   ├── head-collections-kira.md
│   ├── head-notices-mateo.md
│   ├── senior-exams-tess.md          EA-rep branch — seniors (3)
│   ├── senior-collections-rafa.md
│   ├── senior-notices-ines.md
│   ├── cap-everett.md                CPA-attest branch — suite (2)
│   ├── cap-ea-juno.md
│   ├── head-audit-priscilla.md       CPA-attest branch — dept heads (3)
│   ├── head-attest-mason.md
│   ├── head-quality-saira.md
│   ├── senior-audit-niall.md         CPA-attest branch — seniors (3)
│   ├── senior-attest-orla.md
│   ├── senior-quality-finn.md
│   ├── cmo-margot.md                 CMO branch — suite (2)
│   ├── cmo-ea-rina.md
│   ├── head-brand-sela.md            CMO branch — dept heads (4)
│   ├── head-demand-rocco.md
│   ├── head-content-yara.md
│   ├── head-analytics-arlo.md
│   ├── senior-brand-fern.md          CMO branch — seniors (4)
│   ├── senior-demand-tate.md
│   ├── senior-content-luca.md
│   └── senior-analytics-iggy.md
└── marathons/
    ├── marathon-org.md               unattended org-routed marathon
    └── work-orders-org.md            single-WO org-routed run
```
