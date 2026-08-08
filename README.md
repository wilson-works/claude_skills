# Internal Claude Skills

**Private fork of [wilson-works/claude_skills](https://github.com/wilson-works/claude_skills).** Do not redistribute.

This is the internal WilsonWorks skill pack for [Claude Code](https://claude.com/claude-code). It's a strict superset of the public pack with two additions that we keep in-house:

1. A **multi-branch organizational hierarchy** — **70 agents across seven branches** (the public pack ships the 18-agent CTO-only version). The internal pack adds six advisory branches (52 agents) alongside the 18-agent engineering branch:
   - **CFO branch** (14 agents) — Controller, Treasury, Tax, FP&A heads, each with two seniors, plus the CFO (Elle) and CFO-EA (Soph). Domain-fluent in accounting policy, monthly close, runway, §7216 / 6107(b) / Pub 4557 WISP compliance, ASC 606 / 740, budgets + variance + forecasts.
   - **COO branch** (5 agents) — HR Director (Roz) + two HR seniors, plus the COO (Mara) and COO-EA (Jas). Domain-fluent in CPE compliance, §7216 training records, WISP §III attestation, onboarding gating.
   - **EA-rep branch** (8 agents) — Director of Representation (Marisol) + EA (Anika) + Examinations head (Otto), Collections head (Kira), Notices/E-services head (Mateo), each with one senior. Domain-fluent in Circular 230 practice, IRS examinations + appeals, CDP / OIC / installment agreements / CNC, CP2000-through-NOD response, multi-state representation, Tax Court (USTCP) limits, IRC 6107(b) preparer-retention + §7216 boundary.
   - **CPA-attest branch** (8 agents) — Engagement Partner (Everett) + EA (Juno) + Audit head (Priscilla), Attest head (Mason), Quality head (Saira), each with one senior. Domain-fluent in AICPA AU-C clarified standards, PCAOB AS (when applicable), SSAE/SSARS, SOC 1/2/3, FASB ASC pronouncements (606/740/805/842/326), GASB + Yellow Book, peer review, SQMS 1/2, independence + AICPA Code, audit committee comms (KAMs/CAMs).
   - **CAO branch** (7 agents) — Chief Awareness Officer (Amelia) + VP-AI (Victor) + EA (Elena) + Claude-Ops head (Clay), Copy head (Camille), Coding-CAO head (Cole), Wellness Officer (Wren). Oversees the AI org itself — model selection, prompt structure, eval discipline, brand-voice for AI-generated copy, adversarial review of AI-generated diffs, wellness signals across the comms bus.
   - **CMO branch** (10 agents) — Chief Marketing Officer (Margot) + EA (Rina) + Brand head (Sela), Demand head (Rocco), Content head (Yara), Analytics head (Arlo), each with one senior. Domain-fluent in positioning + STP, brand architecture + equity, demand generation, content + earned, paid acquisition, SEO/GEO + AI Overviews, MarOps/RevOps seam, attribution + incrementality.
   - Cross-branch coordination via the `exec-eas` channel — the dev team's bridge to all advisory expertise, with the seven EAs (Tim / Soph / Jas / Anika / Juno / Elena / Rina) as the only members.

2. A set of **SMB / firm-ops skills** for owner-operator workflows that aren't in the public pack: cash-flow forecasting, AR chasing, monthly close, payroll planning, quarterly-review decks, tax-season prep, and a daily / weekly briefing cadence.

The pack is tuned for the current Claude lineup — **Opus 4.8 decides, Sonnet 5 ships, Haiku 4.5 sweeps**: review gates run Opus at high effort, implementation runs Sonnet, and one env var (`CLAUDE_CODE_SUBAGENT_MODEL=sonnet`) turns any org run into a budget all-Sonnet night. See **[docs/MODELS.md](docs/MODELS.md)**.

Everything else is identical to the public pack — same browser QA, same marathons, same councils, same backlog tooling. If a skill is in `wilson-works/claude_skills` it's in here too, at the same version, unless we've deliberately forked it.

## Why two repos?

The public pack is biased toward AI coding work — devs running marathons, councils for product decisions, browser QA for shipping. That's the audience we publish to.

The internal pack carries the same engineering muscle PLUS the finance + ops + representation + attest + AI-oversight + marketing muscle for running an owner-operated services firm. Those agents (the CFO, COO, EA-rep, CPA-attest, CAO, and CMO branches) embed WilsonWorks-default policy choices that we've validated across client engagements — most notably CBFC, the accounting-system client this org was first shipped to. The SMB skills assume the WilsonWorks reference connector stack (QuickBooks live, the rest deferred). They aren't a fit for a public release.

## Skills (133)

Skills from the public pack are listed in their original sections. New additions are flagged **[internal]**.

### Browser / QA (Chrome DevTools MCP)
- **[audit-page](skills/audit-page/)** -- Lighthouse audit on a running page. `/audit-page [url]`
- **[review-ui](skills/review-ui/)** -- Screenshot desktop + mobile, check console, report visual issues. `/review-ui [url]`
- **[test-flow](skills/test-flow/)** -- Walk a user flow step-by-step with screenshots. `/test-flow [description]`
- **[perf-trace](skills/perf-trace/)** -- Performance trace + Core Web Vitals analysis. `/perf-trace [url]`
- **[qa-sweep](skills/qa-sweep/)** -- Parameterized section audit. `/qa-sweep [section]`
- **[smoke-check](skills/smoke-check/)** -- Fast post-implementation sanity check. `/smoke-check`
- **[preflight](skills/preflight/)** -- Validates dev server, MCP, auth state before QA skills. `/preflight`

### Multi-Agent / Council
- **[llm-council](skills/llm-council/)** -- Run a question through 5 AI advisors who independently analyze, peer-review, and synthesize a verdict. Based on Karpathy's LLM Council methodology. `/llm-council [question]`
- **[premortem](skills/premortem/)** -- Assume your plan already failed 6 months from now and work backward to find every reason why. Spawns one parallel agent per failure mode, then synthesizes a revised plan with blind spots exposed. Based on Klein's premortem methodology. `/premortem [plan]`
- **[council-orders](skills/council-orders/)** -- Convene a 5-member product council that files 25-30 prioritized work orders to your backlog in one session. `/council-orders [focus]`
- **[council-rd](skills/council-rd/)** -- Per-research-folder mini-councils that pick the top 2-3 work orders from each report and emit an HTML approval tool. `/council-rd [research-root]`
- **[agent-org](skills/agent-org/)** -- **[internal: 70-agent seven-branch build]** Organizational hierarchy with hard-ACL Slack-style channels (22 of them). C-suite (Opus) directs, exec assistant routes, department heads review, juniors ship. SQLite-backed comms bus + path-guard hook enforces dept ownership. `/agent-org` — **diagrams: [docs/ORG.md](docs/ORG.md)** (chain of command, comms ACL, the loop) + a one-page [poster](docs/org-poster.html) + a [people directory](docs/profiles.html) (a human profile card per agent)

### Long-Running Marathons (walkaway sessions)
- **[marathon-council](skills/marathon-council/)** -- Rotates through focus areas, researches the codebase, convenes councils, files work orders. The intake half. `/marathon-council`
- **[marathon-orders](skills/marathon-orders/)** -- Spawns 1-2 sub-agents per wave, each completing one work order with a review-and-merge gate. The execution half. `/marathon-orders`
- **[marathon-org](skills/marathon-org/)** -- Org-routed walkaway marathon. Same loop as marathon-orders but every wave routes CTO -> exec assistant -> dept head -> junior with the comms bus and path claims active. `/marathon-org`
- **[workday](skills/workday/)** -- Standardized 4-lane parallel overnight run: 4 territory-disjoint org-routed lanes (schema / backend / frontend / api) in separate git worktrees + an automated Lane E merge, a per-lane completion goal set by the chief engineer, an honest session-recovery table, keep-last-1 cleanup. The big-overnight-bite half. `/workday [theme]`
- **[workday-watch](skills/workday-watch/)** -- Optional non-destructive C-suite surveillance session for an in-flight `/workday` run: periodically inspects each lane for drift / breakage / hallucination and posts steering corrections the lanes obey, catching problems in ~20 min instead of at the morning merge. `/workday-watch`
- **[marathon-research](skills/marathon-research/)** -- Processes a queue of research topics with WebSearch/WebFetch, produces cited markdown reports under 750 lines. `/marathon-research [topics]`
- **[marathon-research-council](skills/marathon-research-council/)** -- Cross-cut council across N completed marathons. Produces a build-ready summary with per-marathon decision cards, dependency graph, first-PR spec, and ADR placeholders. The bridge from raw R&D to the backlog. `/marathon-research-council [slugs|--since|--all-pending]`
- **[distill](skills/distill/)** -- Post-processor for `marathon-research`. Turns 5,000-line research dumps into <=200-line summary cards with surgical `@-references` back to source. Auto-fires at the end of every marathon, or invoke standalone. `/distill [slug]`
- **[marathon-bughunter](skills/marathon-bughunter/)** -- Drives a Chrome DevTools browser through your app to hunt for new bugs introduced by recent work. `/marathon-bughunter`
- **[marathon-condenser](skills/marathon-condenser/)** -- Condenses an oversized work order backlog: merges duplicates, closes already-completed items, rewrites vague entries, prunes stale ones. `/marathon-condenser`
- **[bg-pipeline](skills/bg-pipeline/)** -- Run a sequence of skills as background sub-agents to keep your main session's context clean. `/bg-pipeline [pipeline]`
- **[caveman](skills/caveman/)** -- Semantic text compression for long autonomous sessions. 40-58% token savings by stripping filler while preserving facts. `/caveman [on|off|compress]`

### Backlog & Work Orders
- **[backlog](skills/backlog/)** — `/backlog [command]`
- **[work-orders](skills/work-orders/)** — `/work-orders [category]`
- **[work-orders-org](skills/work-orders-org/)** — `/work-orders-org [ID|pick]`
- **[user-feedback](skills/user-feedback/)** — `/user-feedback [command]`

### Design & Decisions
- **[quick-design](skills/quick-design/)** -- `/quick-design [change]`
- **[gate-check](skills/gate-check/)** -- `/gate-check [milestone]`
- **[scope-check](skills/scope-check/)** -- `/scope-check`
- **[retro](skills/retro/)** -- `/retro`

### Design Intelligence
- **[ui-ux-pro-max](skills/ui-ux-pro-max/)**, **[design](skills/design/)**, **[design-system](skills/design-system/)**, **[ui-styling](skills/ui-styling/)**, **[brand](skills/brand/)**, **[banner-design](skills/banner-design/)**, **[slides](skills/slides/)**

### Marketing & Growth

**Conversion Optimization**
- **[page-cro](skills/page-cro/)**, **[signup-flow-cro](skills/signup-flow-cro/)**, **[onboarding-cro](skills/onboarding-cro/)**, **[paywall-upgrade-cro](skills/paywall-upgrade-cro/)**, **[form-cro](skills/form-cro/)**, **[popup-cro](skills/popup-cro/)**, **[ab-test-setup](skills/ab-test-setup/)**

**Content & Copy**
- **[copywriting](skills/copywriting/)**, **[copy-editing](skills/copy-editing/)**, **[ad-creative](skills/ad-creative/)**, **[content-strategy](skills/content-strategy/)**, **[content-engine](skills/content-engine/)**, **[social-content](skills/social-content/)**, **[brand-voice](skills/brand-voice/)**, **[image](skills/image/)**, **[video](skills/video/)**

**SEO & Discovery**
- **[seo-audit](skills/seo-audit/)**, **[ai-seo](skills/ai-seo/)**, **[programmatic-seo](skills/programmatic-seo/)**, **[schema-markup](skills/schema-markup/)**, **[site-architecture](skills/site-architecture/)**, **[directory-submissions](skills/directory-submissions/)**, **[competitor-alternatives](skills/competitor-alternatives/)**, **[aso-audit](skills/aso-audit/)**

**Paid & Distribution**
- **[paid-ads](skills/paid-ads/)**, **[cold-email](skills/cold-email/)**, **[email-sequence](skills/email-sequence/)**, **[co-marketing](skills/co-marketing/)**, **[community-marketing](skills/community-marketing/)**

**Strategy & Monetization**
- **[pricing-strategy](skills/pricing-strategy/)**, **[launch-strategy](skills/launch-strategy/)**, **[lead-magnets](skills/lead-magnets/)**, **[free-tool-strategy](skills/free-tool-strategy/)**, **[marketing-ideas](skills/marketing-ideas/)**, **[marketing-psychology](skills/marketing-psychology/)**, **[product-marketing-context](skills/product-marketing-context/)**

**Research & Measurement**
- **[customer-research](skills/customer-research/)**, **[competitor-profiling](skills/competitor-profiling/)**, **[analytics-tracking](skills/analytics-tracking/)**

**Retention & RevOps**
- **[churn-prevention](skills/churn-prevention/)**, **[referral-program](skills/referral-program/)**, **[revops](skills/revops/)**, **[sales-enablement](skills/sales-enablement/)**

### Fundraising & Investor Communications
- **[investor-materials](skills/investor-materials/)**, **[investor-outreach](skills/investor-outreach/)**

### Business / Strategy (BMC brain)
- **[business-notes](skills/business-notes/)**, **[business-pass](skills/business-pass/)**, **[business-roundtable](skills/business-roundtable/)**

### SMB / Firm Ops **[internal]**
Skills for running an owner-operated firm (accounting/bookkeeping/tax) on top of QuickBooks + payment processors. Most fall back to a CSV upload when a connector is not live.

**Daily / weekly cadence**
- **[monday-brief](skills/monday-brief/)** -- One-page Monday morning briefing: cash, sales, pipeline, week ahead, top three to-dos. `/monday-brief`
- **[friday-brief](skills/friday-brief/)** -- Friday end-of-week pulse: revenue vs prior week, top sellers, wins and watches. `/friday-brief`
- **[business-pulse](skills/business-pulse/)** -- Cross-functional snapshot — cash, sales, pipeline, commitments, watch-list, the one thing that matters today. Scopes gracefully to whichever connectors are live.

**Cash + AR**
- **[cash-flow-snapshot](skills/cash-flow-snapshot/)** -- 30/60/90-day forecast with variance bands and named risks. Chat summary + XLSX workbook.
- **[invoice-chase](skills/invoice-chase/)** -- Drafts overdue-invoice reminders matched to each customer's payment history. PayPal sends with approval, mail drafts otherwise.
- **[call-list](skills/call-list/)** -- Ranks top-5 leads worth calling today with talking points + calendar blocks + follow-up drafts. `/call-list [count]`
- **[plan-payroll](skills/plan-payroll/)** -- Forecast cash, rank overdue invoices, stage reminders so payroll runs confidently.

**Close + reporting**
- **[close-month](skills/close-month/)** -- Reconciles QuickBooks against processors, flags gaps, writes the P&L narrative, exports the close packet. `/close-month [month]`
- **[month-end-prep](skills/month-end-prep/)** -- Same shape as close-month but framed as the lead-up rather than the close itself.
- **[month-heads-up](skills/month-heads-up/)** -- Runs on the 25th — next-30-day cash outlook + everything needing attention before month-end.
- **[quarterly-review](skills/quarterly-review/)** -- Full QBR narrative — revenue/margin trend, customer health, opportunities + risks — as a presentation-ready PDF or deck.

**Tax**
- **[tax-prep](skills/tax-prep/)** -- Quarterly estimated tax calc OR year-end 1099 prep. Produces an accountant handoff packet. `/tax-prep [mode] [year]`
- **[tax-season-organizer](skills/tax-season-organizer/)** -- Owner-friendly tax-season organizer framed as deliverables for the accountant, not tax advice.

### Architecture & Documentation
- **[arch-diagram](skills/arch-diagram/)**, **[systems-map](skills/systems-map/)**, **[reverse-doc](skills/reverse-doc/)**, **[spec-audit](skills/spec-audit/)**

### Research & Discovery
- **[deep-research](skills/deep-research/)** -- Multi-source deep research using firecrawl and exa MCPs. Searches the web, synthesizes findings, delivers cited reports with source attribution. `/deep-research [topic]`
- **[quick-research](skills/quick-research/)** -- Single-session cited research for short-but-complex on-the-job questions. Same hard rules as marathon-research (every claim carries a verifiable URL, unclear scope fails fast, no bluffing) at 5-20 minute scale with an inline answer. `/quick-research [question]`

### Personal Productivity & Onboarding
Skills for chat-first and new-to-Claude users -- and the personal-ops layer that makes every other skill stick.

- **[notetaker](skills/notetaker/)** -- Persistent personal notes system -- like the backlog, but for knowledge instead of work orders. Captures notes into topic buckets that grow with you over time, so any future session can recall them. `/notetaker [command]`
- **[prompt-coach](skills/prompt-coach/)** -- Critique and rewrite underperforming prompts with line-by-line explanations, drill one pattern at a time on your own domain, and maintain a personal golden-prompts library. `/prompt-coach [prompt]`
- **[meeting-digest](skills/meeting-digest/)** -- Turn raw meeting notes or transcripts into a structured digest: TL;DR, decisions, action items, open questions. Routes actions to the backlog and context to notetaker. `/meeting-digest`
- **[weekly-review](skills/weekly-review/)** -- Guided 15-20 minute weekly review: wins, loose ends, lessons, next week's Top 3, written to a one-page review file. `/weekly-review`
- **[sop-writer](skills/sop-writer/)** -- Turn a process into a Standard Operating Procedure a cold reader could execute: numbered steps with expected results, failure/escalation table, quick-checklist version. `/sop-writer`
- **[file-organizer](skills/file-organizer/)** -- Plan-first, never-destructive folder cleanup: scan, propose a fitted taxonomy + full move manifest, execute only on approval with an undo log. `/file-organizer [folder]`
- **[spreadsheet-doctor](skills/spreadsheet-doctor/)** -- Examine, prescribe, treat: profile a messy CSV/XLSX, propose an explicit cleaning plan, execute to a new file with a before/after change report, then summarize. `/spreadsheet-doctor [file]`

### Video & Media
- **[create-onboarding-video](skills/create-onboarding-video/)**

### Workflow Utilities
- **[handoff](skills/handoff/)**, **[skill-stocktake](skills/skill-stocktake/)**, **[eval-harness](skills/eval-harness/)**, **[mcp-server-patterns](skills/mcp-server-patterns/)**

### Dev Workflow
- **[deploy](skills/deploy/)** -- `/deploy [message]`

## Installation

Skills live in `~/.claude/skills/` (or `<repo>/.claude/skills/` for project-scoped). To install one:

```bash
cp -r skills/agent-org ~/.claude/skills/
```

Or symlink the whole folder for one-command updates:

```bash
ln -s "$(pwd)/skills" ~/.claude/skills-shared
```

Then restart Claude Code. Invoke via `/skill-name`.

### agent-org installation (3-branch internal version)

The agent-org skill is the biggest delta from the public pack. Full install steps are in [skills/agent-org/INSTALL.md](skills/agent-org/INSTALL.md). Quick recipe:

```bash
SKILL_SRC=path/to/internal_claude_skills/skills/agent-org
REPO=$(git rev-parse --show-toplevel)

mkdir -p "$REPO/.claude/agents" "$REPO/.claude/comms" "$REPO/.claude/hooks"

cp "$SKILL_SRC"/agents/*.md       "$REPO/.claude/agents/"     # all 37 agents
cp "$SKILL_SRC"/comms/comms.py    "$REPO/.claude/comms/"
cp "$SKILL_SRC"/comms/schema.sql  "$REPO/.claude/comms/"
cp "$SKILL_SRC"/hooks/path_guard.py "$REPO/.claude/hooks/"
cp "$SKILL_SRC"/org.config.example.json "$REPO/.claude/agents/org.config.json"
# then edit org.config.json to map your repo's paths
# then add the path_guard hook to .claude/settings.json — see INSTALL.md
```

If a target repo is pure-engineering (no firm-ops use case), skip the `cfo-*`, `coo-*`, and `senior-*` files — comms.py knows about all 37 but un-installed agents simply never get spawned.

## Configuring for your project

Most skills include a `## Configure for your project` section near the top of their `SKILL.md` listing the placeholders to swap. Common ones:

- `<project-root>` -- your repo's absolute path
- `<your-project-backlog-path>` -- where your backlog markdown files live
- `<state-dir>` -- where long-running skill state files are written
- `<src-path>` / `<core-path>` -- your source roots
- `<design-spec>` / `<DESIGN-DOC>` -- your design documentation
- `<PRODUCT_DESCRIPTION>` -- a one-paragraph project description (council-style skills)
- `<dev-server-url>` -- usually `http://localhost:5173` or similar

Skills that need the most configuration: backlog, work-orders, marathon-*, council-*, gate-check, qa-sweep, spec-audit, systems-map, arch-diagram, agent-org. Open the SKILL.md and look for "EDIT THIS" callouts.

## Prerequisites

- **Browser skills** (`audit-page`, `review-ui`, `test-flow`, `perf-trace`, `qa-sweep`, `smoke-check`, `marathon-bughunter`, `preflight`) require the [Chrome DevTools MCP server](https://github.com/ChromeDevTools/chrome-devtools-mcp) to be connected.
- **llm-council** requires API keys for the models it polls (see [skills/llm-council/INSTALL.md](skills/llm-council/INSTALL.md)).
- **agent-org / marathon-org / work-orders-org** install a SQLite-backed comms bus + path-guard hook into your project (see [skills/agent-org/INSTALL.md](skills/agent-org/INSTALL.md)).
- **marathon-research / deep-research / quick-research** use WebSearch and WebFetch; both ship with Claude Code. `deep-research` additionally benefits from firecrawl and exa MCPs.
- **spreadsheet-doctor** uses Python for the cleaning phase (`py` on Windows, `python3` elsewhere); pandas preferred, stdlib fallback works.
- **deploy** assumes a CI/CD pipeline that triggers on push (Railway, Vercel, Netlify, GitHub Actions, etc.).
- **Backlog-aware skills** (`backlog`, `work-orders`, `work-orders-org`, `council-orders`, `council-rd`, `marathon-council`, `marathon-orders`, `marathon-org`, `marathon-condenser`, `user-feedback`, `scope-check`) require a backlog directory with `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, and `completed.md` files (each with a `<!-- Next ID: 001 -->` header).
- **Walkaway marathons** (`marathon-*`) use CronCreate to self-schedule their wave loop. Cron jobs are **session-only** — they do not persist to disk and `durable` has no effect — which is fine here because the cron drives the session it lives in. A cron cannot recover a session that has died.
- **create-onboarding-video** requires Remotion installed in the target project (`npm i remotion @remotion/cli`) and a `remotion-best-practices` skill in scope.
- **SMB / firm-ops skills** prefer live connectors (QuickBooks Online, PayPal, Stripe, Square) but fall back to CSV upload.
- **Design Intelligence skills** ship as SKILL.md + reference docs only -- the original `ui-ux-pro-max` python helper scripts and `ui-styling` canvas-fonts are not bundled here. Add them locally if you want the full tooling.

## Skill provenance

Public-pack skills come from the original [wilson-works/claude_skills](https://github.com/wilson-works/claude_skills) (MIT) which is itself sourced from:

- **Original** -- Browser/QA, Multi-Agent/Council, Marathons, Backlog, Design & Decisions, Business/Strategy, Architecture, Dev Workflow.
- **[coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)** -- the 41-skill Marketing & Growth section. The per-skill `references/` files and the shared `tools/` registry (REGISTRY.md, clis/, integrations/) were restored verbatim from upstream commit `30dbd7f` (2026-07-02); they retain the upstream MIT copyright (© 2025 Corey Haines).
- **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** -- the 7-skill Design Intelligence section.
- **[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)** -- investor-materials, investor-outreach, deep-research, content-engine, brand-voice, skill-stocktake, eval-harness, mcp-server-patterns.
- **[bidah/skill-set](https://github.com/bidah/skill-set)** -- create-onboarding-video.
- **[mattpocock/skills](https://github.com/mattpocock/skills)** -- handoff.

Internal additions (the CFO + COO + EA-rep + CPA-attest + CAO + CMO branch agents, the multi-branch comms/hook updates, and the SMB firm-ops skill pack) are written for WilsonWorks use across client engagements (including CBFC, the accounting-system client this org was first shipped to) and are not redistributed.

## License

Internal use only. Public-pack components retain their original MIT license; internal additions are not licensed for redistribution.
