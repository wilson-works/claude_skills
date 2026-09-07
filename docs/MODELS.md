# Model & Effort Routing

How this skill pack decides **which Claude model does which job**. The orchestration
skills (work-orders, marathons, councils, agent-org) follow these conventions.

Verified against code.claude.com docs, 2026-09-07:
[model-config](https://code.claude.com/docs/en/model-config.md) ·
[sub-agents](https://code.claude.com/docs/en/sub-agents.md).

## The model aliases

| Alias | Resolves to | Context | Use for |
|---|---|---|---|
| `opus` | Claude Opus 5 (`claude-opus-5`) | 1M native | Architecture, review gates, deep research, judgment under ambiguity |
| `sonnet` | Claude Sonnet 5 (`claude-sonnet-5`) | **1M native** | Implementation, refactors, context briefs, batch execution — the default worker |
| `haiku` | Claude Haiku 4.5 (`claude-haiku-4-5`) | 200K | Mechanical steps: formatting, log scans, cheap gates |
| `fable` | Claude Fable 5.1 (`claude-fable-5-1`) | 1M native | Review gates at both ends of a run, and the orchestrator on a Fable lane |
| `best` | Latest Fable where available, else `opus` | — | "The strongest thing you have" — non-reproducible by design |
| `default` | Clears the override; account-type default | — | Undoing a session-scoped `/model` change |
| `opusplan` | Opus in plan mode → Sonnet in execution | — | Hybrid interactive work |
| `inherit` | The parent session's model | — | Skills/agents that shouldn't change the caller's tier |

Sonnet 5 has 1M context natively — long marathon lanes no longer thin out on Sonnet
workers. `[1m]` on Sonnet 5 is therefore redundant, but it is still valid syntax and
still meaningful on models that are not 1M-native, so never strip it as a "fix".
Context discipline (`/caveman`, one-line comms reads) still pays: you're billed
for what you carry.

## The routing rule

**Opus decides, Sonnet ships, Haiku sweeps.**

| Role in a run | Model |
|---|---|
| Review / merge gate (John) | `opus` (at `effort: xhigh` — one cranked review per WO is the cheapest quality you can buy) |
| Orchestrator on a Fable lane; the compose and close gates of a run | `fable` — the highest output price in the lineup, so spend it where one call decides the shape of many, never per work order |
| Implementers (juniors, work-order agents) | `sonnet` — escalate a task to Opus only after it fails on Sonnet |
| Deep research synthesis (marathon-research) | `opus` |
| Scope checks, context briefs, distill/split passes | `sonnet` at `effort: low`/`medium` |
| Council/premortem advisors (breadth work) | `sonnet`; the chairman synthesis gets `opus` |
| Log collation, formatting | `haiku` |

## Where routing lives (precedence — highest wins)

1. `CLAUDE_CODE_SUBAGENT_MODEL` env var — overrides every subagent's model. The budget
   lever: `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` turns any org run into an all-Sonnet night
   with zero file edits.
2. The `model:` / `effort:` parameters on an individual Agent call (how the marathon
   skills route).
3. The agent file's `model:` / `effort:` frontmatter (this pack's standing assignments).
4. The main session model.

Skills can also pin `model:`/`effort:` in SKILL.md frontmatter — a one-turn override.

**Effort has its own ladder**, separate from the model one. Highest wins:
`CLAUDE_CODE_EFFORT_LEVEL` → `claude --effort <level>` → `/effort <level>` in-session →
per-model `"modelSettings"` in settings.json → top-level `"effortLevel"` → the model's
default (`high`). The levels are `low` `medium` `high` `xhigh` `max` `ultracode`;
`ultracode` is `xhigh` plus dynamic workflows and is worth it only when the agent has to
decide its own steps, not merely think harder about steps you already specified. The
per-model `modelSettings` block is the only way to pin effort per tier without editing
every agent file.

## Two rules of thumb

1. **Never route a task to Opus that has not failed on Sonnet** — unless it's a review
   gate, cross-source synthesis, or an irreversibility decision. (`/marathon-orders` is
   the deliberate exception: its queue is depth work by definition.)
2. **A cheaper front-runner protects the expensive pass.** Sonnet scope-check before the
   Opus researcher; Sonnet context brief before the executor. Never cold-start an
   expensive agent on work a cheap summary could frame.

Version floors: `effort:` frontmatter needs Claude Code v2.1.145+, subagent `memory:`
needs v2.1.196+. Both are ignored harmlessly on older versions.
