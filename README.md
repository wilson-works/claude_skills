# Claude Skills

A collection of reusable [Claude Code](https://claude.com/claude-code) skills for browser QA, multi-agent coordination, long-running autonomous sessions, backlog management, marketing and growth, design intelligence, fundraising, business strategy, dev workflow, and architecture work. Project-agnostic -- drop them into any repo, swap a few placeholders, and go.

## Skills (126)

### Browser / QA (Chrome DevTools MCP)
- **[audit-page](skills/audit-page/)** -- Lighthouse audit (performance, a11y, best practices, SEO) on a running page. `/audit-page [url]`
- **[review-ui](skills/review-ui/)** -- Screenshot desktop + mobile, check console, report visual issues. `/review-ui [url]`
- **[test-flow](skills/test-flow/)** -- Walk a user flow step-by-step with screenshots. `/test-flow [description]`
- **[perf-trace](skills/perf-trace/)** -- Record a performance trace, analyze Core Web Vitals and bottlenecks. `/perf-trace [url]`
- **[qa-sweep](skills/qa-sweep/)** -- Parameterized section audit: walks a section, verifies functionality, flags friction, returns severity-ranked findings. `/qa-sweep [section]`
- **[smoke-check](skills/smoke-check/)** -- Fast post-implementation sanity check (build + secrets + key-page browser hit). Binary PASS/FAIL in ~2 minutes. `/smoke-check`
- **[preflight](skills/preflight/)** -- Validates dev server, MCP, and auth state before other QA skills. `/preflight`

### Multi-Agent / Council
- **[llm-council](skills/llm-council/)** -- Run a question through 5 AI advisors who independently analyze, peer-review, and synthesize a verdict. Based on Karpathy's LLM Council methodology. `/llm-council [question]`
- **[premortem](skills/premortem/)** -- Assume your plan already failed 6 months from now and work backward to find every reason why. Spawns one parallel agent per failure mode, then synthesizes a revised plan with blind spots exposed. Based on Klein's premortem methodology. `/premortem [plan]`
- **[council-orders](skills/council-orders/)** -- Convene a 5-member product council that files 25-30 prioritized work orders to your backlog in one session. `/council-orders [focus]`
- **[council-rd](skills/council-rd/)** -- Per-research-folder mini-councils that pick the top 2-3 work orders from each report and emit an HTML approval tool. `/council-rd [research-root]`
- **[agent-org](skills/agent-org/)** -- 18-agent organizational hierarchy with hard-ACL Slack-style channels. C-suite (Opus) directs, exec assistant routes, department heads review, juniors ship. SQLite-backed comms bus + path-guard hook enforces dept ownership. `/agent-org`
- **[org-knowledge-audit](skills/org-knowledge-audit/)** -- Knowledge-integrity audit for an agent organization: reads every agent definition, extracts the domain claims embedded in them, classifies each by volatility risk (annually-changing figures down to pure workflow), flags...
- **[org-reference-packs](skills/org-reference-packs/)** -- The refresh mechanism for an agent organization's factual knowledge: per-department reference packs where every fact carries its source URL and as-of date, grouped by volatility tier with a named refresh trigger per...

### Long-Running Marathons (walkaway sessions)
- **[marathon-council](skills/marathon-council/)** -- Rotates through focus areas, researches the codebase, convenes councils, files work orders. The intake half. `/marathon-council`
- **[marathon-orders](skills/marathon-orders/)** -- Spawns 1-2 sub-agents per wave, each completing one work order with a review-and-merge gate. The execution half. `/marathon-orders`
- **[marathon-org](skills/marathon-org/)** -- Org-routed walkaway marathon. Same loop as marathon-orders but every wave routes CTO -> exec assistant -> dept head -> junior with the comms bus and path claims active. `/marathon-org`
- **[marathon-research](skills/marathon-research/)** -- Processes a queue of research topics with WebSearch/WebFetch, produces cited markdown reports under 750 lines. `/marathon-research [topics]`
- **[marathon-research-council](skills/marathon-research-council/)** -- Cross-cut council across N completed marathons. Produces a build-ready summary with per-marathon decision cards, dependency graph, first-PR spec, and ADR placeholders. The bridge from raw R&D to the backlog. `/marathon-research-council [slugs|--since|--all-pending]`
- **[distill](skills/distill/)** -- Post-processor for `marathon-research`. Turns 5,000-line research dumps into <=200-line summary cards with surgical `@-references` back to source. Auto-fires at the end of every marathon, or invoke standalone. `/distill [slug]`
- **[marathon-bughunter](skills/marathon-bughunter/)** -- Drives a Chrome DevTools browser through your app to hunt for new bugs introduced by recent work. `/marathon-bughunter`
- **[marathon-condenser](skills/marathon-condenser/)** -- Condenses an oversized work order backlog: merges duplicates, closes already-completed items, rewrites vague entries, prunes stale ones. `/marathon-condenser`
- **[bg-pipeline](skills/bg-pipeline/)** -- Run a sequence of skills as background sub-agents to keep your main session's context clean. `/bg-pipeline [pipeline]`
- **[caveman](skills/caveman/)** -- Semantic text compression for long autonomous sessions. 40-58% token savings by stripping filler while preserving facts. `/caveman [on|off|compress]`
- **[workday](skills/workday/)** -- Standardized 4-lane parallel overnight engineering run.
- **[workday-watch](skills/workday-watch/)** -- Optional C-suite surveillance session for an in-flight /workday parallel run.

### Backlog & Work Orders
- **[backlog](skills/backlog/)** -- View, add, close, and manage work order backlog items across categories (bugs, design, features, tech debt). `/backlog [command]`
- **[work-orders](skills/work-orders/)** -- Triage the backlog and spawn sub-agents to execute prioritized items with a Sonnet-first context-brief pattern. `/work-orders [category]`
- **[work-orders-org](skills/work-orders-org/)** -- Single work order routed through the org (CTO -> exec assistant -> dept head -> junior) with full review gates and named accountability. `/work-orders-org [ID|pick]`
- **[user-feedback](skills/user-feedback/)** -- Manage public user feedback in a dev review log; promote actionable items to the backlog. `/user-feedback [command]`

### Design & Decisions
- **[quick-design](skills/quick-design/)** -- Lightweight spec for small feature/architecture changes that don't warrant a full council session. `/quick-design [change]`
- **[gate-check](skills/gate-check/)** -- Formal milestone readiness validation (MVP, beta, GA, etc.) with multi-perspective review. PASS / CONCERNS / FAIL. `/gate-check [milestone]`
- **[scope-check](skills/scope-check/)** -- Compares original work order or plan scope against actual git diff to detect scope creep. PASS / CONCERNS / FAIL. `/scope-check`
- **[retro](skills/retro/)** -- Post-marathon or post-session retrospective from git log + backlog + plan files. Outputs 3-5 action items. `/retro`
- **[brainstorm](skills/brainstorm/)** -- A structured two-phase ideation session.
- **[decision-policy](skills/decision-policy/)** -- Stops recurring decisions from being re-litigated: mines your notes, backlog, and session history for decisions made repeatedly, surfaces the latent rule behind each, triages by reversibility x stakes (one-way-door...

### Design Intelligence
- **[ui-ux-pro-max](skills/ui-ux-pro-max/)** -- Comprehensive UI/UX design intelligence: 50+ styles, 161 color palettes, 57 font pairings, 99 UX guidelines, 25 chart types, prioritized rules (accessibility/touch/performance/style/layout/typography/animation/forms/navigation/charts).
- **[design](skills/design/)** -- Comprehensive design generation: brand identity, logos (55 styles), corporate identity programs (50 deliverables), HTML presentations (Chart.js), banner design (22 styles), icons (15 styles), social photos for every major platform.
- **[design-system](skills/design-system/)** -- Token architecture, component specifications, slide generation. Three-layer tokens (primitive -> semantic -> component), CSS variables, spacing/typography scales.
- **[ui-styling](skills/ui-styling/)** -- shadcn + Tailwind patterns with accessibility, theming, responsive design, and utility references.
- **[brand](skills/brand/)** -- Brand voice, visual identity, messaging frameworks, asset management, brand consistency. Approval checklist, color-palette management, logo usage rules, typography specs.
- **[banner-design](skills/banner-design/)** -- Design banners for social media, ads, website heroes, creative assets, and print. Multiple platforms, multiple art direction options.
- **[slides](skills/slides/)** -- HTML slide templates, layout patterns, copywriting formulas, and slide strategies for decks and presentations.

### Marketing & Growth
**Conversion Optimization**
- **[page-cro](skills/page-cro/)** -- Optimize any marketing page (homepage, landing, pricing, feature, blog) for conversions. `/page-cro [url]`
- **[signup-flow-cro](skills/signup-flow-cro/)** -- Optimize signup, registration, and trial activation flows.
- **[onboarding-cro](skills/onboarding-cro/)** -- Optimize post-signup onboarding, activation, and time-to-value.
- **[paywall-upgrade-cro](skills/paywall-upgrade-cro/)** -- In-app paywalls, upgrade screens, upsell modals, feature gates.
- **[form-cro](skills/form-cro/)** -- Optimize non-signup forms (lead capture, contact, demo, application, checkout).
- **[popup-cro](skills/popup-cro/)** -- Popups, modals, overlays, slide-ins, exit-intent, sticky bars.
- **[ab-test-setup](skills/ab-test-setup/)** -- Plan, design, or implement A/B tests and growth experimentation programs.

**Content & Copy**
- **[copywriting](skills/copywriting/)** -- Write/rewrite marketing copy for any page (homepage, landing, pricing, feature, about).
- **[copy-editing](skills/copy-editing/)** -- Edit, review, refresh existing marketing copy.
- **[ad-creative](skills/ad-creative/)** -- Generate, iterate, or scale ad creative for any paid platform.
- **[content-strategy](skills/content-strategy/)** -- Plan content strategy, topic clusters, editorial calendar.
- **[content-engine](skills/content-engine/)** -- Platform-native content for X, LinkedIn, TikTok, YouTube, newsletters, plus repurposed multi-platform campaigns.
- **[social-content](skills/social-content/)** -- Create, schedule, and optimize social media content.
- **[brand-voice](skills/brand-voice/)** -- Build a source-derived writing style profile from real posts/essays/launch notes/docs, then reuse it across content, outreach, and social.
- **[image](skills/image/)** -- Create, generate, edit, or optimize images for marketing (blog heroes, social, mockups, banners, OG images).
- **[video](skills/video/)** -- Create, generate, or produce video content using AI tools.

**SEO & Discovery**
- **[seo-audit](skills/seo-audit/)** -- Audit, review, diagnose SEO issues on a website.
- **[ai-seo](skills/ai-seo/)** -- Optimize content for AI search engines (ChatGPT, Perplexity, AI Overviews, etc.).
- **[programmatic-seo](skills/programmatic-seo/)** -- Create SEO-driven pages at scale using templates and data.
- **[schema-markup](skills/schema-markup/)** -- Add, fix, or optimize schema markup and structured data.
- **[site-architecture](skills/site-architecture/)** -- Plan and restructure website hierarchy and URL structure.
- **[directory-submissions](skills/directory-submissions/)** -- Submit products to startup, SaaS, AI, agent, MCP, no-code, and review directories for backlinks.
- **[competitor-alternatives](skills/competitor-alternatives/)** -- Create competitor comparison and alternative pages for SEO and sales enablement.
- **[aso-audit](skills/aso-audit/)** -- Audit or optimize App Store and Google Play listings.

**Paid & Distribution**
- **[paid-ads](skills/paid-ads/)** -- Campaigns on Google Ads, Meta, LinkedIn, Twitter/X, and other ad platforms.
- **[cold-email](skills/cold-email/)** -- B2B cold emails and follow-up sequences that get replies.
- **[email-sequence](skills/email-sequence/)** -- Drip campaigns, lifecycle emails, onboarding/welcome/re-engagement series.
- **[co-marketing](skills/co-marketing/)** -- Find partners, plan joint campaigns, brainstorm partnership opportunities.
- **[community-marketing](skills/community-marketing/)** -- Build and leverage online communities (Discord, Slack, forums).

**Strategy & Monetization**
- **[pricing-strategy](skills/pricing-strategy/)** -- Pricing decisions, packaging, monetization, freemium, value metrics, Van Westendorp.
- **[launch-strategy](skills/launch-strategy/)** -- Plan product launches, feature announcements, Product Hunt drops, beta launches, waitlists.
- **[lead-magnets](skills/lead-magnets/)** -- Plan and optimize lead magnets (gated content, downloadables, templates).
- **[free-tool-strategy](skills/free-tool-strategy/)** -- Plan, evaluate, or build free tools for lead generation, SEO, or brand.
- **[marketing-ideas](skills/marketing-ideas/)** -- Marketing ideas, inspiration, growth strategies when you're stuck.
- **[marketing-psychology](skills/marketing-psychology/)** -- Apply psychological principles and behavioral science to marketing.
- **[product-marketing-context](skills/product-marketing-context/)** -- Foundational product/audience/positioning context that all other marketing skills reference.

**Research & Measurement**
- **[customer-research](skills/customer-research/)** -- Conduct, analyze, synthesize customer research (interviews, transcripts, surveys, review mining, VOC).
- **[competitor-profiling](skills/competitor-profiling/)** -- Research, profile, analyze competitors from URLs into structured profile markdown files.
- **[analytics-tracking](skills/analytics-tracking/)** -- Set up, improve, or audit analytics tracking (GA4, GTM, Mixpanel, Segment, conversion tracking, UTM).

**Retention & RevOps**
- **[churn-prevention](skills/churn-prevention/)** -- Cancellation flows, save offers, payment recovery, win-back, exit surveys, dunning.
- **[referral-program](skills/referral-program/)** -- Create, optimize, or analyze referral, affiliate, and word-of-mouth programs.
- **[revops](skills/revops/)** -- Revenue operations and lead lifecycle management.
- **[sales-enablement](skills/sales-enablement/)** -- Sales collateral, pitch decks, demo scripts, battle cards.

### Fundraising & Investor Communications
- **[investor-materials](skills/investor-materials/)** -- Pitch decks, one-pagers, investor memos, accelerator applications, financial models. Keeps multiple fundraising assets internally consistent. `/investor-materials`
- **[investor-outreach](skills/investor-outreach/)** -- Cold emails, warm intro blurbs, follow-ups, update emails, and investor communications for angels, VCs, strategic investors, accelerators. `/investor-outreach`

### Business / Strategy (BMC brain)
- **[business-notes](skills/business-notes/)** -- Capture strategy notes (marketing, pricing, partnerships, customer hypotheses) and auto-file them into a Business Model Canvas brain. Builds the business plan in parallel with the product. `/business-notes [command]`
- **[business-pass](skills/business-pass/)** -- Proactively grow the BMC brain. Two modes: `scan` (autonomous codebase/app sweep extracting BMC evidence) and `interview` (Q&A to fill gaps in any of the 9 BMC blocks). `/business-pass [scan|interview]`
- **[business-roundtable](skills/business-roundtable/)** -- Send a business note through a 5-advisor council (Marketing, Pricing, Customer Discovery, Competitor Watcher, Operations), finalize, then lock the verdict into the BMC brain. `/business-roundtable [NOTE-ID]`

### Architecture & Documentation
- **[arch-diagram](skills/arch-diagram/)** -- Generates dark-themed SVG architecture diagrams from a configurable arch-config file. `/arch-diagram [view]`
- **[systems-map](skills/systems-map/)** -- Maps interlocking systems in your codebase, produces a Mermaid diagram and dependency matrix to visualize ripple effects. `/systems-map`
- **[reverse-doc](skills/reverse-doc/)** -- Generates missing spec docs from existing code via an intent-clarification step. `/reverse-doc [system]`
- **[spec-audit](skills/spec-audit/)** -- Compares spec documents against component implementations to detect drift (tokens, mechanics, principles). `/spec-audit`

### Research & Discovery
- **[deep-research](skills/deep-research/)** -- Multi-source deep research using firecrawl and exa MCPs. Searches the web, synthesizes findings, delivers cited reports with source attribution. `/deep-research [topic]`
- **[quick-research](skills/quick-research/)** -- Single-session cited research for short-but-complex on-the-job questions.

### Video & Media
- **[create-onboarding-video](skills/create-onboarding-video/)** -- Short, punchy iOS app onboarding videos in Remotion that showcase a feature in action by animating isolated UI pieces (cropped components, not full screens). Useful for App Store previews, landing page demos, mission walkthroughs. `/create-onboarding-video`

### Workflow Utilities
- **[handoff](skills/handoff/)** -- Compact the current conversation into a handoff document for another agent to pick up. `/handoff [what next session is for]`
- **[skill-stocktake](skills/skill-stocktake/)** -- Audit Claude skills and commands for quality. Quick Scan (changed only) and Full Stocktake modes with sequential subagent batch evaluation. `/skill-stocktake`
- **[eval-harness](skills/eval-harness/)** -- Formal evaluation framework for Claude Code sessions implementing eval-driven development (EDD) principles. `/eval-harness`
- **[mcp-server-patterns](skills/mcp-server-patterns/)** -- Build MCP servers with Node/TypeScript SDK -- tools, resources, prompts, Zod validation, stdio vs Streamable HTTP. `/mcp-server-patterns`
- **[file-organizer](skills/file-organizer/)** -- Bring order to a messy folder -- Downloads, Desktop, a shared-drive dump -- with a plan-first, never-destructive discipline: SCAN inventories the folder read-only, PROPOSE presents a fitted taxonomy plus a complete...
- **[meeting-digest](skills/meeting-digest/)** -- Turn raw meeting material -- pasted notes, a transcript file, a voice-memo transcription, or your from-memory recap right after a call -- into a structured digest: TL;DR, decisions, action items, open questions,...
- **[notetaker](skills/notetaker/)** -- Persistent personal notes system -- like the backlog, but for your work and thinking instead of work orders.
- **[journal](skills/journal/)** -- A method-true journaling companion: at setup you pick a named practice -- plain reflection, gratitude (weekly counting-blessings or nightly three-good-things), expressive-writing deep dives, or a morning-pages-style...
- **[sop-writer](skills/sop-writer/)** -- Turn any process into a Standard Operating Procedure that someone else could execute cold -- via a gap-hunting interview, a confirmed workflow map you already have, or revision of an existing SOP after a process change.
- **[spreadsheet-doctor](skills/spreadsheet-doctor/)** -- Diagnose and clean messy CSV/XLSX files with a three-phase medical-triage discipline: EXAMINE profiles the file read-only and presents a diagnosis report, PRESCRIBE proposes an explicit numbered cleaning plan that...
- **[weekly-review](skills/weekly-review/)** -- A guided 15--20 minute weekly review ritual -- GTD-flavored but tool-agnostic -- that closes the loop on the week and produces next week's focus.
- **[life-loop](skills/life-loop/)** -- Captures a recurring personal mental loop -- what's for dinner, packing, gifts, workouts, weekend plans, chores -- through a zero-jargon interview, converts it into a stored personal loop file with your actual decision...
- **[meal-prep](skills/meal-prep/)** -- Profile-driven weekly meal planning: a one-time interview captures your household size, user-supplied dietary rules, budget shape, cooking time and skill, equipment, and dislikes into a stored profile; each weekly run...
- **[travel-plan](skills/travel-plan/)** -- Plans a trip end to end without pretending to know the world: a capture interview for dates, party, budget, pace, and constraints; a day-by-day itinerary skeleton with one anchor per day; a run-time research discipline...
- **[prompt-coach](skills/prompt-coach/)** -- Interactive coaching that improves how you ask Claude for things.
- **[extract-approach](skills/extract-approach/)** -- Captures how a non-trivial engineering problem was solved, at the moment it is solved, as an atomic claim-titled approach note -- recurrence trigger, failure symptom, checkable rule, counter-example -- filed in a...
- **[power-chains](skills/power-chains/)** -- A library of named, versioned multi-skill playbook chains with a gated runner: each chain file declares its steps as skill invocations, the explicit artifact handoff between every step (what gets written where, and how...
- **[cleanup-stale](skills/cleanup-stale/)** -- Survey-and-prune stale scratch artifacts from the project root, the `.claude/` orchestration directory, and the shared `d:\tmp` scratch dir.

### Dev Workflow
- **[deploy](skills/deploy/)** -- Commit staged changes and push to GitHub to trigger a CI/CD deploy. `/deploy [message]`
- **[harness-audit](skills/harness-audit/)** -- Audits your entire Claude Code harness against its purpose: enumerates every configurable surface (settings scopes, permission rules and modes, sandboxing, hooks, CLAUDE.md/rules hierarchy, auto memory, skills,...
- **[claude-md-doctor](skills/claude-md-doctor/)** -- Audits and rewrites a project's instruction files -- CLAUDE.md, folder-scoped files, path-scoped rules, AGENTS.md bridging -- into an operating manual a weaker model can execute: a scored audit across seven dimensions...
- **[attack-surface](skills/attack-surface/)** -- Builds and maintains a living attacksurface.md inventory of everything you have deployed -- per system: platform class, provider, auth method, exposure tier, criticality, matching CIS Benchmark checklist, and a...
- **[skill-graph](skills/skill-graph/)** -- Builds and queries a machine-readable graph of your skill pack: every skill becomes a node with its invocation, triggers, and the artifacts it produces and consumes; Pairs-with lines and workflow text become edges.

## Installation

Skills live in `~/.claude/skills/`. To install one:

```bash
# macOS / Linux / Windows (bash)
cp -r skills/llm-council ~/.claude/skills/
```

Or symlink the whole folder:

```bash
ln -s "$(pwd)/skills" ~/.claude/skills-shared
```

Then restart Claude Code. Invoke via `/skill-name`.

## Configuring for your project

Most skills include a `## Configure for your project` section near the top of their `SKILL.md` listing the placeholders you need to swap in for your repo. Common placeholders:

- `<project-root>` -- your repo's absolute path
- `<your-project-backlog-path>` -- where your backlog markdown files live
- `<state-dir>` -- where long-running skill state files are written
- `<src-path>` / `<core-path>` -- your source roots
- `<design-spec>` / `<DESIGN-DOC>` -- your design documentation
- `<PRODUCT_DESCRIPTION>` -- a one-paragraph description of what your project is (for council-style skills)
- `<dev-server-url>` -- usually `http://localhost:5173` or similar

Skills that need the most configuration: backlog, work-orders, marathon-*, council-*, gate-check, qa-sweep, spec-audit, systems-map, arch-diagram, agent-org. Open the SKILL.md and look for "EDIT THIS" callouts.

Many of the marketing skills look for a `.agents/product-marketing-context.md` file in your repo. Run `/product-marketing-context` once to create it -- every other marketing skill then references it for product, audience, and positioning context.

## Prerequisites

- **Browser skills** (`audit-page`, `review-ui`, `test-flow`, `perf-trace`, `qa-sweep`, `smoke-check`, `marathon-bughunter`, `preflight`) require the [Chrome DevTools MCP server](https://github.com/ChromeDevTools/chrome-devtools-mcp) to be connected.
- **llm-council** requires API keys for the models it polls (see [skills/llm-council/INSTALL.md](skills/llm-council/INSTALL.md)).
- **agent-org / marathon-org / work-orders-org** install a SQLite-backed comms bus + path-guard hook into your project (see [skills/agent-org/INSTALL.md](skills/agent-org/INSTALL.md)).
- **marathon-research / deep-research** use WebSearch and WebFetch; both ship with Claude Code. `deep-research` additionally benefits from firecrawl and exa MCPs.
- **deploy** assumes a CI/CD pipeline that triggers on push (Railway, Vercel, Netlify, GitHub Actions, etc.).
- **Backlog-aware skills** (`backlog`, `work-orders`, `work-orders-org`, `council-orders`, `council-rd`, `marathon-council`, `marathon-orders`, `marathon-org`, `marathon-condenser`, `user-feedback`, `scope-check`) require a backlog directory with `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, and `completed.md` files (each with a `<!-- Next ID: 001 -->` header).
- **Walkaway marathons** (`marathon-*`) require CronCreate support in your Claude Code build for self-scheduling.
- **create-onboarding-video** requires Remotion installed in the target project (`npm i remotion @remotion/cli`) and a `remotion-best-practices` skill in scope.
- **Design Intelligence skills** ship as SKILL.md + reference docs only -- the original `ui-ux-pro-max` python helper scripts and `ui-styling` canvas-fonts are not bundled here. Add them locally if you want the full tooling.

## Skill provenance

Skills in this repo come from several sources, all MIT-licensed or equivalent:

- **Original** -- Browser/QA, Multi-Agent/Council, Marathons, Backlog, Design & Decisions, Business/Strategy, Architecture, Dev Workflow.
- **[coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)** -- the 41-skill Marketing & Growth section.
- **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** -- the 7-skill Design Intelligence section.
- **[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)** -- investor-materials, investor-outreach, deep-research, content-engine, brand-voice, skill-stocktake, eval-harness, mcp-server-patterns.
- **[bidah/skill-set](https://github.com/bidah/skill-set)** -- create-onboarding-video.
- **[mattpocock/skills](https://github.com/mattpocock/skills)** -- handoff.

## What's not included

Some highly project-specific skills from the source library were intentionally not generalized because their value is tied to a specific game/business domain (game economy validators, cosmetic catalog generators, season planners, business-model-canvas notebooks, etc.). The patterns in `quick-design`, `systems-map`, `spec-audit`, and `reverse-doc` cover most of what those specialized skills did, generalized.

## License

MIT
