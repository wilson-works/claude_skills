# Claude Skills

A collection of reusable [Claude Code](https://claude.com/claude-code) skills for browser QA, multi-agent coordination, long-running autonomous sessions, backlog management, business strategy, dev workflow, and architecture work. Project-agnostic — drop them into any repo, swap a few placeholders, and go.

## Skills (33)

### Browser / QA (Chrome DevTools MCP)
- **[audit-page](skills/audit-page/)** — Lighthouse audit (performance, a11y, best practices, SEO) on a running page. `/audit-page [url]`
- **[review-ui](skills/review-ui/)** — Screenshot desktop + mobile, check console, report visual issues. `/review-ui [url]`
- **[test-flow](skills/test-flow/)** — Walk a user flow step-by-step with screenshots. `/test-flow [description]`
- **[perf-trace](skills/perf-trace/)** — Record a performance trace, analyze Core Web Vitals and bottlenecks. `/perf-trace [url]`
- **[qa-sweep](skills/qa-sweep/)** — Parameterized section audit: walks a section, verifies functionality, flags friction, returns severity-ranked findings. `/qa-sweep [section]`
- **[smoke-check](skills/smoke-check/)** — Fast post-implementation sanity check (build + secrets + key-page browser hit). Binary PASS/FAIL in ~2 minutes. `/smoke-check`
- **[preflight](skills/preflight/)** — Validates dev server, MCP, and auth state before other QA skills. `/preflight`

### Multi-Agent / Council
- **[llm-council](skills/llm-council/)** — Run a question through 5 AI advisors who independently analyze, peer-review, and synthesize a verdict. Based on Karpathy's LLM Council methodology. `/llm-council [question]`
- **[council-orders](skills/council-orders/)** — Convene a 5-member product council that files 25-30 prioritized work orders to your backlog in one session. `/council-orders [focus]`
- **[council-rd](skills/council-rd/)** — Per-research-folder mini-councils that pick the top 2-3 work orders from each report and emit an HTML approval tool. `/council-rd [research-root]`
- **[crew](skills/crew/)** — Multi-agent session coordination: callsigns, file ownership, conflict detection, inter-agent comms. `/crew [join|status|claim|...]`

### Long-Running Marathons (walkaway sessions)
- **[marathon-council](skills/marathon-council/)** — Rotates through focus areas, researches the codebase, convenes councils, files work orders. The intake half. `/marathon-council`
- **[marathon-orders](skills/marathon-orders/)** — Spawns 1-2 sub-agents per wave, each completing one work order with a review-and-merge gate. The execution half. `/marathon-orders`
- **[marathon-research](skills/marathon-research/)** — Processes a queue of research topics with WebSearch/WebFetch, produces cited markdown reports under 750 lines. `/marathon-research [topics]`
- **[marathon-bughunter](skills/marathon-bughunter/)** — Drives a Chrome DevTools browser through your app to hunt for new bugs introduced by recent work. `/marathon-bughunter`
- **[marathon-condenser](skills/marathon-condenser/)** — Condenses an oversized work order backlog: merges duplicates, closes already-completed items, rewrites vague entries, prunes stale ones. `/marathon-condenser`
- **[bg-pipeline](skills/bg-pipeline/)** — Run a sequence of skills as background sub-agents to keep your main session's context clean. `/bg-pipeline [pipeline]`
- **[caveman](skills/caveman/)** — Semantic text compression for long autonomous sessions. 40-58% token savings by stripping filler while preserving facts. `/caveman [on|off|compress]`

### Backlog & Work Orders
- **[backlog](skills/backlog/)** — View, add, close, and manage work order backlog items across categories (bugs, design, features, tech debt). `/backlog [command]`
- **[work-orders](skills/work-orders/)** — Triage the backlog and spawn sub-agents to execute prioritized items with a Sonnet-first context-brief pattern. `/work-orders [category]`
- **[user-feedback](skills/user-feedback/)** — Manage public user feedback in a dev review log; promote actionable items to the backlog. `/user-feedback [command]`

### Design & Decisions
- **[quick-design](skills/quick-design/)** — Lightweight spec for small feature/architecture changes that don't warrant a full council session. `/quick-design [change]`
- **[gate-check](skills/gate-check/)** — Formal milestone readiness validation (MVP, beta, GA, etc.) with multi-perspective review. PASS / CONCERNS / FAIL. `/gate-check [milestone]`
- **[scope-check](skills/scope-check/)** — Compares original work order or plan scope against actual git diff to detect scope creep. PASS / CONCERNS / FAIL. `/scope-check`
- **[retro](skills/retro/)** — Post-marathon or post-session retrospective from git log + backlog + plan files. Outputs 3-5 action items. `/retro`

### Business / Strategy (BMC brain)
- **[business-notes](skills/business-notes/)** — Capture strategy notes (marketing, pricing, partnerships, customer hypotheses) and auto-file them into a Business Model Canvas brain. Builds the business plan in parallel with the product. `/business-notes [command]`
- **[business-pass](skills/business-pass/)** — Proactively grow the BMC brain. Two modes: `scan` (autonomous codebase/app sweep extracting BMC evidence) and `interview` (Q&A to fill gaps in any of the 9 BMC blocks). `/business-pass [scan|interview]`
- **[business-roundtable](skills/business-roundtable/)** — Send a business note through a 5-advisor council (Marketing, Pricing, Customer Discovery, Competitor Watcher, Operations), finalize, then lock the verdict into the BMC brain. `/business-roundtable [NOTE-ID]`

### Architecture & Documentation
- **[arch-diagram](skills/arch-diagram/)** — Generates dark-themed SVG architecture diagrams from a configurable arch-config file. `/arch-diagram [view]`
- **[systems-map](skills/systems-map/)** — Maps interlocking systems in your codebase, produces a Mermaid diagram and dependency matrix to visualize ripple effects. `/systems-map`
- **[reverse-doc](skills/reverse-doc/)** — Generates missing spec docs from existing code via an intent-clarification step. `/reverse-doc [system]`
- **[spec-audit](skills/spec-audit/)** — Compares spec documents against component implementations to detect drift (tokens, mechanics, principles). `/spec-audit`

### Dev Workflow
- **[deploy](skills/deploy/)** — Commit staged changes and push to GitHub to trigger a CI/CD deploy. `/deploy [message]`

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

- `<project-root>` — your repo's absolute path
- `<your-project-backlog-path>` — where your backlog markdown files live
- `<state-dir>` — where long-running skill state files are written
- `<src-path>` / `<core-path>` — your source roots
- `<design-spec>` / `<DESIGN-DOC>` — your design documentation
- `<PRODUCT_DESCRIPTION>` — a one-paragraph description of what your project is (for council-style skills)
- `<dev-server-url>` — usually `http://localhost:5173` or similar

Skills that need the most configuration: backlog, work-orders, marathon-*, council-*, gate-check, qa-sweep, spec-audit, systems-map, arch-diagram. Open the SKILL.md and look for "EDIT THIS" callouts.

## Prerequisites

- **Browser skills** (`audit-page`, `review-ui`, `test-flow`, `perf-trace`, `qa-sweep`, `smoke-check`, `marathon-bughunter`, `preflight`) require the [Chrome DevTools MCP server](https://github.com/ChromeDevTools/chrome-devtools-mcp) to be connected.
- **llm-council** requires API keys for the models it polls (see [skills/llm-council/INSTALL.md](skills/llm-council/INSTALL.md)).
- **marathon-research** uses WebSearch and WebFetch; both ship with Claude Code.
- **deploy** assumes a CI/CD pipeline that triggers on push (Railway, Vercel, Netlify, GitHub Actions, etc.).
- **Backlog-aware skills** (`backlog`, `work-orders`, `council-orders`, `council-rd`, `marathon-council`, `marathon-orders`, `marathon-condenser`, `user-feedback`, `scope-check`) require a backlog directory with `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, and `completed.md` files (each with a `<!-- Next ID: 001 -->` header).
- **Walkaway marathons** (`marathon-*`) require CronCreate support in your Claude Code build for self-scheduling.

## What's not included

Some highly project-specific skills from the source library were intentionally not generalized because their value is tied to a specific game/business domain (game economy validators, cosmetic catalog generators, season planners, business-model-canvas notebooks, etc.). The patterns in `quick-design`, `systems-map`, `spec-audit`, and `reverse-doc` cover most of what those specialized skills did, generalized.

## License

MIT
