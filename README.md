# Claude Skills

A collection of reusable [Claude Code](https://claude.com/claude-code) skills for browser QA, multi-agent coordination, deploys, and long-running autonomous sessions. Project-agnostic — drop them into any repo.

## Skills

### Browser / QA (Chrome DevTools MCP)
- **[audit-page](skills/audit-page/)** — Lighthouse audit (performance, a11y, best practices, SEO) on a running page. `/audit-page [url]`
- **[review-ui](skills/review-ui/)** — Screenshot desktop + mobile, check console, report visual issues. `/review-ui [url]`
- **[test-flow](skills/test-flow/)** — Walk a user flow step-by-step with screenshots. `/test-flow [description]`
- **[perf-trace](skills/perf-trace/)** — Record a performance trace, analyze Core Web Vitals and bottlenecks. `/perf-trace [url]`

### Multi-Agent / Long Sessions
- **[llm-council](skills/llm-council/)** — Run a question through 5 AI advisors who independently analyze, peer-review, and synthesize a verdict. Based on Karpathy's LLM Council methodology. `/llm-council [question]`
- **[council-orders](skills/council-orders/)** — Convene a 5-member product council that files 25-30 prioritized work orders to your backlog in one session. `/council-orders [focus]`
- **[marathon-council](skills/marathon-council/)** — Long-running walkaway session (4-8 hrs) that rotates through focus areas, researches the codebase, and convenes councils each wave. Intake half of a continuous improvement loop. `/marathon-council`
- **[crew](skills/crew/)** — Multi-agent session coordination: callsigns, file ownership, conflict detection, inter-agent comms. `/crew [join|status|claim|...]`
- **[caveman](skills/caveman/)** — Semantic text compression for long autonomous sessions. 40-58% token savings by stripping filler while preserving facts. `/caveman [on|off|compress]`

### Dev Workflow
- **[deploy](skills/deploy/)** — Commit staged changes and push to GitHub to trigger a Railway deploy. `/deploy [message]`

## Installation

Skills live in `~/.claude/skills/`. To install one:

```bash
# macOS / Linux
cp -r skills/llm-council ~/.claude/skills/

# Windows (bash)
cp -r skills/llm-council ~/.claude/skills/
```

Or symlink the whole folder:

```bash
ln -s "$(pwd)/skills" ~/.claude/skills-shared
```

Then restart Claude Code. Invoke via `/skill-name`.

## Prerequisites

- **Browser skills** (`audit-page`, `review-ui`, `test-flow`, `perf-trace`) require the [Chrome DevTools MCP server](https://github.com/modelcontextprotocol/servers) to be connected.
- **llm-council** requires API keys for the models it polls (see [skills/llm-council/INSTALL.md](skills/llm-council/INSTALL.md)).
- **deploy** assumes a GitHub-connected Railway project.
- **council-orders** and **marathon-council** require a backlog directory with `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, and `completed.md` files (each with a `<!-- Next ID: 001 -->` header). Edit the `EDIT THESE` sections in each SKILL.md for your project paths and product context.
- **marathon-council** requires CronCreate support for walkaway sessions. Pairs with a `marathon-orders` skill (not included) for the execution half of the loop.

## License

MIT
