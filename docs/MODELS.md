# Model & Effort Routing

How this skill pack decides **which Claude model does which job**. The orchestration
skills (work-orders, marathons, councils, agent-org) follow these conventions.

## The model aliases

| Alias | Resolves to | Context | Use for |
|---|---|---|---|
| `opus` | Claude Opus 4.8 | 1M native | Architecture, review gates, deep research, judgment under ambiguity |
| `sonnet` | Claude Sonnet 5 | **1M native** | Implementation, refactors, context briefs, batch execution — the default worker |
| `haiku` | Claude Haiku 4.5 | 200K | Mechanical steps: formatting, log scans, cheap gates |
| `opusplan` | Opus in plan mode → Sonnet in execution | — | Hybrid interactive work |
| `inherit` | The parent session's model | — | Skills/agents that shouldn't change the caller's tier |

Sonnet 5 has 1M context natively — long marathon lanes no longer thin out on Sonnet
workers. Context discipline (`/caveman`, one-line comms reads) still pays: you're billed
for what you carry.

## The routing rule

**Opus decides, Sonnet ships, Haiku sweeps.**

| Role in a run | Model |
|---|---|
| Review / merge gate (John) | `opus` (at `effort: xhigh` — one cranked review per WO is the cheapest quality you can buy) |
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

## Two rules of thumb

1. **Never route a task to Opus that has not failed on Sonnet** — unless it's a review
   gate, cross-source synthesis, or an irreversibility decision. (`/marathon-orders` is
   the deliberate exception: its queue is depth work by definition.)
2. **A cheaper front-runner protects the expensive pass.** Sonnet scope-check before the
   Opus researcher; Sonnet context brief before the executor. Never cold-start an
   expensive agent on work a cheap summary could frame.

Version floors: `effort:` frontmatter needs Claude Code v2.1.145+, subagent `memory:`
needs v2.1.196+. Both are ignored harmlessly on older versions.
