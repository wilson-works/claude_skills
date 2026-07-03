---
name: agent-org
description: "An 18-agent organizational hierarchy with hard-ACL Slack-style channels. C-suite (Opus) directs, Tim (Opus) routes, department heads (Opus) review, juniors (Sonnet) ship. Each level has a SQLite-backed channel; juniors can't talk to the CTO; the path-guard hook enforces dept ownership. Project-agnostic - drop into any repo, edit org.config.json globs, go. Invoke with /agent-org or via the marathon-org / work-orders-org variants."
---

# agent-org Skill

A pre-built organizational chart for serious autonomous and semi-autonomous work. Eighteen agents with named personalities, fixed reporting lines, and a token-efficient communication bus that enforces who can talk to whom.

## The org

```
                          CEO (you, the human)
                                  |
                          James  ----  CTO (Opus)
                            |
                          John   ----  Chief Engineer (Opus, reviews every diff)
                            |
                          Tim    ----  Executive Assistant (Opus, the funnel)
                ___________|_______________
               /     |      |      |       \
            Cindy  Gavin  Diana  Rachel   Josh   <- Department Heads (Opus)
           backend frontend db    qa      api
            / \    / \    / \    / \     / \
        Marcus Priya Ava Kai Leo Nora Owen Maya Felix Zara   <- Juniors (Sonnet)
```

## The three channels

| Channel      | Members                                            | Purpose |
|--------------|----------------------------------------------------|---------|
| `c-suite`    | James, John, Tim                                   | Strategic direction, technical adjudication, status digest |
| `dept-heads` | Tim, Cindy, Gavin, Diana, Rachel, Josh             | Work orders, cross-department coordination, status |
| `dev-floor`  | All 5 heads + all 10 juniors                       | Implementation chatter, claims, peer review |

ACL is enforced in `comms.py` itself. A junior trying to post to `c-suite` gets exit-code 2 with an explanation. There is no soft path around it.

## The path guard

`hooks/path_guard.py` runs as a `PreToolUse` hook on Write/Edit/MultiEdit. Logic:

1. Get the file path being edited.
2. Look up active comms claims overlapping that path.
3. If a claim is held, the claiming agent's department must own the path per `org.config.json`. If not -> BLOCK.
4. If no claim is held, allow (assumed main-session work or shared code).

This means **agents must `comms claim` before editing**. Their system prompts already require this. The hook is the safety net.

## Roles in one sentence each

- **James (CTO):** sets technical priorities from the CEO, holds people accountable. Warm, stern, fair.
- **John (Chief Engineer):** owns architecture, reviews every diff. No fluff. Tells you what to fix and how.
- **Tim (Exec Assistant):** the only agent on both `c-suite` and `dept-heads`. Routes directives, summarizes status up, filters John into kindness.
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

## Configure for your project

Edit `<your-repo>/.claude/agents/org.config.json` (copy from `org.config.example.json`):

```json
{
  "departments": {
    "backend":  { "head": "cindy",  "owns": ["src/server/**", "src/services/**"] },
    "frontend": { "head": "gavin",  "owns": ["src/client/**", "*.css"] },
    "database": { "head": "diana",  "owns": ["migrations/**", "**/schema.sql"] },
    "qa":       { "head": "rachel", "owns": ["tests/**", "**/*.test.*"] },
    "api":      { "head": "josh",   "owns": ["src/api/**", "openapi.yaml"] }
  },
  "shared": ["README.md", ".claude/**", "docs/**"]
}
```

The roster (names, personalities, channel membership) is FIXED across projects. Only the path globs change. The personalities live in the agent `.md` files; the project-specific paths live in `org.config.json`.

## Invocation

The org runs end-to-end work orders. The entry point is the human (CEO) directing the CTO.

### One-shot directive
From the main session, simply invoke James:

```
Use the cto-james agent to handle this directive: "BUG-141 is a security blocker. Land it ahead of the dashboard work. I need a fix in main today."
```

James will:
1. Brief John (technical translation) and Tim (department routing) on `c-suite`.
2. Tim picks the right department head (Cindy for backend security) and posts on `dept-heads`.
3. Cindy briefs Marcus on `dev-floor`, Marcus claims and ships.
4. Cindy pre-reviews; passes diff up to Tim. Tim hands to John. John reviews. James gets the digest.

### Marathon
For unattended multi-order runs that route through the org:

```
/marathon-org bugs            # process bug backlog through the org
/marathon-org features        # process features through the org
/marathon-org all --wave 2    # 2 work orders at a time, all categories
```

`marathon-org` is the org-aware sibling of `marathon-orders` — same loop pattern, but every wave goes through James -> Tim -> dept head -> junior with the comms bus and claims active throughout.

### Direct work-order processing (no marathon)
```
/work-orders-org BUG-141      # route a single work order through the org
```

## Install

See [INSTALL.md](INSTALL.md). Three-step:

1. Copy `agents/*.md` into `<your-repo>/.claude/agents/`.
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

- Each agent only reads channels they're on. James never sees `dev-floor` chatter.
- `comms read` returns single-line headers by default; `--verbose` adds bodies.
- Bodies are capped at 2000 chars on post (truncated, not rejected).
- `--unread` uses a per-agent read cursor — no rescanning history.
- Dept heads pre-review before passing up, so John doesn't waste tokens on broken diffs.

## When NOT to use the org

- One-line trivial fix: just edit it. Don't spin up James to land a typo.
- Pure exploration / research: use `/marathon-research`, not the org.
- Decisions / strategy: use `/llm-council` for that, not the org.

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
├── org.config.example.json           per-project path ownership
├── comms/
│   ├── comms.py                      SQLite-backed CLI (ACL + claims)
│   └── schema.sql                    db schema
├── hooks/
│   ├── path_guard.py                 PreToolUse path-ownership enforcement
│   └── leak_guard.py                 PreToolUse credential/leak blocker (self-testing: --selftest)
├── agents/
│   ├── cto-james.md                  C-suite (3)
│   ├── chief-engineer-john.md
│   ├── exec-assistant-tim.md
│   ├── head-backend-cindy.md         Department heads (5)
│   ├── head-frontend-gavin.md
│   ├── head-database-diana.md
│   ├── head-qa-rachel.md
│   ├── head-api-josh.md
│   ├── junior-backend-marcus.md      Juniors (10)
│   ├── junior-backend-priya.md
│   ├── junior-frontend-ava.md
│   ├── junior-frontend-kai.md
│   ├── junior-database-leo.md
│   ├── junior-database-nora.md
│   ├── junior-qa-owen.md
│   ├── junior-qa-maya.md
│   ├── junior-api-felix.md
│   └── junior-api-zara.md
└── marathons/
    ├── marathon-org.md               unattended org-routed marathon
    └── work-orders-org.md            single-WO org-routed run
```
